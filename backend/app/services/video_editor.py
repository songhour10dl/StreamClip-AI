"""
Video editing service using FFmpeg for clip generation and formatting
"""
import os
import subprocess
import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class VideoEditor:
    """Service for generating and editing video clips"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {
            "output_resolution": "1080x1920",  # 9:16 vertical
            "fps": 30,
            "video_codec": "libx264",
            "audio_codec": "aac",
            "video_bitrate": "2M",
            "audio_bitrate": "128k",
            "preset": "medium",
            "crf": 23,
        }
    
    def extract_clip(
        self,
        video_path: str,
        start: float,
        end: float,
        output_path: str,
        vertical: bool = True
    ) -> Dict[str, Any]:
        """Extract a clip from video and convert to vertical format"""
        
        try:
            duration = end - start
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(start),
                '-i', video_path,
                '-t', str(duration),
            ]
            
            if vertical:
                # Convert to vertical 9:16
                width, height = self.config['output_resolution'].split('x')
                cmd.extend([
                    '-vf', f'scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black',
                    '-c:v', self.config['video_codec'],
                    '-preset', self.config['preset'],
                    '-crf', str(self.config['crf']),
                ])
            else:
                cmd.extend([
                    '-c:v', self.config['video_codec'],
                    '-preset', self.config['preset'],
                    '-crf', str(self.config['crf']),
                ])
            
            # Audio settings
            cmd.extend([
                '-c:a', self.config['audio_codec'],
                '-b:a', self.config['audio_bitrate'],
                '-ar', '44100',
            ])
            
            cmd.append(output_path)
            
            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr
                }
            
            # Verify output
            if not os.path.exists(output_path):
                return {
                    "success": False,
                    "error": "Output file not created"
                }
            
            return {
                "success": True,
                "output_path": output_path,
                "duration": duration,
                "size": os.path.getsize(output_path)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "FFmpeg timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_subtitles(
        self,
        video_path: str,
        subtitle_path: str,
        output_path: str,
        style: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add animated subtitles to video"""
        
        default_style = {
            "font": "Arial",
            "font_size": 24,
            "color": "white",
            "outline_color": "black",
            "outline_width": 2,
            "position": "bottom",
        }
        
        style = style or default_style
        
        try:
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-vf', f"subtitles={subtitle_path}:force_style='FontName={style['font']},FontSize={style['font_size']},PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,OutlineThickness={style['outline_width']}'",
                '-c:a', 'copy',
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr
                }
            
            return {
                "success": True,
                "output_path": output_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_thumbnail(
        self,
        video_path: str,
        timestamp: float,
        output_path: str
    ) -> Dict[str, Any]:
        """Generate thumbnail from video at specific timestamp"""
        
        try:
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(timestamp),
                '-i', video_path,
                '-vframes', '1',
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease',
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr
                }
            
            return {
                "success": True,
                "output_path": output_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def normalize_audio(
        self,
        video_path: str,
        output_path: str
    ) -> Dict[str, Any]:
        """Normalize audio levels"""
        
        try:
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
                '-c:v', 'copy',
                '-c:a', self.config['audio_codec'],
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr
                }
            
            return {
                "success": True,
                "output_path": output_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
