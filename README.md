# TVS - Text-Video-Summarizer

A standalone Python tool for downloading, transcribing, and summarizing videos automatically.

## Features

✅ **Single Video Processing** - Process one video at a time
✅ **Batch Processing** - Process multiple videos from a URL list file
✅ **Smart Download Detection** - Detects already downloaded videos and skips re-downloading
✅ **Vibe-Only Transcription** - Uses only vibe (Whisper Large V3 Turbo) for accurate transcription
✅ **Automatic Summarization** - Generates structured markdown summaries
✅ **Colored Terminal Output** - Beautiful progress indicators and status messages
✅ **Error Handling** - Clear error messages with troubleshooting steps

## Requirements

- Python 3.13+
- yt-dlp (video downloader)
- vibe (AI transcription tool)
- Whisper Large V3 Turbo model (1.5 GB, auto-downloaded by vibe GUI)

## Installation

```bash
# Install yt-dlp
sudo pacman -S yt-dlp

# Install vibe
yay -S vibe-bin

# Run vibe GUI once to download the model
vibe

# Make script executable
chmod +x tvs.py
```

## Usage

### Single Video

```bash
python3.13 tvs.py -u <URL>
python3.13 tvs.py --url <URL>
```

**Example:**
```bash
python3.13 tvs.py -u https://vediosite.com/123
```

### Batch Processing

```bash
python3.13 tvs.py -l <file.txt>
python3.13 tvs.py --list <file.txt>
```

**Example:**
```bash
python3.13 tvs.py --list my-videos.txt
```

#### URL List File Format

```
# Comments start with #
# Blank lines are ignored

https://vediosite.com/123
https://vediosite.com/123

# Another comment
https://youtu.be/VIDEO3
```

### Help

```bash
python3.13 tvs.py --help
```

## Output Structure

### Files Created

```
~/Videos/
├── Video_Title_Here.webm                    # Downloaded video
└── Video_Title_Here-transcript.txt          # Transcription

~/Work/Kai/video/
├── Video_Title_Here-transcript.txt          # Transcription (backup)
└── Video_Title_Here-summarize.md            # Summary ⭐
```

### Summary Contents

Each generated summary includes:
- Executive Summary
- Key Takeaways
- Full Transcript
- Analysis Notes (word count, sentence count, etc.)
- Processing Details (workflow, file locations, tools used)

## Processing Time

For a typical 1-minute video:
- Download: ~5-15 seconds
- Transcription: ~10-15 seconds
- Summary generation: ~2-5 seconds
- **Total: ~20-30 seconds**

## Features in Detail

### 1. Smart Download Detection

If a video was already downloaded:
```
⚠️  Video already exists: Video_Title_Here.webm
ℹ️  Skipping download (file already present)
```

The script will skip the download and proceed directly to transcription.

### 2. Batch Processing Statistics

After processing multiple videos:
```
Batch Processing Complete!

Statistics:
  ✅ Successful: 5
  ❌ Failed:     1
  📊 Total:      6
  ⏱️  Time:       125.3s (2.1 min)
```

### 3. Error Handling

If transcription fails, you get actionable troubleshooting steps:
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
| `python3.13 tvs.py -u <URL>` | Process single video |
| `python3.13 tvs.py --url <URL>` | Process single video (long form) |
| `python3.13 tvs.py -l <file>` | Process URLs from file |
| `python3.13 tvs.py --list <file>` | Process URLs from file (long form) |
| `python3.13 tvs.py --help` | Show help message |

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

### Model Not Found

```bash
# Run vibe GUI to download model
vibe
```

The model will be downloaded to:
```
~/.local/share/github.com.thewh1teagle.vibe/ggml-large-v3-turbo.bin
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

### Transcription Timeout

For very long videos (>1 hour), you may need to increase the timeout in the script:
```python
success, stdout, stderr = run_command(cmd, cwd=VIDEOS_DIR, timeout=1800)  # 30 min
```


