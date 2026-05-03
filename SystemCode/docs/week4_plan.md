# Week 4 Plan: Analysis & Reporting

> **Goal:** Transform all collected evidence into report-ready tables, write the evaluation section of the final report, and prepare the demo and presentation.  
> **Scope:** IT roles only.  
> **Budget:** ~8–10 hours per person · ~30–40 hours total

---

## Entry Criteria (from Week 3)

| Item | Expected State |
|------|---------------|
| `evaluation/results/final_YYYYMMDD.json` | Scored — all 8 techniques have numeric results |
| `evaluation/results/uat_results_summary.csv` | Exported from Forms — 8 sessions complete |
| `evaluation/results/failure_mode_results.md` | 4 scenarios tested (pass/fail) |
| `evaluation/results/llm_quality_results.md` | 20 outputs fact-checked |
| `evaluation/results/fairness_notes.md` | Experience parity check written |

---

## Task Breakdown

### Task 1 — Compile Metrics Tables (~2 hours)

**Deliverable:** `evaluation/results/metrics_summary.md` — all scores in one place, baseline vs final.

This is the primary evidence document for Section 4.1 and 4.2 of the report.

#### 1a. Baseline vs Final Table (Section 4.1)

Compare `baseline_YYYYMMDD.json` (Week 1, mock/stub) with `final_YYYYMMDD.json` (Week 3, scored):

| Metric | Baseline (Week 1) | Final (Week 3) | Target | Status |
|--------|-------------------|----------------|--------|--------|
| Semantic Similarity mean score | — | X.XX | ≥ 0.80 | ✅/⚠️ |
| KG Query Correctness | — | X% | ≥ 85% | ✅/⚠️ |
| NER Precision | — | X% | ≥ 80% | ✅/⚠️ |
| CSP Constraint Satisfaction | — | X% | ≥ 90% | ✅/⚠️ |
| CBR Kendall's τ | — | 0.XX | ≥ 0.65 | ✅/⚠️ |
| Fuzzy Near-miss Detection | — | X% | ≥ 75% | ✅/⚠️ |
| Competing Experts Alignment | — | X% | ≥ 70% | ✅/⚠️ |
| RAG Groundedness | — | X% | ≥ 90% | ✅/⚠️ |
| E2E Latency | Xs | Xs | < 15s | ✅/⚠️ |
| Skill Gap Latency | Xs | Xs | < 5s | ✅/⚠️ |
| Course Rec Latency | Xs | Xs | < 7s | ✅/⚠️ |

#### 1b. Dimension 1 metrics (Section 4.1 — KR Quality)

From `data/gold_standard_jds.json` and `data/gold_standard_cvs.json` annotations:

| Metric | Target | Result |
|--------|--------|--------|
| Skill Mapping Accuracy | ≥ 80% | X% |
| Role-to-Skills Relevance | ≥ 75% | X% |
| NER Precision | ≥ 80% | X% |
| Graph Connectivity | ≥ 90% | X% |

#### 1c. Dimension 3 metrics (Section 4.3 — LLM Quality)

From `evaluation/results/llm_quality_results.md`:

| Metric | Target | Result |
|--------|--------|--------|
| Hallucination Prevention | ≥ 95% | X% |
| Explanation Groundedness | ≥ 90% | X% |
| Response Relevance | ≥ 85% | X% |

---

### Task 2 — Analyse UAT Results (~2 hours)

**Deliverable:** `evaluation/results/uat_analysis.md` — scenario-by-scenario breakdown.

From `evaluation/results/uat_results_summary.csv`:

#### 2a. Per-scenario outcome table

| Scenario | Profile | Q1 Profile | Q2 Gaps | Q3 Courses | Q4 Groundedness | Q5 Hallucinations | Satisfaction | Outcome |
|----------|---------|-----------|---------|-----------|----------------|------------------|-------------|---------|
| S1 | Accountant → DA | ✅ | ✅ | ✅ | ✅ | None | 4/5 | **Pass** |
| ... | | | | | | | | |

Fill in actual results from the Forms export.

#### 2b. Aggregate satisfaction

- Mean satisfaction score across all 8 sessions (target ≥ 3.5/5, stretch ≥ 4.0/5)
- Mean clarity score across all 8 sessions
- Count of Pass / Partial / Fail scenarios (target ≥ 6 Pass)

#### 2c. Qualitative themes

From Q11 ("what worked well") and Q12 ("what could be improved"), group volunteer feedback into 3–5 themes. Use direct quotes in the report.

---

### Task 3 — Write Evaluation Section of Final Report (~4 hours, split across team)

The evaluation section maps to **grading criterion: Evaluation & Validation (30%)**.

Divide writing by subsection:

#### Section 4.1: Baseline vs Final Metrics Table
- Use the table from Task 1a/1b
- Narrative: describe what improved between Week 1 (baseline) and Week 3 (final)
- Attribute each improvement to a specific IRS technique or infrastructure fix
- ~300 words + table

#### Section 4.2: IRS Technique Validation Evidence
One subsection per technique (7 × 150–200 words each):
- State the technique and its role in the pipeline
- State the success criterion
- State the result (pass or fall-back applied)
- Include a representative sample output (log line or JSON snippet)
- Where a fall-back was applied (from the Risk Register), explain why

Template per technique:
> **[Technique name]** — *[IRS module: MR/RS/CGS]* · *[Pipeline stage]*  
> Success criterion: [from evaluation.md]  
> Result: X% / τ=0.XX · **[Pass ✅ / Partial ⚠️ / Fallback applied ❌]**  
> Evidence: [snippet from logs or validation notebook output]  
> Notes: [any caveats]

