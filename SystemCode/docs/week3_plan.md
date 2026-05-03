# Week 3 Plan: UAT & Validation

> **Goal:** Complete all user acceptance testing, run final technique validation with scoring against targets, validate failure modes, and produce the raw evidence needed for the report.  
> **Scope:** IT roles only.  
> **Budget:** ~6–8 hours per person · ~24–32 hours total

---

## Entry Criteria (from Week 2)

| Item | Expected State |
|------|---------------|
| `evaluation/results/week2_YYYYMMDD.json` | All 8 techniques showing `"runs"` status |
| `evaluation/cbr_ground_truth.json` | 10 human-ranked profiles committed |
| `evaluation/competing_experts_labels.json` | 10 team-consensus gap labels committed |
| UAT form | Live on Google/Microsoft Forms; 8 volunteers scheduled |
| `run_cbr()` and `compute_gap_weight()` | Callable from validation notebook |

If any entry criterion is unmet, resolve it before beginning validation scoring.

---

## Task Breakdown

### Task 1 — Conduct UAT Sessions (S1–S8) (~4 hours)

**Deliverable:** 8 completed form submissions in Google/Microsoft Forms.

**Preparation (before sessions):**
- Print or share `data/test_profiles.json` scenario descriptions with the evaluator running each session
- Ensure the Databricks app is deployed and accessible
- Have the UAT form link ready

**Session protocol (per scenario, ~20 minutes each):**
1. Brief volunteer: "You'll be playing the role of [profile]. Walk through the SkillUp system naturally."
2. Load the scenario profile into the system
3. Observe and note any unexpected behaviour
4. After the session: evaluator completes the UAT form (Q1–Q14)
5. Ask volunteer Q9–Q12 (satisfaction and open feedback) verbally, record in form

**Scenarios and their key focus:**

| Scenario | Profile | What to watch for |
|----------|---------|-------------------|
| S1 | Accountant → Data Analyst | Does system bridge non-IT background? Skill gap quality |
| S2 | Admin → Junior Developer | Does it handle zero coding background gracefully? |
| S3 | Software Dev → ML Engineer | Does CSP satisfy $2000 budget? Gap priority correct? |
| S4 | QA → DevOps | Adjacent IT move — are recommended courses practical? |
| S5 | Fresh CS Grad → Junior Dev | Entry-level handling — no over-qualification? |
| S6 | Career Break → Re-entry | Does it flag skill obsolescence risk appropriately? |
| S7 | Data Analyst, $350 budget | Does it suggest phased approach for tight budget? |
| S8 | Contradictory constraints | Does it identify contradictions clearly? No crash? |

**If a volunteer is unavailable:** Run the scenario with a team member as the volunteer and flag as `evaluator_is_volunteer: true` in form notes.

---

### Task 2 — Test Failure Modes (~1 hour)

**Deliverable:** 4 rows added to `evaluation/results/failure_mode_results.md` (pass/fail per mode).

Run each failure mode scenario manually and record outcome:

| Failure Mode | Input to test | Expected outcome | Result |
|--------------|---------------|------------------|--------|
| **Zero Results** | S8 profile with budget $10 | "No courses found" explanation + constraint relaxation suggestion | Pass/Fail |
| **Conflicting Constraints** | S8 profile as-is (senior AI target + no background + $200) | Contradiction identified, guided relaxation steps offered | Pass/Fail |
| **Insufficient Budget** | S7 with budget $50 | Phased approach suggested; subsidy options mentioned | Pass/Fail |
| **Ambiguous CV** | E5 profile (vague CV text) | Clarification request raised; reasonable defaults applied | Pass/Fail |

Record for each: what actually happened, whether the system crashed, and how the explanation read.

---

### Task 3 — Final Technique Validation (Scoring Against Targets) (~3 hours)

**Deliverable:** `evaluation/results/final_YYYYMMDD.json` — validation run with actual pass/fail scores.

Open `Technique_Validation.ipynb` on Databricks and run in full scoring mode. Update the notebook to score each technique against its success criteria (add scoring cells if not done in Week 2).

#### Semantic Similarity (target: ≥ 80%, n=30 pairs)
- Extend the sample from 5 to 30 skill pairs from `data/skill_mappings_gold.json`
- Count pairs with cosine similarity above the match threshold (0.80)
- **Score:** `(pairs_above_threshold / 30) × 100%`

#### Knowledge Graph (target: ≥ 85% correctness, n=20 queries)
- Run 20 role queries from `data/gold_standard_jds.json`
- For each result, manually verify: does the returned skill list match the JD's `required_skills`?
- **Score:** `(correct_results / 20) × 100%`

#### NER Precision (target: ≥ 80%, n=10 CVs)
- Run spaCy NER on all 10 `data/cvs/cv*.md` files
- For each CV, compare extracted skill entities against the gold `skills` list in `data/gold_standard_cvs.json`
- **Score:** `precision = correct_extractions / total_extractions`

#### CSP (target: ≥ 90% constraint satisfaction, n=10 profiles)
- Run CSP on all 8 UAT scenarios + E1 + E2 (=10)
- For each: verify that every recommended course satisfies **all** stated constraints (budget ≤ limit, hours ≤ limit, modality matches)
- **Score:** `(scenarios_fully_satisfied / 10) × 100%`

