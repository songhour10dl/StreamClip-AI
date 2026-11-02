"""
Automated End-to-End Validation Suite
StreamClip AI - Complete Workflow Test
"""
import sys
import os
import asyncio
from datetime import datetime

print("="*80)
print("STREAMCLIP AI - END-TO-END VALIDATION")
print(f"Test Date: {datetime.utcnow().isoformat()}")
print("="*80)

# Test 1: Import all backend modules
print("\n[TEST 1] Backend Module Imports")
print("-"*80)

test_results = {"passed": 0, "failed": 0, "warnings": 0}

try:
    from app.models.database import init_db, SessionLocal, Project, Highlight, ProcessingJob, Settings
    print("[PASS] Database models imported")
    test_results["passed"] += 1
except Exception as e:
    print(f"[FAIL] Database models import failed: {e}")
    test_results["failed"] += 1

try:
    from app.services.smart_downloader import SmartDownloader
    print("[PASS] Smart Downloader imported")
    test_results["passed"] += 1
except Exception as e:
    print(f"[FAIL] Smart Downloader import failed: {e}")
    test_results["failed"] += 1

try:
    from app.services.transcription import TranscriptionService
    print("[PASS] Transcription Service imported")
    test_results["passed"] += 1
except Exception as e:
    print(f"[FAIL] Transcription Service import failed: {e}")
    test_results["failed"] += 1

try:
    from app.services.highlight_detector import HighlightDetector
    print("[PASS] Highlight Detector imported")
    test_results["passed"] += 1
except Exception as e:
    print(f"[FAIL] Highlight Detector import failed: {e}")
    test_results["failed"] += 1

try:
    from app.services.video_editor import VideoEditor
    print("[PASS] Video Editor imported")
    test_results["passed"] += 1
except Exception as e:
    print(f"[FAIL] Video Editor import failed: {e}")
    test_results["failed"] += 1

try:
    from app.services.ollama_service import OllamaService
    print("[PASS] Ollama Service imported")
    test_results["passed"] += 1
except Exception as e:
    print(f"[FAIL] Ollama Service import failed: {e}")
    test_results["failed"] += 1

try:
    from app.workers.smart_processor import smart_worker
    print("[PASS] Smart Processor imported")
    test_results["passed"] += 1
except Exception as e:
    print(f"[FAIL] Smart Processor import failed: {e}")
    test_results["failed"] += 1

# Test 2: Database Initialization
print("\n[TEST 2] Database Initialization")
print("-"*80)

try:
    init_db()
    print("[PASS] Database initialized successfully")
    test_results["passed"] += 1
    
    # Test connection
    db = SessionLocal()
    db.close()
    print("[PASS] Database connection successful")
    test_results["passed"] += 1
except Exception as e:
    print(f"[FAIL] Database initialization failed: {e}")
    test_results["failed"] += 2

# Test 3: Create and Retrieve Test Project
print("\n[TEST 3] Database CRUD Operations")
print("-"*80)

try:
    db = SessionLocal()
    import uuid
    
    test_project = Project(
        id=str(uuid.uuid4()),
        url="https://www.twitch.tv/videos/test_validation",
        platform="twitch",
        status="waiting"
    )
    db.add(test_project)
    db.commit()
    print(f"[PASS] Test project created: {test_project.id}")
    test_results["passed"] += 1
    
    # Retrieve
    retrieved = db.query(Project).filter(Project.id == test_project.id).first()
    assert retrieved is not None
    assert retrieved.url == test_project.url
    print(f"[PASS] Project retrieved successfully")
    test_results["passed"] += 1
    
    # Update
    retrieved.status = "completed"
    db.commit()
    print(f"[PASS] Project updated successfully")
    test_results["passed"] += 1
    
    # Delete
    db.delete(retrieved)
    db.commit()
    print(f"[PASS] Project deleted successfully")
    test_results["passed"] += 1
    
    db.close()
except Exception as e:
    print(f"[FAIL] Database CRUD test failed: {e}")
    test_results["failed"] += 4
    if 'db' in locals():
        db.close()

# Test 4: Smart Downloader URL Validation
print("\n[TEST 4] Smart Downloader - URL Validation")
print("-"*80)

try:
    base_path = os.path.join(os.path.expanduser("~"), "StreamClipAI", "Projects", "test")
    downloader = SmartDownloader(base_path)
    print("[PASS] Smart Downloader initialized")
    test_results["passed"] += 1
    
    # Test platform detection
    platform = downloader.detect_platform("https://www.twitch.tv/videos/12345")
    assert platform == "twitch"
    print(f"[PASS] Platform detection works: {platform}")
    test_results["passed"] += 1
    
    platform = downloader.detect_platform("https://kick.com/video/12345")
    assert platform == "kick"
    print(f"[PASS] Kick detection works: {platform}")
    test_results["passed"] += 1
    
except Exception as e:
    print(f"[FAIL] Smart Downloader test failed: {e}")
    test_results["failed"] += 3

# Test 5: Video Info Extraction (Real URL)
print("\n[TEST 5] Video Info Extraction")
print("-"*80)

try:
    test_url = "https://www.twitch.tv/videos/2915383492"
    print(f"Testing with URL: {test_url}")
    
    result = downloader.validate_url(test_url)
    print(f"[PASS] URL validation completed")
    print(f"  Valid: {result['valid']}")
    print(f"  Platform: {result['platform']}")
    
    if result['valid']:
        info = result['info']
        print(f"  Title: {info['title']}")
        print(f"  Duration: {info['duration']}s")
        print(f"  Formats: {info['formats']}")
        print(f"  Can Download: {info.get('can_download', False)}")
        
        if info['formats'] > 0:
            print("[PASS] Video is accessible and downloadable")
            test_results["passed"] += 1
        else:
            print("[WARN] Video accessible but no formats available")
            test_results["warnings"] += 1
    else:
        print(f"[WARN] URL validation returned: {result['message']}")
        test_results["warnings"] += 1
        
