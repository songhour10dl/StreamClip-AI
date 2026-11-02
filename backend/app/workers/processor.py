import os
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.database import Project, ProcessingJob, SessionLocal
from app.services.downloader import VideoDownloader
from app.services.validator import VideoValidator


class ProcessingWorker:
    """Background worker for processing video projects"""
    
    def __init__(self):
        self.base_path = os.path.join(os.path.expanduser("~"), "StreamClipAI", "Projects")
        os.makedirs(self.base_path, exist_ok=True)
        self.downloader = VideoDownloader(self.base_path)
        self.validator = VideoValidator()
        
    async def process_project(self, project_id: str):
        """Process a complete project from download to export"""
        db = SessionLocal()
        
        try:
            # Get project
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return
            
            # Create processing job
            job = ProcessingJob(
                id=str(uuid.uuid4()),
                project_id=project_id,
                status='downloading',
                progress=0.0,
                current_step='Initializing download',
                logs='Starting video acquisition\n'
            )
            db.add(job)
            db.commit()
            
            # Update project status
            project.status = 'downloading'
            db.commit()
            
            # Download video
            def progress_callback(data):
                if data['status'] == 'downloading':
                    job.progress = data.get('percent', 0)
                    job.current_step = f"Downloading: {data.get('percent', 0):.1f}%"
                    job.logs += f"Downloaded: {data.get('downloaded_bytes', 0) / 1024 / 1024:.1f} MB\n"
                    db.commit()
            
            try:
                download_result = self.downloader.download_video(
                    project.url,
                    project_id,
                    progress_callback
                )
                
                # Validate downloaded video
                job.current_step = 'Validating video file'
                job.logs += 'Validating downloaded video\n'
                db.commit()
                
                validation_result = self.validator.validate_video_file(
                    download_result['video_path']
                )
                
                if not validation_result['valid']:
                    raise Exception(f"Invalid video file: {validation_result.get('error', 'Unknown error')}")
                
                # Update project with video information
                project.video_path = download_result['video_path']
                project.title = download_result['metadata'].get('title', 'Unknown')
                project.duration = download_result['metadata'].get('duration', 0)
                project.thumbnail = download_result['metadata'].get('thumbnail', '')
                project.status = 'completed'
                project.video_metadata = str(download_result['metadata'])
                
                # Update job
                job.status = 'completed'
                job.progress = 100.0
                job.current_step = 'Download completed'
                job.completed_at = datetime.utcnow()
                job.logs += f'Video downloaded successfully: {download_result["video_path"]}\n'
                job.logs += f'Duration: {validation_result["duration"]:.1f}s\n'
                job.logs += f'Resolution: {validation_result["width"]}x{validation_result["height"]}\n'
                
                db.commit()
                
            except Exception as e:
                project.status = 'failed'
                job.status = 'failed'
                job.error = str(e)
                job.logs += f'ERROR: {str(e)}\n'
                db.commit()
                
        except Exception as e:
            print(f"Processing error: {str(e)}")
        finally:
            db.close()


# Global worker instance
worker = ProcessingWorker()


async def start_processing(project_id: str):
    """Start processing a project in the background"""
    asyncio.create_task(worker.process_project(project_id))
