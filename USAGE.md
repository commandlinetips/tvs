# TVS Quick Usage Guide

## Basic Commands

### 1. Simple Video Download (480p max)

```bash
python3.13 tvs.py -u "https://vedio link"
```

- Downloads video at 480p quality
- ~300-500 MB for 56-min video
- Shows output in log/background

### 2. Audio Only (RECOMMENDED) ⭐

```bash
python3.13 tvs.py -u "vedio link" -a
```

- Downloads ONLY audio (not video)
- ~30-80 MB for 56-min video (10x smaller!)
- Perfect for transcription (vibe only needs audio)

### 3. Live Terminal Output

```bash
python3.13 tvs.py -u "vedio link" -t
```

- Shows real-time progress in terminal
- No need to tail log file
- See messages as they happen

### 4. Combined: Audio + Live Output ⭐⭐

```bash
python3.13 tvs.py -u "vedio link" -a -t
```

- Audio-only (fast, small)
- Live updates in terminal
- **RECOMMENDED for interactive use**

### 5. Force Re-transcription

```bash
python3.13 tvs.py -u "vedio link" -a -t -f
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
https://vedio link.com/watch?v=VIDEO1
https://vedio link.com/watch?v=VIDEO2
https://vedio link.com/watch?v=VIDEO3
EOF

# Process all (audio-only, live output)
python3.13 tvs.py --list urls.txt -a -t

# Force re-transcription for all videos in batch
python3.13 tvs.py --list urls.txt -a -t -f
```

## Flag Reference

| Flag | Long Form      | Description                                  |
| ---- | -------------- | -------------------------------------------- |
| `-u` | `--url`        | Single video URL                             |
| `-l` | `--list`       | URL list file                                |
| `-a` | `--audio-only` | Download audio only (small, fast)            |
| `-t` | `--terminal`   | Show live output (no buffering)              |
| `-f` | `--force`      | Force re-transcription (skip existing check) |
| `-h` | `--help`       | Show help message                            |

## File Size Comparison (56-minute video)

| Mode        | File Size   | Download Time | Command                    |
| ----------- | ----------- | ------------- | -------------------------- |
| 1080p       | ~1.5 GB     | 5-15 min      | (not available, too large) |
| 720p        | ~800 MB     | 3-10 min      | (not available)            |
| **480p**    | ~300-500 MB | 2-8 min       | `tvs.py -u "URL"`          |
| **Audio** ⭐ | ~30-80 MB   | 30-90 sec     | `tvs.py -u "URL" -a`       |

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
python3.13 tvs.py -u "https://vedio link.com/s" -a -t
```

## Output Files

Every processed video creates organized output by platform:

```
~/Videos/
├── instagram/                    # Instagram videos
│   ├── C_ABC123.m4a             # Audio file (ID-based)
│   └── C_ABC123-transcript.txt
├── youtube/                      # YouTube videos
│   ├── Video_Title_Here.m4a
│   └── Video_Title_Here-transcript.txt
├── tiktok/                       # TikTok videos
├── threads/                      # Threads videos (manual download)
├── x/                            # X/Twitter videos
└── other/                        # Other platforms

~/Work/Kai/video/
├── Video_Title_Here-transcript.txt         # Backup (YouTube)
├── Video_Title_Here-summarize.md           # Summary with hashtags ⭐
├── python-tutorial-C_ABC123-transcript.txt # Instagram backup
└── python-tutorial-C_ABC123-summarize.md   # AI-named summary ⭐
```

## Examples with Your Video

```bash
# Method 1: Interactive (see progress)
python3.13 tvs.py -u "https://vedio link/" -a -t

# Method 2: Background (check later)
python3.13 tvs.py -u "https://vedio link/" -a > dhh.log 2>&1 &
tail -f dhh.log

# Method 3: Save to specific log
python3.13 tvs.py -u "https://vedio link/" -a -t | tee dhh-sqlite.log
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

## New Features in v3.1 (November 2025)

### Multi-Site Support 🌐

- **Site-specific directories:** Videos auto-organized by platform
- **Smart cookie management:** Organized cookies by site in `cookies/` folder
- **Cookie age warnings:** Red alert when cookies ≥30 days old
- **Supported platforms:** Instagram, YouTube, TikTok, X (Twitter), Threads

### AI Smart Naming for Social Media 🎯

