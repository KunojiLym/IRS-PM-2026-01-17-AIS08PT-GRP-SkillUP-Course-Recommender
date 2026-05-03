# SkillUp Evaluation Notebooks

Comprehensive testing and evaluation suite for the SkillUp IRS project. These Databricks notebooks provide systematic validation of recommendation techniques, test execution, and coverage analysis.

> **⚡ Quick Links:** [Configuration Guide](./CONFIGURATION.md) | [Migration Summary](../NOTEBOOK_MIGRATION.md) | [Data Directory](../../data/README.md)

## 📁 Notebooks Overview

### 1. **Technique_Validation.ipynb** (ID: 1353956204946915)
**Purpose:** Validates 8 IRS recommendation techniques against gold standard datasets

**Techniques Evaluated:**
* Semantic Similarity (Sentence Transformers)
* Knowledge Graph Queries (Neo4j traversal)
* Named Entity Recognition (spaCy NER)
* Constraint Satisfaction Problem (CSP solver)
* Case-Based Reasoning (CBR retrieval)
* Fuzzy Logic (skill-course matching)
* Competing Experts (ensemble voting)
* RAG (Retrieval Augmented Generation)

**Key Features:**
* 24 cells: configuration, data loading, technique execution, metrics calculation
* Gold standard validation using precision@K, recall@K, nDCG, MRR
* Artifact storage: `/Volumes/workspace/default/iss-scratchpad/evaluation/baseline_YYYYMMDD.json`
* Runtime: ~5-10 minutes per full run

**Usage:**
```python
# Cell 1: Run all cells sequentially
# Cell 23: View final metrics summary
# Output: JSON artifact with technique comparison
```

---

### 2. **Test_Runner.ipynb** (ID: 984473343373211)
**Purpose:** Comprehensive pytest test suite execution

**Test Categories:**
* All unit tests (`!python -m pytest tests/`)
* Module-specific tests (KG, SG, Recommender, App)
* Smoke tests (fast validation)
* Coverage report generation
* Integration tests (end-to-end)
* Custom test patterns

**Key Features:**
* 21 cells: organized by test scope and module
* Simple shell command execution with `!python -m pytest`
* Inline test output with pass/fail indicators
* Coverage thresholds: Overall ≥80%, KG 80%+, SG 75%+, Recommender 85%+, App 70%+

**Usage:**
```bash
# Run all tests
!python -m pytest tests/ -v

# Run specific module
!python -m pytest tests/unit/knowledgegraph/ -v

# Run with coverage
!python -m pytest tests/ --cov=. --cov-report=term-missing
```

---

### 3. **Quick_Smoke_Tests.ipynb** (ID: 984473343373212)
**Purpose:** Fast validation checks (<30 seconds total)

**Checks Performed:**
* Module imports (KG, SG, Recommender, App)
* Neo4j knowledge graph connectivity
* Skill Gap API endpoints
* Recommender system initialization
* Data file presence (gold standards, mappings)
* Databricks table accessibility

**Key Features:**
* 14 cells: rapid health checks with timing
* ✅/❌/⚠️ status indicators for quick scanning
* Ideal for pre-commit validation
* No external API calls (except Neo4j ping)

**Usage:**
```python
# Run all cells sequentially (Ctrl+Shift+Enter)
# Check for any ❌ indicators
# Typical runtime: 15-25 seconds
```

---

### 4. **Coverage_Analysis.ipynb** (ID: 984473343373213)
**Purpose:** Detailed code coverage reporting and threshold validation

**Analysis Sections:**
* Terminal coverage report
* HTML coverage report generation
* Module-level coverage breakdown
* Threshold validation (with pass/fail)
* Uncovered lines identification
* Coverage trend analysis (optional)

**Key Features:**
* 17 cells: comprehensive coverage metrics
* HTML report: `{REPO_ROOT}/htmlcov/index.html`
* XML report: `coverage.xml` (for CI/CD)
* Module targets: KG 80%+, SG 75%+, Recommender 85%+, App 70%+

