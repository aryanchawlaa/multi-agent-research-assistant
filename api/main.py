import sys
import os

# Make sure imports work regardless of working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from crew.research_crew import run_research_crew
from tools.pdf_exporter import export_to_pdf

app = FastAPI(
    title="Multi-Agent Research Assistant API",
    description="CrewAI-powered academic research pipeline with 3 specialized agents",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store (use Redis in production)
jobs: dict = {}


# ── Request / Response Models ──────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=300,
                       example="Retrieval Augmented Generation for code generation")
    export_pdf: bool = Field(default=False, description="Also generate a PDF of the review")


class JobStatus(BaseModel):
    job_id: str
    status: str  # pending | running | done | error
    topic: str
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None
    pdf_path: Optional[str] = None


# ── Background worker ──────────────────────────────────────────────────────────

def run_job(job_id: str, topic: str, export_pdf: bool):
    jobs[job_id]["status"] = "running"
    try:
        result = run_research_crew(topic)
        pdf_path = None
        if export_pdf:
            pdf_path = export_to_pdf(topic, result["literature_review"])

        jobs[job_id].update({
            "status": "done",
            "result": result,
            "pdf_path": pdf_path,
            "completed_at": datetime.now().isoformat(),
        })
        print(f"\n[JOB {job_id[:8]}] Completed successfully.")

    except Exception as e:
        jobs[job_id].update({
            "status": "error",
            "error": str(e),
            "completed_at": datetime.now().isoformat(),
        })
        print(f"\n[JOB {job_id[:8]}] Failed: {e}")


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.post("/research", response_model=JobStatus, status_code=202)
async def start_research(req: ResearchRequest, background_tasks: BackgroundTasks):
    """Start an async research job. Returns a job_id to poll for results."""
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "topic": req.topic,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "result": None,
        "error": None,
        "pdf_path": None,
    }
    background_tasks.add_task(run_job, job_id, req.topic, req.export_pdf)
    return jobs[job_id]


@app.get("/research/{job_id}", response_model=JobStatus)
async def get_job(job_id: str):
    """Poll this endpoint to check job status and retrieve results."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@app.get("/jobs")
async def list_jobs():
    """List all jobs (latest 20)."""
    all_jobs = list(jobs.values())
    return {"total": len(all_jobs), "jobs": all_jobs[-20:]}


@app.delete("/jobs")
async def clear_jobs():
    """Clear all completed jobs."""
    to_remove = [k for k, v in jobs.items() if v["status"] in ("done", "error")]
    for k in to_remove:
        del jobs[k]
    return {"cleared": len(to_remove)}


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "active_jobs": sum(1 for j in jobs.values() if j["status"] == "running"),
        "total_jobs": len(jobs),
    }
