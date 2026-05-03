# Stage 3: Course Recommendation Model

> Construct a feasible, optimal learning pathway under real-world constraints.

---

## Objective

Given the **prioritised skill gap list** from [Stage 2](stage2_skill_gap.md) and the **user's constraints** from [Stage 1](stage1_user_profile.md), produce:

1. A **ranked, constraint-satisfying course sequence**
2. A **timeline-aware learning plan** that respects budget, time, and modality preferences
3. **Explainable scores** for each recommendation

---

## Pipeline Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         INPUTS                                    │
│  Prioritised Gap List (Stage 2) + Constraint Vector (Stage 1)    │
└──────────────────────────┬───────────────────────────────────────┘
                           │
     ┌─────────────────────┼──────────────────────┐
     ▼                     ▼                      ▼
┌──────────┐      ┌──────────────┐      ┌──────────────────┐
│   CSP    │      │     CBR      │      │   Fuzzy Logic    │
│Filtering │      │  Retrieval   │      │   Scoring        │
└────┬─────┘      └──────┬───────┘      └────────┬─────────┘
     │                   │                        │
     └───────────────────┼────────────────────────┘
                         ▼
              ┌──────────────────────┐
              │  Weighted Score      │
              │  Fusion              │
              └──────────┬───────────┘
                         ▼
              ┌──────────────────────┐
              │  Ranked Course       │
              │  Sequence + Timeline │
              └──────────────────────┘
```

---

## Component 1: Constraint Satisfaction Problem (CSP)

### Purpose
Filter and sequence courses to satisfy **hard constraints** (must-haves) while optimising for **soft constraints** (nice-to-haves).

### CSP Formulation

| Element | Description |
|---------|-------------|
| **Variables** | Course selection (which courses) + ordering (in what sequence) |
| **Hard Constraints** | Budget ceiling, maximum hours/week, required modality |
| **Soft Constraints** | Preferred schedule, course duration, provider preference |
| **Solver** | Backtracking with AC-3 (arc consistency) |

### Hard Constraints

| Constraint | Rule | Example |
|-----------|------|---------|
| **Budget** | Total cost ≤ user's budget (after subsidies) | Total ≤ SGD 3,000 |
| **Time** | Weekly commitment ≤ available hours | ≤ 10 hrs/week |
| **Modality** | Course delivery matches preference | Online only |
| **Prerequisites** | Course A must precede Course B | "Python Basics" before "ML Fundamentals" |
| **SkillsFuture Eligibility** | Only SSG-registered courses if specified | SkillsFuture Credit eligible |

### Soft Constraints

| Constraint | Flexibility | Handling |
|-----------|-------------|----------|
| **Preferred duration** | ±2 weeks tolerance | Fuzzy scoring |
| **Schedule preference** | Weekday/weekend/evening | Penalty for mismatch |
| **Provider preference** | Favoured but not required | Bonus score |

### Trade-Off Surfacing

If the CSP is **infeasible** (no solution satisfies all hard constraints), the system:

1. Identifies which constraint(s) are causing infeasibility
2. Proposes relaxations: *"Your budget covers 3 of 5 recommended courses. Would you like to extend your timeline or increase budget?"*
3. Generates the best partial solution with clear trade-off explanations

---

## Component 2: Case-Based Reasoning (CBR)

### Purpose
Retrieve **similar historical profiles** and adapt their learning paths to the current user's constraints.

### CBR Cycle

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ RETRIEVE │───▶│  REUSE   │───▶│  REVISE  │───▶│  RETAIN  │
│          │    │          │    │          │    │          │
│ Find     │    │ Adapt    │    │ Adjust   │    │ Store    │
│ similar  │    │ retrieved│    │ for new  │    │ new case │
│ cases    │    │ solution │    │ context  │    │ for      │
│          │    │          │    │          │    │ future   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### Similarity Matching

Cases are matched on:

| Feature | Weight | Distance Metric |
|---------|--------|-----------------|
| Current role | 0.20 | Semantic similarity |
| Target role | 0.25 | Semantic similarity |
| Skill overlap | 0.25 | Jaccard + cosine |
| Budget range | 0.15 | Normalised absolute difference |
| Time availability | 0.15 | Normalised absolute difference |

### Adaptation Rules

When adapting a retrieved case to the current user:

1. **Swap courses** that don't match the user's modality preference
2. **Reorder** based on the user's specific skill gap priorities
3. **Substitute** courses that exceed budget with equivalent alternatives
4. **Add/remove** courses based on skill vector differences

### Experiential Reasoning Output

CBR injects qualitative reasoning into explanations:

> *"Users with a similar background to yours typically started with a Python data science course before moving into machine learning. This path had an 85% completion rate and high satisfaction scores."*

---

## Component 3: Fuzzy Logic Reasoning

### Purpose
Handle **near-miss** scenarios where courses almost but don't quite satisfy constraints, avoiding rigid binary accept/reject decisions.

### Fuzzy Membership Functions

#### Budget Fitness

```
μ_budget(course_cost, user_budget):
    if course_cost ≤ user_budget:
        return 1.0                        # Fully within budget
    elif course_cost ≤ user_budget * 1.15:
        return 1.0 - (cost - budget) / (budget * 0.15)  # Slight overage
    else:
        return 0.0                        # Too expensive
