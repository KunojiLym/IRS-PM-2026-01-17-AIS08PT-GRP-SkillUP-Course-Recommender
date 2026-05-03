# Evaluation & IRS Course Mapping

> Metrics, benchmarks, and mapping to Intelligent Reasoning Systems course modules.  
> **Scoped for: 1-month, 4-person, part-time masters project**

---

## Evaluation Framework Overview

SkillUP's evaluation demonstrates **hybrid intelligent reasoning effectiveness** through **three core dimensions**:

1. **Knowledge Representation Quality** — Accuracy of KG and skill mappings
2. **Reasoning Algorithm Effectiveness** — IRS technique validation with quantitative evidence
3. **User Experience & System Usability** — UAT validation and explanation quality

**Philosophy:** Focus on **demonstrating IRS techniques work** with sufficient rigor for a single-module project, not production-scale evaluation.

---

## Dimension 1: Knowledge Representation Quality

### Evaluation Metrics

| Metric | Description | Target | Evaluation Method |
|--------|-------------|--------|-------------------|
| **Skill Mapping Accuracy** | Correct semantic skill matching | ≥ 80% | Sample validation (30 skills) |
| **Role-to-Skills Relevance** | KG edges reflect real job requirements | ≥ 75% | Expert spot-check (20 roles) |
| **NER Precision** | Correct entity extraction from CVs | ≥ 80% | Manual check (10 CVs) |
| **Graph Connectivity** | Major roles reachable in KG | ≥ 90% | Automated graph analysis |

### Evaluation Dataset (Lightweight)
- **20 annotated job descriptions** (2 per industry: Tech, Finance, Healthcare, etc.)
- **10 annotated CVs** (diverse backgrounds: junior, mid, senior)
- **50 manually verified skill mappings** (high-frequency skills only)
- **5 edge case profiles** (rare skills, career break, international)

**Baseline:** Run spot-checks on Week 2 to establish current accuracy before improvements.

---

## Dimension 2: Reasoning Algorithm Effectiveness

### IRS Technique Validation

Each IRS technique must have **quantitative evidence** demonstrating it works. This is the **core evaluation** for the IRS course.

| Technique | Success Criteria | Validation Method | Evidence Location |
|-----------|-----------------|-------------------|-------------------|
| **CSP (OR-Tools)** | ≥ 90% constraint satisfaction on test cases | Automated testing (10 profiles) | Stage 3 logs + report |
| **CBR (k-NN)** | ~~Case retrieval relevance τ ≥ 0.65~~ **DESCOPED** — no historical case data generated within project timeline. Code exists in `recommender/cbr.py` but is not exercised. Documented in Limitations. | — | — |
| **Fuzzy Logic** | Near-miss handling ≥ 75% | Manual test (10 boundary cases) | Stage 3 logs + report |
| **Knowledge Graph** | Query correctness ≥ 85% | Automated (20 queries) | Stage 2 logs + report |
| **Competing Experts** | Arbiter alignment ≥ 70% (agreement with team consensus labeling of 10 skill gaps) | Manual validation (10 gaps) | Stage 2 logs + report |
| **RAG** | Groundedness ≥ 90% | Manual fact-check (20 explanations) | RAG logs + report |
| **Semantic Similarity** | Skill matching accuracy ≥ 80% | Spot-check (30 pairs) | Stage 1/2 logs + report |

### Technique Failure Risk Register

If a technique does not meet its success criteria, apply the following fallback:

| Technique | Fallback Strategy |
|-----------|------------------|
| **CSP (OR-Tools)** | Fall back to hard-filter (budget/time only) + ranked list without constraint proof |
| **CBR (k-NN)** | **Applied:** CBR weight set to 0 in score fusion. Recommendations use remaining 4 signals (relevance, rating, constraints, popularity) |
| **Fuzzy Logic** | Treat near-miss as binary pass/fail; document loss of nuance in limitations |
| **Knowledge Graph** | Fall back to keyword-based skill matching; note reduced semantic depth |
| **Competing Experts** | Use single JD-demand signal only; flag reduced arbitration confidence |
| **RAG** | Surface retrieved chunks directly without LLM synthesis; mark explanations as drafts |
| **Semantic Similarity** | Fall back to exact string matching for skill normalisation |


### Performance Benchmarks (Demo Quality)

> Latency targets are measured against the **Databricks deployment** environment.

| Metric | Target | Acceptable Range |
|--------|--------|------------------|
| **E2E Latency (CV→Plan)** | < 15s | < 25s acceptable for demo |
| **Skill Gap Analysis** | < 5s | < 10s acceptable |
| **Course Recommendation** | < 7s | < 12s acceptable |

---

## Dimension 3: User Experience & System Usability

### A. LLM Quality

| Metric | Target | Evaluation Method |
|--------|--------|-------------------|
| **Hallucination Prevention** | ≥ 95% | Manual fact-check (20 outputs) |
| **Explanation Groundedness** | ≥ 90% | RAG attribution check (20 outputs) |
| **Response Relevance** | ≥ 85% | Manual assessment (20 outputs) |

