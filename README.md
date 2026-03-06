# TVS - Text-Video-Summarizer

A standalone Python tool for downloading, transcribing, and summarizing videos from social media platforms automatically.

## Features

### Core Features
✅ **Single Video Processing** - Process one video at a time
✅ **Batch Processing** - Process multiple videos from a URL list file
✅ **Smart Download Detection** - Detects already downloaded videos and skips re-downloading
✅ **Smart Transcript Caching** - Skips transcription if transcript already exists (use `-f` to force)
✅ **Audio-Only Mode** - Download only audio for 10x faster processing (`-a` flag)
✅ **Live Terminal Output** - Real-time progress updates (`-t` flag)
✅ **Vibe-Only Transcription** - Uses Whisper Large V3 Turbo for accurate transcription
✅ **AI-Powered Summarization** - Claude AI analyzes transcripts and generates intelligent summaries
✅ **Colored Terminal Output** - Beautiful progress indicators and status messages
✅ **Error Handling** - Clear error messages with troubleshooting steps

### v3.1 Features (November 2025)
✅ **Multi-Site Support** - Organize videos by platform (Instagram, TikTok, X, etc.)
✅ **Smart Cookie Management** - Organized cookies by site with expiration warnings
✅ **AI Smart Naming** - Social media videos get descriptive AI-generated filenames
✅ **Automatic Hashtags** - 3-5 relevant hashtags added to all summaries
✅ **Platform Detection** - Automatically detects source and organizes accordingly

## Requirements

- Python 3.13+
- yt-dlp (video downloader)
- vibe (AI transcription tool)
- OpenCode (AI agent framework for summary generation)
- Whisper Large V3 Turbo model (1.5 GB, auto-downloaded by vibe GUI)
- mediainfo (video metadata extraction)

## Installation

```bash
# Install required packages (Arch Linux)
sudo pacman -S yt-dlp mediainfo
yay -S vibe-bin

# Run vibe GUI once to download the Whisper model (1.5 GB)
vibe

# Install OpenCode (if not already installed)
# Follow instructions at https://github.com/opencode/opencode

# Clone the repository
git clone https://github.com/commandlinetips/tvs.git
cd tvs

# Make script executable
chmod +x tvs.py
```

## Usage

### Quick Start (Recommended)

```bash
# Single video - audio-only with live output (fastest)
python3.13 tvs.py -u "VIDEO_URL" -a -t

# Force re-transcription (when needed)
python3.13 tvs.py -u "VIDEO_URL" -a -t -f

# Batch processing
python3.13 tvs.py --list urls.txt -a -t
```

### Command Flags

| Flag | Long Form         | Description                                        |
|------|-------------------|----------------------------------------------------|
| `-u` | `--url`           | Single video URL                                   |
| `-l` | `--list`          | URL list file                                      |
| `-p` | `--playlist`      | YouTube playlist or channel URL                    |
| `-a` | `--audio-only`    | Download audio only (10x faster, smaller)          |
| `-t` | `--terminal`      | Show live output (no buffering)                    |
| `-f` | `--force`         | Force re-transcription (skip existing check)       |
| `-d` | `--download-only` | Download only, skip transcription and summary      |
| `-h` | `--help`          | Show help message                                  |
|      | `--playlist-items`| Select specific items from playlist (e.g. `1-10`) |

### Examples

**Process Single Video:**
```bash
# Instagram/TikTok/social media video
python3.13 tvs.py -u "https://social-media-site.com/video/123" -a -t

# Long video
python3.13 tvs.py -u "https://video-platform.com/watch?v=ABC123" -a -t
```

**Batch Processing:**
```bash
# Create URL list file
cat > urls.txt << 'EOF'
# My videos to process
https://social-media-site.com/video/123
https://video-platform.com/watch?v=ABC123
https://another-site.com/post/XYZ789
EOF

# Process all videos
python3.13 tvs.py --list urls.txt -a -t
```

**Force Re-transcription:**
```bash
# When transcript is corrupted or you want fresh transcription
python3.13 tvs.py -u "VIDEO_URL" -a -t -f
```

