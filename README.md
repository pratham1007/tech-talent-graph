# Tech Talent Graph

A graph database app mapping developers, skills, projects & companies. Uses CognoDB + FastAPI with multi-hop Cypher traversals to answer talent questions that are awkward in SQL. Built with Python and vanilla JS.

**Live demo:** https://tech-talent-graph.onrender.com/
**Screen recording:** (https://www.loom.com/share/bfc127cfaf004e609977e5effdfb5abe)

---

## Screenshots

Developers Page:
<img width="2940" height="1582" alt="image" src="https://github.com/user-attachments/assets/09fa85f0-0e96-4e3b-a253-27f8fb3613f7" />

Skills Page:
<img width="2940" height="1578" alt="image" src="https://github.com/user-attachments/assets/84119736-aebf-46c0-9902-ad16adecdb49" />

Skill Bridges Page:
<img width="2928" height="1578" alt="image" src="https://github.com/user-attachments/assets/78f8b81f-55b8-4fef-aa31-2489a7dcf0ff" />

Projects Page:
<img width="2940" height="1580" alt="image" src="https://github.com/user-attachments/assets/5d0b7652-25e0-4fa2-84e2-d2f0b86a702e" />

---

## Why a graph database?

The interesting questions in talent data are all about connections:

| Question | Relational pain | Graph answer |
|---|---|---|
| "Who shares skills with this developer?" | Self-join on a junction table, GROUP BY, HAVING | 2-hop: `Developer → Skill → Developer` |
| "Which skills bridge the most companies?" | 3-way join + nested GROUP BY | Single MATCH with `collect(DISTINCT)` |
| "Find best-fit developers for a project via shared company context" | 4-table join with correlated subquery | 3-hop traversal in one Cypher clause |

A relational schema would need at least 5 tables and complex joins for every query above. In Cypher, each is a single readable pattern match. The graph model also makes it trivial to add new relationship types (e.g. `MENTORED`, `REVIEWED_CODE_FOR`) without schema migrations.

---

## Data model

```
(Developer)-[:HAS_SKILL]----->(Skill)
(Developer)-[:WORKED_AT]----->(Company)
(Developer)-[:WORKED_ON]----->(Project)
(Company)  -[:RAN]---------->(Project)
(Project)  -[:REQUIRES_SKILL]->(Skill)
```

### Node labels & key properties

| Label | Properties |
|---|---|
| `Developer` | `id`, `name`, `title`, `location`, `bio` |
| `Skill` | `name`, `category` |
| `Company` | `id`, `name`, `industry` |
| `Project` | `id`, `name`, `description`, `status` |

### Relationship types

| Type | From → To | Meaning |
|---|---|---|
| `HAS_SKILL` | Developer → Skill | Developer has this skill |
| `WORKED_AT` | Developer → Company | Developer was employed here |
| `WORKED_ON` | Developer → Project | Developer contributed to this project |
| `RAN` | Company → Project | Company ran / sponsored this project |
| `REQUIRES_SKILL` | Project → Skill | Project needs this skill |

---

## Main queries explained

### 1. Skill network — 2-hop traversal
```cypher
MATCH (d:Developer {id: $id})-[:HAS_SKILL]->(s:Skill)<-[:HAS_SKILL]-(peer:Developer)
WHERE peer.id <> $id
RETURN peer.name, collect(DISTINCT s.name) AS shared_skills, count(DISTINCT s) AS overlap
ORDER BY overlap DESC
```
Finds all developers reachable in exactly 2 hops through shared skills. Impossible to express cleanly in SQL without a self-join on a junction table.

### 2. Skill bridges — cross-company skills
```cypher
MATCH (c:Company)<-[:WORKED_AT]-(d:Developer)-[:HAS_SKILL]->(s:Skill)
WITH s, collect(DISTINCT c.name) AS companies, count(DISTINCT d) AS dev_count
WHERE size(companies) > 1
RETURN s.name, companies, size(companies) AS company_count
ORDER BY company_count DESC
```
Identifies skills that appear across multiple companies — a graph-native aggregation over a variable-length path.

### 3. Project staffing — 3-hop traversal
```cypher
MATCH (p:Project {id: $id})-[:REQUIRES_SKILL]->(s:Skill)<-[:HAS_SKILL]-(d:Developer)
WITH d, collect(DISTINCT s.name) AS matched_skills, count(DISTINCT s) AS match_count
OPTIONAL MATCH (d)-[:WORKED_AT]->(c:Company)-[:RAN]->(p2:Project)-[:REQUIRES_SKILL]->(s2:Skill)
WHERE s2.name IN matched_skills
RETURN d.name, matched_skills, match_count, collect(DISTINCT c.name) AS relevant_companies
ORDER BY match_count DESC
```
Traverses 3 hops to find developers who not only have the required skills but also have company context relevant to the project.

---

## Project structure

```
.
├── backend/
│   ├── __init__.py
│   ├── db.py          # Driver singleton, reads env vars
│   ├── queries.py     # All Cypher queries (parameterised)
│   └── main.py        # FastAPI app + routes
├── frontend/
│   └── index.html     # Single-page app (vanilla JS)
├── scripts/
│   └── seed.py        # Loads realistic seed data
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup & run

### 1. Create a CognoDB instance

1. Sign up at [console.cognodb.com/signup](https://console.cognodb.com/signup) — free, no credit card required
2. Create a free **c0** instance and choose a region
3. Copy the `bolt+s://` URI and the generated password (shown only once)

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your COGNODB_URI and COGNODB_PASSWORD
```

`.env` format:
```
COGNODB_URI=bolt+s://<instance-id>.databases.cognodb.cloud
COGNODB_USER=cognodb
COGNODB_PASSWORD=your-password
```

### 3. Install dependencies

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Seed the database

```bash
python scripts/seed.py
```

This loads 15 developers, 25 skills, 8 companies, 8 projects and all relationships.

### 5. Run the application

```bash
uvicorn backend.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000)

---

## Hosting

Deploy to any platform that runs Python. For free tier hosting:

- **Render / Railway**: push the repo, set the three env vars (`COGNODB_URI`, `COGNODB_USER`, `COGNODB_PASSWORD`), set start command to:
  ```
  uvicorn backend.main:app --host 0.0.0.0 --port 8000
  ```
- The frontend is served as static files by FastAPI — no separate hosting needed.
