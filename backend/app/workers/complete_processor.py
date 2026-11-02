"""
Complete processing worker integrating all phases
"""
import os
import uuid
import asyncio
import json
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.database import Project, ProcessingJob, Highlight, SessionLocal
from app.services.downloader import VideoDownloader
from app.services.validator import VideoValidator
from app.services.transcription import TranscriptionService
from app.services.highlight_detector import HighlightDetector
from app.services.video_editor import VideoEditor
from app.services.ollama_service import OllamaService


class CompleteProcessingWorker:
    """Complete pipeline worker for processing video projects"""
    
    def __init__(self):
        self.base_path = os.path.join(os.path.expanduser("~"), "StreamClipAI", "Projects")
        os.makedirs(self.base_path, exist_ok=True)
        
        # Initialize services
        self.downloader = VideoDownloader(self.base_path)
        self.validator = VideoValidator()
        self.transcription_service = TranscriptionService()
        self.highlight_detector = HighlightDetector()
        self.video_editor = VideoEditor()
        self.ollama_service = OllamaService()
        
    async def process_project(self, project_id: str):
        """Process complete project pipeline"""
        db = SessionLocal()
        
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                return
            
            # Create processing job
            job = ProcessingJob(
                id=str(uuid.uuid4()),
                project_id=project_id,
                status='downloading',
                progress=0.0,
                current_step='Initializing',
                logs='Starting complete pipeline\n'
            )
            db.add(job)
            db.commit()
            
            # Phase 1: Download video
            project.status = 'downloading'
            job.status = 'downloading'
            job.current_step = 'Downloading video'
            db.commit()
            
            try:
                download_result = self.downloader.download_video(
                    project.url,
                    project_id,
                    lambda data: self._update_progress(db, job, data.get('percent', 0), 'Downloading')
                )
                
                validation_result = self.validator.validate_video_file(download_result['video_path'])
                
                if not validation_result['valid']:
                    raise Exception(f"Invalid video: {validation_result.get('error')}")
                
                project.video_path = download_result['video_path']
                project.title = download_result['metadata'].get('title', 'Unknown')
                project.duration = download_result['metadata'].get('duration', 0)
                project.thumbnail = download_result['metadata'].get('thumbnail', '')
                project.video_metadata = json.dumps(download_result['metadata'])
                db.commit()
                
                job.logs += f'✓ Video downloaded: {download_result["video_path"]}\n'
                job.logs += f'Duration: {validation_result["duration"]:.1f}s\n'
                
            except Exception as e:
                self._fail_job(db, project, job, f"Download failed: {str(e)}")
                return
            
            # Phase 2: Transcribe video
            project.status = 'transcribing'
            job.status = 'transcribing'
            job.progress = 20.0
            job.current_step = 'Transcribing audio'
            db.commit()
            
            try:
                transcription_dir = os.path.join(self.base_path, project_id, "Transcription")
                transcription_result = self.transcription_service.transcribe_video(
                    download_result['video_path'],
                    transcription_dir,
                    progress_callback=lambda data: self._update_transcription_progress(db, job, data)
                )
                
                if not transcription_result['success']:
                    raise Exception(transcription_result.get('error', 'Transcription failed'))
                
                job.logs += f'✓ Transcription completed\n'
                job.logs += f'Language: {transcription_result["language"]}\n'
                job.logs += f'Segments: {transcription_result["segment_count"]}\n'
                
            except Exception as e:
                self._fail_job(db, project, job, f"Transcription failed: {str(e)}")
                return
            
            # Phase 3: Analyze and detect highlights
            project.status = 'analyzing'
            job.status = 'analyzing'
            job.progress = 40.0
            job.current_step = 'Analyzing content'
            db.commit()
            
            try:
                analysis_dir = os.path.join(self.base_path, project_id, "Analysis")
                highlights = self.highlight_detector.analyze_video(
                    download_result['video_path'],
                    transcription_result['json_path'],
                    analysis_dir
                )
                
                job.logs += f'✓ Analysis completed\n'
                job.logs += f'Highlights detected: {len(highlights)}\n'
                
                # Enhance with Ollama if available
                if self.ollama_service.check_availability():
                    job.logs += 'Ollama available - enhancing analysis\n'
                    # Load transcription for context
                    with open(transcription_result['json_path'], 'r', encoding='utf-8') as f:
                        trans_data = json.load(f)
                    
                    # TODO: Enhance highlights with AI analysis
                
            except Exception as e:
                self._fail_job(db, project, job, f"Analysis failed: {str(e)}")
                return
            
            # Phase 4: Generate clips
            project.status = 'editing'
            job.status = 'editing'
            job.progress = 60.0
            job.current_step = 'Generating clips'
            db.commit()
            
            try:
                highlights_dir = os.path.join(self.base_path, project_id, "Highlights")
                exports_dir = os.path.join(self.base_path, project_id, "Exports")
                thumbnails_dir = os.path.join(self.base_path, project_id, "Thumbnails")
                
                os.makedirs(highlights_dir, exist_ok=True)
                os.makedirs(exports_dir, exist_ok=True)
                os.makedirs(thumbnails_dir, exist_ok=True)
                
                for idx, highlight in enumerate(highlights[:10], 1):  # Limit to top 10
                    clip_name = f"clip_{idx:03d}.mp4"
                    clip_path = os.path.join(exports_dir, clip_name)
                    thumb_path = os.path.join(thumbnails_dir, f"clip_{idx:03d}.jpg")
                    
                    # Extract clip
                    clip_result = self.video_editor.extract_clip(
                        download_result['video_path'],
                        highlight['start'],
                        highlight['end'],
                        clip_path,
                        vertical=True
                    )
                    
                    if clip_result['success']:
                        # Generate thumbnail
                        mid_time = (highlight['start'] + highlight['end']) / 2
                        self.video_editor.generate_thumbnail(
                            download_result['video_path'],
                            mid_time,
                            thumb_path
                        )
                        
                        # Save highlight to database
                        db_highlight = Highlight(
                            id=str(uuid.uuid4()),
                            project_id=project_id,
                            start=highlight['start'],
                            end=highlight['end'],
                            reason=highlight['reason'],
                            category=highlight['category'],
                            score=highlight['score'],
                            status='completed',
                            export_path=clip_path,
                            thumbnail=thumb_path
                        )
                        db.add(db_highlight)
                        
                        job.logs += f'✓ Clip {idx} generated\n'
                
                db.commit()
                
            except Exception as e:
                self._fail_job(db, project, job, f"Clip generation failed: {str(e)}")
                return
            
            # Complete
            project.status = 'completed'
            job.status = 'completed'
            job.progress = 100.0
            job.current_step = 'Completed'
            job.completed_at = datetime.utcnow()
            job.logs += f'\n✓ PIPELINE COMPLETED\n'
            job.logs += f'Total highlights: {len(highlights)}\n'
            db.commit()
            
        except Exception as e:
            print(f"Processing error: {str(e)}")
            self._fail_job(db, project, job, str(e))
        finally:
            db.close()
    
    def _update_progress(self, db, job, percent, step):
        """Update job progress"""
        job.progress = percent
        job.current_step = f"{step}: {percent:.1f}%"
        db.commit()
    
    def _update_transcription_progress(self, db, job, data):
        """Update transcription progress"""
        if data.get('status') == 'transcribing':
            segment = data.get('segment', 0)
            job.current_step = f"Transcribing: segment {segment}"
            db.commit()
    
    def _fail_job(self, db, project, job, error_msg):
        """Mark job as failed"""
        project.status = 'failed'
        job.status = 'failed'
        job.error = error_msg
        job.logs += f'\n✗ ERROR: {error_msg}\n'
        job.completed_at = datetime.utcnow()
        db.commit()


# Global worker instance
complete_worker = CompleteProcessingWorker()


async def start_complete_processing(project_id: str):
    """Start complete processing pipeline"""
    asyncio.create_task(complete_worker.process_project(project_id))