**Playlist Processing:**
```bash
# Download and process all videos in a playlist
python3.13 tvs.py -p "https://youtube.com/playlist?list=PLxxxxxx" -a -t

# Download playlist videos only (no transcription or summary)
python3.13 tvs.py -p "https://youtube.com/playlist?list=PLxxxxxx" -a -d

# Download specific items from a playlist
python3.13 tvs.py -p "https://youtube.com/playlist?list=PLxxxxxx" --playlist-items 1-10 -a -d
```

> **Note:** Already-downloaded videos are automatically skipped using a download archive
> (`~/Videos/.yt-dlp-archive.txt`). Re-running the same playlist is safe and fast.

### URL List File Format

```
# Comments start with #
# Blank lines are ignored

https://social-media-site.com/video/123
https://video-platform.com/watch?v=ABC

# Another comment
https://another-site.com/post/XYZ
```

## Output Structure

### Files Created (v3.1 - Organized by Platform)

```
~/Videos/
├── instagram/                               # Instagram videos
│   ├── C_ABC123.m4a                        # Audio (ID-based filename)
│   └── C_ABC123-transcript.txt
├── youtube/                                 # YouTube videos
│   ├── Video_Title_Here.m4a
│   └── Video_Title_Here-transcript.txt
├── tiktok/                                  # TikTok videos
├── x/                                       # X/Twitter videos
├── threads/                                 # Threads videos (manual only)
└── other/                                   # Other platforms

~/Work/Kai/video/
├── Video_Title_Here-transcript.txt          # Backup (title-based)
├── Video_Title_Here-summarize.md            # Summary with hashtags ⭐
├── python-tutorial-C_ABC123-transcript.txt  # Backup (AI-named)
└── python-tutorial-C_ABC123-summarize.md    # AI-named summary ⭐
```

### Summary Contents

Each AI-generated summary includes:
- **Comprehensive Analysis:** Deep content analysis by Claude AI
- **Key Themes:** Main topics and insights
- **Notable Quotes:** Important statements from the video
- **Actionable Takeaways:** Practical insights to apply
- **Metadata:** For social media videos (filename suggestion, hashtags, video ID)
- **Hashtags:** 3-5 relevant tags for categorization (all platforms)

### Platform-Specific Naming

| Platform           | Download Filename | Summary Filename                   |
|--------------------|-------------------|------------------------------------|
| YouTube            | `Video_Title.m4a` | `Video_Title-summarize.md`         |
| Instagram          | `C_XYZ123.m4a`    | `ai-topic-C_XYZ123-summarize.md`   |
| TikTok             | `7123456789.m4a`  | `ai-topic-7123456789-summarize.md` |
| X/Twitter          | `username_123.m4a`| `username_123-summarize.md`        |
| Threads (manual)   | `manual_name.m4a` | `ai-topic-manual_name-summarize.md`|

## Processing Time

### Audio-Only Mode (`-a` flag) - RECOMMENDED ⭐

**56-minute video:**
- Download: 30-90 seconds (50 MB audio)
- Transcription: 10-17 minutes (or SKIPPED if transcript exists!)
- Summary: 30-60 seconds (AI analysis)
- **Total: 12-20 minutes** (or ~1 minute if re-run!)

**1-minute video:**
- Download: ~5-10 seconds
- Transcription: ~10-15 seconds (or SKIPPED!)
- Summary: ~30-60 seconds
- **Total: ~45-85 seconds** (or ~30 seconds if re-run!)

### Video Mode (480p) - NOT RECOMMENDED

**56-minute video:**
- Download: 5-8 minutes (500 MB video)
- Transcription: 10-17 minutes (same as audio-only)
- Summary: 30-60 seconds
- **Total: 15-25 minutes** (10x slower download for no benefit!)

**Why Audio-Only is Better:**
- ✅ 10x smaller files (50 MB vs 500 MB)
- ✅ 10x faster download (1 min vs 8 min)
- ✅ Transcription only needs audio anyway
- ✅ Same quality transcripts
- ✅ Saves disk space and bandwidth

## Features in Detail

### 1. Smart Caching (Download + Transcript)

**Download caching:**
```
⚠️  Video already exists: Video_Title_Here.m4a
ℹ️  Skipping download (file already present)
```

**Transcript caching (NEW in v3.0):**
```
⚠️  Transcript already exists: Video_Title_Here-transcript.txt
ℹ️  Skipping transcription (use -f to force)
```

