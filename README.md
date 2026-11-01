# StreamClip AI

A professional, fully local AI streamer clipping application for Windows 11.

## Overview

StreamClip AI automatically analyzes Twitch and Kick VODs/clips to detect interesting moments, generates highlights, and exports vertical format clips with animated subtitles - all without requiring paid AI APIs or cloud services.

## Features

- **Local AI Processing**: No API keys or cloud services required
- **Platform Support**: Twitch and Kick VODs and clips
- **Automatic Transcription**: Using Faster-Whisper
- **AI Highlight Detection**: Multi-signal analysis (audio, visual, transcript)
- **Vertical Format**: 9:16 aspect ratio for social media
- **Animated Subtitles**: Word-level captions
- **Auto Framing**: Intelligent facecam and gameplay positioning
- **Metadata Generation**: Titles, descriptions, and hashtags
- **Queue Management**: Background processing with job persistence

## Technology Stack

**Frontend:**
- React + TypeScript
- Vite
- Tailwind CSS
- Tauri Desktop

**Backend:**
- Python 3.11
- FastAPI
- SQLite
- Background workers

**AI & Video:**
- Faster-Whisper (transcription)
- Ollama (contextual analysis)
- FFmpeg (video processing)
- OpenCV (computer vision)
- yt-dlp (video acquisition)

## System Requirements

- Windows 11
- NVIDIA GPU with 4GB+ VRAM (or CPU fallback)
- 16GB RAM minimum
- Python 3.11+
- Node.js 18+
- FFmpeg
- Ollama (optional, for enhanced AI analysis)

## Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

## Quick Start

1. Launch the application
2. Navigate to "New Project"
3. Paste a Twitch or Kick URL
4. Click "Start Analysis"
5. Monitor progress in "Processing Queue"
6. View generated highlights in "AI Highlights"
7. Export finished clips from "Export Manager"

## Project Structure

```
StreamClipAI/
├── src/                    # React frontend
│   ├── components/
│   ├── pages/
│   ├── types/
│   └── utils/
├── backend/                # Python FastAPI backend
│   └── app/
│       ├── api/           # REST API routes
│       ├── models/        # Database models
│       ├── services/      # Business logic
│       ├── utils/         # Utilities
│       └── workers/       # Background processors
├── src-tauri/             # Tauri desktop wrapper
└── Projects/              # User data (created at runtime)
```

## Development

```bash
# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Run development server (frontend + backend)
npm run dev

# Build for production
npm run build
```

## Configuration

Settings are accessible through the Settings page in the application:

- Processing mode (CPU/GPU)
- AI model selection
- Clip duration and quality
- Highlight detection thresholds
- Storage location
- Output format

## License

Copyright © 2026 StreamClip AI. All rights reserved.

## Important Notes

- Only process content you have permission to use
- Respect platform terms of service and copyright
- This tool is for authorized content only
- Generated clips are your responsibility

## Support

For issues and feature requests, please use the GitHub issue tracker.