**Groundedness Rubric** (used by all evaluators for consistent scoring):

| Level | Label | Definition |
|-------|-------|------------|
| ✅ | **Grounded** | Every factual claim is directly traceable to a retrieved KG node, course record, or peer CV entry |
| ⚠️ | **Partially Grounded** | Core recommendation is correct but contains at least one unverified supporting detail |
| ❌ | **Hallucinated** | One or more key claims (skill names, course fees, provider names) cannot be traced to any retrieved source |

### B. User Acceptance Testing (UAT)

> **⚠️ DESCOPED** — UAT not conducted within project timeline. Survey template exists in `evaluation/uat_survey_template.md` and test profiles in `data/test_profiles.json`. Documented as future work.

**8 Core Scenarios** (sufficient to demonstrate system capabilities):

| # | Profile | Validation Focus |
|---|---------|------------------|
| **S1** | Teacher → UX Designer | Career pivot validation |
| **S2** | Accountant → Data Analyst | Technical upskilling |
| **S3** | Engineer → AI/ML Specialist | Advanced technical path |
| **S4** | Nurse → Healthcare Data Scientist | Domain crossover |
| **S5** | Fresh Graduate → Software Developer | Entry-level handling |
| **S6** | Career Break (3yr) → Re-entry | Skill obsolescence |
| **S7** | Low Budget (<$500) | Budget constraints |
| **S8** | Conflicting Constraints | Failure mode handling |

### Success Criteria (Per Scenario)
- ✅ Profile collected successfully (all 5 fields)
- ✅ Skill gaps are relevant and actionable
- ✅ Courses exist in catalogue and satisfy constraints
- ✅ Explanation is clear and grounded (no hallucinations)
- ✅ User satisfaction ≥ 3.5/5 (basic acceptability); stretch goal: ≥ 4.0/5

**Overall Success:** ≥ 75% scenarios successful (6 out of 8)

---

## Edge Case & Failure Mode Testing (Simplified)

Demonstrate **graceful degradation** with 4 critical failure modes:

| Scenario | Expected Behavior | Test Result |
|----------|-------------------|-------------|
| **Zero Results** | Explain why + suggest constraint relaxation | Pass/Fail |
| **Conflicting Constraints** | Identify contradiction + guide resolution | Pass/Fail |
| **Insufficient Budget** | Suggest phased approach + subsidy options | Pass/Fail |
| **Ambiguous CV** | Request clarification + reasonable defaults | Pass/Fail |

**Target:** 100% of failure modes handled without crashing (4/4)

---

## Fairness & Ethics (Awareness Level)

**Purpose:** Demonstrate understanding of bias in AI career systems (not full audit).

### Experience Parity Check
- Test 2 scenarios with different experience levels (junior vs. senior)
- Measure if recommendation quality differs significantly (>20% NDCG gap)
- Document findings in limitations section

**Deliverable:** 1-paragraph fairness statement in final report acknowledging:
- Potential biases in training data (JDs, peer CVs)
- Scope limited to experience-level parity (demographic fairness is out of scope for this project)
- Future work: systematic fairness audits including demographic parity

---

## IRS Modular Course Mapping

### Machine Reasoning (MR)
- **CSP** → Stage 3 constraint satisfaction
- **CBR** → Stage 3 case-based path recommendations
- **Heuristic Search** → Stage 3 course sequencing

### Reasoning Systems (RS)
- **Knowledge Graph** → Stage 2 skill gap traversal
- **Semantic Similarity** → Stage 1/2 skill normalization
- **Competing Experts** → Stage 2 multi-expert arbitration

### Cognitive Systems (CGS)
- **NLP (spaCy, BERT)** → Data pipeline NER
- **LLM + RAG** → Explanation generation

### Technique Coverage Matrix

| Technique | IRS Module | Data Pipeline | Stage 1 | Stage 2 | Stage 3 | RAG Engine |
|-----------|-----------|:-------------:|:-------:|:-------:|:-------:|:----------:|
| Knowledge Representation / NER | CGS | ✅ | ✅ | | | |
| Semantic Similarity | RS | | ✅ | ✅ | | |
| Knowledge Graph Traversal | RS | ✅ | | ✅ | | |
| Competing Experts (Multi-Expert Arbitration) | RS | | | ✅ | | |
| CSP (OR-Tools) | MR | | | | ✅ | |
| Fuzzy Logic | MR | | | | ✅ | |
| CBR (k-NN) | MR | | | | ✅ | |
| Heuristic Search (Course Sequencing) | MR | | | | ✅ | |
| LLM + RAG | CGS | | | | | ✅ |

> ✅ = implemented and validated in this stage. This matrix maps directly to the Appendix in the final report.

---

## Evaluation Timeline (1-Month Project)

### Week 1: Setup & Baseline (4-6 hours/person)
- Create 20 annotated JDs, 10 CVs, 5 edge profiles
- Set up logging infrastructure, write validation scripts
- Develop UAT protocol and survey forms
- System integration, ensure E2E pipeline works on Databricks
- Run baseline measurement (current accuracy before improvements)

