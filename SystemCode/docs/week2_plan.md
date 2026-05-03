# Week 2 Plan: Development & Iteration

> **Goal:** All 8 IRS techniques run end-to-end on real Databricks data with logging. Validation notebook produces meaningful (non-mock) numbers. Mid-project checkpoint confirms techniques are demonstrable for grading.  
> **Scope:** IT roles only.  
> **Budget:** ~8–10 hours per person · ~30–40 hours total

---

## Entry Criteria (from Week 1)

Before starting Week 2 work, confirm Week 1 exit criteria are met:

| Item | Expected State |
|------|---------------|
| `evaluation/results/baseline_YYYYMMDD.json` | Committed — shows which techniques ran in Week 1 |
| UAT form | Live on Google/Microsoft Forms; 8 volunteers confirmed |
| `data/` gold standard files | All 5 files committed |
| `Technique_Validation.ipynb` | Runs on Databricks; produces baseline results |
| Test notebooks | `Test_Runner`, `Quick_Smoke_Tests`, `Coverage_Analysis` fully implemented |

If any item is missing, complete it before Week 2 development begins (budget from Week 2 time).

---

## Task Breakdown

### Task 1 — Populate Knowledge Graph from Neo4j (~2 hours)

**Deliverable:** `data/knowledge_graph.csv` overwritten with real data.

**Steps:**
1. On Databricks, run `extract_all_role_skill_mappings()` from `knowledgegraph/knowledgegraph.py`
2. Write result to `data/knowledge_graph.csv` (overwrite the 7-row stub)
3. Verify coverage for all 20 IT roles in `gold_standard_jds.json`
4. Log which roles have ≥ 5 skills in KG vs those with sparse/zero coverage
5. Commit the populated CSV

```python
# Databricks — run in a cell or notebook
from knowledgegraph.knowledgegraph import extract_all_role_skill_mappings
import pandas as pd, pathlib

data = extract_all_role_skill_mappings()
df = pd.DataFrame(data)
out_path = pathlib.Path("data/knowledge_graph.csv")
df.to_csv(out_path, index=False)
print(f"✅ Exported {len(df)} role-skill pairs covering {df['role'].nunique()} roles")
```

**If KG coverage is sparse (< 5 skills for a role):** Document which roles are sparse in `evaluation/results/kg_coverage_notes.md`. Those roles will be excluded from KG query validation tests.

---

### Task 2 — Reconcile Skill Mappings (~1 hour)

**Deliverable:** `data/skill_mappings_gold.json` `kg_node` values updated to match real Neo4j node names.

**Steps:**
1. From the populated `data/knowledge_graph.csv`, extract the unique values of `skill_name`
2. Compare against the `canonical` values in `data/skill_mappings_gold.json`
3. Update any `kg_node` fields whose naming convention differs (e.g., if Neo4j uses `"Machine Learning"` not `"Skill:MachineLearning"`)
4. Add any high-frequency IT skills found in Neo4j that are missing from the 50-entry list

**Also check:** Inspect `workspace.default.my_skills_future_course_directory` columns to confirm whether `skills_covered` array values match KG skill names or need a separate mapping.

---

### Task 3 — Expose CBR and Fuzzy Logic Methods (~3 hours)

**Deliverable:** Two public methods added to existing modules, enabling `Technique_Validation.ipynb` to run both techniques without mock mode.

#### 3a. CBR — expose `run_cbr()` in `recommender/recommender.py`

The validation notebook expects:
```python
run_cbr(skills: list[str], target_role: str, k: int = 3) -> list[dict]
# Returns: [{"case_id": str, "similarity": float}, ...]
```

Add this as a module-level function (or static method) that wraps whatever k-NN logic already exists internally, and returns the top-k similar peer profiles with their similarity scores.

#### 3b. Fuzzy Logic — expose `compute_gap_weight()` in `skillgap/skillgap.py`

The validation notebook expects:
```python
# On SkillGapAnalyzer instance:
analyzer.compute_gap_weight(skill: str, user_proficiency: float, required_level: float) -> float
```

Looking at the existing code in `skillgap.py`, `find_skill_gaps()` already computes `gap_weight = max(0.0, 1.0 - max_sim)`. Extract this into a standalone public method.

> **Note:** Keep the internal logic unchanged. These are thin wrappers to expose existing behaviour for testability.

---

### Task 4 — Run Validation Notebook on Real Data (~2 hours)

**Deliverable:** `evaluation/results/week2_YYYYMMDD.json` — first non-mock validation run.

**Steps:**
1. On Databricks, open `Technique_Validation.ipynb` and run all cells
2. Review output for each technique — status should be `"runs"` for all except CBR/Fuzzy if Task 3 is incomplete
3. Record any errors in `evaluation/results/week2_issues.md`
4. Compare technique scores against `baseline_YYYYMMDD.json`:
   - Has semantic similarity score improved (more skill pairs tested)?
   - Are KG queries returning real results?
   - Is latency within acceptable range?
5. Commit results file

**What "runs" means in Week 2 (not yet scoring against targets):**

