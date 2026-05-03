# Stage 1: User Profile Model

> Infer a structured representation of who the user is and what they are trying to achieve.

---

## Objective

Transform a user's **raw CV** and **conversational inputs** into a structured profile containing:

1. **Current Skill Vector** — skills with confidence weights
2. **Target Role** — desired career direction
3. **Constraint Vector** — budget, time, modality, timeline preferences

This structured profile feeds directly into [Stage 2: Skill Gap Model](stage2_skill_gap.md).

---

## Pipeline Overview

```
┌───────────┐    ┌───────────────┐    ┌──────────────┐    ┌────────────────┐
│  Raw CV   │───▶│  LLM-Assisted │───▶│  Rule-Based  │───▶│   Semantic     │
│  Upload   │    │  Extraction   │    │  Validation  │    │   Embeddings   │
└───────────┘    └───────────────┘    └──────────────┘    └────────────────┘
                                                                  │
┌───────────┐                                                     │
│ Onboarding│─────────────────────────────────────────────────────▶│
│   Chat    │   (collects intent, target, constraints)            │
└───────────┘                                                     ▼
                                                         ┌────────────────┐
                                                         │ Structured     │
                                                         │ User Profile   │
                                                         └────────────────┘
```

---

## Component 1: LLM-Assisted Extraction

### Purpose
Parse the uploaded CV to identify roles, skills, tools, and years of experience using large language model information extraction.

### Current Implementation (`app/cv_parser.py`)

The existing implementation uses OpenAI GPT-4 Mini to extract:

| Field | Description | Example |
|-------|-------------|---------|
| `name` | User's first name | "Wei Lin" |
| `current_role` | Current job title | "Senior Data Analyst" |
| `location` | City/country if visible | "Singapore" |
| `summary` | 2–3 sentence background summary | "5 years in data analytics..." |

### Planned Enhancements

The extraction should be extended to capture:

| Field | Description | Example |
|-------|-------------|---------|
| `skills` | List of extracted skills with confidence | `[{"skill": "Python", "confidence": 0.95}, ...]` |
| `experience_years` | Total years of professional experience | `7` |
| `education` | Highest qualification + field | `"BSc Computer Science"` |
| `industries` | Industries worked in | `["Finance", "Technology"]` |
| `tools` | Specific tools and platforms | `["Tableau", "SQL Server", "AWS"]` |
| `certifications` | Professional certifications | `["PMP", "AWS SAA"]` |

### Implementation Approach

```
Input: Raw CV text (up to 4,000 characters)
    ↓
LLM extracts structured JSON with all profile fields
    ↓
Output: Raw extracted profile (unvalidated)
```

**Prompt strategy:**
- System prompt defines the exact JSON schema expected
- CV text passed as user message
- Temperature set low (0.3) for consistency
- Response parsed with robust fallback handling

---

## Component 2: Rule-Based Validation

### Purpose
Enforce schema consistency to ensure auditable inputs for downstream reasoning stages.

### Validation Rules

| Rule | Description | Action |
|------|-------------|--------|
| **Invalid Skill Removal** | Skills not in the canonical taxonomy | Remove or flag for review |
| **Experience Bounding** | Experience years must be 0–50 | Clamp to valid range |
| **Duplicate Merging** | "Python" and "Python 3" → single entry | Merge, keep highest confidence |
| **Confidence Normalisation** | All confidence scores in [0, 1] | Normalise if out of range |
| **Required Field Defaults** | Missing fields get safe defaults | Apply defaults |

### Validation Pipeline

```python
# Pseudocode
def validate_profile(raw_profile: dict) -> dict:
    profile = raw_profile.copy()
    
    # 1. Validate and normalise skills
    profile["skills"] = [
        s for s in profile["skills"]
        if s["skill"] in CANONICAL_TAXONOMY
    ]
    
    # 2. Merge duplicates
    profile["skills"] = merge_duplicate_skills(profile["skills"])
    
    # 3. Bound experience
    profile["experience_years"] = max(0, min(50, profile["experience_years"]))
    
    # 4. Normalise confidence scores
    for s in profile["skills"]:
        s["confidence"] = max(0.0, min(1.0, s["confidence"]))
    
    return profile
```