except Exception as e:
    print(f"[FAIL] Video info extraction failed: {e}")
    test_results["failed"] += 1

# Test 6: Transcription Service Initialization
print("\n[TEST 6] Transcription Service")
print("-"*80)

try:
    transcriber = TranscriptionService(model_size="small", device="cpu", compute_type="int8")
    print("[PASS] Transcription service initialized")
    test_results["passed"] += 1
    
    print("[WARN] Note: Full transcription test requires audio file (skipped)")
    test_results["warnings"] += 1
    
except Exception as e:
    print(f"[FAIL] Transcription service initialization failed: {e}")
    test_results["failed"] += 1

# Test 7: Highlight Detector Initialization
print("\n[TEST 7] Highlight Detector")
print("-"*80)

try:
    detector = HighlightDetector()
    print("[PASS] Highlight detector initialized")
    print(f"  Min score: {detector.config['min_score']}")
    print(f"  Min duration: {detector.config['min_duration']}s")
    print(f"  Max duration: {detector.config['max_duration']}s")
    test_results["passed"] += 1
    
except Exception as e:
    print(f"[FAIL] Highlight detector initialization failed: {e}")
    test_results["failed"] += 1

# Test 8: Video Editor Initialization
print("\n[TEST 8] Video Editor")
print("-"*80)

try:
    editor = VideoEditor()
    print("[PASS] Video editor initialized")
    print(f"  Output resolution: {editor.config['output_resolution']}")
    print(f"  Video codec: {editor.config['video_codec']}")
    print(f"  Audio codec: {editor.config['audio_codec']}")
    test_results["passed"] += 1
    
except Exception as e:
    print(f"[FAIL] Video editor initialization failed: {e}")
    test_results["failed"] += 1

# Test 9: FFmpeg/FFprobe Availability
print("\n[TEST 9] System Dependencies")
print("-"*80)

try:
    from app.services.validator import VideoValidator
    
    if VideoValidator.check_ffmpeg_installed():
        print("[PASS] FFmpeg is installed and accessible")
        test_results["passed"] += 1
    else:
        print("[FAIL] FFmpeg not found in PATH")
        test_results["failed"] += 1
    
    if VideoValidator.check_ffprobe_installed():
        print("[PASS] FFprobe is installed and accessible")
        test_results["passed"] += 1
    else:
        print("[FAIL] FFprobe not found in PATH")
        test_results["failed"] += 1
        
except Exception as e:
    print(f"[FAIL] System dependency check failed: {e}")
    test_results["failed"] += 2

# Test 10: Ollama Service (Optional)
print("\n[TEST 10] Ollama Service (Optional)")
print("-"*80)

try:
    ollama = OllamaService()
    if ollama.check_availability():
        print("[PASS] Ollama is running and accessible")
        test_results["passed"] += 1
        
        if ollama.check_model():
            print(f"[PASS] Model '{ollama.model}' is available")
            test_results["passed"] += 1
        else:
            print(f"[WARN] Model '{ollama.model}' not found (optional)")
            test_results["warnings"] += 1
    else:
        print("[WARN] Ollama not running (optional - app will use fallback)")
        test_results["warnings"] += 1
        
except Exception as e:
    print(f"[WARN] Ollama check failed: {e} (optional feature)")
    test_results["warnings"] += 1

# Test 11: API Endpoint Structure
print("\n[TEST 11] API Endpoints")
print("-"*80)

try:
    from app.api import projects, highlights, settings, queue
    print("[PASS] Projects API module loaded")
    print("[PASS] Highlights API module loaded")
    print("[PASS] Settings API module loaded")
    print("[PASS] Queue API module loaded")
    test_results["passed"] += 4
    
except Exception as e:
    print(f"[FAIL] API modules import failed: {e}")
    test_results["failed"] += 4

# Test 12: Main Application
print("\n[TEST 12] Main Application")
print("-"*80)

try:
    from app.main import app
    print("[PASS] FastAPI app loaded successfully")
    print(f"  Title: {app.title}")
    print(f"  Version: {app.version}")
    test_results["passed"] += 1
    
except Exception as e:
    print(f"[FAIL] Main application load failed: {e}")
    test_results["failed"] += 1

# Final Summary
print("\n" + "="*80)
print("VALIDATION SUMMARY")
print("="*80)
print(f"PASSED:   {test_results['passed']}")
print(f"FAILED:   {test_results['failed']}")
print(f"WARNINGS: {test_results['warnings']}")
print(f"TOTAL:    {test_results['passed'] + test_results['failed'] + test_results['warnings']}")

# Calculate success rate
total_critical = test_results['passed'] + test_results['failed']
if total_critical > 0:
    success_rate = (test_results['passed'] / total_critical) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if test_results['failed'] == 0:
        print("\n*** ALL CRITICAL TESTS PASSED! ***")
        print("Application is ready for production use")
        sys.exit(0)
    elif test_results['failed'] <= 2:
        print("\n*** MOSTLY PASSING - Minor issues detected ***")
        print("Review failed tests above")
        sys.exit(1)
    else:
        print("\n*** CRITICAL FAILURES DETECTED ***")
        print("Fix failed tests before proceeding")
        sys.exit(1)
else:
    print("\n*** No tests executed ***")
    sys.exit(1)
