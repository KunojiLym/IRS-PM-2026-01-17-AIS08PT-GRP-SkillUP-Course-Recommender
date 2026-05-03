# Week 1 Plan: Setup & Baseline

> **Goal:** By end of Week 1, the team has gold standard data, a working validation script scaffold, UAT instruments, a verified E2E run on Databricks, and a baseline measurement snapshot.  
> **Scope:** IT roles only (constrained by Neo4j free-tier graph size).  
> **Budget:** ~4–6 hours per person · ~18–22 hours total

---

## Situation Assessment (What Already Exists)

| Area | Status | Notes |
|------|--------|-------|
| Logging | ✅ Done | `app/logging_config.py` — structured logging with file rotation |
| Metrics collection | ✅ Done | `app/metrics.py` — `MetricsCollector`, `Timer`, LLM/CV/error helpers |
| KG module | ✅ Done | `knowledgegraph/knowledgegraph.py` |
| Skill gap module | ✅ Done | `skillgap/skillgap.py` |
| Recommender module | ✅ Done | `recommender/recommender.py` |
| Unit tests | ✅ Done | `tests/unit/app/test_app.py` |
| Gold standard data | ✅ Created (Week 1) | See `data/` — IT-only scope |
| CV markdown files | ✅ Created (Week 1) | `data/cvs/cv001.md` – `cv010.md` |
| Validation notebook | ✅ Created | `Technique_Validation.ipynb` — adapted from .py file |
| Test notebooks | ✅ Created | `Test_Runner`, `Quick_Smoke_Tests`, `Coverage_Analysis` |
| UAT survey template | ✅ Created (Week 1) | `evaluation/uat_survey_template.md` — for Google/Microsoft Forms setup |
| Databricks E2E | ❓ To verify | Run E2E check this week; log latency baseline |
| Baseline snapshot | ❌ To produce | Run `Technique_Validation` notebook on Databricks → `evaluation/results/` |

---

## Scope Note: IT Jobs Only

All gold standard data (JDs, CVs, test profiles, skill mappings) is **scoped to IT roles only**.

**Reason:** The Neo4j free-tier graph database has node/relationship limits that make multi-industry coverage impractical for this project. Expanding scope to other industries would require a paid Neo4j plan or AuraDB upgrade.

**Impact on evaluation:**
- Evaluation dimensions and IRS technique validation are unaffected
- UAT scenarios S1–S8 have been updated to use IT-adjacent career pivots
- Future work: scale to other industries with a production Neo4j deployment

---

## What Needs to Be Done with Existing Artifacts

These existing files are **stubs** that need to be populated from real infrastructure before
the validation script can produce meaningful results:

### `data/knowledge_graph.csv` (7 rows — stub)
**❗ Action required (on Databricks, Week 1–2):**
1. Connect to Neo4j using credentials in Databricks secrets (`skillup` scope)
2. Run `extract_all_role_skill_mappings()` from `knowledgegraph/knowledgegraph.py`
3. Export the result to `data/knowledge_graph.csv` (overwrite stub)
4. Verify IT roles (Data Scientist, Software Engineer, ML Engineer, DevOps, etc.) have sufficient node coverage

```python
# Run on Databricks:
from knowledgegraph.knowledgegraph import extract_all_role_skill_mappings
import json, csv
data = extract_all_role_skill_mappings()
# write to data/knowledge_graph.csv
```

### `data/skillsfuture_courses.csv` (4 rows — stub, safe to ignore)
**✅ No action required** — SkillsFuture course data is already loaded into a Databricks Delta table.
The stub CSV in `data/` is superseded by the live table. All modules (recommender, skill gap)
should query the Databricks table directly, not this file.

> If you need a local reference copy for offline testing, export from the Databricks table:
> ```python
> # Table name from skillgap.py widget default:
> df = spark.table("workspace.default.my_skills_future_course_directory")
> # Key columns: coursereferencenumber, skills_covered, what_you_learn, coursetitle
> df.toPandas().to_csv("data/skillsfuture_courses.csv", index=False)
> ```
>
> ⚠️ Note: the primary key column is `coursereferencenumber`, **not** `course_id`.
> Update `data/skill_mappings_gold.json` `kg_node` references accordingly once the table is inspected.

### `data/skill_mappings_gold.json` (created — 50 mappings)
**❗ Action required (Week 2):**
- Cross-reference the 50 canonical skill names against actual Neo4j node names once the KG is populated
- Update `kg_node` field if the actual node naming convention differs from the assumed format (`Skill:MachineLearning`, etc.)
- Add any high-frequency IT skills missing from the 50 entries

### `Technique_Validation.ipynb` — CBR & Fuzzy Logic methods
**❗ ACTION NEEDED comments inline in notebook:**
- **CBR**: Expose `run_cbr(skills, target_role, k=3)` as a public function from `recommender/recommender.py`
- **Fuzzy Logic**: Expose `compute_gap_weight(skill, user_proficiency, required_level)` as a public method on `SkillGapAnalyzer` in `skillgap/skillgap.py`

---

## Task Breakdown

### Task 1 — Gold Standard Data ✅ Complete

All 5 data files created:

| File | Description |
|------|-------------|
| `data/gold_standard_jds.json` | 20 IT job descriptions (JD001–JD020) |
| `data/gold_standard_cvs.json` | 10 annotated CV records |
| `data/cvs/cv001.md` – `cv010.md` | Full CV markdown files (synthetic) |
| `data/test_profiles.json` | 8 UAT scenarios (S1–S8) + 5 edge cases (E1–E5) |
| `data/skill_mappings_gold.json` | 50 IT skill alias → canonical mappings |