Saves 10-17 minutes on re-runs! Use `-f` flag to force re-transcription.

### 2. Multi-Site Cookie Management (v3.1)

**Cookie age warning:**
```
ℹ️  Using instagram cookies for authentication
⚠️  Cookie file is 32 days old (threshold: 30 days)
⚠️  COOKIES MAY HAVE EXPIRED - CONSIDER UPDATING
ℹ️  Cookie location: ~/tools/automation/tvs/cookies/instagram/www.instagram.com_cookies.txt
```

**Cookie directory structure:**
```
cookies/
├── instagram/www.instagram.com_cookies.txt
├── tiktok/www.tiktok.com_cookies.txt
├── x/x.com_cookies.txt
└── youtube/www.youtube.com_cookies.txt
```

### 3. AI Smart Naming for Social Media (v3.1)

**For Instagram/TikTok/Threads:**
- AI reads transcript and generates descriptive filename
- Max 3-4 words, lowercase-with-hyphens
- Video ID preserved for tracking
- Example: `C_ABC123.m4a` → `python-tutorial-C_ABC123-summarize.md`

**For YouTube/X:**
- Keeps original title-based naming (already descriptive)

### 4. Automatic Hashtag Generation (v3.1)

**All summaries include hashtags:**
```markdown
## Metadata (for social media)
**Suggested Filename:** python-async-programming
**Hashtags:** #python #async #tutorial #programming
**Video ID:** C_ABC123

Or (for YouTube):
#python #webdev #tutorial #coding #opensource
```

### 5. Batch Processing Statistics

After processing multiple videos:
```
Batch Processing Complete!

Statistics:
  ✅ Successful: 5
  ❌ Failed:     1
  📊 Total:      6
  ⏱️  Time:       125.3s (2.1 min)
```

### 6. Error Handling

If transcription fails:
```
❌ Transcription failed
⚠️  Troubleshooting:
  1. Verify model exists:
     ls -lh ~/.local/share/github.com.thewh1teagle.vibe/ggml-large-v3-turbo.bin
  2. Check video has audio:
     ffprobe -v error -select_streams a:0 ...
  3. Try running vibe GUI first
```

## Command Reference

| Command | Description |
|---------|-------------|
| `python3.13 tvs.py -u <URL> -a -t` | Single video (audio-only, live output) ⭐ |
| `python3.13 tvs.py -u <URL> -a -t -f` | Force re-transcription |
| `python3.13 tvs.py -l <file> -a -t` | Batch process with live output |
| `python3.13 tvs.py --help` | Show help message |

**Recommended flags:**
- Always use `-a` (audio-only) - 10x faster
- Use `-t` (terminal output) - see progress in real-time
- Use `-f` (force) - only when transcript needs regeneration

## Configuration

### Directories

Configured at the top of the script:
```python
VIDEOS_DIR = Path.home() / "Videos"
WORK_DIR = Path.home() / "Work" / "Kai" / "video"
```

### Vibe Model

```python
VIBE_MODEL = Path.home() / ".local/share/github.com.thewh1teagle.vibe/ggml-large-v3-turbo.bin"
```

### Timeouts

```python
# In run_command() function
timeout=600  # Download timeout: 10 minutes
timeout=900  # Transcription timeout: 15 minutes
```

## Workflow

```
1. Environment Validation
   ├── Check yt-dlp installed
   ├── Check vibe installed
   ├── Check vibe model exists
   └── Create directories if needed

2. Download Video (yt-dlp)
   ├── Check if already exists
   ├── Download with --restrict-filenames
   └── Verify video file created

3. Transcribe Audio (vibe)
   ├── Use Whisper Large V3 Turbo model
   ├── Automatic language detection
   └── Save as plain text

4. Copy Transcript
   └── Create backup in work directory

5. Generate Summary
   ├── Read transcript
   ├── Analyze content
   ├── Create structured markdown
   └── Save to work directory
```

## Troubleshooting

### vibe GTK Error: "cannot open display"

**Symptom:** Transcription fails immediately with:
```
(vibe:XXXXX): Gtk-WARNING **: cannot open display:
```

**Cause:** vibe uses GTK internally even in CLI mode and requires `DISPLAY` to be set.

