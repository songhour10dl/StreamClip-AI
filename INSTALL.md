# Installation Guide

## Prerequisites

Before installing StreamClip AI, ensure you have the following installed:

### Required Software

1. **Python 3.11 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - Ensure "Add Python to PATH" is checked during installation
   - Verify: `python --version`

2. **Node.js 18 or higher**
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify: `node --version` and `npm --version`

3. **FFmpeg**
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Add FFmpeg to your system PATH
   - Verify: `ffmpeg -version`

4. **Rust** (for Tauri)
   - Download from [rustup.rs](https://rustup.rs/)
   - Follow the installation instructions
   - Verify: `rustc --version`

### Optional Software

5. **Ollama** (for enhanced AI analysis)
   - Download from [ollama.ai](https://ollama.ai/)
   - Install and run: `ollama pull qwen:3b`
   - This enables contextual highlight analysis

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/songhour10dl/StreamClip-AI.git
cd StreamClip-AI
```

### 2. Install Frontend Dependencies

```bash
npm install
```

### 3. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
cd ..
```

### 4. Download AI Models

The application will automatically download required models on first use:
- Faster-Whisper small model (~500MB)
- Optional: Pull Ollama models manually: `ollama pull qwen:3b`

### 5. Configure Storage

The application creates the following directory structure:
```
C:\Users\<YourUsername>\StreamClipAI\
├── Projects\
├── Models\
├── Database\
├── Logs\
└── Cache\
```

You can change the storage location in Settings after the first launch.

## Running the Application

### Development Mode

**Option 1: Run everything together**
```bash
npm run dev
```

**Option 2: Run separately**

Terminal 1 (Backend):
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Terminal 2 (Frontend):
```bash
npm run tauri dev
```

### Production Build

```bash
npm run tauri build
```

The installer will be created in `src-tauri/target/release/bundle/`

## First Launch Setup

1. **Launch the application**
   - The first launch may take a few minutes to initialize
   - Models will be downloaded automatically

2. **Configure Settings**
   - Navigate to Settings
   - Set your preferred storage location
   - Choose CPU or GPU processing mode
   - Select AI model (Qwen 3B recommended for 4GB VRAM)

3. **Verify FFmpeg**
   - The application will check for FFmpeg
   - If not found, install it and restart

4. **Optional: Configure Ollama**
   - If Ollama is installed, the application will use it automatically
   - Pull recommended model: `ollama pull qwen:3b`

## Troubleshooting

### FFmpeg Not Found
```bash
# Download FFmpeg and add to PATH
# Windows: Add FFmpeg bin directory to System Environment Variables
```

### Python Dependencies Failed
```bash
# Try upgrading pip first
python -m pip install --upgrade pip

# Install dependencies with verbose output
pip install -r backend/requirements.txt -v
```

### CUDA/GPU Issues
```bash
# If GPU processing fails, switch to CPU mode in Settings
# The application will automatically fall back to CPU
```

### Ollama Connection Issues
```bash
# Ensure Ollama is running
ollama serve

# Verify models are available
ollama list
```

### Port Already in Use
```bash
# Change backend port in backend/app/main.py
# Default port: 8000
```

## Hardware Recommendations

### Minimum
- CPU: Quad-core processor
- RAM: 8GB
- Storage: 50GB free space
- GPU: Not required (CPU fallback available)

### Recommended
- CPU: 6+ core processor
- RAM: 16GB
- Storage: 100GB+ SSD
- GPU: NVIDIA GPU with 4GB+ VRAM (RTX 3050 or better)

### Optimal
- CPU: 8+ core processor
- RAM: 32GB
- Storage: 500GB+ NVMe SSD
- GPU: NVIDIA GPU with 8GB+ VRAM (RTX 3060 or better)

## Storage Requirements

- AI Models: ~2GB
- Per VOD Processing: 5-20GB temporary storage
- Final Clips: ~100MB per minute of content
- Database: <100MB

## Performance Notes

### RTX 3050 4GB Optimization
- Use CPU mode for transcription (Faster-Whisper small)
- Use GPU for video encoding (NVENC)
- Process one video at a time
- Enable automatic cleanup of temporary files
- Limit max RAM usage to 8GB in settings

### CPU-Only Mode
- Transcription will be slower but still functional
- Video encoding uses software encoding
- Expect 2-3x longer processing times
- Close other applications during processing

## Updating

```bash
git pull origin main
npm install
cd backend
pip install -r requirements.txt --upgrade
cd ..
```

## Uninstallation

1. Uninstall the application through Windows Settings
2. Optionally delete user data: `C:\Users\<YourUsername>\StreamClipAI\`
3. Remove Ollama models if no longer needed: `ollama rm qwen:3b`

## Support

For issues during installation:
1. Check the logs in `C:\Users\<YourUsername>\StreamClipAI\Logs\`
2. Open an issue on GitHub with error details
3. Include your system specifications and error messages