#### CBR (target: τ ≥ 0.65 vs human-ranked ground truth, n=10 cases)
- Run CBR on the 10 profiles from `evaluation/cbr_ground_truth.json`
- For each profile, compute Kendall's τ between CBR ranking and human ranking:
  ```python
  from scipy.stats import kendalltau
  tau, _ = kendalltau(cbr_ranked_ids, human_ranked_ids)
  ```
- **Score:** mean τ across all 10 profiles

#### Fuzzy Logic (target: ≥ 75% near-miss detection, n=10 boundary cases)
- Define 10 boundary skill pairs: user proficiency 0.3–0.6, required level 0.6–0.8
- Run `compute_gap_weight()` on each
- A "near-miss" is `0.0 < gap_weight ≤ 0.3` (partial gap, not full miss)
- **Score:** `(near_miss_detected / 10) × 100%`

#### Competing Experts (target: ≥ 70% arbiter alignment, n=10 gaps)
- Compare arbiter priority output against `evaluation/competing_experts_labels.json`
- Alignment = arbiter priority matches team consensus (exact match: Critical/High/Medium/Low)
- **Score:** `(aligned_gaps / 10) × 100%`

#### RAG (target: ≥ 90% groundedness, n=20 explanations)
- Generate 20 explanations (use all 8 UAT outputs + 12 ad-hoc role queries)
- Apply the groundedness rubric from [evaluation.md](evaluation.md):
  - ✅ Grounded = all claims traceable to retrieved source
  - ⚠️ Partially Grounded = core correct, ≥ 1 unverified detail
  - ❌ Hallucinated = ≥ 1 key claim untraceable
- **Score:** `(grounded_count / 20) × 100%`

---

### Task 4 — LLM Hallucination Check (~2 hours)

**Deliverable:** `evaluation/results/llm_quality_results.md` with hallucination and relevance scores.

Fact-check 20 LLM outputs (same set used for RAG groundedness):

For each output, check:
1. **Hallucination Prevention** — Are course names, fees, and providers factually correct? Cross-check against `workspace.default.my_skills_future_course_directory`
2. **Explanation Groundedness** — Does the explanation cite specific KG nodes / courses? (Already covered in Task 3 RAG check)
3. **Response Relevance** — Is the recommended path relevant to the user's actual target role and constraints?

Record as a simple table:

| Output # | Profile | Hallucination | Groundedness | Relevance | Notes |
|----------|---------|--------------|--------------|-----------|-------|
| 1 | S1 | None | Grounded | Relevant | — |

---

### Task 5 — Experience Parity Check (~1 hour)

**Deliverable:** 1 paragraph in `evaluation/results/fairness_notes.md`.

Compare recommendation quality between:
- **Junior profile:** S5 (Fresh Graduate → Software Developer)
- **Senior profile:** CV006 (Senior Full Stack → Tech Lead)

Compute NDCG (or simple ranked relevance score) for both recommendation lists. If the gap exceeds 20%, document it as a bias risk. Either way, write the fairness statement for the report (see [evaluation.md](evaluation.md#fairness--ethics-awareness-level)).

```python
# Simple NDCG approximation using binary relevance
from sklearn.metrics import ndcg_score
import numpy as np

# relevance[i] = 1 if course[i] covers a required skill, else 0
ndcg_junior = ndcg_score([relevance_junior], [scores_junior])
ndcg_senior = ndcg_score([relevance_senior], [scores_senior])
gap = abs(ndcg_junior - ndcg_senior)
print(f"NDCG gap: {gap:.3f} ({'⚠️ exceeds 20%' if gap > 0.2 else '✅ within threshold'})")
```

---

## Exit Criteria for Week 3

- [ ] 8 UAT form submissions completed (≥ 6 must be Pass — overall success threshold)
- [ ] 4 failure mode results recorded in `failure_mode_results.md`
- [ ] `evaluation/results/final_YYYYMMDD.json` committed — all 8 techniques scored
- [ ] `evaluation/results/llm_quality_results.md` committed — 20 outputs checked
- [ ] `evaluation/results/fairness_notes.md` committed — experience parity check complete
- [ ] UAT responses exported from Forms to `evaluation/results/uat_results_summary.csv`

---

## File Structure After Week 3

```
evaluation/
├── results/
│   ├── baseline_YYYYMMDD.json          ✅ Week 1
│   ├── week2_YYYYMMDD.json             ✅ Week 2
│   ├── final_YYYYMMDD.json             ✅ Week 3 (scored)
│   ├── uat_results_summary.csv         ✅ Exported from Forms
│   ├── failure_mode_results.md         ✅ 4 scenarios tested
│   ├── llm_quality_results.md          ✅ 20 outputs checked
│   └── fairness_notes.md               ✅ Experience parity check
├── cbr_ground_truth.json               ✅ From Week 2
└── competing_experts_labels.json       ✅ From Week 2
```

---

## Related Documentation

- [Week 2 Plan](week2_plan.md) — development & iteration
- [Week 4 Plan](week4_plan.md) — analysis & reporting
- [Evaluation Plan](evaluation.md) — full metrics and success criteria
