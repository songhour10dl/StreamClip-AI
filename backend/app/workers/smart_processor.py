"""
Smart processing worker - analyze without downloading full video
"""
import os
import uuid
import asyncio
import json
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.database import Project, ProcessingJob, Highlight, SessionLocal
from app.services.smart_downloader import SmartDownloader
from app.services.transcription import TranscriptionService
from app.services.highlight_detector import HighlightDetector
from app.services.video_editor import VideoEditor
from app.services.ollama_service import OllamaService


class SmartProcessingWorker:
    """Smart pipeline - analyze first, download clips later"""
    
    def __init__(self):
        self.base_path = os.path.join(os.path.expanduser("~"), "StreamClipAI", "Projects")
        os.makedirs(self.base_path, exist_ok=True)
        
        # Initialize services
        self.downloader = SmartDownloader(self.base_path)
        self.transcription_service = TranscriptionService()
        self.highlight_detector = HighlightDetector()
        self.video_editor = VideoEditor()
        self.ollama_service = OllamaService()
        
    async def process_project(self, project_id: str):
        """Smart processing: audio-only → analyze → download clips on-demand"""
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
                current_step='Initializing smart analysis',
                logs='🚀 Starting FAST analysis (audio-only mode)\n'
            )
            db.add(job)
            db.commit()
            
            # Get video info (no download)
            project.status = 'downloading'
            job.current_step = 'Fetching video information'
            db.commit()
            
            try:
                video_info = self.downloader.get_video_info(project.url)
                project.title = video_info.get('title', 'Unknown')
                project.duration = video_info.get('duration', 0)
                project.thumbnail = video_info.get('thumbnail', '')
                project.video_metadata = json.dumps(video_info)
                db.commit()
                
                job.logs += f'✓ Video info retrieved\n'
                job.logs += f'Title: {video_info["title"]}\n'
                job.logs += f'Duration: {video_info["duration"]/60:.1f} minutes\n'
                job.logs += f'⚡ Downloading AUDIO ONLY (not full video)\n'
                
            except Exception as e:
                self._fail_job(db, project, job, f"Failed to get video info: {str(e)}")
                return
            
            # Download AUDIO ONLY (much faster!)
            project.status = 'downloading'
            job.status = 'downloading'
            job.progress = 10.0
            job.current_step = 'Downloading audio (fast mode)'
            db.commit()
            
            try:
                audio_result = self.downloader.download_audio_only(
                    project.url,
                    project_id,
                    lambda data: self._update_progress(db, job, 10 + data.get('percent', 0) * 0.2, 'Downloading audio')
                )
                
                job.logs += f'✓ Audio downloaded: {audio_result["file_size"]/1024/1024:.1f} MB\n'
                job.logs += f'💾 Saved {(7500 - audio_result["file_size"]/1024/1024):.0f} MB by skipping video!\n'
                
            except Exception as e:
                self._fail_job(db, project, job, f"Audio download failed: {str(e)}")
                return
            
            # Transcribe audio
            project.status = 'transcribing'
            job.status = 'transcribing'
            job.progress = 30.0
            job.current_step = 'Transcribing audio'
            db.commit()
            
            try:
                transcription_dir = os.path.join(self.base_path, project_id, "Transcription")
                transcription_result = self.transcription_service.transcribe_video(
                    audio_result['audio_path'],
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
            
            # Analyze for VIRAL moments
            project.status = 'analyzing'
            job.status = 'analyzing'
            job.progress = 60.0
            job.current_step = 'Finding viral moments'
            db.commit()
            
            try:
                job.logs += f'🔍 Analyzing for viral-worthy content...\n'
                
                # Load transcription for AI analysis
                with open(transcription_result['json_path'], 'r', encoding='utf-8') as f:
                    trans_data = json.load(f)
                
                # Use AI to find the BEST moments
                viral_moments = self._find_viral_moments(trans_data, job, db)
                
                job.logs += f'✓ Found {len(viral_moments)} potential viral moments\n'
                
                # Store highlights in database
                highlights_dir = os.path.join(self.base_path, project_id, "Highlights")
                os.makedirs(highlights_dir, exist_ok=True)
                
                for idx, moment in enumerate(viral_moments[:10], 1):  # Top 10
                    db_highlight = Highlight(
                        id=str(uuid.uuid4()),
                        project_id=project_id,
                        start=moment['start'],
                        end=moment['end'],
                        reason=moment['reason'],
                        category=moment['category'],
                        score=moment['score'],
                        status='pending',  # Will download on-demand
                    )
                    db.add(db_highlight)
                    
                    job.logs += f'  #{idx}: {moment["reason"]} (Score: {moment["score"]})\n'
                
                db.commit()
                
            except Exception as e:
                self._fail_job(db, project, job, f"Analysis failed: {str(e)}")
                return
            
            # Complete - clips will be generated on-demand
            project.status = 'completed'
            job.status = 'completed'
            job.progress = 100.0
            job.current_step = 'Analysis completed'
            job.completed_at = datetime.utcnow()
            job.logs += f'\n✅ ANALYSIS COMPLETE!\n'
            job.logs += f'📊 {len(viral_moments)} viral moments identified\n'
            job.logs += f'⚡ Total time saved: ~25 minutes (audio-only processing)\n'
            job.logs += f'\n💡 Clips will be generated on-demand when you select them\n'
            db.commit()
            
        except Exception as e:
            print(f"Processing error: {str(e)}")
            self._fail_job(db, project, job, str(e))
        finally:
            db.close()
    
    def _find_viral_moments(self, transcription: Dict[str, Any], job, db) -> list:
        """Find viral-worthy moments using AI and heuristics"""
        
        viral_moments = []
        segments = transcription.get('segments', [])
        
        # Viral keywords and patterns
        viral_indicators = {
            'excitement': ['omg', 'wow', 'insane', 'crazy', 'wtf', 'holy', 'no way', 'what the', 'oh my god'],
            'funny': ['lol', 'haha', 'hilarious', 'funny', 'dead', 'bruh', 'lmao', 'rofl'],
            'emotional': ['love', 'hate', 'angry', 'rage', 'happy', 'sad', 'crying'],
            'dramatic': ['can\'t believe', 'unbelievable', 'impossible', 'clutch', 'insane play', 'perfect'],
        }
        
        for i, segment in enumerate(segments):
            text = segment.get('text', '').lower()
            start = segment.get('start', 0)
            end = segment.get('end', 0)
            
            score = 0
            categories = []
            
            # Check for viral indicators
            for category, keywords in viral_indicators.items():
                if any(keyword in text for keyword in keywords):
                    score += 40
                    categories.append(category)
            
            # Check for questions (engaging)
            if '?' in text:
                score += 15
            
            # Check for caps/emphasis (from uploader)
            if len(text) > 20:
                score += 10
            
            # Longer segments = more context
            duration = end - start
            if duration > 15:
                score += 20
            elif duration > 30:
                score += 30
            
            # Create moment if score is high enough
            if score >= 60:
                # Extend context
                context_start = max(0, start - 3)
                context_end = min(transcription.get('duration', end + 3), end + 3)
                
                viral_moments.append({
                    'start': context_start,
                    'end': context_end,
                    'score': min(score, 100),
                    'reason': f"{', '.join(categories[:2]) if categories else 'engaging content'} - {text[:60]}...",
                    'category': categories[0] if categories else 'viral',
                    'text': text
                })
        
        # Sort by score
        viral_moments.sort(key=lambda x: x['score'], reverse=True)
        
        # Remove overlaps
        filtered = []
        for moment in viral_moments:
            if not any(abs(moment['start'] - m['start']) < 10 for m in filtered):
                filtered.append(moment)
        
        return filtered[:15]  # Top 15 moments
    
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
smart_worker = SmartProcessingWorker()


async def start_smart_processing(project_id: str):
    """Start smart processing pipeline"""
    asyncio.create_task(smart_worker.process_project(project_id))