### Week 2: Development & Iteration (8-10 hours/person)
- Implement IRS techniques with logging
- Run weekly validation tests, track improvements
- Validate skill mappings and KG quality
- Mid-project checkpoint: are techniques demonstrable?

### Week 3: UAT & Validation (6-8 hours/person)
- Conduct 8 UAT scenarios with volunteers (classmates/family)
- Validate LLM groundedness (20 outputs)
- Run final technique validation tests
- Test failure modes and edge cases

### Week 4: Analysis & Reporting (8-10 hours/person)
- Generate metrics tables and evidence logs
- Analyze UAT results, satisfaction scores
- Write evaluation section (divide by dimension)
- Prepare demo and presentation slides

**Total Effort:** ~30 hours/person over 4 weeks (reasonable for part-time alongside jobs)

---

## Evaluation Artifacts (Deliverables)

### Code Artifacts (Simplified)
1. `evaluation/technique_validation.py` - Single script for all IRS technique tests
2. `evaluation/uat_tracker.xlsx` - Spreadsheet to track UAT results
3. `logs/` - Execution logs showing technique evidence

### Data Artifacts (Minimal Viable)
1. `data/gold_standard_jds.json` - 20 annotated job descriptions
2. `data/gold_standard_cvs.json` - 10 annotated CVs
3. `data/test_profiles.json` - 8 UAT scenarios + 5 edge cases
4. `data/skill_mappings_gold.json` - 50 verified skill relationships

### Report Components (Required for Grading)
1. **Section 4.1: Baseline vs. Final Metrics Table**
   - Show improvement over 4 weeks
   - Highlight IRS technique contributions

2. **Section 4.2: IRS Technique Validation Evidence**
   - One subsection per technique (7 techniques)
   - Quantitative results vs. success criteria
   - Sample logs/outputs demonstrating technique works

3. **Section 4.3: UAT Results & User Feedback**
   - 8 scenario results (pass/fail/partial)
   - User satisfaction scores
   - Qualitative feedback quotes

4. **Section 4.4: Limitations & Future Work**
   - Fairness considerations
   - Scope limitations (1-month project)
   - Production readiness gaps

5. **Appendix: Technique Coverage Matrix**
   - Visual showing which techniques are used in each stage
   - Maps to IRS course modules (MR, RS, CGS)

---

## Academic Rigor Checklist (Scaled for 1-Month Project)

- ✅ **Baseline Measurements** - Spot-check baseline before improvements
- ✅ **Quantitative Evidence** - Each IRS technique has success/failure data
- ✅ **UAT Validation** - 8 scenarios with real users (volunteers)
- ✅ **Failure Mode Coverage** - 4 critical failure modes tested
- ✅ **Reproducibility** - Simple scripts can be re-run
- ✅ **Documentation** - Clear methodology in report
- ✅ **Limitations Acknowledged** - Honest about scope constraints
- ✅ **Course Mapping** - Clear connection to IRS modules

**What We're NOT Doing (Out of Scope for 1-Month):**
- ❌ Statistical significance testing (t-tests, ANOVA) - not enough samples
- ❌ Inter-rater reliability (Kappa) - only 1 evaluator per UAT scenario
- ❌ Large-scale gold standard data - 100+ annotations too time-consuming
- ❌ Load testing - demo-quality performance sufficient
- ❌ Comprehensive fairness audit - awareness-level only
- ❌ Ablation studies - would require multiple system variants

---

## Grading Alignment

This evaluation framework supports the following grading criteria:

**Technical Implementation (40%)**
- IRS techniques implemented and logged ✅
- System produces end-to-end recommendations ✅
- Code quality and documentation ✅

**Evaluation & Validation (30%)**
- Quantitative evidence for each technique ✅
- UAT demonstrates system usability ✅
- Baseline vs. final improvement shown ✅

**IRS Course Mapping (20%)**
- Clear mapping to MR/RS/CGS modules ✅
- Technique coverage matrix provided ✅
- Justification for technique choices ✅

**Presentation & Documentation (10%)**
- Clear evaluation section in report ✅
- Evidence artifacts (logs, tables) ✅
- Honest discussion of limitations ✅

---

## Quick Start Guide for Team

**Week 1 Action Items:**
1. Download 20 job descriptions from MyCareersFuture, annotate skills (4 hours)
2. Write `technique_validation.py` script with test cases (4 hours)
3. Create UAT survey form and recruit 8 volunteers (4 hours)
4. Ensure system runs E2E on Databricks, add basic logging (4 hours)
5. Run baseline tests as a team, divide Week 2 tasks (2 hours)

**Golden Rule:** If something takes more than 2 hours, simplify or skip it. Focus on **demonstrating IRS techniques work**, not production perfection.

---

## Related Documentation

- [Architecture](architecture.md) — System overview
- [Stage 1](stage1_user_profile.md) · [Stage 2](stage2_skill_gap.md) · [Stage 3](stage3_course_recommendation.md)
- [RAG Explanation Engine](rag_explanation_engine.md) — Explanation quality
- [Tech Stack](tech_stack.md) — Implementation details
