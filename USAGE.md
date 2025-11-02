# TVS Quick Usage Guide

## Basic Commands

### 1. Simple Video Download (480p max)
```bash
python3.13 tvs.py -u "https://youtube.com/watch?v=VIDEO_ID"
```
- Downloads video at 480p quality
- ~300-500 MB for 56-min video
- Shows output in log/background

### 2. Audio Only (RECOMMENDED) ⭐
```bash
python3.13 tvs.py -u "https://youtube.com/watch?v=VIDEO_ID" -a
```
- Downloads ONLY audio (not video)
- ~30-80 MB for 56-min video (10x smaller!)
- Perfect for transcription (vibe only needs audio)

### 3. Live Terminal Output
```bash
python3.13 tvs.py -u "https://youtube.com/watch?v=VIDEO_ID" -t
```
- Shows real-time progress in terminal
- No need to tail log file
- See messages as they happen

### 4. Combined: Audio + Live Output ⭐⭐
```bash
python3.13 tvs.py -u "https://youtube.com/watch?v=VIDEO_ID" -a -t
```
- Audio-only (fast, small)
- Live updates in terminal
- **RECOMMENDED for interactive use**

### 5. Force Re-transcription
```bash
python3.13 tvs.py -u "https://youtube.com/watch?v=VIDEO_ID" -a -t -f
```
- Forces re-transcription even if transcript exists
- Useful when transcript file is corrupted
- Normally skips transcription if file already present (saves 4-5 min!)

### 6. Background with Log
```bash
python3.13 tvs.py -u "URL" -a > tvs.log 2>&1 &
tail -f tvs.log
```
- Runs in background
- Saves output to log
- Monitor with tail

### 7. Batch Processing
```bash
# Create URL list file
cat > urls.txt << 'EOF'
# My videos to process
https://youtube.com/watch?v=VIDEO1
https://youtube.com/watch?v=VIDEO2
https://youtube.com/watch?v=VIDEO3
EOF

# Process all (audio-only, live output)
python3.13 tvs.py --list urls.txt -a -t

# Force re-transcription for all videos in batch
python3.13 tvs.py --list urls.txt -a -t -f
```

## Flag Reference

| Flag | Long Form | Description |
|------|-----------|-------------|
| `-u` | `--url` | Single video URL |
| `-l` | `--list` | URL list file |
| `-a` | `--audio-only` | Download audio only (small, fast) |
| `-t` | `--terminal` | Show live output (no buffering) |
| `-f` | `--force` | Force re-transcription (skip existing check) |
| `-h` | `--help` | Show help message |

## File Size Comparison (56-minute video)

| Mode | File Size | Download Time | Command |
|------|-----------|---------------|---------|
| 1080p | ~1.5 GB | 5-15 min | (not available, too large) |
| 720p | ~800 MB | 3-10 min | (not available) |
| **480p** | ~300-500 MB | 2-8 min | `tvs.py -u "URL"` |
| **Audio** ⭐ | ~30-80 MB | 30-90 sec | `tvs.py -u "URL" -a` |

## Processing Time (56-minute video)

### With Video (480p)
```
Download:      5-8 minutes (500 MB)
Transcription: 10-17 minutes
Summary:       5 seconds
Total:         15-25 minutes
```

### With Audio Only ⭐
```
Download:      30-90 seconds (50 MB)
Transcription: 10-17 minutes (SKIPPED if transcript exists!)
Summary:       30-60 seconds (AI analysis via OpenCode)
Total:         12-20 minutes (faster!)
              OR ~1 minute if transcript exists! 🚀
```

## Common Usage Patterns

### Interactive Single Video (RECOMMENDED)
```bash
python3.13 tvs.py -u "https://youtu.be/0rlATWBNvMw" -a -t
```
**Why:**
- Audio-only = fast download
- Live terminal = see progress
- Perfect for one video

### Background Batch Processing
```bash
python3.13 tvs.py --list my-videos.txt -a > batch.log 2>&1 &
```
**Why:**
- Process multiple videos
- Runs in background
- Check log later

### Quick Test
```bash
# Short video for testing
python3.13 tvs.py -u "https://youtube.com/shorts/8YULk160fIw" -a -t
```

## Output Files

Every processed video creates:
```
~/Videos/
└── Video_Title_Here.m4a          # Audio file (if -a used)
└── Video_Title_Here-transcript.txt

~/Work/Kai/video/
├── Video_Title_Here-transcript.txt    # Backup
└── Video_Title_Here-summarize.md      # Summary ⭐
```

## Examples with Your Video

```bash
# Method 1: Interactive (see progress)
python3.13 tvs.py -u "https://youtu.be/0rlATWBNvMw" -a -t

# Method 2: Background (check later)
python3.13 tvs.py -u "https://youtu.be/0rlATWBNvMw" -a > dhh.log 2>&1 &
tail -f dhh.log

# Method 3: Save to specific log
python3.13 tvs.py -u "https://youtu.be/0rlATWBNvMw" -a -t | tee dhh-sqlite.log
```

## Tips

### 1. Always Use `-a` for Transcription
Since vibe only needs audio, downloading full video wastes:
- Time (10x slower)
- Bandwidth (10x more data)
- Disk space (10x larger)

### 2. Use `-t` for Single Videos
When processing one video interactively:
```bash
python3.13 tvs.py -u "URL" -a -t
```
You'll see real-time progress without needing to tail logs.

### 3. Skip `-t` for Batch Processing
For multiple videos in background:
```bash
python3.13 tvs.py --list urls.txt -a > batch.log 2>&1 &
```
Check log file periodically instead.

### 4. Use `-f` to Force Re-transcription
Only use when transcript is corrupted or you want fresh transcription:
```bash
python3.13 tvs.py -u "URL" -a -t -f
```
Without `-f`, transcription is automatically skipped if file exists (saves 4-5 minutes).

### 5. Monitor Running Process
```bash
# Check if running
ps aux | grep "tvs.py"

# See what it's downloading
ls -lh ~/Videos/ | tail -5

# Watch disk usage
watch -n 5 'du -sh ~/Videos/'
```

## Troubleshooting

### No Output in Background Mode
**Problem:** Log file stays empty
**Solution:** Use `-t` flag or run in foreground

### Download Too Slow
**Problem:** Large video file downloading
**Solution:** Use `-a` flag for audio-only

### Transcription Timeout
**Problem:** Very long video times out
**Solution:** Already configured for 40-min timeout, should work

## Quick Reference Card

```
# BEST FOR SINGLE VIDEO (with smart transcript caching)
python3.13 tvs.py -u "URL" -a -t

# FORCE RE-TRANSCRIPTION (when needed)
python3.13 tvs.py -u "URL" -a -t -f

# BEST FOR BATCH
python3.13 tvs.py --list urls.txt -a > batch.log 2>&1 &

# BEST FOR TESTING
python3.13 tvs.py -u "SHORT_URL" -a -t

# CHECK HELP
python3.13 tvs.py --help
```

## New Features in v3.0

### Smart Transcript Caching 🚀
- Automatically skips transcription if transcript file already exists
- Saves 4-5 minutes per re-run!
- Use `-f` flag to force re-transcription when needed

### AI-Powered Summaries 🤖
- Uses OpenCode transcript-analyzer agent
- Powered by Claude AI for intelligent analysis
- Extracts key themes, quotes, and actionable insights
- No more template-based summaries!

---

**Created:** 2025-10-31
**Updated:** 2025-10-31
**Author:** skull@omarchy
**Tool:** TVS v3.0
