import os
import json
import uuid
from typing import Optional, Dict, Any, Callable
import yt_dlp
from pathlib import Path


class VideoDownloader:
    """Service for downloading videos from Twitch and Kick using yt-dlp"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def detect_platform(self, url: str) -> Optional[str]:
        """Detect platform from URL"""
        if 'twitch.tv' in url.lower():
            return 'twitch'
        elif 'kick.com' in url.lower():
            return 'kick'
        return None
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Extract video metadata without downloading"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'id': info.get('id', str(uuid.uuid4())),
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', ''),
                    'view_count': info.get('view_count', 0),
                    'formats': len(info.get('formats', [])),
                    'webpage_url': info.get('webpage_url', url),
                }
        except Exception as e:
            raise Exception(f"Failed to extract video info: {str(e)}")
    
    def download_video(
        self,
        url: str,
        project_id: str,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """Download video and return file information"""
        
        project_path = self.base_path / project_id / "Original"
        project_path.mkdir(parents=True, exist_ok=True)
        
        output_template = str(project_path / "video.%(ext)s")
        
        def progress_hook(d):
            if progress_callback:
                if d['status'] == 'downloading':
                    progress_data = {
                        'status': 'downloading',
                        'downloaded_bytes': d.get('downloaded_bytes', 0),
                        'total_bytes': d.get('total_bytes') or d.get('total_bytes_estimate', 0),
                        'speed': d.get('speed', 0),
                        'eta': d.get('eta', 0),
                        'percent': d.get('downloaded_bytes', 0) / max(d.get('total_bytes', 1), 1) * 100
                    }
                    progress_callback(progress_data)
                elif d['status'] == 'finished':
                    progress_callback({
                        'status': 'finished',
                        'filename': d.get('filename', '')
                    })
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_template,
            'progress_hooks': [progress_hook],
            'quiet': False,
            'no_warnings': False,
            'merge_output_format': 'mp4',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Find the downloaded file
                video_file = None
                for file in project_path.glob("video.*"):
                    if file.suffix in ['.mp4', '.mkv', '.webm', '.flv']:
                        video_file = file
                        break
                
                if not video_file or not video_file.exists():
                    raise Exception("Downloaded file not found")
                
                # Save metadata
                metadata = {
                    'id': info.get('id'),
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'thumbnail': info.get('thumbnail'),
                    'uploader': info.get('uploader'),
                    'upload_date': info.get('upload_date'),
                    'description': info.get('description'),
                    'view_count': info.get('view_count'),
                    'webpage_url': info.get('webpage_url'),
                    'format': info.get('format'),
                    'width': info.get('width'),
                    'height': info.get('height'),
                    'fps': info.get('fps'),
                }
                
                metadata_path = self.base_path / project_id / "Metadata" / "video_info.json"
                metadata_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                return {
                    'video_path': str(video_file),
                    'metadata_path': str(metadata_path),
                    'metadata': metadata,
                    'file_size': video_file.stat().st_size
                }
                
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")
    
    def validate_url(self, url: str) -> Dict[str, Any]:
        """Validate if URL is supported and accessible"""
        try:
            info = self.get_video_info(url)
            platform = self.detect_platform(url)
            
            return {
                'valid': True,
                'platform': platform,
                'info': info,
                'message': 'URL is valid and accessible'
            }
        except Exception as e:
            return {
                'valid': False,
                'platform': None,
                'info': None,
                'message': str(e)
            }
