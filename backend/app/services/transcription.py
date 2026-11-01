"""
Transcription service using Faster-Whisper for local speech-to-text
"""
import os
import json
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from faster_whisper import WhisperModel


class TranscriptionService:
    """Service for transcribing audio from videos using Faster-Whisper"""
    
    def __init__(self, model_size: str = "small", device: str = "cpu", compute_type: str = "int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None
        
    def load_model(self):
        """Load the Whisper model"""
        if self.model is None:
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
    
    def transcribe_video(
        self,
        video_path: str,
        output_dir: str,
        language: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """Transcribe video and save results in multiple formats"""
        
        # Load model
        self.load_model()
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Transcribe
            segments, info = self.model.transcribe(
                video_path,
                language=language,
                word_timestamps=True,
                vad_filter=True,
            )
            
            # Collect segments
            all_segments = []
            for segment in segments:
                seg_data = {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                    "words": []
                }
                
                if hasattr(segment, 'words') and segment.words:
                    for word in segment.words:
                        seg_data["words"].append({
                            "start": word.start,
                            "end": word.end,
                            "word": word.word,
                            "probability": word.probability
                        })
                
                all_segments.append(seg_data)
                
                if progress_callback:
                    progress_callback({
                        "status": "transcribing",
                        "segment": len(all_segments),
                        "text": segment.text[:50]
                    })
            
            # Save JSON
            json_path = output_path / "transcription.json"
            json_data = {
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
                "segments": all_segments
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            # Save SRT
            srt_path = output_path / "transcription.srt"
            self._save_srt(all_segments, srt_path)
            
            # Save VTT
            vtt_path = output_path / "transcription.vtt"
            self._save_vtt(all_segments, vtt_path)
            
            return {
                "success": True,
                "language": info.language,
                "duration": info.duration,
                "segment_count": len(all_segments),
                "json_path": str(json_path),
                "srt_path": str(srt_path),
                "vtt_path": str(vtt_path),
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _save_srt(self, segments, output_path):
        """Save transcription in SRT format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                start = self._format_timestamp_srt(segment['start'])
                end = self._format_timestamp_srt(segment['end'])
                f.write(f"{i}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{segment['text']}\n\n")
    
    def _save_vtt(self, segments, output_path):
        """Save transcription in VTT format"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            for segment in segments:
                start = self._format_timestamp_vtt(segment['start'])
                end = self._format_timestamp_vtt(segment['end'])
                f.write(f"{start} --> {end}\n")
                f.write(f"{segment['text']}\n\n")
    
    def _format_timestamp_srt(self, seconds):
        """Format timestamp for SRT format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _format_timestamp_vtt(self, seconds):
        """Format timestamp for VTT format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
