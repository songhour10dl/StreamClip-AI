from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.database import get_db, ProcessingJob
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class JobResponse(BaseModel):
    id: str
    project_id: str
    status: str
    progress: float
    current_step: str | None
    error: str | None
    started_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True

@router.get("/", response_model=List[JobResponse])
async def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(ProcessingJob).order_by(ProcessingJob.started_at.desc()).all()
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