| Technique | Week 2 acceptance |
|-----------|------------------|
| Semantic Similarity | Real cosine scores, not mock — sample mean recorded |
| Knowledge Graph | Real Neo4j results for ≥ 3 of 5 IT roles |
| NER | spaCy extracting entities from CV markdown files |
| CSP | Recommender returns a result for S3 and S7 profiles |
| CBR | `run_cbr()` returns ≥ 1 case with a similarity score |
| Fuzzy Logic | `compute_gap_weight()` returns a float for each boundary case |
| Competing Experts | `SkillGapAnalyzer.analyze()` returns arbitrated gap list |
| RAG | LLM explanation generated with at least 1 attributed source |

---

### Task 5 — Build CBR Ground Truth Labels (~2 hours)

**Deliverable:** `evaluation/cbr_ground_truth.json` — human-ranked ordering of cases for 10 profiles (needed to compute Kendall's τ in Week 3).

**Why now:** τ calculation in Week 3 requires a pre-existing human ranking that was created *before* seeing CBR output (to avoid bias).

**Steps:**
1. Select 10 profiles from `data/test_profiles.json` (use S1–S8 + E1, E2)
2. For each profile, manually rank the top-3 most relevant peer cases (from `data/gold_standard_cvs.json`) by human judgement
3. Record as:
   ```json
   [
     {
       "profile_id": "S1",
       "human_ranked_cases": ["CV002", "CV005", "CV009"],
       "rationale": "CV002 is an accountant with SQL exposure, closest to S1 target"
     }
   ]
   ```
4. Commit to `evaluation/cbr_ground_truth.json`

> ⚠️ The human ranking must be done **before** running CBR on these profiles. Run CBR output in Week 3, then compare.

---

### Task 6 — Build Competing Experts Consensus Labels (~2 hours)

**Deliverable:** `evaluation/competing_experts_labels.json` — team consensus on skill gap priority for 10 gaps (needed to compute arbiter alignment in Week 3).

**Steps:**
1. Run `SkillGapAnalyzer.analyze()` for 5 IT profiles (use S3, S4, S5, S6, S7)
2. Extract the top-2 raw gaps per profile (= 10 gaps total)
3. For each gap, record the team's consensus priority (Critical / High / Medium / Low) based on own judgement of the target role requirements — **without** looking at the arbiter output
4. Record as:
   ```json
   [
     {
       "profile_id": "S3",
       "skill": "Deep Learning",
       "team_consensus_priority": "critical",
       "rationale": "ML Engineer JDs consistently list this as a core requirement"
     }
   ]
   ```
5. Commit to `evaluation/competing_experts_labels.json`

---

### Task 7 — Mid-Project Checkpoint (Team Meeting, ~2 hours)

**Agenda:**
1. Review `week2_YYYYMMDD.json` — which techniques pass Week 2 acceptance criteria?
2. Are CBR and Fuzzy Logic methods exposed? If not, what is blocking?
3. Are CBR ground truth and Competing Experts labels complete?
4. Is KG coverage adequate for IT roles? Any roles to drop/replace?
5. Re-confirm UAT volunteer availability for Week 3 sessions
6. Assign groundtruth tasks for Week 3

**Key question to answer:** *Can we demonstrate all 8 techniques by end of Week 3?*

If the answer is **No** for any technique, apply the fallback strategy from the [Technique Failure Risk Register](evaluation.md#technique-failure-risk-register) and document the decision now.

---

## Exit Criteria for Week 2

- [ ] `data/knowledge_graph.csv` populated with real Neo4j data (≥ 5 roles with ≥ 5 skills each)
- [ ] `data/skill_mappings_gold.json` `kg_node` values reconciled
- [ ] `run_cbr()` and `compute_gap_weight()` exposed and callable
- [ ] `evaluation/results/week2_YYYYMMDD.json` committed — all 8 techniques showing `"runs"` status
- [ ] `evaluation/cbr_ground_truth.json` committed (10 human-ranked profiles)
- [ ] `evaluation/competing_experts_labels.json` committed (10 team-consensus labels)
- [ ] Mid-project checkpoint completed — Week 3 assignments confirmed

---

## File Structure After Week 2

```
skillup/
├── data/
│   ├── knowledge_graph.csv             ✅ Populated (overwrite stub)
│   ├── skill_mappings_gold.json        ✅ Reconciled with Neo4j node names
├── evaluation/
│   ├── cbr_ground_truth.json           ✅ 10 human-ranked profiles
│   ├── competing_experts_labels.json   ✅ 10 team-consensus labels
│   └── results/
│       ├── baseline_YYYYMMDD.json      ✅ From Week 1
│       ├── week2_YYYYMMDD.json         ✅ First real validation run
│       └── kg_coverage_notes.md        📝 If any roles are sparse
├── notebooks/
│   └── Technique_Validation.ipynb      ✅ Running with real data
├── recommender/
│   └── recommender.py                  ✅ `run_cbr()` exposed
├── skillgap/
│   └── skillgap.py                     ✅ `compute_gap_weight()` exposed
```

---

## Related Documentation

- [Week 1 Plan](week1_plan.md) — baseline setup
- [Week 3 Plan](week3_plan.md) — UAT & validation scoring
- [Evaluation Plan](evaluation.md) — full metrics and success criteria
