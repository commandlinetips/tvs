# TVS - Text-Video-Summarizer

A standalone Python CLI tool for downloading, transcribing, and summarizing videos from social media platforms.

## Features

### Core Features
- **Single Video Processing** - Process one video at a time
- **Batch Processing** - Process multiple videos from a URL list file
- **Smart Caching** - Skips already downloaded videos and existing transcripts
- **Audio-Only Mode** - Download only audio for faster processing (`-a` flag)
- **Live Terminal Output** - Real-time progress updates (`-t` flag)
- **Parakeet Transcription** - NVIDIA NeMo parakeet-tdt-0.6b-v3 for accurate ASR
- **AI Summarization** - OpenCode agent generates intelligent summaries
- **Color Demo** - View available terminal colors (`--colors` flag)

### v4.0 Features (March 2026)
- **Parakeet Migration** - Replaced vibe with NVIDIA NeMo parakeet-tdt-0.6b-v3
- **Cross-Platform Support** - macOS, Ubuntu/Debian, Fedora, Arch Linux
- **Local Model** - 2.3 GB model stored in repository directory
- **Conda Environment** - Isolated `nemo` environment for transcription
- **Opencode-Style Colors** - Clean, semantic color names

### v3.x Features
- **Multi-Site Support** - YouTube, Instagram, TikTok, X/Twitter
- **Cookie Management** - Organized by site with expiration warnings
- **AI Smart Naming** - Descriptive filenames for social media videos
- **Automatic Hashtags** - 3-5 relevant hashtags in summaries
- **Platform Detection** - Auto-detect source and organize accordingly

## Requirements

