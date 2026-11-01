"""
Highlight detection service using audio, visual, and transcript analysis
"""
import os
import json
import subprocess
import numpy as np
from typing import Dict, Any, List, Optional
from pathlib import Path
import cv2


class HighlightDetector:
    """Service for detecting highlights using multi-signal analysis"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {
            "weights": {
                "transcript_relevance": 0.20,
                "emotional_speech": 0.20,
                "audio_intensity": 0.20,
                "visual_activity": 0.15,
                "humor_reaction": 0.15,
                "standalone_context": 0.10
            },
            "min_score": 70,
            "min_duration": 15,
            "max_duration": 180,
            "context_before": 2,
            "context_after": 2,
            "sampling_interval": 1  # Analyze every N seconds
        }
    
    def analyze_video(
        self,
        video_path: str,
        transcription_path: str,
        output_dir: str
    ) -> List[Dict[str, Any]]:
        """Analyze video and detect highlights"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Load transcription
        with open(transcription_path, 'r', encoding='utf-8') as f:
            transcription = json.load(f)
        
        # Analyze different signals
        audio_events = self._analyze_audio(video_path)
        visual_events = self._analyze_visual(video_path)
        transcript_events = self._analyze_transcript(transcription)
        
        # Combine signals and score
        candidates = self._combine_signals(
            audio_events,
            visual_events,
            transcript_events,
            transcription.get('duration', 0)
        )
        
        # Filter and rank
        highlights = self._filter_and_rank(candidates)
        
        # Merge overlapping highlights
        highlights = self._merge_overlapping(highlights)
        
        # Save results
        output_file = output_path / "highlights.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "highlights": highlights,
                "total_candidates": len(candidates),
                "selected_highlights": len(highlights),
                "config": self.config
            }, f, indent=2)
        
        return highlights
    
    def _analyze_audio(self, video_path: str) -> List[Dict[str, Any]]:
        """Analyze audio for intensity peaks and events"""
        events = []
        
        try:
            # Extract audio stats using FFmpeg
            cmd = [
                'ffmpeg', '-i', video_path,
                '-af', 'volumedetect,astats=metadata=1:reset=1',
                '-f', 'null', '-'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse output for volume information
            # This is a simplified implementation
            # In production, you'd use more sophisticated audio analysis
            
            lines = result.stderr.split('\n')
            for line in lines:
                if 'mean_volume' in line or 'max_volume' in line:
                    # Extract timestamps and volumes
                    # Simplified for now
                    pass
            
            # For now, create sample events
            # TODO: Implement proper audio analysis with librosa or similar
            
        except Exception as e:
            print(f"Audio analysis error: {e}")
        
        return events
    
    def _analyze_visual(self, video_path: str) -> List[Dict[str, Any]]:
        """Analyze video for scene changes and motion"""
        events = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            if duration == 0:
                cap.release()
                return events
            
            # Sample frames at intervals
            sample_interval = int(fps * self.config['sampling_interval'])
            prev_frame = None
            frame_idx = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % sample_interval == 0:
                    # Resize for faster processing
                    small_frame = cv2.resize(frame, (320, 180))
                    gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
                    
                    if prev_frame is not None:
                        # Calculate frame difference
                        diff = cv2.absdiff(prev_frame, gray)
                        activity = np.mean(diff)
                        
                        # Detect high activity
                        if activity > 30:  # Threshold
                            timestamp = frame_idx / fps
                            events.append({
                                "timestamp": timestamp,
                                "type": "visual_activity",
                                "intensity": float(activity),
                                "score": min(activity / 50 * 100, 100)
                            })
                    
                    prev_frame = gray.copy()
                
                frame_idx += 1
            
            cap.release()
            
        except Exception as e:
            print(f"Visual analysis error: {e}")
        
        return events
    
    def _analyze_transcript(self, transcription: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze transcript for interesting moments"""
        events = []
        
        # Keywords that indicate interesting moments
        excitement_words = [
            'wow', 'omg', 'crazy', 'insane', 'amazing', 'incredible',
            'holy', 'what', 'no way', 'unbelievable', 'perfect'
        ]
        
        humor_words = [
            'lol', 'haha', 'funny', 'hilarious', 'joke', 'laugh'
        ]
        
        emotional_words = [
            'love', 'hate', 'angry', 'happy', 'sad', 'excited',
            'scared', 'nervous', 'worried'
        ]
        
        segments = transcription.get('segments', [])
        
        for segment in segments:
            text = segment.get('text', '').lower()
            start = segment.get('start', 0)
            end = segment.get('end', 0)
            
            score = 0
            categories = []
            
            # Check for excitement
            if any(word in text for word in excitement_words):
                score += 30
                categories.append('exciting')
            
            # Check for humor
            if any(word in text for word in humor_words):
                score += 25
                categories.append('funny')
            
            # Check for emotional content
            if any(word in text for word in emotional_words):
                score += 20
                categories.append('emotional')
            
            # Check for questions (often interesting)
            if '?' in text:
                score += 10
            
            # Check for longer segments (more context)
            duration = end - start
            if duration > 10:
                score += 10
            
            if score > 0:
                events.append({
                    "timestamp": start,
                    "duration": duration,
                    "type": "transcript",
                    "text": segment.get('text', ''),
                    "score": score,
                    "categories": categories
                })
        
        return events
    
    def _combine_signals(
        self,
        audio_events: List[Dict[str, Any]],
        visual_events: List[Dict[str, Any]],
        transcript_events: List[Dict[str, Any]],
        total_duration: float
    ) -> List[Dict[str, Any]]:
        """Combine all signals into scored candidates"""
        
        candidates = []
        
        # Group events by time windows
        window_size = 30  # seconds
        num_windows = int(total_duration / window_size) + 1
        
        for i in range(num_windows):
            window_start = i * window_size
            window_end = window_start + window_size
            
            # Collect events in this window
            window_audio = [e for e in audio_events if window_start <= e.get('timestamp', 0) < window_end]
            window_visual = [e for e in visual_events if window_start <= e.get('timestamp', 0) < window_end]
            window_transcript = [e for e in transcript_events if window_start <= e.get('timestamp', 0) < window_end]
            
            if not (window_audio or window_visual or window_transcript):
                continue
            
            # Calculate combined score
            score = 0
            reason_parts = []
            categories = set()
            
            # Audio contribution
            if window_audio:
                audio_score = np.mean([e.get('score', 0) for e in window_audio])
                score += audio_score * self.config['weights']['audio_intensity']
                reason_parts.append("audio intensity")
            
            # Visual contribution
            if window_visual:
                visual_score = np.mean([e.get('score', 0) for e in window_visual])
                score += visual_score * self.config['weights']['visual_activity']
                reason_parts.append("visual activity")
            
            # Transcript contribution
            if window_transcript:
                transcript_score = np.mean([e.get('score', 0) for e in window_transcript])
                score += transcript_score * (
                    self.config['weights']['transcript_relevance'] +
                    self.config['weights']['emotional_speech'] +
                    self.config['weights']['humor_reaction']
                )
                reason_parts.append("interesting dialogue")
                
                for event in window_transcript:
                    categories.update(event.get('categories', []))
            
            if score > self.config['min_score']:
                candidates.append({
                    "start": window_start - self.config['context_before'],
                    "end": window_end + self.config['context_after'],
                    "score": round(score, 2),
                    "reason": ", ".join(reason_parts),
                    "category": list(categories)[0] if categories else "highlight",
                    "events": {
                        "audio": len(window_audio),
                        "visual": len(window_visual),
                        "transcript": len(window_transcript)
                    }
                })
        
        return candidates
    
    def _filter_and_rank(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and rank highlight candidates"""
        
        # Filter by minimum score
        filtered = [c for c in candidates if c['score'] >= self.config['min_score']]
        
        # Filter by duration
        filtered = [
            c for c in filtered
            if self.config['min_duration'] <= (c['end'] - c['start']) <= self.config['max_duration']
        ]
        
        # Sort by score
        filtered.sort(key=lambda x: x['score'], reverse=True)
        
        return filtered
    
    def _merge_overlapping(self, highlights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge overlapping highlight segments"""
        
        if not highlights:
            return []
        
        merged = []
        current = highlights[0].copy()
        
        for next_hl in highlights[1:]:
            if next_hl['start'] <= current['end']:
                # Overlapping - merge
                current['end'] = max(current['end'], next_hl['end'])
                current['score'] = max(current['score'], next_hl['score'])
            else:
                # Not overlapping - save current and start new
                merged.append(current)
                current = next_hl.copy()
        
        merged.append(current)
        
        return merged
