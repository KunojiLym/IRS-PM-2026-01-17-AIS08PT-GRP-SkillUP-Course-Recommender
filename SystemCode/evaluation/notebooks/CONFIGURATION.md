# Notebook Configuration Guide

Standardized paths and configuration for all SkillUp evaluation notebooks.

## 🗂️ Directory Structure

```
/Workspace/Users/{username}/skillup/
├── evaluation/
│   ├── notebooks/                          # All evaluation notebooks (this folder)
│   │   ├── Technique_Validation.ipynb
│   │   ├── Test_Runner.ipynb
│   │   ├── Quick_Smoke_Tests.ipynb
│   │   ├── Coverage_Analysis.ipynb
│   │   ├── Recommender_Evaluation.ipynb
│   │   ├── Data_Quality_Evaluation.ipynb
│   │   ├── E2E_Pipeline_Evaluation.ipynb
│   │   ├── README.md
│   │   └── CONFIGURATION.md (this file)
│   ├── technique_validation.py             # Shared validation utilities
│   ├── uat_survey_template.md
│   └── STATUS_UPDATE.md
├── data/                                   # Source data (version controlled)
│   ├── skill_mappings_gold.json
│   ├── gold_standard_cvs.json
│   ├── gold_standard_jds.json
│   └── test_profiles.json
└── ... (other modules)

/Volumes/workspace/default/iss-scratchpad/  # Persistent artifact storage
├── evaluation/                             # Evaluation artifacts
│   ├── baseline_YYYYMMDD.json
│   ├── validation_YYYYMMDD.log
│   └── historical/
└── data/                                   # Data artifacts (generated/processed)
    ├── processed_cvs/
    ├── processed_jds/
    └── enriched_profiles/
```

---

## 📍 Standard Path Configuration

Copy this configuration block into **Cell 2 or 3** of every notebook:

```python
import sys
from pathlib import Path
from datetime import datetime

# ============================================================================
# PATH CONFIGURATION (Standard for all notebooks)
# ============================================================================

# Dynamic REPO_ROOT detection (works for any user)
try:
    # Try spark.conf first (works on Serverless)
    notebook_path = spark.conf.get("spark.databricks.notebook.path")
except:
    # Fallback to dbutils for classic compute
    try:
        notebook_path = dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
    except:
        # Last resort - use current working directory
        notebook_path = str(Path.cwd())
        print("⚠️  Could not detect notebook path, using current directory")

# Convert notebook path to workspace path and derive repo root
# notebook_path is like: /Users/{username}/skillup/evaluation/notebooks/NotebookName
if notebook_path.startswith("/"):
    workspace_path = Path("/Workspace") / notebook_path.lstrip("/")
else:
    workspace_path = Path(notebook_path)

# Navigate up from notebooks -> evaluation -> skillup (repo root)
REPO_ROOT = workspace_path.parent.parent.parent if "notebooks" in str(workspace_path) else workspace_path

# Source data directory (version controlled)
DATA_DIR = REPO_ROOT / "data"

# Persistent artifact storage (Volumes - shared, not in git)
EVAL_ARTIFACTS = Path("/Volumes/workspace/default/iss-scratchpad/evaluation")
DATA_ARTIFACTS = Path("/Volumes/workspace/default/iss-scratchpad/data")

# Ensure artifact directories exist
EVAL_ARTIFACTS.mkdir(parents=True, exist_ok=True)
DATA_ARTIFACTS.mkdir(parents=True, exist_ok=True)

# Add skillup to Python path for imports
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

print(f"📁 REPO_ROOT: {REPO_ROOT}")
print(f"📁 DATA_DIR (source): {DATA_DIR}")
print(f"📦 EVAL_ARTIFACTS: {EVAL_ARTIFACTS}")
print(f"📦 DATA_ARTIFACTS: {DATA_ARTIFACTS}")
```

### Key Features:
* **Dynamic path detection**: Works for any username, no hardcoding required
* **Serverless compatible**: Uses `spark.conf` as primary detection method
* **Multiple fallbacks**: Classic compute (dbutils), local execution (cwd)
* **Automatic path derivation**: Calculates repo root from notebook location
* **Idempotent imports**: Checks if REPO_ROOT already in sys.path before adding

---

## 🔑 Databricks Secrets Access

Environment secrets from app.yaml are available as Databricks secrets.
See README.md for detailed examples.

**Scope name:** skillup

**Common keys:** NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, OPENAI_API_KEY

---

**Last Updated:** 2026-04-25  
**Maintainer:** yzouyang-iss@u.nus.edu
