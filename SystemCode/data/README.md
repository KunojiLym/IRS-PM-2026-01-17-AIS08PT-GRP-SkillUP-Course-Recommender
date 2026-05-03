# SkillUp Data Directory

This directory contains **source data files** under version control. These are gold standards, test fixtures, and local development fallbacks.

## 📂 Data Storage Architecture

```
Source Data (this directory - version controlled):
  /Workspace/Users/yzouyang-iss@u.nus.edu/skillup/data/
  ├── skill_mappings_gold.json      # Gold standard skill mappings
  ├── gold_standard_cvs.json        # Validated CV skill extractions
  ├── gold_standard_jds.json        # Validated JD skill extractions
  ├── test_profiles.json            # Test user profiles for validation
  ├── user_profiles.csv             # Local dev fallback
  ├── knowledge_graph.csv           # Local dev fallback
  └── skillsfuture_courses.csv      # Local dev fallback

Artifact Data (Volumes - NOT in git):
  /Volumes/workspace/default/iss-scratchpad/data/
  ├── processed_cvs/                # Processed CV data
  ├── processed_jds/                # Processed JD data
  ├── enriched_profiles/            # Enriched user profiles
  └── [generated outputs]           # Any generated/computed data
```

**Key Principle:** Source data (gold standards, test fixtures) stays in git. Generated/processed artifacts go to Volumes.

---

## 📋 Source Data Files (in this directory)

### Gold Standard Datasets

#### skill_mappings_gold.json
Verified skill-to-canonical-skill mappings for semantic similarity validation.
- **Purpose:** Technique validation (semantic similarity baseline)
- **Format:** `[{"raw": "...", "canonical": "...", "verified_by": "..."}]`
- **Used by:** Technique_Validation.ipynb

#### gold_standard_cvs.json
Manually validated CV skill extractions.
- **Purpose:** NER precision evaluation
- **Format:** `[{"cv_id": "...", "skills": [...], "verified": true}]`
- **Used by:** Technique_Validation.ipynb, NER evaluation

#### gold_standard_jds.json
Manually validated job description skill requirements.
- **Purpose:** Knowledge graph query validation
- **Format:** `[{"jd_id": "...", "role": "...", "skills": [...], "verified": true}]`
- **Used by:** Technique_Validation.ipynb, KG evaluation

#### test_profiles.json
Synthetic user profiles for CSP and CBR testing.
- **Purpose:** Constraint satisfaction and recommendation testing
- **Format:** `[{"user_id": "...", "skills": [...], "budget": ..., "preferences": {...}}]`
- **Used by:** Technique_Validation.ipynb, recommender tests

---

### Local Development Fallbacks

These CSV files are loaded when running outside Databricks (local development).

#### user_profiles.csv
Sample user profiles with skills, target roles, budget, and preferences.
- **Columns:** user_id, skills, target_role, budget, time_horizon, preferred_mode
- **Used by:** `skillgap.py` when `IN_DATABRICKS = False`
- **Note:** Small sample only (~10-20 users)

#### knowledge_graph.csv
Sample skill-to-role mappings from the knowledge graph.
- **Columns:** role, skill_name, demand_count, category, prerequisites
- **Used by:** `skillgap.py` for local skill gap analysis
- **Note:** Subset of full Neo4j graph

#### skillsfuture_courses.csv
Sample course catalog from SkillsFuture.
- **Columns:** course_title, provider, duration_hours, fee, skills_covered
- **Used by:** `recommender.py` for local course matching
- **Note:** Representative sample (~50-100 courses)

---

## 📦 Artifact Data (Volumes - not in this directory)

**Location:** `/Volumes/workspace/default/iss-scratchpad/data/`

Generated or processed data should be written to Volumes, not this git directory.

### Examples

```python
from pathlib import Path
from datetime import datetime
import json

# Artifact storage location
DATA_ARTIFACTS = Path("/Volumes/workspace/default/iss-scratchpad/data")

# Write processed CV batch
output_path = DATA_ARTIFACTS / "processed_cvs" / f"batch_{datetime.now().strftime('%Y%m%d')}.json"
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w') as f:
    json.dump(processed_data, f, indent=2)
```

### Artifact Categories
* `processed_cvs/` - Processed resume data with extracted skills
* `processed_jds/` - Processed job descriptions with requirements
* `enriched_profiles/` - User profiles with enriched metadata
* `recommendation_logs/` - Historical recommendation results
* `model_outputs/` - ML model predictions and embeddings

---

## 🔄 Usage Patterns

### In Notebooks (Databricks)

```python
from pathlib import Path

# Source data (read-only, version controlled)
DATA_DIR = Path("/Workspace/Users/yzouyang-iss@u.nus.edu/skillup/data")
gold_cvs = DATA_DIR / "gold_standard_cvs.json"

# Artifact data (write outputs here)
DATA_ARTIFACTS = Path("/Volumes/workspace/default/iss-scratchpad/data")
output = DATA_ARTIFACTS / "processed_cvs" / "batch_20250110.json"
```

### Automatic Fallback (Python modules)

```python
# In skillgap.py, recommender.py, etc.
try:
    dbutils  # noqa
    IN_DATABRICKS = True
    # Load from Delta tables
    df = spark.table("workspace.default.resume_dataset_1200")
except NameError:
    IN_DATABRICKS = False
    # Load from local CSV fallback
    import pandas as pd
    df = pd.read_csv("data/user_profiles.csv")
```

---

## 📊 Databricks Tables

Production data is stored in Unity Catalog tables:

| Table | Description |
|-------|-------------|
| `workspace.default.my_skills_future_course_directory` | Full SkillsFuture catalog |
| `workspace.default.job_description` | Job postings dataset |
| `workspace.default.resume_dataset_1200` | Resume corpus (1200 samples) |
| `workspace.default.knowledge_graph_output` | Neo4j knowledge graph export |
| `skillsup.gap_analysis.user_analysis_log` | User interaction logs |

---

## 🧪 Updating Test Data

### To update gold standards:
1. Run validation notebooks with manual verification
2. Export verified results to JSON
3. Update files in this directory
4. Commit to git with descriptive message

### To update CSV fallbacks:
1. Export small sample from Databricks tables
2. Convert to CSV maintaining schema
3. Save to this directory (max 100 rows per file)
4. Test with `IN_DATABRICKS = False`

---

## ⚠️ Important Notes

* **Never commit large files (>10MB)** to this directory
* **Never commit generated artifacts** - they belong in Volumes
* **Always validate data** before committing gold standards
* **Use `.gitignore`** to exclude temporary files
* **Document schema changes** when updating files

---

**Last Updated:** 2025-01-10  
**Maintainer:** yzouyang-iss@u.nus.edu