- **Instagram/TikTok/Threads:** AI analyzes content and generates descriptive filenames
  - Example: `C_XYZ123.m4a` → `python-tutorial-C_XYZ123-summarize.md`
- **YouTube:** Keeps original title-based naming (already descriptive)
- **Filename validation:** Max 3-4 words, prevents overly long names
- **Video ID preserved:** Original ID kept in filename for tracking

### Automatic Hashtag Generation 🏷️

- **All summaries:** 3-5 relevant hashtags added automatically
- **Content-based:** Generated from actual video analysis, not just titles
- **Future-ready:** Foundation for search/categorization features

### Platform-Specific Features

| Platform  | Directory    | Naming Style        | Hashtags | Status |
|-----------|--------------|---------------------|----------|--------|
| YouTube   | `~/Videos/youtube/` | Title-based | End of summary | ✅ Working |
| Instagram | `~/Videos/instagram/` | AI + Video ID | Metadata section | ✅ Working |
| TikTok    | `~/Videos/tiktok/` | AI + Video ID | Metadata section | ✅ Working |
| X/Twitter | `~/Videos/x/` | Title-based | End of summary | ✅ Working |
| Threads   | `~/Videos/threads/` | AI + Video ID | Metadata section | ❌ Not supported by yt-dlp yet |

### Known Limitations

**Threads Support:**
- yt-dlp (version 2025.10.22) doesn't have Threads extractor yet
- Cookies are properly configured, but yt-dlp can't process Threads URLs
- **Workaround:** Download videos manually and place in `~/Videos/threads/`
- TVS can still transcribe and summarize manually downloaded Threads videos
- Check for yt-dlp updates: `yt-dlp -U`

## Cookie Management

### Setting Up Cookies

1. **Export cookies from browser** using extension (e.g., "Get cookies.txt LOCALLY")
2. **Place in correct directory:**
   ```bash
   # Instagram
   ~/tools/automation/tvs/cookies/instagram/www.instagram.com_cookies.txt

   # TikTok
   ~/tools/automation/tvs/cookies/tiktok/www.tiktok.com_cookies.txt

   # X (Twitter)
   ~/tools/automation/tvs/cookies/x/x.com_cookies.txt

   # YouTube (optional, most videos don't need authentication)
   ~/tools/automation/tvs/cookies/youtube/www.youtube.com_cookies.txt
   ```

3. **Update cookies when you see warning:**
   ```
   ⚠️  Cookie file is 32 days old (threshold: 30 days)
   ⚠️  COOKIES MAY HAVE EXPIRED - CONSIDER UPDATING
   ```

### Cookie Expiration

- Most cookies expire after ~30 days
- TVS warns you when cookies are ≥30 days old
- Update cookies by re-exporting from browser
- Shows cookie location for easy updating

## Examples by Platform

### Instagram Video
```bash
python3.13 tvs.py -u "https://instagram.com/reel/C_XYZ123" -a -t

# Output:
# - Video: ~/Videos/instagram/C_XYZ123.m4a
# - Summary: ~/Work/Kai/video/python-tutorial-C_XYZ123-summarize.md
# - Hashtags in metadata section
# - AI-generated descriptive filename
```

### TikTok Video
```bash
python3.13 tvs.py -u "https://www.tiktok.com/@user/video/123" -a -t

# Output:
# - Video: ~/Videos/tiktok/7123456789.m4a
# - Summary: ~/Work/Kai/video/cooking-tips-7123456789-summarize.md
# - AI smart naming based on content
```

### X (Twitter) Video
```bash
python3.13 tvs.py -u "https://x.com/user/status/123456789" -a -t

# Output:
# - Video: ~/Videos/x/username_status_123.m4a
# - Summary: ~/Work/Kai/video/username_status_123-summarize.md
# - Hashtags at end of summary
```

### YouTube Video (Unchanged)
```bash
python3.13 tvs.py -u "https://youtube.com/watch?v=dQw4w9WgXcQ" -a -t

# Output:
# - Video: ~/Videos/youtube/Rick_Astley_Never_Gonna_Give_You_Up.m4a
# - Summary: ~/Work/Kai/video/Rick_Astley_Never_Gonna_Give_You_Up-summarize.md
# - Title-based naming preserved
# - Hashtags at end of summary
```

---

**Created:** 2025-10-31
**Updated:** 2025-11-06
**Author:** skullthoughts
**Tool:** TVS v3.1
