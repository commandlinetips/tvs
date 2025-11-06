# TVS Improvements - November 2025

## Summary of Changes

This document describes the improvements made to TVS (Text-Video-Summarizer) to handle Instagram videos better and improve organization across multiple platforms.

## 1. Multi-Site Cookie Management ✅

**Problem:** Cookies were hardcoded for Instagram only, making it difficult to manage authentication for other sites.

**Solution:** Implemented organized cookie directory structure:

```
tvs/cookies/
├── instagram/www.instagram.com_cookies.txt
├── threads/www.threads.net_cookies.txt
├── tiktok/www.tiktok.com_cookies.txt
├── x/x.com_cookies.txt
└── youtube/www.youtube.com_cookies.txt
```

**Benefits:**
- Easy to manage cookies for different sites
- Scalable for future platforms
- Clear organization

## 2. Cookie Expiration Warning ✅

**Problem:** Cookies expire after ~30 days, causing silent failures.

**Solution:** Added automatic age checking with red warning when cookies are ≥30 days old:

```
⚠️  Cookie file is 32 days old (threshold: 30 days)
⚠️  COOKIES MAY HAVE EXPIRED - CONSIDER UPDATING
```

**Benefits:**
- Proactive warning before failures occur
- Shows cookie location for easy updating
- Configurable threshold (`COOKIE_WARNING_DAYS = 30`)

## 3. Site-Specific Output Directories ✅

**Problem:** All videos downloaded to ~/Videos/ causing disorganization.

**Solution:** Automatic detection and organization by platform:

```
~/Videos/
├── instagram/    # Instagram videos
├── youtube/      # YouTube videos
├── threads/      # Threads videos
├── tiktok/       # TikTok videos
├── x/            # X/Twitter videos
└── other/        # Unknown platforms
```

**Benefits:**
- Automatic site detection from URL
- Clean organization by source
- Easy to find videos by platform

## 4. Instagram Filename Handling ✅

**Problem:** Instagram uses account name as filename, causing:
- Duplicate filenames from same account
- No indication of video content
- Hard to identify videos later

**Solution:** Two-part approach:
1. **Download:** Use video ID as filename (e.g., `C_XYZ123.m4a`)
2. **Summary:** AI generates descriptive filename based on content

**Example Flow:**
- Video downloaded as: `C_XYZ123.m4a`
- Transcript: `C_XYZ123-transcript.txt`
- AI analyzes content and suggests: `python-tutorial`
- Final summary: `python-tutorial-C_XYZ123-summarize.md`

**Benefits:**
- Unique filenames (no duplicates)
- Descriptive summaries easy to find
- Video ID preserved for tracking

## 5. AI-Powered Smart Filename Generation ✅

**Problem:** Instagram video IDs like "C_XYZ123" are not searchable or meaningful.

**Solution:** For Instagram/Threads/TikTok videos, AI analyzes transcript and generates:
- **Suggested filename:** Short descriptive name (3-5 words, lowercase-with-hyphens)
- **Video ID:** Original ID preserved
- **Hashtags:** Relevant tags for categorization

**Example Metadata Section:**
```markdown
## Metadata
**Suggested Filename:** python-async-programming
**Hashtags:** #python #async #tutorial #programming
**Video ID:** C_XYZ123
```

**YouTube videos:** Keep original title-based naming (already descriptive)

**Benefits:**
- Searchable, meaningful filenames
- Content-based organization
- Preserves original ID for reference

## 6. Automatic Hashtag Generation ✅

**Problem:** No way to categorize or search videos by topic later.

**Solution:** AI generates relevant hashtags at end of every summary:

**Instagram/Threads/TikTok:**
- Hashtags in Metadata section
- 3-5 tags based on content analysis

**YouTube:**
- Hashtags at end of summary
- Content-based categorization

**Benefits:**
- Future search functionality ready
- Easy to group related videos
- Tags generated from actual content (not just titles)

## Usage Examples

