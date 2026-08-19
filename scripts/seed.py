"""
Seed script — loads realistic Tech Talent Graph data into CognoDB.
Run: python scripts/seed.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

load_dotenv()

SKILLS = [
    ("s-python",     "Python",        "Language"),
    ("s-js",         "JavaScript",    "Language"),
    ("s-ts",         "TypeScript",    "Language"),
    ("s-go",         "Go",            "Language"),
    ("s-rust",       "Rust",          "Language"),
    ("s-java",       "Java",          "Language"),
    ("s-react",      "React",         "Frontend"),
    ("s-vue",        "Vue.js",        "Frontend"),
    ("s-nextjs",     "Next.js",       "Frontend"),
    ("s-fastapi",    "FastAPI",       "Backend"),
    ("s-django",     "Django",        "Backend"),
    ("s-node",       "Node.js",       "Backend"),
    ("s-graphql",    "GraphQL",       "Backend"),
    ("s-postgres",   "PostgreSQL",    "Database"),
    ("s-neo4j",      "Neo4j",         "Database"),
    ("s-redis",      "Redis",         "Database"),
    ("s-kafka",      "Kafka",         "Data"),
    ("s-spark",      "Apache Spark",  "Data"),
    ("s-ml",         "Machine Learning", "AI"),
    ("s-llm",        "LLM Fine-tuning",  "AI"),
    ("s-k8s",        "Kubernetes",    "DevOps"),
    ("s-docker",     "Docker",        "DevOps"),
    ("s-terraform",  "Terraform",     "DevOps"),
    ("s-aws",        "AWS",           "Cloud"),
    ("s-gcp",        "GCP",           "Cloud"),
]

COMPANIES = [
    ("c-stripe",    "Stripe",         "Fintech"),
    ("c-vercel",    "Vercel",         "Developer Tools"),
    ("c-databricks","Databricks",     "Data & AI"),
    ("c-figma",     "Figma",          "Design Tools"),
    ("c-linear",    "Linear",         "Productivity"),
    ("c-openai",    "OpenAI",         "AI"),
    ("c-cloudflare","Cloudflare",     "Infrastructure"),
    ("c-hashicorp", "HashiCorp",      "DevOps"),
]

DEVELOPERS = [
    ("d-01", "Aisha Patel",      "Senior Backend Engineer",  "San Francisco, CA",
     "Passionate about distributed systems and open-source.",
     ["s-python","s-go","s-fastapi","s-postgres","s-kafka","s-k8s","s-docker"],
     ["c-stripe","c-cloudflare"]),
    ("d-02", "Marcus Chen",      "Full-Stack Engineer",      "New York, NY",
     "Loves building products from zero to one.",
     ["s-ts","s-react","s-nextjs","s-node","s-postgres","s-docker"],
     ["c-vercel","c-linear"]),
    ("d-03", "Sofia Rossi",      "ML Engineer",              "London, UK",
     "Bridging research and production ML.",
     ["s-python","s-ml","s-llm","s-spark","s-kafka","s-aws"],
     ["c-databricks","c-openai"]),
    ("d-04", "James Okafor",     "DevOps / Platform Eng",    "Lagos, Nigeria",
     "Infrastructure as code evangelist.",
     ["s-k8s","s-terraform","s-docker","s-go","s-aws","s-gcp"],
     ["c-hashicorp","c-cloudflare"]),
    ("d-05", "Yuki Tanaka",      "Frontend Engineer",        "Tokyo, Japan",
     "Obsessed with performance and accessibility.",
     ["s-ts","s-react","s-vue","s-nextjs","s-graphql"],
     ["c-figma","c-vercel"]),
    ("d-06", "Priya Nair",       "Data Engineer",            "Bangalore, India",
     "Pipelines, lakes, and everything in between.",
     ["s-python","s-spark","s-kafka","s-postgres","s-redis","s-aws"],
     ["c-databricks","c-stripe"]),
    ("d-07", "Luca Bianchi",     "Backend Engineer",         "Berlin, Germany",
     "API design and reliability engineering.",
     ["s-go","s-rust","s-graphql","s-postgres","s-redis","s-k8s"],
     ["c-cloudflare","c-linear"]),
    ("d-08", "Elena Volkov",     "AI Research Engineer",     "Amsterdam, NL",
     "From transformers to production inference.",
     ["s-python","s-ml","s-llm","s-rust","s-gcp"],
     ["c-openai","c-databricks"]),
    ("d-09", "Carlos Mendez",    "Full-Stack Engineer",      "Mexico City, MX",
     "React, Node, and a love for great DX.",
     ["s-js","s-ts","s-react","s-node","s-graphql","s-docker"],
     ["c-vercel","c-figma"]),
    ("d-10", "Amara Diallo",     "Security Engineer",        "Paris, France",
     "Zero-trust, supply-chain security, and Rust.",
     ["s-rust","s-go","s-k8s","s-terraform","s-aws"],
     ["c-hashicorp","c-stripe"]),
    ("d-11", "Noah Kim",         "Senior Frontend Engineer", "Seoul, South Korea",
     "Design systems and component architecture.",
     ["s-ts","s-react","s-vue","s-nextjs","s-graphql"],
     ["c-figma","c-linear"]),
    ("d-12", "Fatima Al-Hassan", "Backend Engineer",         "Dubai, UAE",
     "High-throughput APIs and event-driven systems.",
     ["s-java","s-kafka","s-postgres","s-redis","s-docker","s-aws"],
     ["c-stripe","c-cloudflare"]),
    ("d-13", "Raj Sharma",       "Platform Engineer",        "Toronto, Canada",
     "Kubernetes, observability, and chaos engineering.",
     ["s-go","s-k8s","s-terraform","s-docker","s-gcp"],
     ["c-hashicorp","c-databricks"]),
    ("d-14", "Mei Lin",          "Data Scientist",           "Singapore",
     "Statistical modeling and ML pipelines.",
     ["s-python","s-ml","s-spark","s-postgres","s-gcp"],
     ["c-databricks","c-openai"]),
    ("d-15", "Oliver Schmidt",   "Rust Systems Engineer",    "Munich, Germany",
     "Low-latency systems and WebAssembly.",
     ["s-rust","s-go","s-docker","s-k8s","s-aws"],
     ["c-cloudflare","c-hashicorp"]),
]

PROJECTS = [
    ("p-01", "Payments Reliability Platform",
     "Real-time payment processing with sub-10ms p99 latency.",
     "active",
     ["s-go","s-kafka","s-postgres","s-redis","s-k8s"],
     ["c-stripe"],
     ["d-01","d-07","d-12"]),
    ("p-02", "Edge Rendering Engine",
     "Server-side rendering at the CDN edge for Next.js apps.",
     "active",
     ["s-ts","s-nextjs","s-rust","s-k8s"],
     ["c-vercel","c-cloudflare"],
     ["d-02","d-05","d-15"]),
    ("p-03", "LLM Fine-tuning Pipeline",
     "Scalable pipeline for domain-specific LLM fine-tuning.",
     "active",
     ["s-python","s-ml","s-llm","s-spark","s-aws"],
     ["c-openai","c-databricks"],
     ["d-03","d-08","d-14"]),
    ("p-04", "Infrastructure Automation Suite",
     "Terraform modules and Kubernetes operators for multi-cloud.",
     "active",
     ["s-terraform","s-k8s","s-go","s-aws","s-gcp"],
     ["c-hashicorp"],
     ["d-04","d-13","d-10"]),
    ("p-05", "Design System v3",
     "Accessible, themeable component library used across all products.",
     "active",
     ["s-ts","s-react","s-vue","s-graphql"],
     ["c-figma","c-linear"],
     ["d-05","d-09","d-11"]),
    ("p-06", "Real-time Data Lake",
     "Streaming ingestion and query layer over petabyte-scale data.",
     "completed",
     ["s-python","s-spark","s-kafka","s-postgres","s-gcp"],
     ["c-databricks"],
     ["d-06","d-03","d-14"]),
    ("p-07", "Zero-Trust Network Gateway",
     "Identity-aware proxy with mTLS and policy engine.",
     "active",
     ["s-rust","s-go","s-k8s","s-terraform"],
     ["c-cloudflare","c-hashicorp"],
     ["d-07","d-10","d-15"]),
    ("p-08", "GraphQL Federation Layer",
     "Unified graph API across 12 microservices.",
     "active",
     ["s-ts","s-graphql","s-node","s-redis"],
     ["c-linear","c-figma"],
     ["d-09","d-11","d-02"]),
]


def seed(session):
    print("Clearing existing data...")
    session.run("MATCH (n) DETACH DELETE n")

    print("Creating constraints...")
    for label, prop in [("Developer","id"),("Skill","name"),("Company","id"),("Project","id")]:
        session.run(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE")

    print("Creating Skills...")
    for sid, name, category in SKILLS:
        session.run(
            "MERGE (s:Skill {name: $name}) SET s.category = $category",
            name=name, category=category
        )

    print("Creating Companies...")
    for cid, name, industry in COMPANIES:
        session.run(
            "MERGE (c:Company {id: $id}) SET c.name = $name, c.industry = $industry",
            id=cid, name=name, industry=industry
        )

    print("Creating Developers + relationships...")
    for dev_id, name, title, location, bio, skill_ids, company_ids in DEVELOPERS:
        session.run(
            """
            MERGE (d:Developer {id: $id})
            SET d.name=$name, d.title=$title, d.location=$location, d.bio=$bio
            """,
            id=dev_id, name=name, title=title, location=location, bio=bio
        )
        skill_names = [s[1] for s in SKILLS if s[0] in skill_ids]
        for sname in skill_names:
            session.run(
                """
                MATCH (d:Developer {id: $did}), (s:Skill {name: $sname})
                MERGE (d)-[:HAS_SKILL]->(s)
                """,
                did=dev_id, sname=sname
            )
        for cid in company_ids:
            session.run(
                """
                MATCH (d:Developer {id: $did}), (c:Company {id: $cid})
                MERGE (d)-[:WORKED_AT]->(c)
                """,
                did=dev_id, cid=cid
            )

    print("Creating Projects + relationships...")
    for pid, name, desc, status, skill_ids, company_ids, dev_ids in PROJECTS:
        session.run(
            """
            MERGE (p:Project {id: $id})
            SET p.name=$name, p.description=$desc, p.status=$status
            """,
            id=pid, name=name, desc=desc, status=status
        )
        skill_names = [s[1] for s in SKILLS if s[0] in skill_ids]
        for sname in skill_names:
            session.run(
                """
                MATCH (p:Project {id: $pid}), (s:Skill {name: $sname})
                MERGE (p)-[:REQUIRES_SKILL]->(s)
                """,
                pid=pid, sname=sname
            )
        for cid in company_ids:
            session.run(
                """
                MATCH (p:Project {id: $pid}), (c:Company {id: $cid})
                MERGE (c)-[:RAN]->(p)
                """,
                pid=pid, cid=cid
            )
        for did in dev_ids:
            session.run(
                """
                MATCH (d:Developer {id: $did}), (p:Project {id: $pid})
                MERGE (d)-[:WORKED_ON]->(p)
                """,
                did=did, pid=pid
            )

    print("✓ Seed complete.")


if __name__ == "__main__":
    uri      = os.environ["COGNODB_URI"]
    user     = os.environ["COGNODB_USER"]
    password = os.environ["COGNODB_PASSWORD"]
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        with driver.session() as session:
            seed(session)
        driver.close()
    except (ServiceUnavailable, AuthError) as e:
        print(f"✗ Could not connect to database: {e}")
        sys.exit(1)