**Usage:**
```bash
# Generate coverage report
!python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# View HTML report (opens in browser)
displayHTML("<a href='/htmlcov/index.html' target='_blank'>Open Coverage Report</a>")

# Validate thresholds
!python -m pytest tests/ --cov=. --cov-fail-under=80
```

---

### 5. **Recommender_Evaluation.ipynb** (ID: 3792847049696744)
**Purpose:** Direct evaluation of course recommender system quality (serverless-compatible)

**Evaluation Features:**
* Live testing mode: On-demand recommendation generation for test scenarios
* Saved paths mode: Batch evaluation of pre-generated recommendations
* Reasoning trace analysis from recommender pipeline
* Metrics calculation directly from LearningPath objects
* Test scenario validation across different user profiles

**Key Features:**
* 27 cells: test scenarios, evaluation metrics, visualization
* Performance optimized: Pandas batch conversion (10-100x faster)
* Test modes: Limited (500 courses) or full catalog (50,000+ courses)
* Metrics: Skill gap coverage, weighted coverage, constraint satisfaction
* Direct testing approach (MLflow-free for serverless compatibility)

**Test Scenarios:**
* Data Analyst → Data Engineer (budget, time, modality constraints)
* Admin Assistant career transitions
* Budget optimization and SkillsFuture eligibility
* Multi-skill gap coverage validation

**Usage:**
```python
# Cell 1-5: Setup and imports
# Cell 13: Run test scenario 1 (Data Engineer transition)
# Cell 15+: Load course catalog and generate recommendations
# Outputs: Evaluation metrics, constraint validation, reasoning traces
```


### 6. **Data_Quality_Evaluation.ipynb** (ID: 3792847049696802)
**Purpose:** Comprehensive data quality assessment across all SkillUP datasets

**Quality Dimensions Evaluated:**
* **Completeness**: % of required fields populated (target: ≥95%)
* **Validity**: Data conforms to expected formats/ranges
* **Consistency**: No duplicates, relationships are valid (target: ≥98% integrity)
* **Freshness**: Data is up-to-date (identify stale records >90 days)
* **Coverage**: Sufficient breadth across skill domains (target: ≥80%)

**Key Features:**
* 15 cells: course catalog validation, knowledge graph integrity, missing value analysis
* Evaluation outputs: JSON quality report, CSV analyses
* Artifact storage: `/Volumes/workspace/default/iss-scratchpad/evaluation/`
* Metrics: completeness scores, freshness analysis, field-level missing value rates
* Visualizations: missing data heatmaps, completeness scores, age distributions

**Datasets Evaluated:**
* Course Catalog: title, provider, duration, cost, prerequisites completeness
* Knowledge Graph: node/edge integrity, orphaned nodes, relationship validity
* Skill Taxonomy: coverage across job market skills

**Usage:**
```python
# Cell 1-3: Setup and configuration
# Cell 4-12: Run quality checks across all datasets
# Cell 15: Export quality report
# Outputs: data_quality_report.json, missing_values_analysis.csv, course_freshness_analysis.csv
```

---

### 7. **E2E_Pipeline_Evaluation.ipynb** (ID: 3792847049696801)
**Purpose:** End-to-end pipeline evaluation from CV input through all three stages

**Pipeline Stages Evaluated:**
* **Stage 1**: Named Entity Recognition (NER) - Extract skills from CV/JD
* **Stage 2**: Skill Gap Analysis - Identify gaps between CV and JD
* **Stage 3**: Course Recommendations - Suggest courses to fill gaps

**Key Metrics:**
* **Pipeline Success Rate**: % of test cases completing all stages without errors (target: ≥90%)
* **Stage Latency**: Time taken at each stage (p50, p95, p99)
* **End-to-End Latency**: Total time from CV input to recommendations (target: p95 ≤500ms)
* **Quality Propagation**: How errors in Stage 1 affect Stage 2 and 3 quality
* **Error Analysis**: Cascading failure patterns and recovery rates

