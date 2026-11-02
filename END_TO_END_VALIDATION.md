# StreamClip AI - End-to-End Validation Test Plan

## Test Execution Date: November 2, 2026, 9:58 AM UTC

---

## 1. COMPONENT INVENTORY CHECK

### Frontend Components
- [ ] Dashboard page
- [ ] New Project page with URL validation
- [ ] Processing Queue page
- [ ] AI Highlights page
- [ ] Clip Library page
- [ ] Video Preview page
- [ ] Export Manager page
- [ ] Settings page

### Backend Services
- [ ] Smart Downloader (audio-only mode)
- [ ] Video Validator (FFprobe)
- [ ] Transcription Service (Faster-Whisper)
- [ ] Highlight Detector (multi-signal analysis)
- [ ] Video Editor (FFmpeg)
- [ ] Ollama Service (AI enhancement)

### Database Models
- [ ] Projects table
- [ ] Highlights table
- [ ] ProcessingJobs table
- [ ] Settings table

### API Endpoints
- [ ] GET /api/projects/
- [ ] GET /api/projects/{id}
- [ ] POST /api/projects/
- [ ] POST /api/projects/validate
- [ ] DELETE /api/projects/{id}
- [ ] GET /api/projects/stats/dashboard
- [ ] GET /api/highlights/
- [ ] GET /api/queue/

---

## 2. DEPENDENCY VERIFICATION

### Python Dependencies
```bash
cd backend
pip list | grep -E "(fastapi|uvicorn|sqlalchemy|yt-dlp|faster-whisper|opencv-python)"
```

### Node.js Dependencies
```bash
npm list --depth=0 | grep -E "(react|typescript|vite|tailwindcss|lucide-react)"
```

### System Dependencies
- [ ] FFmpeg installed and accessible
- [ ] FFprobe installed and accessible
- [ ] Python 3.11+ available
- [ ] Node.js 18+ available

---

## 3. DATABASE INITIALIZATION TEST

### Test Script
```python
from app.models.database import init_db, SessionLocal, Project, Highlight, ProcessingJob, Settings
import uuid
from datetime import datetime

# Initialize database
init_db()

# Create test project
db = SessionLocal()
test_project = Project(
    id=str(uuid.uuid4()),
    url="https://www.twitch.tv/videos/test",
    platform="twitch",
    status="waiting",
    created_at=datetime.utcnow()
)
db.add(test_project)
db.commit()
print(f"✓ Test project created: {test_project.id}")

# Verify retrieval
retrieved = db.query(Project).filter(Project.id == test_project.id).first()
assert retrieved is not None, "Failed to retrieve project"
print(f"✓ Project retrieved successfully")

# Cleanup
db.delete(test_project)
db.commit()
db.close()
print(f"✓ Database test completed successfully")
```

---

## 4. API ENDPOINT VALIDATION

### Test Each Endpoint
```bash
# Start backend
cd backend
uvicorn app.main:app --port 8000 &

# Test health check
curl http://localhost:8000/
curl http://localhost:8000/health

# Test dashboard stats
curl http://localhost:8000/api/projects/stats/dashboard

# Test URL validation
curl -X POST http://localhost:8000/api/projects/validate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.twitch.tv/videos/2915383492"}'

# Test project list
curl http://localhost:8000/api/projects/
```

---

## 5. SMART DOWNLOADER TEST

### Test Audio-Only Download
```python
from app.services.smart_downloader import SmartDownloader
import os

downloader = SmartDownloader("./test_projects")

# Test 1: URL validation
result = downloader.validate_url("https://www.twitch.tv/videos/2915383492")
assert result['valid'] == True, "URL validation failed"
print(f"✓ URL validation: {result['message']}")

# Test 2: Get video info
info = downloader.get_video_info("https://www.twitch.tv/videos/2915383492")
assert info['formats'] > 0, "No formats available"
print(f"✓ Video info retrieved: {info['title']}")
print(f"✓ Available formats: {info['formats']}")
```

---

## 6. TRANSCRIPTION SERVICE TEST

### Test Audio Transcription
```python
from app.services.transcription import TranscriptionService
import os

# Create test audio file (or use downloaded audio)
transcriber = TranscriptionService(model_size="small", device="cpu", compute_type="int8")

# Test model loading
transcriber.load_model()
print("✓ Whisper model loaded successfully")

# Note: Full transcription test requires actual audio file
```

---

## 7. HIGHLIGHT DETECTION TEST

### Test Viral Moment Detection
```python
from app.services.highlight_detector import HighlightDetector
import json

detector = HighlightDetector()

# Create mock transcription data
mock_transcription = {
    "language": "en",
    "duration": 300,
    "segments": [
        {"start": 10, "end": 15, "text": "OMG this is insane!"},
        {"start": 50, "end": 55, "text": "That was so funny lol"},
        {"start": 100, "end": 105, "text": "No way that just happened"},
    ]
}

# Save mock transcription
with open("./test_transcription.json", "w") as f:
    json.dump(mock_transcription, f)

# Test highlight detection
highlights = detector.analyze_video(
    video_path="./dummy_video.mp4",  # Won't actually process without real video
    transcription_path="./test_transcription.json",
    output_dir="./test_output"
)

print(f"✓ Highlight detector initialized")
```

