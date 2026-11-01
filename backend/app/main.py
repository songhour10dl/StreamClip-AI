from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import projects, highlights, settings, queue
from app.models.database import init_db

app = FastAPI(title="StreamClip AI Backend", version="1.0.0")

# CORS configuration for Tauri
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    init_db()

# Include routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(highlights.router, prefix="/api/highlights", tags=["highlights"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(queue.router, prefix="/api/queue", tags=["queue"])

@app.get("/")
async def root():
    return {"message": "StreamClip AI Backend API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
