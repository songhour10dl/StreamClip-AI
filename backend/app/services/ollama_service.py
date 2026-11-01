"""
Ollama integration for local AI analysis
"""
import json
import requests
from typing import Dict, Any, List, Optional


class OllamaService:
    """Service for interacting with local Ollama models"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen:3b"):
        self.base_url = base_url
        self.model = model
    
    def check_availability(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_model(self) -> bool:
        """Check if the configured model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [m.get('name', '') for m in data.get('models', [])]
                return self.model in models
            return False
        except:
            return False
    
    def analyze_transcript_chunk(
        self,
        transcript_text: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze transcript chunk for highlights"""
        
        prompt = f"""Analyze this transcript from a livestream and identify entertaining moments.

Transcript:
{transcript_text}

Identify any moments that are:
- Funny or humorous
- Exciting or intense
- Emotionally engaging
- Unexpected reactions
- Interesting stories

For each moment found, provide:
- A brief description
- Why it's entertaining
- A score from 0-100

Respond in JSON format:
{{"moments": [{{"description": "...", "reason": "...", "score": 85}}]}}
"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '{}')
                
                try:
                    parsed = json.loads(response_text)
                    return {
                        "success": True,
                        "data": parsed
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Invalid JSON response from model"
                    }
            else:
                return {
                    "success": False,
                    "error": f"API request failed: {response.status_code}"
                }
                
        except requests.Timeout:
            return {
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_metadata(
        self,
        clip_description: str,
        transcript_sample: str
    ) -> Dict[str, Any]:
        """Generate title, description, and hashtags for a clip"""
        
        prompt = f"""Create social media metadata for this clip:

Clip description: {clip_description}
Sample dialogue: {transcript_sample}

Generate:
1. A catchy, short title (under 60 characters)
2. A brief description (1-2 sentences)
3. 5-10 relevant hashtags

Respond in JSON format:
{{"title": "...", "description": "...", "hashtags": ["tag1", "tag2"]}}
"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '{}')
                
                try:
                    parsed = json.loads(response_text)
                    return {
                        "success": True,
                        "data": parsed
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Invalid JSON response"
                    }
            else:
                return {
                    "success": False,
                    "error": f"API request failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
