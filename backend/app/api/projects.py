from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.database import get_db, Project
from app.services.smart_downloader import SmartDownloader
from app.workers.smart_processor import start_smart_processing
from pydantic import BaseModel
from datetime import datetime
import uuid
import os

router = APIRouter()

# Initialize smart downloader
base_path = os.path.join(os.path.expanduser("~"), "StreamClipAI", "Projects")
downloader = SmartDownloader(base_path)

class ProjectCreate(BaseModel):
    url: str
    platform: str

class URLValidate(BaseModel):
    url: str

class ProjectResponse(BaseModel):
    id: str
    url: str
    platform: str
    title: str | None
    duration: float | None
    thumbnail: str | None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/", response_model=ProjectResponse)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    new_project = Project(
        id=str(uuid.uuid4()),
        url=project.url,
        platform=project.platform,
        status="waiting"
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    # Start SMART processing (audio-only, fast analysis)
    await start_smart_processing(new_project.id)
    
    return new_project

@router.post("/validate")
async def validate_url(data: URLValidate):
    """Validate URL and get video information"""
    result = downloader.validate_url(data.url)
    return result

@router.delete("/{project_id}")
async def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}

@router.get("/stats/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    total_projects = db.query(Project).count()
    videos_processed = db.query(Project).filter(Project.status == "completed").count()
    
    from app.models.database import Highlight, ProcessingJob
    highlights_generated = db.query(Highlight).count()
    processing_jobs = db.query(ProcessingJob).filter(
        ProcessingJob.status.in_(["downloading", "transcribing", "analyzing", "editing", "rendering"])
    ).count()
    
    
    # Calculate actual storage usage
    storage_used = 0
    base_path = Path(os.path.expanduser("~")) / "StreamClipAI" / "Projects"
    
    if base_path.exists():
        for item in base_path.rglob('*'):
            if item.is_file():
                try:
                    storage_used += item.stat().st_size
                except (OSError, PermissionError):
                    pass  # Skip files we can't access
    
    # Convert to GB with 2 decimal places
    storage_gb = storage_used / (1024 ** 3)
    storage_used_str = f"{storage_gb:.2f} GB"
    
    return {
        "total_projects": total_projects,
        "videos_processed": videos_processed,
        "highlights_generated": highlights_generated,
        "processing_jobs": processing_jobs,
        "storage_used": storage_used_str
    }


