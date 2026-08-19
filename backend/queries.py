from neo4j import Session

# ── Developers ────────────────────────────────────────────────────────────────

def search_developers(session: Session, query: str = "", skill: str = ""):
    cypher = """
    MATCH (d:Developer)
    WHERE ($query = '' OR toLower(d.name) CONTAINS toLower($query))
    WITH d
    OPTIONAL MATCH (d)-[:HAS_SKILL]->(s:Skill)
    WITH d, collect(DISTINCT s.name) AS allSkills
    WHERE $skill = '' OR any(sk IN allSkills WHERE toLower(sk) = toLower($skill))
    OPTIONAL MATCH (d)-[:WORKED_ON]->(p:Project)
    OPTIONAL MATCH (d)-[:WORKED_AT]->(c:Company)
    RETURN d.id AS id, d.name AS name, d.title AS title, d.location AS location,
           collect(DISTINCT p.name) AS projects,
           collect(DISTINCT c.name) AS companies,
           allSkills AS skills
    ORDER BY d.name
    """
    result = session.run(cypher, {"query": query, "skill": skill})
    return [r.data() for r in result]


def get_developer(session: Session, dev_id: str):
    cypher = """
    MATCH (d:Developer {id: $id})
    OPTIONAL MATCH (d)-[:HAS_SKILL]->(s:Skill)
    OPTIONAL MATCH (d)-[:WORKED_ON]->(p:Project)
    OPTIONAL MATCH (d)-[:WORKED_AT]->(c:Company)
    RETURN d.id AS id, d.name AS name, d.title AS title,
           d.location AS location, d.bio AS bio,
           collect(DISTINCT s.name) AS skills,
           collect(DISTINCT p.name) AS projects,
           collect(DISTINCT c.name) AS companies
    """
    result = session.run(cypher, id=dev_id)
    record = result.single()
    return record.data() if record else None


# ── Skills ────────────────────────────────────────────────────────────────────

def get_all_skills(session: Session):
    cypher = """
    MATCH (s:Skill)<-[:HAS_SKILL]-(d:Developer)
    RETURN s.name AS skill, s.category AS category, count(d) AS developer_count
    ORDER BY developer_count DESC
    """
    result = session.run(cypher)
    return [r.data() for r in result]


# ── Multi-hop: developers reachable via shared skills (2 hops) ────────────────

def get_skill_network(session: Session, dev_id: str):
    """
    2-hop traversal: Developer → Skill → Developer
    Returns all developers who share at least one skill with the given developer,
    along with the bridging skills.
    """
    cypher = """
    MATCH (d:Developer {id: $id})-[:HAS_SKILL]->(s:Skill)<-[:HAS_SKILL]-(peer:Developer)
    WHERE peer.id <> $id
    RETURN peer.id AS id, peer.name AS name, peer.title AS title,
           collect(DISTINCT s.name) AS shared_skills,
           count(DISTINCT s) AS overlap
    ORDER BY overlap DESC
    LIMIT 20
    """
    result = session.run(cypher, id=dev_id)
    return [r.data() for r in result]


# ── Skill bridge: skills that connect the most companies ─────────────────────

def get_skill_bridges(session: Session):
    """
    Finds skills that appear across the most distinct companies —
    a query that is awkward in SQL (requires multiple joins + GROUP BY + HAVING).
    """
    cypher = """
    MATCH (c:Company)<-[:WORKED_AT]-(d:Developer)-[:HAS_SKILL]->(s:Skill)
    WITH s, collect(DISTINCT c.name) AS companies, count(DISTINCT d) AS dev_count
    WHERE size(companies) > 1
    RETURN s.name AS skill, s.category AS category,
           companies, size(companies) AS company_count, dev_count
    ORDER BY company_count DESC, dev_count DESC
    LIMIT 15
    """
    result = session.run(cypher)
    return [r.data() for r in result]


# ── Project staffing: find best-fit developers for a project ─────────────────

def find_developers_for_project(session: Session, project_id: str):
    """
    3-hop traversal: Project → required Skill → Developer (who has that skill)
    then checks if that developer already worked at a company that ran a similar project.
    """
    cypher = """
    MATCH (p:Project {id: $id})-[:REQUIRES_SKILL]->(s:Skill)<-[:HAS_SKILL]-(d:Developer)
    WITH d, collect(DISTINCT s.name) AS matched_skills, count(DISTINCT s) AS match_count
    OPTIONAL MATCH (d)-[:WORKED_AT]->(c:Company)-[:RAN]->(p2:Project)-[:REQUIRES_SKILL]->(s2:Skill)
    WHERE s2.name IN matched_skills
    RETURN d.id AS id, d.name AS name, d.title AS title,
           matched_skills, match_count,
           collect(DISTINCT c.name) AS relevant_companies
    ORDER BY match_count DESC
    LIMIT 10
    """
    result = session.run(cypher, id=project_id)
    return [r.data() for r in result]


# ── Projects ──────────────────────────────────────────────────────────────────

def get_all_projects(session: Session):
    cypher = """
    MATCH (p:Project)
    OPTIONAL MATCH (p)<-[:WORKED_ON]-(d:Developer)
    OPTIONAL MATCH (p)-[:REQUIRES_SKILL]->(s:Skill)
    OPTIONAL MATCH (p)<-[:RAN]-(c:Company)
    RETURN p.id AS id, p.name AS name, p.description AS description,
           p.status AS status,
           collect(DISTINCT d.name) AS team,
           collect(DISTINCT s.name) AS required_skills,
           collect(DISTINCT c.name) AS companies
    ORDER BY p.name
    """
    result = session.run(cypher)
    return [r.data() for r in result]


# ── Stats ─────────────────────────────────────────────────────────────────────

def get_stats(session: Session):
    counts = {}
    for label in ["Developer", "Skill", "Project", "Company"]:
        r = session.run(f"MATCH (n:{label}) RETURN count(n) AS c")
        counts[label.lower() + "s"] = r.single()["c"]
    r = session.run("MATCH ()-[r]->() RETURN count(r) AS c")
    counts["rels"] = r.single()["c"]
    return counts
    result = session.run(cypher)
    record = result.single()
    return record.data() if record else {}
