from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.database import get_db, Highlight
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class HighlightResponse(BaseModel):
    id: str
    project_id: str
    start: float
    end: float
    reason: str | None
    category: str | None
    score: float | None
    status: str
    export_path: str | None
    thumbnail: str | None
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[HighlightResponse])
async def get_highlights(project_id: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Highlight)
    if project_id:
        query = query.filter(Highlight.project_id == project_id)
    highlights = query.order_by(Highlight.score.desc()).all()
    return highlights

@router.get("/{highlight_id}", response_model=HighlightResponse)
async def get_highlight(highlight_id: str, db: Session = Depends(get_db)):
    highlight = db.query(Highlight).filter(Highlight.id == highlight_id).first()
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")
    return highlight