**⚠️ Still needed:** Update `kg_node` values once real Neo4j node names are confirmed (see above).

---

### Task 2 — Validation Notebook ✅ Complete

`Technique_Validation.ipynb` is ready. It:
- Covers all 8 IRS techniques
- Runs natively in Databricks notebooks (no `__file__` issues)
- Uses `/Workspace/Users/yzouyang-iss@u.nus.edu/skillup` as REPO_ROOT
- Produces `evaluation/results/baseline_YYYYMMDD.json`
- Logs to `evaluation/results/validation_YYYYMMDD.log`
- Contains inline `ACTION NEEDED` comments for CBR and Fuzzy Logic method exposure

**To run Week 1 baseline on Databricks:**
Open the notebook in Databricks workspace and run all cells.

---

### Task 3 — Test Notebooks ✅ Complete

All test notebooks are now fully implemented:

| Notebook | Status | Description |
|----------|--------|-------------|
| `Test_Runner.ipynb` | ✅ Complete | Comprehensive test suite with module-by-module execution |
| `Quick_Smoke_Tests.ipynb` | ✅ Complete | Fast validation (< 30 seconds) with health checks |
| `Coverage_Analysis.ipynb` | ✅ Complete | Detailed coverage reporting and threshold validation |

**Benefits:**
- ✅ Visual test execution in Databricks
- ✅ No local setup required
- ✅ Automatic dependency installation
- ✅ Easy to share with team

---

### Task 4 — UAT Instruments ✅ Template Complete

`evaluation/uat_survey_template.md` contains the full question set for building the form on
**Google Forms** or **Microsoft Forms**.

**Remaining steps (this week):**
1. One team member builds the form on Google Forms / Microsoft Forms using the template
2. Enable response collection to a linked Google Sheet (or MS Excel Online)
3. Share form link with 8 UAT volunteers; confirm availability for Week 3
4. Do NOT create `uat_tracker.xlsx` — responses are tracked in Forms natively; mirror a CSV summary to `evaluation/results/uat_results_summary.csv` after Week 3

---

### Task 5 — Databricks E2E Verification ❌ To Do

**Steps:**
1. Deploy the current app to Databricks using `app.yaml`
2. Run one complete profile through the pipeline (use CV003 + scenario S3: Software Developer → ML Engineer)
3. Timing is captured automatically by `measure_e2e_latency()` in `Technique_Validation.ipynb`
4. Confirm `evaluation/results/baseline_YYYYMMDD.json` is written with latency values
5. If deployment fails, document the blocker in `evaluation/results/deployment_issues.md`

**Success criterion for Week 1:** Pipeline completes without crashing. Latency numbers are recorded (any value — targets are Week 3 goals).

---

### Task 6 — Team Baseline Checkpoint ❌ To Do (Team Meeting)

**Agenda:**
1. Review `baseline_YYYYMMDD.json` together — which techniques ran, which failed
2. Identify missing method exposures (CBR, Fuzzy Logic) — assign to Week 2
3. Confirm KG population plan (run `extract_all_role_skill_mappings()` on Databricks)
4. Confirm course data scraping plan (data pipeline)
5. Confirm UAT form is live and 8 volunteers are confirmed
6. Divide Week 2 implementation tasks across the team

**Exit criteria for Week 1:**
- [x] All 5 gold standard data files committed to `data/`
- [x] `Technique_Validation.ipynb` created and runnable on Databricks
- [x] Test notebooks (`Test_Runner`, `Quick_Smoke_Tests`, `Coverage_Analysis`) implemented
- [ ] `evaluation/results/baseline_YYYYMMDD.json` produced from Databricks run
- [ ] UAT form live (Google/Microsoft Forms) with 8 volunteers confirmed
- [ ] KG population and course scraping tasks assigned for Week 2

---

## File Structure After Week 1

```
skillup/
├── data/
│   ├── gold_standard_jds.json      ✅ Created
│   ├── gold_standard_cvs.json      ✅ Created
│   ├── test_profiles.json          ✅ Created
│   ├── skill_mappings_gold.json    ✅ Created
│   ├── knowledge_graph.csv         ⚠️  Stub — needs real KG export
│   └── cvs/
│       ├── cv001.md – cv010.md     ✅ Created
├── evaluation/
│   ├── technique_validation.py     ⚠️  Deprecated (use notebook instead)
│   ├── uat_survey_template.md      ✅ Created
│   └── results/
│       └── baseline_YYYYMMDD.json  ❌ To produce (run Technique_Validation notebook)
├── notebooks/
│   ├── Technique_Validation.ipynb  ✅ Complete (Week 1 baseline runner)
│   ├── Test_Runner.ipynb           ✅ Complete (comprehensive test suite)
│   ├── Quick_Smoke_Tests.ipynb     ✅ Complete (fast validation)
│   └── Coverage_Analysis.ipynb     ✅ Complete (coverage reporting)
```

---

## Related Documentation

- [Evaluation Plan](evaluation.md) — full metrics and success criteria
- [Architecture](architecture.md) — pipeline overview
- [Stage 1](stage1_user_profile.md) · [Stage 2](stage2_skill_gap.md) · [Stage 3](stage3_course_recommendation.md)
- [Tests README](../tests/README.md) — comprehensive testing guide