**Fix:** Already handled automatically in tvs.py — the script sets `DISPLAY=:0` before
calling vibe if the variable is missing. If it still fails, verify XWayland is running:
```bash
echo $DISPLAY          # Should be :0 or :1
ls /tmp/.X11-unix/     # Shows available X displays
```

---

### Model Not Found

```bash
# Run vibe GUI to download Whisper model (1.5 GB)
vibe
```

Model location:
```
~/.local/share/github.com.thewh1teagle.vibe/ggml-large-v3-turbo.bin
```

### Cookie Issues (Social Media)

**Problem:** "Sign in to confirm you're not a bot"

**Solution:**
1. Export fresh cookies from browser using extension (e.g., "Get cookies.txt LOCALLY")
2. Place in correct directory:
   ```bash
   ~/tools/automation/tvs/cookies/instagram/www.instagram.com_cookies.txt
   ~/tools/automation/tvs/cookies/tiktok/www.tiktok.com_cookies.txt
   ~/tools/automation/tvs/cookies/x/x.com_cookies.txt
   ```
3. TVS warns when cookies are ≥30 days old

### Threads Not Supported

**Current Status:** yt-dlp (version 2025.10.22) doesn't support Threads yet

**Workaround:**
1. Download Threads video manually from browser
2. Place in `~/Videos/threads/`
3. Run TVS on the downloaded file (transcription and summary will work)

**Check for updates:**
```bash
yt-dlp -U  # Update yt-dlp
```

### Video Has No Audio

Some videos don't have audio tracks. Check with:
```bash
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name VIDEO_FILE
```

### Download Fails

- Check internet connection
- Verify URL is valid
- Try updating yt-dlp: `yay -S yt-dlp`
- For social media: check cookies are fresh

### Transcription Timeout

Already configured for 40-minute timeout (sufficient for most videos).

For extremely long videos (>2 hours), increase timeout in code:
```python
# Line ~289 in tvs.py
success, stdout, stderr = run_command(cmd, cwd=VIDEOS_DIR, timeout=3600)  # 60 min
```

### AI Summary Generation Fails

**Requirements:**
- OpenCode must be installed and configured
- transcript-analyzer agent must be available

**Check:**
```bash
opencode agent list | grep transcript-analyzer
```

## Supported Platforms

| Platform  | Download | Transcribe | Summary | AI Naming | Status         |
|-----------|----------|------------|---------|-----------|----------------|
| YouTube   | ✅       | ✅         | ✅      | ❌        | Fully working  |
| Instagram | ✅       | ✅         | ✅      | ✅        | Fully working  |
| TikTok    | ✅       | ✅         | ✅      | ✅        | Fully working  |
| X/Twitter | ✅       | ✅         | ✅      | ❌        | Fully working  |
| Threads   | ❌       | ✅*        | ✅*     | ✅*       | Manual download only |

*Requires manual video download first

## Project Links

- **GitHub:** https://github.com/commandlinetips/tvs
- **Documentation:** See `USAGE.md` and `IMPROVEMENTS.md`
- **Issues:** Report bugs or request features on GitHub

## Version History

### v3.1 (November 2025)
- ✅ Multi-site support with platform detection
- ✅ Organized cookie management by site
- ✅ Cookie expiration warnings (30-day threshold)
- ✅ AI-powered smart naming for social media videos
- ✅ Automatic hashtag generation for all summaries
- ✅ Filename length validation (3-4 words max)
- ✅ Site-specific output directories
- ✅ Short video duration parsing fix
- ✅ Threads site detection (download not supported by yt-dlp yet)

### v3.0 (October 2025)
- ✅ Smart transcript caching (skip if exists)
- ✅ AI-powered summaries using Claude via OpenCode
- ✅ Audio-only mode (`-a` flag)
- ✅ Live terminal output (`-t` flag)
- ✅ Force re-transcription flag (`-f`)
- ✅ Improved error handling with troubleshooting steps

### v2.0 (Earlier)
- ✅ Batch processing support
- ✅ Smart download detection
- ✅ Colored terminal output
- ✅ Template-based summaries

---

**Created:** 2025-10-31
**Updated:** 2025-11-06
**Author:** skullthoughts
**Version:** TVS v3.1
**License:** MIT


