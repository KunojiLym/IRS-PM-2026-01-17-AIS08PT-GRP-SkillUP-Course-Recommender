# RAG Explanation Engine

> Human-interpretable, auditable recommendations and explanations — no hallucinated facts, all grounded in retrieved records.

---

## Objective

Provide **transparent, trustworthy explanations** for every recommendation by:

1. **Tracing the reasoning chain** through all three pipeline stages
2. **Grounding all claims** in retrieved data (courses, skills, rules)
3. **Adapting dynamically** as the user progresses through their learning journey

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  RAG EXPLANATION ENGINE                          │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Retrieval Layer                               │  │
│  │                                                            │  │
│  │  ┌──────────┐  ┌──────────────┐  ┌─────────────────────┐ │  │
│  │  │ KG Data  │  │ Vector Store │  │ Reasoning Traces    │ │  │
│  │  │ (Neo4j)  │  │ (Embeddings) │  │ (Stages 1-2-3)      │ │  │
│  │  └────┬─────┘  └──────┬───────┘  └──────────┬──────────┘ │  │
│  │       └───────────────┬──────────────────────┘            │  │
│  └───────────────────────┼───────────────────────────────────┘  │
│                          ▼                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Generation Layer                              │  │
│  │                                                            │  │
│  │  LLM generates explanations by tracing:                   │  │
│  │    • Skill gaps from KG traversal (Stage 2)               │  │
│  │    • Expert arbitration outcomes (Stage 2)                │  │
│  │    • CSP constraint satisfaction (Stage 3)                │  │
│  │    • Confidence signals from scoring (Stage 3)            │  │
│  └───────────────────────┬───────────────────────────────────┘  │
│                          ▼                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Output: Grounded Explanations                 │  │
│  │                                                            │  │
│  │  Natural language explanations with source attribution     │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## How RAG Works in SkillUP

### Retrieval-Augmented Generation (RAG) Flow

```
User receives recommendation
    ↓
System retrieves supporting evidence:
  1. KG: Why this skill is a gap (role requirements, peer data)
  2. Vector Store: Similar courses and their outcomes
  3. Reasoning Traces: CSP decisions, fuzzy scores, CBR matches
    ↓
LLM synthesises evidence into natural language explanation
    ↓
Output: Grounded, attributable explanation
```

### Key Principle: No Hallucinated Facts

Every factual claim in an explanation must trace back to a **retrieved record**:

| Claim Type | Source | Example |
|-----------|--------|---------|
| "This skill is required for ML Engineers" | KG: `Role-[REQUIRES]→Skill` | 87% of MCF postings require it |
| "This course covers deep learning" | KG: `Course-[TEACHES]→Skill` | SSG course catalogue entry |
| "Similar users completed this in 6 months" | CBR case database | 12 matching historical profiles |
| "This fits your budget after SkillsFuture" | CSP constraint trace | SGD 500 - SGD 350 subsidy = SGD 150 |
| "Course rated 4.5/5" | Ratings database | 230 learner reviews averaged |

---

## Explanation Templates

### Per-Course Explanation

```markdown
### Why This Course?

**[Course Title]** by [Provider]

📊 **Skill Gap**: This course addresses your gap in **[Skill Name]**, which is 
required in [X]% of [Target Role] postings on MyCareersFuture.

👥 **Peer Insight**: [Y]% of professionals already in [Target Role] hold this 
skill, making it essential for your transition.

💰 **Budget Fit**: At SGD [Cost] (SGD [Subsidised] after SkillsFuture credits), 
this course fits within your monthly budget of SGD [Budget].

⏱️ **Time Fit**: [Duration] weeks at [Hours/week] hrs/week aligns with your 
availability of [Available] hrs/week.

⭐ **Quality**: Rated [Rating]/5 by [N] learners with a [Completion]% 
completion rate.

🔗 **Sequence**: This course builds on [Prerequisite] and prepares you for 
[Next Course].
```

### Full Learning Path Explanation