**Key Features:**
* 13 cells: test data loading, pipeline execution, latency analysis, error propagation
* Stage-wise success tracking with detailed error logging
* Artifact storage: `/Volumes/workspace/default/iss-scratchpad/evaluation/`
* Visualizations: success rates by stage, latency distributions, error propagation
* Test scenarios: CV-JD matching across different career transitions

**Usage:**
```python
# Cell 1-3: Setup and path configuration
# Cell 4-7: Execute end-to-end pipeline tests
# Cell 8-12: Calculate metrics and visualizations
# Cell 13: Export results
# Outputs: e2e_pipeline_results.csv, e2e_pipeline_evaluation_YYYYMMDD_HHMMSS.json
```

---

## 🔧 Configuration



### Repository Paths
```python
# Repository root
REPO_ROOT = Path("/Workspace/Users/{user}/skillup")

# Data directories (local repo)
DATA_DIR = REPO_ROOT / "data"

# Artifact storage (Volumes - persistent)
EVAL_ARTIFACTS = Path("/Volumes/workspace/default/iss-scratchpad/evaluation")
DATA_ARTIFACTS = Path("/Volumes/workspace/default/iss-scratchpad/data")
```

### Databricks Secrets Access

Environment secrets configured in the SkillUp app (`app.yaml`) are available as Databricks secrets in notebooks:

```python
# Access secrets using dbutils
neo4j_password = dbutils.secrets.get(scope="skillup", key="NEO4J_PASSWORD")
openai_key = dbutils.secrets.get(scope="skillup", key="OPENAI_API_KEY")
databricks_token = dbutils.secrets.get(scope="skillup", key="DATABRICKS_TOKEN")

# Example: Initialize Neo4j connection
from neo4j import GraphDatabase

neo4j_uri = dbutils.secrets.get(scope="skillup", key="NEO4J_URI")
neo4j_user = dbutils.secrets.get(scope="skillup", key="NEO4J_USER")
neo4j_password = dbutils.secrets.get(scope="skillup", key="NEO4J_PASSWORD")

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
```

**Available Secret Scope:** `skillup`

**Common Secret Keys:**
* `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
* `OPENAI_API_KEY`
* `DATABRICKS_TOKEN`, `DATABRICKS_WAREHOUSE_ID`
* `MOSAICML_API_KEY` (if using Mosaic LLMs)

> **📖 Full configuration details:** See [CONFIGURATION.md](./CONFIGURATION.md)

---

## 📊 Data Files

### Gold Standard Datasets (in `{REPO_ROOT}/data/`)
* `skill_mappings_gold.json` - Verified skill-to-skill mappings
* `gold_standard_cvs.json` - Validated CV skill extractions
* `gold_standard_jds.json` - Validated job description skill extractions
* `test_profiles.json` - User profiles for testing

### Databricks Tables
* `workspace.default.my_skills_future_course_directory` - SkillsFuture courses
* `workspace.default.job_description` - Job postings dataset
* `workspace.default.resume_dataset_1200` - Resume corpus
* `workspace.default.knowledge_graph_output` - Neo4j export
* `skillsup.gap_analysis.user_analysis_log` - User interaction logs

---

## 🚀 Quick Start

### 1. Run Smoke Tests (Fast Validation)
```python
# Open Quick_Smoke_Tests.ipynb
# Run all cells: Ctrl+Shift+Enter
# Expected: All ✅, runtime <30 seconds
```

### 2. Run Full Test Suite
```python
# Open Test_Runner.ipynb
# Run "All Unit Tests" cell
# Expected: 100% pass, runtime ~2-5 minutes
```

### 3. Generate Coverage Report
```python
# Open Coverage_Analysis.ipynb
# Run cells 1-10 (up to HTML report)
# View: {REPO_ROOT}/htmlcov/index.html
```

### 4. Validate Techniques (Weekly/Monthly)
```python
# Open Technique_Validation.ipynb
# Update baseline date in cell 3 if needed
# Run all cells: Ctrl+Shift+Enter
# Output: /Volumes/.../evaluation/baseline_YYYYMMDD.json
```

### 5. Evaluate Recommender Quality
```python
# Open Recommender_Evaluation.ipynb
# Run cells 1-15 (setup and test scenario 1)
# View metrics and reasoning traces
# Runtime: ~1-2 minutes (test mode), ~2-5 minutes (full catalog)
```

---

## 🔍 Troubleshooting

### Import Errors
**Problem:** `ModuleNotFoundError: No module named 'knowledgegraph'`

**Solution:**
```python
# Add repo root to Python path (should be in cell 1 of each notebook)
import sys
from pathlib import Path
REPO_ROOT = Path("/Workspace/Users/{user}/skillup")
sys.path.insert(0, str(REPO_ROOT))
```

### Neo4j Connection Errors
**Problem:** `ServiceUnavailable: Unable to connect to Neo4j`

**Solution:**
```python
# Verify secrets
neo4j_uri = dbutils.secrets.get(scope="skillup", key="NEO4J_URI")
print(f"Connecting to: {neo4j_uri}")  # Should NOT print the actual URI for security

