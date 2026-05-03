# Technology Stack

> Full reference of technologies, libraries, and infrastructure used in SkillUP.

---

## Stack Overview

| Layer | Technologies |
|-------|-------------|
| **Infrastructure** | Databricks, Neo4j, OpenAI GPT-4 Mini, GitHub |
| **NLP** | spaCy, Sentence-BERT, HuggingFace Transformers |
| **Reasoning** | LangChain, Google OR-Tools, PyTorch |
| **Data** | Scrapy, BeautifulSoup, PyPDF2 |
| **Frontend** | Streamlit |

---

## Infrastructure

### Databricks
- **Role:** Data processing, model training, pipeline orchestration
- **Usage:** Batch processing of job descriptions, course catalogues, and CV data
- **Features used:** Notebooks, Jobs, MLflow for experiment tracking

### Neo4j
- **Role:** Knowledge Graph storage and traversal
- **Usage:** Stores skill-role-course-industry relationships; powers Stage 2 gap analysis
- **Query language:** Cypher
- **Key operations:** Path traversal, pattern matching, aggregate queries

### OpenAI GPT-4 Mini
- **Role:** LLM for conversational AI, CV analysis, and explanation generation
- **Usage:**
  - Maya chatbot (conversational profile collection)
  - CV parsing and structured extraction
  - Career plan generation
  - RAG-based explanation synthesis
- **Configuration:** `gpt-4o-mini`, temperature 0.7 (conversation), 0.3 (extraction)

### GitHub
- **Role:** Version control and CI/CD
- **Usage:** Source code management, pull requests, issue tracking

---

## NLP Layer

### spaCy
- **Role:** Named Entity Recognition (NER) and text processing
- **Usage:** Extract skills, roles, organisations from JDs and CVs
- **Model:** Custom-trained on Singapore labour market data
- **Entities:** `SKILL`, `ROLE`, `ORGANISATION`, `QUALIFICATION`, `TOOL`

### Sentence-BERT (via HuggingFace)
- **Role:** Semantic embedding generation
- **Usage:** Encode skills, roles, courses into dense vector space
- **Model:** `all-MiniLM-L6-v2` (384 dimensions)
- **Application:** Skill normalisation, semantic similarity matching

### HuggingFace Transformers
- **Role:** Model hosting and inference
- **Usage:** Sentence-BERT model loading; future fine-tuned models
- **Integration:** Via `sentence-transformers` Python package

---

## Reasoning Layer

### LangChain
- **Role:** LLM orchestration and RAG pipeline
- **Usage:**
  - Chain multiple LLM calls with context
  - Retrieval-Augmented Generation pipeline
  - Prompt templating and management
- **Components:** Chains, Retrievers, Output Parsers

### Google OR-Tools
- **Role:** Constraint Satisfaction Problem (CSP) solver
- **Usage:** Course selection and sequencing under hard constraints
- **Solver:** CP-SAT solver for backtracking with arc consistency (AC-3)
- **Constraints modelled:** Budget, time, modality, prerequisites

### PyTorch
- **Role:** Neural network components
- **Usage:**
  - Neural ranker for course scoring (future MLP optimisation)
  - Embedding fine-tuning (if needed)
  - Score fusion weight learning

---

## Data Layer

### Scrapy
- **Role:** Web scraping framework
- **Usage:** Crawl MyCareersFuture portal for job postings
- **Features:** Politeness policies, rate limiting, proxy rotation

### BeautifulSoup
- **Role:** HTML parsing
- **Usage:** Parse SkillsFuture course catalogue pages
- **Integration:** Used alongside Scrapy for complex page structures

### PyPDF2
- **Role:** PDF text extraction
- **Usage:** Extract text from uploaded CV files (PDF format)
- **Fallback:** python-docx for DOCX format CVs

---

## Frontend

### Streamlit
- **Role:** Web application framework
- **Usage:** Full user interface including:
  - CV upload interface
  - Maya chatbot with suggestion chips
  - Career plan display with streaming
  - Debug panel for development
- **Deployment:** Google Cloud App Engine (via `app.yaml`)
- **Styling:** Custom CSS for branded UI

---

## Python Dependencies

```
# Core
streamlit              # Web app framework
openai                 # GPT-4 Mini API client
pandas                 # Data manipulation

# CV Parsing
PyPDF2                 # PDF text extraction
python-docx            # DOCX text extraction

# NLP (planned)
spacy                  # NER and text processing
sentence-transformers  # Sentence-BERT embeddings
transformers           # HuggingFace models

# Knowledge Graph (planned)
neo4j                  # Neo4j Python driver
py2neo                 # High-level Neo4j interface

# Reasoning (planned)
langchain              # LLM orchestration + RAG
ortools                # Google OR-Tools CSP solver
torch                  # PyTorch for neural ranking

# Data Ingestion (planned)
scrapy                 # Web scraping
beautifulsoup4         # HTML parsing
requests               # HTTP client

# Infrastructure
databricks-sdk         # Databricks integration
databricks-sql-connector  # Databricks SQL
```

---

## Deployment Configuration

### `app.yaml` (Google Cloud App Engine)

```yaml
command:
  - "streamlit"
  - "run"
  - "app/app.py"

env:
  - name: OPENAI_API_KEY
    value: "<secret>"
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 Mini | ✅ Yes |
| `NEO4J_URI` | Neo4j database connection URI | Planned |
| `NEO4J_USER` | Neo4j username | Planned |
| `NEO4J_PASSWORD` | Neo4j password | Planned |
| `DATABRICKS_HOST` | Databricks workspace URL | Planned |
| `DATABRICKS_TOKEN` | Databricks access token | Planned |

---

## Related Documentation

- [Architecture](architecture.md) — How the tech stack pieces fit together
- [Data Pipeline](data_pipeline.md) — Data layer details
- [Stage 3: Course Recommendation](stage3_course_recommendation.md) — OR-Tools usage
