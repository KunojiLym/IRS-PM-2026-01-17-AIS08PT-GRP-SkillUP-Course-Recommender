# SkillUp UAT Survey — Evaluator Template

> **Purpose:** Use this document as the question template when setting up the UAT survey on **Google Forms** or **Microsoft Forms**.  
> **One form per session** (evaluate one scenario per form submission).  
> Results collected via Forms are the source of truth; mirror a summary into `evaluation/results/uat_results_summary.csv` after each session week.

---

## Section 1: Session Metadata

| Field | Type | Notes |
|-------|------|-------|
| Scenario ID | Dropdown (S1–S8) | Which UAT scenario is being evaluated |
| Evaluator Name | Short text | Team member conducting the evaluation |
| Volunteer ID | Short text | Anonymous e.g. "V01", "V02" (do not collect real names) |
| Date | Date picker | Session date |
| Session Duration (minutes) | Number | How long the full interaction took |

---

## Section 2: Functional Checklist

*Answer Yes / No / Partial for each item.*

**Q1 — Profile Collection**  
Were all 5 required fields collected successfully (current role, target role, skills, budget, time availability)?  
`Yes | Partial | No`  
*If Partial/No:* Which field(s) were missing or incorrect? [Short text]

**Q2 — Skill Gap Relevance**  
Are the identified skill gaps relevant and actionable for the stated target role?  
`Yes | Partial | No`  
*If Partial/No:* Describe the issue: [Short text]

**Q3 — Course Catalogue Validity**  
Do all recommended courses exist in the SkillsFuture catalogue with correct fees, provider, and duration?  
`Yes | Partial | No`  
*If Partial/No:* Which course(s) had issues? [Short text]

**Q4 — Explanation Groundedness**  
Does the system's explanation reference specific skills, courses, and gaps (no generic or vague statements)?  
`Yes | Partial | No`  
*If Partial/No:* Describe: [Short text]

**Q5 — Hallucination Check**  
Were any factual errors noticed? (e.g. wrong course name, incorrect fee, non-existent provider)  
`No issues | Minor issue | Major hallucination`  
*If issue:* Describe the error: [Short text]

---

## Section 3: Constraint Satisfaction

**Q6** — Were budget constraints respected (all courses within stated budget)?  
`Yes | No` — If No: [Short text]

**Q7** — Were time constraints respected (total course hours fit within stated weekly availability)?  
`Yes | No` — If No: [Short text]

**Q8** — Were modality constraints respected (online/hybrid/in-person as requested)?  
`Yes | No` — If No: [Short text]

---

## Section 4: User Satisfaction

**Q9 — Overall Satisfaction**  
*Ask the volunteer:* "On a scale of 1–5, how satisfied are you with the learning path recommended?"  
`1 (Very dissatisfied) | 2 | 3 | 4 | 5 (Very satisfied)`

**Q10 — Clarity of Explanation**  
*Ask the volunteer:* "How clear and understandable was the explanation provided?"  
`1 (Very unclear) | 2 | 3 | 4 | 5 (Very clear)`

**Q11 — What worked well?**  
[Long text — volunteer's own words]

**Q12 — What could be improved?**  
[Long text — volunteer's own words]

---

## Section 5: Scenario Outcome

**Q13 — Overall Scenario Result**  
Based on Q1–Q8, how do you rate this scenario?  
`Pass (all 5 core criteria met) | Partial (3–4 criteria met) | Fail (≤2 criteria met)`

**Q14 — Evaluator Notes**  
[Long text — any additional observations, unexpected behaviour, or edge cases noticed]

---

## Scoring Reference (Evaluator Use Only)

| Core Criterion | Maps To | Pass Condition |
|----------------|---------|----------------|
| Profile collected | Q1 | Yes or Partial acceptable |
| Skill gaps relevant | Q2 | Yes |
| Courses in catalogue | Q3 | Yes |
| Explanation grounded | Q4 | Yes |
| No hallucinations | Q5 | No issues |

**Overall Pass:** All 5 criteria met = Pass. Volunteer satisfaction Q9 ≥ 3.5 average across scenarios.

---

## Forms Setup Notes

- Create **one form** with the above questions
- Use **Conditional questions** to show follow-up text fields only when Partial/No is selected (Google Forms supports this via "Go to section based on answer")
- Set responses to collect into a **Google Sheet** (Forms → Responses → Link to Sheets)
- Share the Sheet link with the team to mirror results into `evaluation/results/uat_results_summary.csv` after Week 3
- Do **not** collect volunteer real names — use anonymous IDs (V01, V02, ...)