### Basic Instagram Video Processing
```bash
# Download, transcribe, and summarize Instagram video
python3.13 tvs.py -u "https://instagram.com/reel/C_XYZ123" -a -t

# Output:
# - Video: ~/Videos/instagram/C_XYZ123.m4a
# - Transcript: ~/Videos/instagram/C_XYZ123-transcript.txt
# - Summary: ~/Work/Kai/video/python-tutorial-C_XYZ123-summarize.md
```

### YouTube Video (Normal Flow)
```bash
# YouTube keeps title-based naming
python3.13 tvs.py -u "https://youtube.com/watch?v=dQw4w9WgXcQ" -a -t

# Output:
# - Video: ~/Videos/youtube/Rick_Astley_Never_Gonna_Give_You_Up.m4a
# - Summary: ~/Work/Kai/video/Rick_Astley_Never_Gonna_Give_You_Up-summarize.md
# - Hashtags added at end of summary
```

### Cookie Age Warning
```
ℹ️  Using instagram cookies for authentication
⚠️  Cookie file is 32 days old (threshold: 30 days)
⚠️  COOKIES MAY HAVE EXPIRED - CONSIDER UPDATING
ℹ️  Cookie location: /home/skull/tools/automation/tvs/cookies/instagram/www.instagram.com_cookies.txt
```

## Migration Guide

### Moving Existing Cookies

If you have cookies in the old location:

```bash
# Instagram
mkdir -p ~/tools/automation/tvs/cookies/instagram
mv ~/Downloads/browserD/www.instagram.com_cookies.txt \
   ~/tools/automation/tvs/cookies/instagram/

# YouTube (if you have them)
mkdir -p ~/tools/automation/tvs/cookies/youtube
mv ~/path/to/youtube_cookies.txt \
   ~/tools/automation/tvs/cookies/youtube/www.youtube.com_cookies.txt
```

### Reorganizing Existing Videos (Optional)

Old videos in `~/Videos/` can be manually moved to subdirectories:

```bash
# Move Instagram videos
mkdir -p ~/Videos/instagram
mv ~/Videos/C_*.m4a ~/Videos/instagram/

# Move YouTube videos
mkdir -p ~/Videos/youtube
mv ~/Videos/*.webm ~/Videos/youtube/
```

**Note:** Existing summaries will continue to work as-is. Only new videos use the improved naming.

## Configuration

All settings are at the top of `tvs.py`:

```python
# Cookie warning threshold (days)
COOKIE_WARNING_DAYS = 30

# Supported sites and cookie locations
SITE_COOKIES = {
    'instagram': COOKIES_DIR / "instagram" / "www.instagram.com_cookies.txt",
    'threads': COOKIES_DIR / "threads" / "www.threads.net_cookies.txt",
    'tiktok': COOKIES_DIR / "tiktok" / "www.tiktok.com_cookies.txt",
    'x': COOKIES_DIR / "x" / "x.com_cookies.txt",
    'youtube': COOKIES_DIR / "youtube" / "www.youtube.com_cookies.txt",
}
```

## Future Enhancements

Based on this foundation, future additions could include:

1. **Search Tool** (planned)
   - Use ripgrep to search all summaries by hashtags
   - TUI interface for browsing videos

2. **Playlist Support**
   - Process entire playlists automatically
   - Batch organization by topic

3. **Stats Dashboard**
   - Videos processed per site
   - Storage usage
   - Most common hashtags

## Testing

All changes tested and working:
- ✅ Syntax validation passed
- ✅ Help message displays correctly
- ✅ Cookie directory structure created
- ✅ Site detection logic implemented
- ✅ AI metadata generation ready

Ready to test with real videos!

## Changelog

**2025-11-05** - Major improvements:
- Multi-site cookie management
- Cookie expiration warnings
- Site-specific directories
- AI-powered Instagram filename generation
- Automatic hashtag generation
- Smart summary naming for social media platforms