---

## Component 3: Semantic Embeddings

### Purpose
Normalise skills via Sentence-BERT so that semantically equivalent terms map to a unified representation.

### Examples of Semantic Normalisation

| CV Text | Normalised Skill | Similarity Score |
|---------|-----------------|-----------------|
| "data wrangling" | Data Preparation | 0.92 |
| "ETL basics" | Data Preparation | 0.87 |
| "Python scripting" | Python Programming | 0.94 |
| "ML engineering" | Machine Learning | 0.89 |
| "agile methodology" | Agile Development | 0.91 |

### Embedding Pipeline

```
User's extracted skills (raw text)
    ↓
Sentence-BERT encoding (e.g., all-MiniLM-L6-v2)
    ↓
Cosine similarity against canonical skill embeddings
    ↓
Map to nearest canonical skill (if similarity > threshold)
    ↓
Output: Normalised skill vector with confidence weights
```

**Threshold:** Cosine similarity ≥ 0.80 for automatic mapping; 0.60–0.80 flagged for review.

---

## Component 4: Conversational Profile Collection (Maya Chatbot)

### Purpose
Collect the remaining profile fields through natural conversation that the CV cannot provide.

### Current Implementation (`app/llm.py`)

The Maya chatbot collects **5 required fields**, one at a time:

| Field | Description | Example Values |
|-------|-------------|----------------|
| `intent` | Switching careers OR advancing in current role | "Switch to a new field" |
| `target` | Target role / industry / advancement goal | "Data Scientist in healthcare" |
| `skill_gaps` | Self-perceived skill gaps | "Not sure about statistics" |
| `time_commit` | Available time (hrs/week + course length) | "10 hrs/week, 3-month courses" |
| `budget` | Budget range for courses/programmes | "SGD 500/month, use SkillsFuture credits" |

### Conversation Flow

```
1. CV Upload → Auto-extraction
2. Personalised greeting (references CV specifics)
3. Ask: Career direction (intent)
4. Ask: Target role (target)
5. Ask: Perceived gaps (skill_gaps)
6. Ask: Time availability (time_commit)
7. Ask: Budget range (budget)
8. Profile complete → Trigger plan generation
```

### Design Principles
- **Warm, human, never robotic** — one question per reply
- **Personalised suggestion chips** — 2–4 context-aware quick replies per question
- **Graceful handling of vagueness** — probe once, then move on
- **Acknowledge before transitioning** — warm acknowledgment of each answer
- **Never re-ask collected fields** — system tracks state

---

## Output Schema

The completed User Profile Model produces:

```json
{
  "user_profile": {
    "name": "Wei Lin",
    "current_role": "Senior Data Analyst",
    "location": "Singapore",
    "experience_years": 7,
    "education": "BSc Computer Science, NUS",
    "industries": ["Finance", "Technology"],
    
    "skill_vector": [
      {"skill": "Python Programming", "confidence": 0.95},
      {"skill": "SQL", "confidence": 0.90},
      {"skill": "Data Visualisation", "confidence": 0.85},
      {"skill": "Statistics", "confidence": 0.70}
    ],
    
    "target": {
      "role": "Machine Learning Engineer",
      "industry": "Healthcare",
      "intent": "career_switch"
    },
    
    "constraints": {
      "budget_monthly": 500,
      "skillsfuture_credits": true,
      "hours_per_week": 10,
      "preferred_duration": "3_months",
      "modality": "blended",
      "perceived_gaps": ["deep learning", "healthcare domain knowledge"]
    }
  }
}
```

---

## IRS Techniques Applied

| Technique | Application in Stage 1 |
|-----------|----------------------|
| **Knowledge Representation** | Structured skill vectors and constraint schemas |
| **Rule-Based Reasoning** | Validation rules for schema consistency |
| **Semantic Similarity** | Sentence-BERT normalisation of skill terminology |

---

## Related Documentation

- [Architecture](architecture.md) — Where Stage 1 fits in the overall pipeline
- [Data Pipeline](data_pipeline.md) — How canonical skill taxonomy is built
- [Stage 2: Skill Gap Model](stage2_skill_gap.md) — Consumer of the user profile