```

#### Time Fitness

```
μ_time(course_hours, available_hours):
    if course_hours ≤ available_hours:
        return 1.0                        # Fits schedule
    elif course_hours ≤ available_hours * 1.2:
        return 1.0 - (hours - available) / (available * 0.2)  # Slight stretch
    else:
        return 0.0                        # Too time-intensive
```

#### Skill Relevance

```
μ_relevance(course_skills, gap_skills):
    overlap = len(course_skills ∩ gap_skills) / len(gap_skills)
    return overlap                        # Proportion of gaps addressed
```

### Fuzzy Output

Each course receives a **degree-of-satisfaction** score (0.0–1.0) for each soft constraint. Near-misses pass with flags:

```json
{
  "course": "Advanced ML with Python",
  "fuzzy_scores": {
    "budget_fitness": 0.85,
    "time_fitness": 0.92,
    "relevance": 0.95,
    "modality_match": 1.0
  },
  "flags": ["⚠️ Slightly over budget by SGD 75 — consider SkillsFuture credits"]
}
```

---

## Component 4: Weighted Score Fusion

### Purpose
Combine relevance, ratings, popularity, constraint fit into one **explainable composite score**.

### Fusion Formula

```
final_score = w₁ × relevance_score     # How well it fills skill gaps
            + w₂ × rating_score        # Course quality (learner ratings)
            + w₃ × constraint_score    # Budget/time/modality fit
            + w₄ × cbr_score          # Similar users' success
            + w₅ × popularity_score    # Market validation

Where (MVP weights, manually tuned):
  w₁ = 0.35  (relevance)
  w₂ = 0.20  (ratings)
  w₃ = 0.20  (constraints)
  w₄ = 0.15  (CBR)
  w₅ = 0.10  (popularity)
```

### Future Optimisation

MVP uses **manually tuned weights**. Post-MVP, weights will be optimised by:
- **MLP (Multi-Layer Perceptron)** — learn optimal weights from user satisfaction data
- **Genetic Algorithm** — evolve weight combinations for maximum engagement

---

## Sequencing Logic

After ranking individual courses, the system constructs a **learning path sequence**:

### Sequencing Rules

1. **Prerequisites first** — foundational courses before advanced
2. **Quick wins early** — high-relevance, low-difficulty courses to build momentum
3. **Parallel where possible** — non-dependent courses can run concurrently
4. **Budget pacing** — distribute costs across the timeline

### Timeline Generation

```
Month 1-2:  [Python for Data Science]     ← Foundation / Quick win
Month 2-3:  [Statistics & Probability]     ← Parallel with above
Month 3-5:  [Machine Learning Fundamentals]← Requires Python
Month 5-7:  [Deep Learning Specialisation] ← Requires ML
Month 7-8:  [Healthcare Data Analytics]    ← Domain knowledge
```

---

## Output Schema

```json
{
  "learning_path": {
    "total_courses": 5,
    "total_duration_weeks": 32,
    "total_cost": 2850,
    "total_cost_after_subsidy": 1200,
    "courses": [
      {
        "rank": 1,
        "course_id": "SF-PY-101",
        "title": "Python for Data Science",
        "provider": "NUS-ISS",
        "duration_weeks": 8,
        "cost": 500,
        "cost_after_subsidy": 150,
        "modality": "blended",
        "skills_covered": ["Python Programming", "Data Analysis"],
        "final_score": 0.92,
        "score_breakdown": {
          "relevance": 0.95,
          "rating": 0.88,
          "constraint_fit": 0.90,
          "cbr": 0.85,
          "popularity": 0.92
        },
        "sequence_position": "Month 1-2",
        "prerequisites": [],
        "flags": []
      }
    ],
    "trade_offs": [],
    "cbr_insight": "Users with similar profiles completed this path in ~8 months with a 78% completion rate."
  }
}
```

---

## IRS Techniques Applied

| Technique | Application in Stage 3 |
|-----------|----------------------|
| **Constraint Satisfaction (CSP)** | Hard/soft constraint filtering with backtracking + AC-3 |
| **Case-Based Reasoning (CBR)** | Historical profile matching and path adaptation |
| **Fuzzy Logic** | Degree-of-satisfaction scoring for near-miss constraint handling |
| **Weighted Score Fusion** | Multi-criteria ranking with explainable composite scores |

---

## Related Documentation

- [Stage 2: Skill Gap Model](stage2_skill_gap.md) — Producer of the prioritised gap list
- [RAG Explanation Engine](rag_explanation_engine.md) — How recommendations are explained to the user
- [Evaluation](evaluation.md) — How recommendation quality is measured