| Requirement | Purpose | Install |
|-------------|---------|---------|
| Python 3.13+ | Runtime | System package |
| yt-dlp | Video downloading | `brew install yt-dlp` / `pip install yt-dlp` |
| ffmpeg | Audio conversion | `brew install ffmpeg` / `sudo apt install ffmpeg` |
| mediainfo | Duration detection (optional) | `brew install mediainfo` |
| conda (miniforge) | Environment management | `brew install --cask miniforge` |
| nemo_toolkit | ASR transcription | `pip install 'nemo_toolkit[asr]'` |
| opencode | Summary generation | See [opencode.ai](https://opencode.ai) |

## Installation

### macOS (Apple Silicon/Intel)

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install yt-dlp ffmpeg mediainfo

# Install Miniforge (conda)
brew install --cask miniforge

# Initialize conda
conda init zsh  # or bash
source ~/.zshrc

# Create nemo environment
conda create -n nemo python=3.11 -y
conda activate nemo
pip install 'nemo_toolkit[asr]'

# Clone repository
git clone https://github.com/commandlinetips/tvs.git
cd tvs

# Download parakeet model (2.3 GB)
git clone https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3

# Verify model
ls -la parakeet-tdt-0.6b-v3/parakeet-tdt-0.6b-v3.nemo
```

### Ubuntu/Debian

```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3.11 python3-pip ffmpeg mediainfo

# Install yt-dlp
pip install yt-dlp --break-system-packages
# Or: sudo wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O /usr/local/bin/yt-dlp && sudo chmod +x /usr/local/bin/yt-dlp

# Install Miniforge
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh
source ~/.bashrc

# Create nemo environment
conda create -n nemo python=3.11 -y
conda activate nemo
pip install 'nemo_toolkit[asr]'

# Clone repository
git clone https://github.com/commandlinetips/tvs.git
cd tvs

# Download parakeet model (2.3 GB)
git clone https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
```

### Fedora

```bash
# Install system dependencies
sudo dnf install -y python3.11 python3-pip ffmpeg mediainfo

# Install yt-dlp
pip install yt-dlp

# Install Miniforge
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh
source ~/.bashrc

# Create nemo environment
conda create -n nemo python=3.11 -y
conda activate nemo
pip install 'nemo_toolkit[asr]'

# Clone and setup
git clone https://github.com/commandlinetips/tvs.git
cd tvs
git clone https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
```

### Arch Linux

```bash
# Install system dependencies
sudo pacman -S yt-dlp ffmpeg mediainfo python

# Install miniforge from AUR
yay -S miniforge

# Initialize and create environment
conda init zsh
source ~/.zshrc
conda create -n nemo python=3.11 -y
conda activate nemo
pip install 'nemo_toolkit[asr]'

# Clone and setup
git clone https://github.com/commandlinetips/tvs.git
cd tvs
git clone https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
```

## Usage

### Quick Start

```bash
# Single video - audio-only with live output (recommended)
python3.13 tvs.py -u "VIDEO_URL" -a -t

# Force re-transcription
python3.13 tvs.py -u "VIDEO_URL" -a -t -f

# Download only (skip transcription)
python3.13 tvs.py -u "VIDEO_URL" -a -t -d

# Batch processing
python3.13 tvs.py --list urls.txt -a -t

# Show color demo
python3.13 tvs.py --colors
```

### Command Flags

| Flag | Long Form | Description |
|------|-----------|-------------|
| `-u` | `--url` | Single video URL |
| `-l` | `--list` | URL list file (one per line) |
| `-a` | `--audio-only` | Download audio only (faster, smaller) |
| `-t` | `--terminal` | Show live output (no buffering) |
| `-f` | `--force` | Force re-transcription |
| `-d` | `--download-only` | Download only, skip transcription |
| | `--colors` | Show color demo and exit |
| `-h` | `--help` | Show help message |

### URL List Format

```
# Comments start with #
# Blank lines are ignored

https://youtube.com/watch?v=ABC123
https://instagram.com/reel/XYZ789

# More URLs
https://tiktok.com/@user/video/123456
```

## Directory Structure

```
tvs/
├── tvs.py                    # Main script
├── videos/                   # Downloaded media
│   ├── youtube/
│   ├── instagram/
│   ├── tiktok/
│   └── x/
├── transcripts/              # Transcripts and summaries
├── logs/                     # Debug and processed logs
├── cookies/                  # Platform cookies (optional)
│   ├── instagram/
│   ├── tiktok/
│   └── x/
└── parakeet-tdt-0.6b-v3/     # Transcription model (2.3 GB)
    └── parakeet-tdt-0.6b-v3.nemo
```

## Processing Pipeline

```
URL → download_video() → transcribe_video() → copy_transcript() → generate_summary()
        (yt-dlp)            (parakeet)           (shutil)          (OpenCode)
```

### Step Details

1. **Environment Validation** - Check yt-dlp, ffmpeg, conda, nemo env
2. **Download** - yt-dlp downloads video/audio to `videos/<platform>/`
3. **Transcribe** - parakeet-tdt-0.6b-v3 transcribes audio (requires conda env)
4. **Copy** - Transcript copied to `transcripts/`
5. **Summarize** - OpenCode agent generates AI summary

## Output Files

```
videos/
├── youtube/Video_Title.m4a           # Audio file
├── youtube/Video_Title-transcript.txt # Transcript

transcripts/
├── Video_Title-transcript.txt        # Transcript copy
└── Video_Title-summarize.md          # AI summary with hashtags
```

### Platform-Specific Naming

| Platform | Video Filename | Summary Filename |
|----------|----------------|------------------|
| YouTube | `Video_Title.m4a` | `Video_Title-summarize.md` |
| Instagram | `C_XYZ123.m4a` | `ai-topic-C_XYZ123-summarize.md` |
| TikTok | `7123456789.m4a` | `ai-topic-7123456789-summarize.md` |
| X/Twitter | `username_123.m4a` | `username_123-summarize.md` |

## Processing Times

### Audio-Only Mode (Recommended)

| Video Length | Download | Transcribe | Summary | Total |
|--------------|----------|------------|---------|-------|
| 1 minute | ~5s | ~10s | ~30s | ~45s |
| 10 minutes | ~15s | ~1m | ~30s | ~2m |
| 60 minutes | ~60s | ~5m | ~45s | ~7m |

### Why Audio-Only?
- 10x smaller files (50 MB vs 500 MB)
- 10x faster downloads
- Transcription only needs audio
- Same quality transcripts

## Cookie Setup (Social Media)

For Instagram, TikTok, and X/Twitter, cookies may be required.

### Export Cookies

1. Install browser extension "Get cookies.txt LOCALLY"
2. Log into the platform in your browser
3. Export cookies for the site

### Cookie Locations

```
cookies/
├── instagram/www.instagram.com_cookies.txt
├── tiktok/www.tiktok.com_cookies.txt
├── x/x.com_cookies.txt
└── youtube/www.youtube.com_cookies.txt
```

### Cookie Warnings

TVS warns when cookies are 30+ days old:

```
⚠️  Cookie file is 32 days old (threshold: 30 days)
⚠️  COOKIES MAY HAVE EXPIRED - CONSIDER UPDATING
```

## Troubleshooting

### Model Not Found

```bash
# Verify model exists
ls -la parakeet-tdt-0.6b-v3/parakeet-tdt-0.6b-v3.nemo

# Download if missing
git clone https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
```

### Conda Environment Issues

```bash
# Verify nemo environment
conda env list

# Recreate if needed
conda create -n nemo python=3.11 -y
conda activate nemo
pip install 'nemo_toolkit[asr]'

# Test import
python -c "import nemo.collections.asr; print('OK')"
```

### Transcription Fails

```bash
# Check video has audio
ffprobe -v error -select_streams a:0 VIDEO_FILE

# Check ffmpeg
ffmpeg -version

# Run manually to debug
conda activate nemo
python -c "
import nemo.collections.asr as nemo_asr
model = nemo_asr.models.ASRModel.restore_from('parakeet-tdt-0.6b-v3/parakeet-tdt-0.6b-v3.nemo')
print(model.transcribe(['test.wav']))
"
```

### Download Fails

- Check internet connection
- Verify URL is valid
- Update yt-dlp: `yt-dlp -U` or `pip install -U yt-dlp`
- For social media: ensure cookies are fresh

### Threads Not Supported

yt-dlp doesn't support Threads yet. Workaround:

1. Download Threads video manually
2. Place in `videos/threads/`
3. Transcription and summary will work

## Supported Platforms

| Platform | Download | Transcribe | Summary | AI Naming | Status |
|----------|----------|------------|---------|-----------|--------|
| YouTube | Yes | Yes | Yes | No | Fully working |
| Instagram | Yes | Yes | Yes | Yes | Fully working |
| TikTok | Yes | Yes | Yes | Yes | Fully working |
| X/Twitter | Yes | Yes | Yes | No | Fully working |
| Threads | No | Yes* | Yes* | Yes* | Manual download |

*Requires manual video download first

## Model Information

### parakeet-tdt-0.6b-v3

- **Source:** NVIDIA NeMo
- **Size:** 2.3 GB
- **Download:** https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
- **Requirements:** nemo_toolkit[asr], Python 3.11+

```bash
# Clone model
git clone https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3

# Or download specific file
wget https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3/resolve/main/parakeet-tdt-0.6b-v3.nemo
```

## Version History

### v4.0 (March 2026)
- Migrated from vibe to parakeet-tdt-0.6b-v3 (NVIDIA NeMo)
- Added cross-platform installation instructions
- Added conda environment isolation (`nemo`)
- Updated color class to opencode-style semantic names
- Added `--colors` flag for color demo
- Model stored in repository directory (not user home)
- Removed dependency on vibe-bin

### v3.1 (November 2025)
- Multi-site support with platform detection
- Organized cookie management by site
- Cookie expiration warnings (30-day threshold)
- AI-powered smart naming for social media
- Automatic hashtag generation

### v3.0 (October 2025)
- Smart transcript caching
- AI summaries via OpenCode
- Audio-only mode
- Live terminal output
- Force re-transcription flag

### v2.0 (Earlier)
- Batch processing support
- Smart download detection
- Colored terminal output

## License

MIT License

## Links

- **GitHub:** https://github.com/commandlinetips/tvs
- **Model:** https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
- **NeMo:** https://github.com/NVIDIA/NeMo
- **OpenCode:** https://opencode.ai

---

**Created:** 2025-10-31
**Updated:** 2026-03-27
**Author:** skullthoughts
**Version:** TVS v4.0