#### Section 4.3: UAT Results & User Feedback
- Use the per-scenario table from Task 2a
- Aggregate satisfaction (mean score, pass/fail count)
- 3–5 qualitative themes with volunteer quotes
- ~400 words + table

#### Section 4.4: Limitations & Future Work
- IT-only scope (Neo4j free-tier constraint)
- Small evaluation dataset (10 CVs, 20 JDs) — insufficient for statistical significance
- Experience parity only — demographic fairness out of scope
- Production readiness gaps (latency targets not met on free Databricks tier, etc.)
- Future work: multi-industry expansion, demographic fairness audit, load testing, ablation studies
- ~300 words

#### Appendix: Technique Coverage Matrix
- Copy the inline matrix from [evaluation.md](evaluation.md#technique-coverage-matrix)
- Update any ✅ marks to match what was actually implemented vs planned

---

### Task 4 — Prepare Demo Script (~2 hours)

**Deliverable:** `evaluation/demo_script.md` — step-by-step walkthrough for the live demo.

The demo should cover the full E2E pipeline in ≤ 8 minutes:

| Segment | Duration | What to show |
|---------|----------|-------------|
| 1. Profile Input | 1 min | Upload CV003 (Software Dev → ML Engineer); system parses and extracts skills |
| 2. Skill Gap Analysis | 2 min | KG traversal result; competing experts scores; gap priority list |
| 3. Course Recommendation | 2 min | CSP filtering; CBR justification; fuzzy near-miss example |
| 4. RAG Explanation | 2 min | Grounded explanation tracing skills → gaps → courses |
| 5. Edge Case | 1 min | S8 (conflicting constraints) — show graceful failure handling |

**Demo preparation checklist:**
- [ ] CV003 pre-loaded for fast demo start
- [ ] S3 scenario parameters ready to paste
- [ ] S8 scenario ready for failure mode demo
- [ ] Databricks app URL confirmed working
- [ ] Fallback: pre-recorded screen capture in case live demo fails

---

### Task 5 — Prepare Presentation Slides (~2 hours)

**Deliverable:** Presentation slide deck (PowerPoint or Google Slides).

Recommended structure:

| Slide | Title | Content |
|-------|-------|---------|
| 1 | SkillUp — Hybrid IRS for Career Guidance | Team names, date |
| 2 | Problem & Motivation | Skill gap in Singapore IT workforce; Why hybrid IRS? |
| 3 | System Architecture | Architecture diagram from [architecture.md](architecture.md) |
| 4 | IRS Techniques Used | Technique Coverage Matrix |
| 5 | Pipeline Demo (live or recorded) | Walk through S3 profile |
| 6 | Evaluation Results | Baseline vs Final metrics table |
| 7 | UAT Results | Per-scenario outcomes; satisfaction scores |
| 8 | Failure Mode Handling | S8 conflicting constraints — what the system said |
| 9 | Limitations & Scope | IT-only, small dataset, fairness scope |
| 10 | Future Work | Multi-industry expansion, demographic fairness, production scale |

---

### Task 6 — Academic Rigor Review (~1 hour, team together)

Before submission, verify the [Academic Rigor Checklist](evaluation.md#academic-rigor-checklist-scaled-for-1-month-project):

- [ ] Baseline measurements documented (`baseline_YYYYMMDD.json`)
- [ ] Quantitative evidence for each technique (`final_YYYYMMDD.json`)
- [ ] UAT with real volunteers (`uat_results_summary.csv`)
- [ ] Failure mode coverage (`failure_mode_results.md`)
- [ ] Notebooks re-runnable (`Technique_Validation.ipynb` committed and runnable on Databricks)
- [ ] Limitations acknowledged (Section 4.4 written)
- [ ] Course mapping documented (Appendix: Technique Coverage Matrix)
- [ ] Fairness statement written (`fairness_notes.md` → Section 4.4)

For each ❌ item: either complete it or explicitly note the omission in Section 4.4.

---

## Exit Criteria for Week 4

- [ ] `evaluation/results/metrics_summary.md` committed — all scores in one table
- [ ] `evaluation/results/uat_analysis.md` committed — per-scenario breakdown
- [ ] Report Sections 4.1–4.4 drafted (can be in the report document itself, not repo)
- [ ] Appendix: Technique Coverage Matrix finalised
- [ ] `evaluation/demo_script.md` committed
- [ ] Presentation slide deck ready (PowerPoint/Google Slides)
- [ ] Academic rigor checklist completed

---

## File Structure After Week 4

```
evaluation/
├── results/
│   ├── baseline_YYYYMMDD.json          ✅ Week 1
│   ├── week2_YYYYMMDD.json             ✅ Week 2
│   ├── final_YYYYMMDD.json             ✅ Week 3
│   ├── metrics_summary.md              ✅ Week 4 (compiled)
│   ├── uat_analysis.md                 ✅ Week 4 (compiled)
│   ├── uat_results_summary.csv         ✅ Week 3
│   ├── failure_mode_results.md         ✅ Week 3
│   ├── llm_quality_results.md          ✅ Week 3
│   └── fairness_notes.md               ✅ Week 3
├── demo_script.md                      ✅ Week 4
└── technique_validation.py             ⚠️  Deprecated (use Technique_Validation.ipynb)
```

**Presentation:**
- [ ] `SkillUp_Presentation.pptx` or Google Slides link

**Final Report:**
- [ ] Section 4 (Evaluation) complete
- [ ] Appendix (Technique Coverage Matrix) complete

---

## Related Documentation

- [Week 3 Plan](week3_plan.md) — UAT & validation scoring
- [Evaluation Plan](evaluation.md) — full metrics and success criteria
- [Tests README](../tests/README.md) — comprehensive testing guide
