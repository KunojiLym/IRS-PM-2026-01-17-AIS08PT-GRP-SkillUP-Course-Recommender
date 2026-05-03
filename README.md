## SECTION 1 : PROJECT TITLE
## SkillUP — AI-Powered Personalised Learning Path Coach for Singapore's Adult Upskilling Ecosystem

<img src="ProjectReport/SkillUP.png"
     style="float: left; margin-right: 0px;" />

---

## SECTION 2 : EXECUTIVE SUMMARY / PAPER ABSTRACT

Singapore has one of the world's most ambitious lifelong learning programmes. The SkillsFuture movement has invested billions in adult education subsidies and provides every Singaporean aged 40 and above with a S$4,000 top-up specifically for career transition through the SkillsFuture Level-Up Programme launched in May 2024. Participation has grown steadily — 555,000 Singaporeans enrolled in SSG-supported training in 2024, up from 520,000 in 2023, representing roughly one in five of the entire workforce. SkillsFuture Credit usage surged 35% year-on-year, from 192,000 users to 260,000, the fastest growth since the programme's inception.

Despite this momentum, a critical gap persists. Research acknowledges "information asymmetry" as a primary barrier to upskilling — people do not know which pathway is right for them. The existing MySkillsFuture portal is a directory, not an advisor. It can tell a user that a course exists; it cannot tell them whether that course is the right next step given their background, career goals, and personal constraints such as budget, schedule, and learning modality. ManpowerGroup's 2025 Talent Shortage Survey reports that 83% of Singapore employers have difficulty finding skilled talent, while another survey showed that 45% of employers plan to invest in employee upskilling in 2025. The demand is clear, but the navigation infrastructure is missing.

SkillUP addresses this navigation crisis through a **Hybrid Intelligent Reasoning Architecture (HIRA)** that combines multiple AI paradigms in a three-stage pipeline:

| Stage | Objective | Key IRS Techniques |
|-------|-----------|-------------------|
| **Preprocessing** | Ingesting and preparing the initial data | LLM extraction, Sentence-BERT, NER (spaCy) |
| **Stage 1 — User Profile Model** | Who is the user and what do they want? | LLM extraction, Sentence-BERT, Rule-Based Validation |
| **Stage 2 — Skill Gap Model** | Which skills is the user missing? | Neo4j KG Traversal, Embedding Similarity, Competing Experts, Meta-Arbiter |
| **Stage 3 — Course Recommendation** | Which courses should the user take? | CSP, Fuzzy Logic, Weighted Score Fusion |
| **RAG Explanation Engine** | Why is each course recommended? | RAG, GPT-4 Mini, Anti-hallucination safeguards |

The system takes a user's uploaded CV, target career role, budget, available time, and learning preferences, cross-references them against real Singapore job market demand data scraped from MyCareersFuture (MCF), and generates a personalised, sequenced, and fully explainable course pathway using SkillsFuture-eligible programmes.

Our team of 4 NUS-ISS graduate students built SkillUP as a one-month part-time academic sprint, leveraging Databricks for compute and MLflow tracking, Neo4j for knowledge graph operations, OpenAI GPT-4 Mini for natural language understanding, and Streamlit for the frontend. The system is validated with 143+ automated tests, and 7 IRS techniques mapped across MR, RS, and CGS course modules.

---

## SECTION 3 : CREDITS / PROJECT CONTRIBUTION

| Official Full Name | Student ID (MTech Applicable) | Work Items (Who Did What) | Email (Optional) |
| :------------ |:---------------:| :-----| :-----|
| Chachanond Ruenthongchai | A0339875H | xxxxxxxxxx yyyyyyyyyy zzzzzzzzzz | |
| Deebak Harsha S/O Sekar | A0340505R | xxxxxxxxxx yyyyyyyyyy zzzzzzzzzz | |
| Nazeer Bin Basir | A0340533N | xxxxxxxxxx yyyyyyyyyy zzzzzzzzzz | |
| Ouyang Yingzhao | A0021914R | xxxxxxxxxx yyyyyyyyyy zzzzzzzzzz | |

---

## SECTION 4 : VIDEO OF SYSTEM MODELLING & USE CASE DEMO

