from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, Settings as SettingsModel
from pydantic import BaseModel
import json

router = APIRouter()

class SettingsUpdate(BaseModel):
    key: str
    value: str

class SettingsResponse(BaseModel):
    key: str
    value: str

    class Config:
        from_attributes = True

@router.get("/", response_model=dict)
async def get_all_settings(db: Session = Depends(get_db)):
    settings = db.query(SettingsModel).all()
    return {s.key: s.value for s in settings}

@router.get("/{key}", response_model=SettingsResponse)
async def get_setting(key: str, db: Session = Depends(get_db)):
    setting = db.query(SettingsModel).filter(SettingsModel.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting

@router.put("/")
async def update_settings(settings: dict, db: Session = Depends(get_db)):
    for key, value in settings.items():
        setting = db.query(SettingsModel).filter(SettingsModel.key == key).first()
        if setting:
            setting.value = json.dumps(value) if not isinstance(value, str) else value
        else:
            new_setting = SettingsModel(key=key, value=json.dumps(value) if not isinstance(value, str) else value)
            db.add(new_setting)
    
    db.commit()
    return {"message": "Settings updated successfully"}
