from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from neo4j.exceptions import ServiceUnavailable, AuthError
import os

from backend.db import get_driver, close_driver
from backend import queries

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify connection on startup
    try:
        get_driver().verify_connectivity()
    except (ServiceUnavailable, AuthError) as e:
        print(f"[WARN] Database unreachable at startup: {e}")
    yield
    close_driver()

app = FastAPI(title="Tech Talent Graph", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

def db_session():
    try:
        return get_driver().session()
    except (ServiceUnavailable, AuthError) as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {e}")


# ── API routes ────────────────────────────────────────────────────────────────

@app.get("/api/stats")
def stats():
    with db_session() as s:
        return queries.get_stats(s)

@app.get("/api/developers")
def list_developers(q: str = Query(""), skill: str = Query("")):
    with db_session() as s:
        return queries.search_developers(s, query=q, skill=skill)

@app.get("/api/developers/{dev_id}")
def developer_detail(dev_id: str):
    with db_session() as s:
        dev = queries.get_developer(s, dev_id)
    if not dev:
        raise HTTPException(status_code=404, detail="Developer not found")
    return dev

@app.get("/api/developers/{dev_id}/network")
def developer_network(dev_id: str):
    with db_session() as s:
        return queries.get_skill_network(s, dev_id)

@app.get("/api/skills")
def list_skills():
    with db_session() as s:
        return queries.get_all_skills(s)

@app.get("/api/skills/bridges")
def skill_bridges():
    with db_session() as s:
        return queries.get_skill_bridges(s)

@app.get("/api/projects")
def list_projects():
    with db_session() as s:
        return queries.get_all_projects(s)

@app.get("/api/projects/{project_id}/team")
def project_team(project_id: str):
    with db_session() as s:
        return queries.find_developers_for_project(s, project_id)


# ── Serve frontend ────────────────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    return FileResponse("frontend/index.html")