[SkillUP Demo Video](https://nusu.sharepoint.com/sites/ProjectTeam_bcnss7/_layouts/15/stream.aspx?id=%2Fsites%2FProjectTeam%5Fbcnss7%2FShared%20Documents%2FGeneral%2FSkillUP%20Intro%20and%20Demo%20Video%201080p%2Emp4&referrer=StreamWebApp%2EWeb&referrerScenario=AddressBarCopied%2Eview%2E764b0c97%2Dfb5f%2D45be%2Dad16%2D3f3abeb752f4)

[SkillUP Architecture Video](https://nusu.sharepoint.com/sites/ProjectTeam_bcnss7/_layouts/15/stream.aspx?id=%2Fsites%2FProjectTeam%5Fbcnss7%2FShared%20Documents%2FGeneral%2FSkillUP%20System%20Architecture%20Video%2Ewebm)

---
## SECTION 5 : USER GUIDE

`Refer to appendix <Installation & User Guide> in project report at Github Folder: ProjectReport`

### [ 1 ] To run the already deployed system:

> Request user access to the Databricks workspace from a team member

> Wait for team member to a) grant access and b) start the Databricks app

> Access the app: https://skillup-7474646515679193.aws.databricksapps.com/

### [ 2 ] To run the system locally (testing purposes only):

> **Prerequisites:** Python 3.8+, Neo4j database, OpenAI API key

> $ git clone https://github.com/KunojiLym/skillup.git

> $ cd skillup

> $ python -m venv .venv

> $ source .venv/bin/activate  *(or `.venv\Scripts\activate` on Windows)*

> $ pip install -r requirements.txt

> $ cp .env.example .env  *(edit .env with your API keys and credentials)*

> $ streamlit run app/app.py

> **Go to URL using web browser** http://localhost:8501

### [ 3 ] To run the system on Databricks (full functionality):

> Deploy to Databricks workspace with Unity Catalog access

> Configure environment variables: `OPENAI_API_KEY`, `NEO4J_URL`, `NEO4J_USER`, `NEO4J_PASSWORD`

> Preprocessing step needs to be done manually in Databricks and on Neo4k Aura

> Full data pipeline uses Delta tables, MLflow tracking, and PySpark operations

### [ 4 ] To run the test suite:

> $ cd skillup

> $ uv run pytest tests/ -m unit  *(all unit tests)*

> $ uv run pytest tests/ --cov=. --cov-report=html  *(with coverage report)*

> $ ./run_tests.sh smoke  *(quick smoke tests — or `.\run_tests.ps1 smoke` on Windows)*

---

## SECTION 6 : PROJECT REPORT / PAPER

`Refer to project report at Github Folder: ProjectReport`

**Recommended Sections for Project Report / Paper:**
- Executive Summary / Paper Abstract
- Business Problem Background — Singapore's SkillsFuture navigation gap
- Market Research — 555K SSG enrolments, 83% employer talent shortage, 9,000+ courses
- Project Objectives & Success Measurements
- Project Solution — Hybrid Intelligent Reasoning Architecture (HIRA) with 3-stage pipeline
- Project Implementation — Databricks + Neo4j + OpenAI + Streamlit
- Project Performance & Validation — 143+ tests
- Project Conclusions: Findings & Recommendation
- Appendix of report: Project Proposal
- Appendix of report: Mapped System Functionalities against knowledge, techniques and skills of modular courses: MR, RS, CGS
- Appendix of report: Installation and User Guide
- Appendix of report: 1-2 pages individual project report per project member, including: Individual reflection of project journey: (1) personal contribution to group project (2) what learnt is most useful for you (3) how you can apply the knowledge and skills in other situations or your workplaces
- Appendix of report: List of Abbreviations (if applicable)
- Appendix of report: References (if applicable)

---

## SECTION 7 : MISCELLANEOUS

### Project Structure

```
skillup/
├── app/                    # 🖥️ Streamlit frontend
├── knowledgegraph/         # 🔗 Knowledge Graph module (Neo4j)
├── skillgap/               # 🎯 Skill Gap Analysis module
├── recommender/            # 📋 Course Recommendation module (CSP, CBR, Fuzzy, Neural)
├── preprocessing/          # 🔄 Data preprocessing (Databricks notebooks)
├── evaluation/             # 📊 Evaluation notebooks & UAT
├── data/                   # 📊 Local data files (CSV fallbacks for test only, gold standards)
├── tests/                  # 🧪 Comprehensive test suite (143+ tests)
├── docs/                   # 📖 Project documentation
├── requirements.txt        # Python dependencies
├── app.yaml                # Databricks Apps deployment config
└── run_tests.sh/.ps1       # Test runner scripts
```

---