```markdown
## Your Personalised Learning Path

Based on your background as a **[Current Role]** aiming for **[Target Role]**, 
I've identified **[N] key skill gaps** and mapped them to a **[M]-month 
learning path**.

### Why This Path?

1. **Market-Driven**: These skills appear in [X]% of [Target Role] postings 
   in Singapore (MCF data, last 3 months).
   
2. **Peer-Validated**: Professionals who made similar transitions typically 
   acquired these skills in this order.

3. **Constraint-Aware**: Total cost SGD [Total] (SGD [Subsidised] after 
   subsidies), [Hours] hrs/week commitment, [Modality] delivery.

### Trade-Offs Made

- ⚠️ [Trade-off 1, e.g., "Course X is SGD 75 over your monthly budget — 
  consider using SkillsFuture credits for this month"]
- ✅ [Positive, e.g., "All courses are available in your preferred blended 
  modality"]
```

---

## Explanation Traceability

Each explanation includes **provenance metadata** so the user (or an auditor) can verify every claim:

```json
{
  "explanation": "This course addresses your gap in Deep Learning...",
  "provenance": [
    {
      "claim": "Deep Learning is required in 87% of ML Engineer postings",
      "source": "MCF_job_analysis",
      "query": "MATCH (r:Role {title:'ML Engineer'})-[:REQUIRES]->(s:Skill {name:'Deep Learning'}) ...",
      "timestamp": "2025-03-15"
    },
    {
      "claim": "Course rated 4.5/5 by 230 learners",
      "source": "course_ratings_db",
      "record_id": "SF-DL-001",
      "timestamp": "2025-03-10"
    }
  ]
}
```

---

## Adaptive Feedback Loop

The explanation engine doesn't stop after initial recommendations. It evolves as the user progresses.

### Feedback Loop Architecture

```
┌──────────────────────────────────────────────────────┐
│                   FEEDBACK LOOP                       │
│                                                       │
│  User completes a course                             │
│       ↓                                              │
│  Skill vector updated (remove completed gap)         │
│       ↓                                              │
│  Gap Model (Stage 2) reruns automatically            │
│       ↓                                              │
│  Remaining gaps re-prioritised                       │
│       ↓                                              │
│  Recommendation trimmed or extended dynamically      │
│       ↓                                              │
│  New explanations generated for updated path         │
│       ↓                                              │
│  SkillUP: one-off recommender → live career coach    │
└──────────────────────────────────────────────────────┘
```

### Adaptive Scenarios

| User Action | System Response |
|-------------|-----------------|
| Completes Course A | Removes covered skills from gap list; suggests next course |
| Drops a course | Suggests alternative; explains trade-offs |
| Budget changes | Re-runs CSP with new constraints; explains adjusted path |
| New job postings shift demand | Re-weights gaps; explains why priorities changed |
| User provides course feedback | Updates ratings; adjusts future recommendations |

---

## Anti-Hallucination Safeguards

| Safeguard | Implementation |
|-----------|----------------|
| **Fact grounding** | Every claim linked to a retrieved record |
| **Confidence thresholds** | Low-confidence claims flagged or omitted |
| **No fabricated courses** | Only recommend courses verified in the SSG catalogue |
| **No invented prices** | Prices sourced directly from course catalogue data |
| **Uncertainty disclosure** | When data is incomplete, say so explicitly |

### Example: Handling Uncertainty

```markdown
> I found several courses that could help with **MLOps**, but I don't have 
> enough data to rank them confidently. Here are your options — I'd recommend 
> checking the provider websites for the latest schedules:
>
> 1. [Course A] — covers 3 of 4 relevant skills
> 2. [Course B] — highest rated but schedule data may be outdated
```

---

## Related Documentation

- [Stage 3: Course Recommendation](stage3_course_recommendation.md) — Produces the recommendations to explain
- [Evaluation](evaluation.md) — Hallucination prevention rate metric
- [Architecture](architecture.md) — Where the RAG engine fits in the system
