# Stage 2: Skill Gap Model

> Determine which skills the user is missing relative to real labour market expectations. **Diagnosis, not prescription.**

---

## Objective

Given the user's current skill vector (from [Stage 1](stage1_user_profile.md)) and their target role, identify:

1. **Which skills are missing** — gaps between the user's current skills and target role requirements
2. **How important each gap is** — weighted by real labour market demand
3. **Initial candidate courses** — a pre-constraint set of courses that could fill each gap

This stage is purely **diagnostic** — it identifies *what* is missing, not *how* to fill it (that's [Stage 3](stage3_course_recommendation.md)).

---

## Pipeline Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                      INPUTS FROM STAGE 1                         │
│  Current Skill Vector · Target Role · Constraint Vector          │
└──────────────────────────┬───────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                                 ▼
┌──────────────────┐              ┌──────────────────┐
│   Knowledge      │              │   Embedding-     │
│   Graph          │              │   Based          │
│   Traversal      │              │   Similarity     │
└────────┬─────────┘              └────────┬─────────┘
         │                                 │
         └────────────┬────────────────────┘
                      ▼
         ┌────────────────────────┐
         │   Competing Experts    │
         │   Framework            │
         │                        │
         │  ┌──────┐  ┌────────┐ │
         │  │  JD  │  │ Peer   │ │
         │  │Demand│  │  CV    │ │
         │  │Expert│  │ Expert │ │
         │  └──┬───┘  └───┬────┘ │
         │     └────┬──────┘     │
         │          ▼            │
         │   Meta-Arbiter        │
         └──────────┬────────────┘
                    ▼
         ┌────────────────────────┐
         │  Prioritised Gap List  │
         │  + Candidate Courses   │
         └────────────────────────┘
```

---

## Component 1: Knowledge Graph Traversal

### Purpose
Identify skills required by the target role and compute paths from the user's current skill state through the Neo4j graph.

### How It Works

1. **Locate target role node** in the Knowledge Graph
2. **Traverse `REQUIRES` edges** to find all required skills
3. **Diff against user's current skill vector** to identify gaps
4. **Compute graph distance** from user's existing skills to missing skills (closer = easier transition)

### Example Query

```cypher
// Find skills required by target role that the user doesn't have
MATCH (target:Role {title: $target_role})-[:REQUIRES]->(needed:Skill)
WHERE NOT needed.name IN $user_skills
RETURN needed.name AS skill, 
       needed.category AS category,
       COUNT { (target)-[:REQUIRES]->(needed) } AS demand_weight
ORDER BY demand_weight DESC
```

### Graph Distance as Difficulty Signal

Skills that are **graph-adjacent** to the user's existing skills are easier to learn:

```
User knows: Python → [RELATED_TO, distance=1] → Data Analysis
User knows: Python → [RELATED_TO, distance=2] → Machine Learning
User knows: Python → [RELATED_TO, distance=3] → Deep Learning
```

**Closer graph distance** → lower learning curve → higher priority for quick wins.

---

## Component 2: Embedding-Based Similarity

### Purpose
Align user skills against required skills even when **terminology differs** between the user's CV and the knowledge graph.

### How It Works

1. **Encode user skills** using Sentence-BERT
2. **Encode target role skill requirements** using Sentence-BERT
3. **Compute cosine similarity** between all pairs
4. **Identify near-matches** (similarity 0.60–0.80) that partial credit should be given for
5. **Identify true gaps** (similarity < 0.60) that are genuinely missing

### Example Similarity Matrix

| User Skill | Required Skill | Cosine Similarity | Verdict |
|-----------|---------------|-------------------|---------|
| "Python scripting" | "Python development" | 0.94 | ✅ Match |
| "Excel reporting" | "Data visualisation" | 0.72 | ⚠️ Partial |
| *(none)* | "Deep learning" | 0.00 | ❌ Gap |
| "SQL queries" | "Database management" | 0.81 | ✅ Match |
| "Basic statistics" | "Statistical modelling" | 0.68 | ⚠️ Partial |

### Partial Credit Handling

Skills with partial matches receive a **reduced gap weight**:

```
gap_weight = 1.0 - similarity_score
```

- Full gap (similarity < 0.30): `weight ≈ 1.0`
- Partial match (0.30–0.80): `weight ≈ 0.20–0.70`
- Full match (> 0.80): `weight ≈ 0.0` (not a gap)

---

## Component 3: Competing Experts Framework

### Purpose
Combine multiple signals to determine the **true importance** of each skill gap, resolving disagreements through arbitration.

### Expert 1: Job Demand Expert

Analyses skills **frequently appearing in recent Singapore job postings** for the target role.

| Signal | Source | Weight |
|--------|--------|--------|
| Skill frequency in MCF postings | Knowledge Graph | 0.4 |
| Trend direction (growing/stable/declining) | MCF historical data | 0.2 |
| Salary premium for skill | MCF salary data | 0.2 |
| Posting recency (last 3 months weighted higher) | MCF timestamps | 0.2 |

**Output:** Demand-weighted skill importance scores

### Expert 2: Peer CV Expert

Analyses skills **common in CVs of professionals already in the target role**.

| Signal | Source | Weight |
|--------|--------|--------|
| Skill prevalence in peer CVs | CV database | 0.5 |
| Skill co-occurrence patterns | CV database | 0.3 |
| Experience level alignment | CV database | 0.2 |

**Output:** Peer-benchmarked skill importance scores

### Meta-Arbiter: Unified Gap List

The Meta-Arbiter resolves disagreements between experts:

```
unified_score = α × demand_score + β × peer_score + γ × graph_distance_score

Where:
  α = 0.45  (labour market demand weight)
  β = 0.35  (peer benchmark weight)
  γ = 0.20  (learning difficulty weight — inverted graph distance)
```

**Conflict resolution rules:**
1. If both experts agree a skill is critical → **high priority gap**
2. If only demand expert flags it → likely an **emerging skill** (include with note)
3. If only peer expert flags it → likely a **soft/foundational skill** (include but lower priority)
4. If neither flags it → **not a meaningful gap** (exclude)

---

## Output Schema

```json
{
  "skill_gaps": {
    "target_role": "Machine Learning Engineer",
    "total_gaps": 5,
    "gaps": [
      {
        "skill": "Deep Learning",
        "category": "Technical",
        "gap_weight": 0.95,
        "demand_score": 0.92,
        "peer_score": 0.88,
        "graph_distance": 2,
        "priority": "critical",
        "rationale": "Required in 87% of ML Engineer postings; present in 91% of peer CVs"
      },
      {
        "skill": "MLOps",
        "category": "Technical",
        "gap_weight": 0.82,
        "demand_score": 0.85,
        "peer_score": 0.65,
        "graph_distance": 3,
        "priority": "high",
        "rationale": "Growing demand (+40% YoY); emerging skill not yet common in peer CVs"
      },
      {
        "skill": "Healthcare Domain Knowledge",
        "category": "Domain",
        "gap_weight": 0.70,
        "demand_score": 0.60,
        "peer_score": 0.75,
        "graph_distance": 4,
        "priority": "medium",
        "rationale": "Required for healthcare ML roles; common in peer CVs but less in general postings"
      }
    ],
    "candidate_courses": [
      {"course_id": "SF-DL-001", "covers_skills": ["Deep Learning"], "pre_constraint": true},
      {"course_id": "SF-MLO-012", "covers_skills": ["MLOps"], "pre_constraint": true},
      {"course_id": "SF-HC-045", "covers_skills": ["Healthcare Domain Knowledge"], "pre_constraint": true}
    ]
  }
}
```

---

## IRS Techniques Applied

| Technique | Application in Stage 2 |
|-----------|----------------------|
| **Graph-Based Reasoning** | Neo4j KG traversal to identify skill requirements and learning paths |
| **Inference Under Uncertainty** | Embedding similarity for partial matches; confidence-weighted gap scores |
| **Multi-Expert Arbitration** | Competing Experts (JD Demand + Peer CV) with Meta-Arbiter fusion |

---

## Related Documentation

- [Stage 1: User Profile Model](stage1_user_profile.md) — Producer of the input skill vector
- [Stage 3: Course Recommendation](stage3_course_recommendation.md) — Consumer of the gap list
- [Data Pipeline](data_pipeline.md) — How the KG and vector store are built
