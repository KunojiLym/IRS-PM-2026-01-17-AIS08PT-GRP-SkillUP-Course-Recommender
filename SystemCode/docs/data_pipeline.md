# Data Pipeline

> Data ingestion, NLP processing, and representation layer — transforming raw external data into structured, queryable knowledge.

---

## Overview

The data pipeline is responsible for converting raw, unstructured data from Singapore's labour market and education ecosystem into two queryable stores:

1. **Knowledge Graph (Neo4j)** — Structured relationships between skills, roles, courses, and industries
2. **Vector Store + Ratings Data** — Embedding-based similarity search and course quality signals

```
Raw Data Sources → Scraping → NLP Processing → Structured Stores
```

---

## Data Sources

### 1. MyCareersFuture (MCF) Portal — Job Descriptions

| Attribute | Detail |
|-----------|--------|
| **Source** | [MyCareersFuture API](https://www.mycareersfuture.gov.sg/) |
| **Content** | Job descriptions with tagged skills |
| **Purpose** | Establish real-time skill demand signals for Singapore's labour market |
| **Update Frequency** | Periodic batch scraping (weekly recommended) |

**Key fields extracted:**
- Job title / Role
- Required skills (tagged + free-text)
- Industry / Sector
- Experience level
- Salary range (where available)

### 2. SkillsFuture Course Catalogue — Course Data

| Attribute | Detail |
|-----------|--------|
| **Source** | SSG SkillsFuture directory |
| **Content** | Course catalogue — fees, duration, modality |
| **Purpose** | Populate the course recommendation pool with eligible programmes |
| **Update Frequency** | Monthly sync recommended |

**Key fields extracted:**
- Course title and ID
- Training provider
- Full fee and subsidised fee
- Duration (hours / weeks)
- Delivery modality (online, in-person, blended)
- SkillsFuture Credit eligibility
- Skills taught (mapped to taxonomy)

### 3. Peer CVs — Sample Profiles

| Attribute | Detail |
|-----------|--------|
| **Source** | Public CV databases, anonymised samples |
| **Content** | Professional profiles for benchmarking |
| **Purpose** | Power the "Peer CV Expert" in the Competing Experts framework (Stage 2) |

**Key fields extracted:**
- Current role / Industry
- Skills inventory
- Years of experience
- Education background
- Career transition patterns

### 4. Course Ratings + Reviews — Quality Signals

| Attribute | Detail |
|-----------|--------|
| **Source** | Course feedback, review platforms |
| **Content** | Learner satisfaction data |
| **Purpose** | Quality-weight course recommendations |

**Key fields extracted:**
- Course ID (mapped to catalogue)
- Overall rating (normalised to 0–1)
- Completion rate
- Learner comments (sentiment analysis)

---

## NLP Processing Pipeline

The processing pipeline transforms raw text into structured knowledge through five sequential stages:

```
┌──────────┐    ┌──────────┐    ┌─────────────┐    ┌────────────┐    ┌─────────────┐
│ Scraping  │───▶│   NER    │───▶│    Skill    │───▶│ Embedding  │───▶│    Graph    │
│           │    │          │    │ Extraction  │    │ Generation │    │    Build    │
└──────────┘    └──────────┘    └─────────────┘    └────────────┘    └─────────────┘
```

### Stage 1: Web Scraping

**Tools:** Scrapy, BeautifulSoup, PyPDF2

- Crawl MCF portal for job postings
- Parse SkillsFuture course listings
- Extract text from uploaded CV files (PDF, DOCX)
- Rate limiting and politeness policies for external APIs

**Output:** Raw text corpus per data source

### Stage 2: Named Entity Recognition (NER)

**Tools:** spaCy (custom NER model)

- Identify entities: `SKILL`, `ROLE`, `ORGANISATION`, `QUALIFICATION`, `TOOL`
- Custom-trained on Singapore labour market data
- Handle domain-specific terminology (e.g., "AWS", "Agile", "Six Sigma")

**Output:** Annotated text with tagged entities

### Stage 3: Skill Extraction

**Tools:** Rule-based matchers + ML classifiers

- Map extracted entities to a **canonical skill taxonomy**
- Resolve synonyms and variants:
  - "data wrangling" → "data preparation"
  - "Python scripting" → "Python programming"
  - "ML" → "machine learning"
- Assign confidence scores to extracted skills
- Remove invalid or overly generic skills

**Output:** Normalised skill entities with confidence scores

### Stage 4: Embedding Generation

**Tools:** Sentence-BERT (via HuggingFace)

- Encode each skill, role, and course description into a dense vector
- Model: `all-MiniLM-L6-v2` or equivalent
- Vector dimensions: 384
- Enable semantic similarity search across different terminology

**Output:** Vector embeddings stored in vector store

### Stage 5: Knowledge Graph Construction

**Tools:** Neo4j + Python driver

- Build nodes for: `Skill`, `Role`, `Course`, `Industry`, `Provider`
- Build edges for relationships:
  - `Role -[REQUIRES]→ Skill`
  - `Course -[TEACHES]→ Skill`
  - `Skill -[RELATED_TO]→ Skill`
  - `Course -[PROVIDED_BY]→ Provider`
  - `Role -[BELONGS_TO]→ Industry`
- Weight edges by frequency, recency, and confidence

**Output:** Populated Neo4j knowledge graph

---

## Knowledge Graph Schema

```
(:Role {title, industry, demand_count, avg_salary})
  -[:REQUIRES {weight, recency}]→
(:Skill {name, category, embedding_id})
  ←[:TEACHES {coverage, depth}]-
(:Course {id, title, provider, fee, subsidised_fee, duration, modality, rating})
  -[:PROVIDED_BY]→
(:Provider {name, type, accredited})

(:Skill)-[:RELATED_TO {similarity}]→(:Skill)
(:Role)-[:BELONGS_TO]→(:Industry {name, growth_rate})
```

### Example Traversal

To find courses that bridge a skill gap for a target role:

```
MATCH (target:Role {title: "Data Analyst"})
      -[:REQUIRES]->(needed:Skill)
WHERE NOT needed.name IN $user_skills
MATCH (c:Course)-[:TEACHES]->(needed)
RETURN c, needed, c.rating
ORDER BY c.rating DESC
```

---

## Vector Store Schema

| Collection | Content | Embedding Model |
|------------|---------|-----------------|
| `skills` | Canonical skill descriptions | Sentence-BERT |
| `roles` | Job descriptions from MCF | Sentence-BERT |
| `courses` | Course descriptions from SSG | Sentence-BERT |
| `cv_chunks` | Parsed CV text segments | Sentence-BERT |

**Similarity search** enables matching even when exact terminology differs between a user's CV and the skill taxonomy.

---

## Data Refresh Strategy

| Source | Refresh Cadence | Method |
|--------|----------------|--------|
| MCF Job Descriptions | Weekly | Incremental scrape |
| SkillsFuture Catalogue | Monthly | Full resync |
| Peer CVs | Quarterly | Batch import |
| Course Ratings | Monthly | API pull + sentiment analysis |
| Knowledge Graph | After each data refresh | Incremental graph update |

---

## Related Documentation

- [Architecture](architecture.md) — System-level design
- [Stage 1: User Profile Model](stage1_user_profile.md) — How user CVs are processed
- [Tech Stack](tech_stack.md) — Tools and libraries used