# Test connectivity
from neo4j import GraphDatabase
driver = GraphDatabase.driver(neo4j_uri, auth=(user, password))
with driver.session() as session:
    result = session.run("RETURN 1 AS test")
    print(result.single())  # Should print: <Record test=1>
```

### Volume Access Errors
**Problem:** `FileNotFoundError: /Volumes/workspace/default/iss-scratchpad/...`

**Solution:**
```python
# Verify volume mount
dbutils.fs.ls("/Volumes/workspace/default/iss-scratchpad/")

# Create directories if needed
dbutils.fs.mkdirs("/Volumes/workspace/default/iss-scratchpad/evaluation/")
dbutils.fs.mkdirs("/Volumes/workspace/default/iss-scratchpad/data/")
```

---

## 📈 Metrics and Thresholds

### Coverage Targets
| Module | Target | Current |
|--------|--------|---------|
| Overall | ≥80% | TBD |
| Knowledge Graph | ≥80% | TBD |
| Skill Gap | ≥75% | TBD |
| Recommender | ≥85% | TBD |
| App | ≥70% | TBD |

### Technique Validation Metrics
* **Precision@K:** Proportion of recommended items that are relevant
* **Recall@K:** Proportion of relevant items that are recommended
* **nDCG:** Normalized Discounted Cumulative Gain (ranking quality)
* **MRR:** Mean Reciprocal Rank (first relevant result position)

**Baseline Targets (from prior research):**
* Precision@5: ≥0.60
* Recall@10: ≥0.50
* nDCG@10: ≥0.65

### Recommender Evaluation Metrics
* **Skill Gap Coverage:** % of skill gaps addressed by recommendations
* **Weighted Skill Coverage:** Priority-weighted coverage score
* **Constraint Satisfaction:** Budget, time, modality compliance
* **Reasoning Quality:** Trace analysis and decision validation

---

## 🔗 Related Documentation

* [CONFIGURATION.md](./CONFIGURATION.md) - Path standards and configuration
* [NOTEBOOK_MIGRATION.md](../NOTEBOOK_MIGRATION.md) - Migration details
* [EVALUATION_SETUP.md](../../EVALUATION_SETUP.md) - Initial setup guide
* [data/README.md](../../data/README.md) - Data directory guide
* [tests/README.md](../../tests/README.md) - Pytest framework details

---

## 📝 Maintenance

### Weekly Tasks
1. Run Quick_Smoke_Tests (every commit)
2. Run Test_Runner (before merge)
3. Update Coverage_Analysis (weekly)

### Monthly Tasks
1. Run Technique_Validation (monthly baseline)
2. Run Recommender_Evaluation (quality validation)
3. Archive previous baseline artifacts
4. Update metrics thresholds if needed
5. Review uncovered code and add tests

### Artifact Retention
* **Evaluation artifacts:** Keep last 6 months (monthly baselines)
* **Coverage reports:** Keep last 12 weeks
* **Test logs:** Keep last 4 weeks

---

**Last Updated:** 2026-04-25  
**Notebook Locations:** `/{REPO_ROOT}/evaluation/notebooks/`  
**Maintainer:** yzouyang-iss@u.nus.edu