---

## 8. COMPLETE WORKFLOW TEST

### End-to-End Processing Simulation
```python
import asyncio
from app.workers.smart_processor import smart_worker
from app.models.database import SessionLocal, Project
import uuid

async def test_workflow():
    db = SessionLocal()
    
    # Create test project
    project = Project(
        id=str(uuid.uuid4()),
        url="https://www.twitch.tv/videos/2915383492",
        platform="twitch",
        status="waiting"
    )
    db.add(project)
    db.commit()
    
    print(f"✓ Test project created: {project.id}")
    print(f"Starting smart processing workflow...")
    
    # Start processing (will fail without valid video but will test pipeline)
    try:
        await smart_worker.process_project(project.id)
        print(f"✓ Workflow completed")
    except Exception as e:
        print(f"⚠ Workflow test encountered: {e}")
    finally:
        db.close()

# Run test
asyncio.run(test_workflow())
```

---

## 9. FRONTEND-BACKEND INTEGRATION TEST

### Test API Communication
1. Start backend: `uvicorn app.main:app --port 8000`
2. Start frontend: `npm run dev`
3. Open browser: http://localhost:1420
4. Test flow:
   - [ ] Navigate to New Project
   - [ ] Enter URL: https://www.twitch.tv/videos/2915383492
   - [ ] Click "Validate" - should show video info
   - [ ] Click "Start Analysis" - should create project
   - [ ] Navigate to Processing Queue - should show job
   - [ ] Wait for processing - should update progress
   - [ ] Check AI Highlights - should show detected moments
   - [ ] Navigate to Dashboard - should show stats

---

## 10. ERROR HANDLING TESTS

### Test Error Scenarios
- [ ] Invalid URL format
- [ ] Deleted/private video
- [ ] Network timeout
- [ ] Backend server down
- [ ] Database connection error
- [ ] FFmpeg not found
- [ ] Disk space full
- [ ] Corrupted audio file

---

## 11. PERFORMANCE VALIDATION

### Metrics to Verify
- [ ] Audio download time < 5 minutes for 1-hour video
- [ ] Transcription time < 10 minutes for 1-hour video
- [ ] Highlight detection < 2 minutes
- [ ] Memory usage < 4GB during processing
- [ ] No memory leaks (stable over multiple runs)
- [ ] Database queries < 100ms
- [ ] API response time < 200ms

---

## 12. DATA PERSISTENCE TEST

### Verify Data Storage
- [ ] Projects saved to database
- [ ] Highlights saved to database
- [ ] Processing jobs tracked correctly
- [ ] Audio files saved to correct directory
- [ ] Transcription files created (JSON, SRT, VTT)
- [ ] Analysis results saved
- [ ] Logs persisted

---

## 13. CLEANUP AND ROLLBACK TEST

### Test Data Cleanup
- [ ] Delete project removes all associated data
- [ ] Failed jobs marked correctly
- [ ] Temporary files cleaned up
- [ ] Database transactions rollback on error
- [ ] No orphaned records

---

## 14. FINAL VALIDATION CHECKLIST

### Critical Path Verification
- [x] Repository: All code in GitHub (main branch)
- [ ] Backend: Starts without errors
- [ ] Frontend: Starts without errors
- [ ] Database: Initializes correctly
- [ ] API: All endpoints respond
- [ ] URL Validation: Works with real Twitch URL
- [ ] Smart Download: Audio-only mode functional
- [ ] Transcription: Service loads and ready
- [ ] Highlight Detection: Algorithm functional
- [ ] Processing Queue: Shows job status
- [ ] Dashboard: Displays statistics
- [ ] Error Handling: Graceful failures
- [ ] Performance: Meets requirements
- [ ] Documentation: Complete and accurate

---

## EXECUTION COMMANDS

```bash
# 1. Start Backend
cd "C:\Users\songh\OneDrive\Desktop\StreamClip AI\backend"
python -m uvicorn app.main:app --reload --port 8000

# 2. Start Frontend (new terminal)
cd "C:\Users\songh\OneDrive\Desktop\StreamClip AI"
npm run dev

# 3. Run Database Test
cd backend
python -c "from app.models.database import init_db; init_db(); print('✓ Database initialized')"

# 4. Run Integration Test
cd backend
python test_integration.py

# 5. Open Browser
# Navigate to: http://localhost:1420
# Test complete workflow manually
```

---

## SUCCESS CRITERIA

✅ **Test PASSES if:**
1. Backend starts without errors
2. Frontend displays correctly
3. URL validation returns video info
4. Project creation works
5. Processing job appears in queue
6. Audio download completes
7. Transcription generates files
8. Highlights are detected
9. Dashboard shows updated stats
10. No critical errors in logs

❌ **Test FAILS if:**
1. Import errors in backend
2. API endpoints return 500 errors
3. Database initialization fails
4. Frontend cannot connect to backend
5. Processing hangs indefinitely
6. Memory usage exceeds 8GB
7. Critical exceptions in logs

---

**Status:** Ready for execution
**Tester:** Automated validation script + Manual verification required
**Expected Duration:** 15-20 minutes for complete validation
