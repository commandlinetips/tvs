#!/usr/bin/env python3.13
"""
TVS - Text-Video-Summarizer
A standalone tool for downloading, transcribing, and summarizing videos.

Usage:
    python3.13 tvs.py -u <URL>
    python3.13 tvs.py --url <URL>

Example:
    python3.13 tvs.py -u https://youtube.com/watch?v=dQw4w9WgXcQ
"""

import argparse
import subprocess
import sys
import os
import time
import logging
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()

# Directories
VIDEOS_DIR = Path.home() / "Videos"
WORK_DIR = Path.home() / "Work" / "Kai" / "video"
DOWNLOAD_ARCHIVE = VIDEOS_DIR / ".yt-dlp-archive.txt"
LOG_DIR = SCRIPT_DIR / "logs"

# Vibe configuration
VIBE_MODEL = Path.home() / ".local/share/github.com.thewh1teagle.vibe/ggml-large-v3-turbo.bin"

# Cookies directory structure (organized by site)
COOKIES_DIR = SCRIPT_DIR / "cookies"
SITE_COOKIES = {
    'instagram': COOKIES_DIR / "instagram" / "www.instagram.com_cookies.txt",
    'threads': COOKIES_DIR / "threads" / "www.threads.net_cookies.txt",
    'tiktok': COOKIES_DIR / "tiktok" / "www.tiktok.com_cookies.txt",
    'x': COOKIES_DIR / "x" / "x.com_cookies.txt",
    'youtube': COOKIES_DIR / "youtube" / "www.youtube.com_cookies.txt",
}

# Cookie expiration warning threshold (days)
COOKIE_WARNING_DAYS = 30

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def setup_logging():
    """
    Set up dual logging system:
    1. Debug log - Complete tool execution (all operations, errors, debug info)
    2. Processed files log - Clean history of successfully processed files
    """
    # Create logs directory
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Generate log filenames with format: debug-DD-M-YYYY.log and processed-DD-M-YYYY.log
    now = datetime.now()
    date_suffix = f"{now.day}-{now.month}-{now.year}"
    debug_log_file = LOG_DIR / f"debug-{date_suffix}.log"
    processed_log_file = LOG_DIR / f"processed-{date_suffix}.log"

    # Clear any existing handlers
    logger = logging.getLogger()
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)

    # 1. DEBUG LOG - Verbose logging of all operations
    debug_handler = logging.FileHandler(debug_log_file, mode='a', encoding='utf-8')
    debug_handler.setLevel(logging.DEBUG)
    debug_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    debug_handler.setFormatter(debug_formatter)
    logger.addHandler(debug_handler)

    # 2. PROCESSED FILES LOG - Clean summary handler (only for file processing results)
    # We'll use this separately via a custom logger
    processed_handler = logging.FileHandler(processed_log_file, mode='a', encoding='utf-8')
    processed_handler.setLevel(logging.INFO)
    processed_formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    processed_handler.setFormatter(processed_formatter)

    # Create separate logger for processed files
    processed_logger = logging.getLogger('processed')
    processed_logger.handlers.clear()
    processed_logger.setLevel(logging.INFO)
    processed_logger.addHandler(processed_handler)
    processed_logger.propagate = False  # Don't propagate to root logger

    # Log session start in both logs
    logging.info("="*60)
    logging.info("TVS SESSION STARTED")
    logging.info("="*60)

    processed_logger.info("="*60)
    processed_logger.info("SESSION START")
    processed_logger.info("="*60)

    return debug_log_file, processed_log_file

def detect_site(url):
    """
    Detect which site a URL is from.

    Args:
        url: Video URL

    Returns:
        str: Site name ('instagram', 'youtube', 'tiktok', 'threads', 'x', or 'other')
    """
    url_lower = url.lower()

    if 'instagram.com' in url_lower:
        return 'instagram'
    elif 'threads.net' in url_lower or 'threads.com' in url_lower:
        return 'threads'
    elif 'tiktok.com' in url_lower:
        return 'tiktok'
    elif 'x.com' in url_lower or 'twitter.com' in url_lower:
        return 'x'
    elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    else:
        return 'other'

def get_site_output_dir(site):
    """
    Get the output directory for a specific site.

    Args:
        site: Site name

    Returns:
        Path: Site-specific subdirectory in VIDEOS_DIR
    """
    site_dir = VIDEOS_DIR / site
    site_dir.mkdir(parents=True, exist_ok=True)
    return site_dir

def check_cookie_age(cookie_file):
    """
    Check if cookie file is older than warning threshold.

    Args:
        cookie_file: Path to cookie file

    Returns:
        tuple: (age_in_days, is_expired_warning)
    """
    if not cookie_file.exists():
        return None, False

    file_time = cookie_file.stat().st_mtime
    age_seconds = time.time() - file_time
    age_days = age_seconds / (24 * 3600)

    is_old = age_days >= COOKIE_WARNING_DAYS

    return int(age_days), is_old

def print_header(text):
    """Print colored header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n", flush=True)

def print_step(step_num, text):
    """Print step number and description."""
    print(f"{Colors.OKBLUE}{Colors.BOLD}[Step {step_num}]{Colors.ENDC} {text}", flush=True)

def print_success(text):
    """Print success message."""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}", flush=True)

def print_error(text):
    """Print error message."""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}", flush=True)

def print_warning(text):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}", flush=True)

def print_info(text):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}", flush=True)

def run_command(cmd, cwd=None, timeout=600, env=None):
    """
    Run shell command and return output.

    Args:
        cmd: Command as list or string
        cwd: Working directory
        timeout: Timeout in seconds
        env: Optional environment dict (defaults to current environment)

    Returns:
        tuple: (success, stdout, stderr)
    """
    try:
        if isinstance(cmd, str):
            cmd = cmd.split()

        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=env
        )

        success = result.returncode == 0
        return success, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_environment(download_only=False):
    """Validate that all required tools and paths exist."""
    print_step(0, "Validating environment...")
    logging.info("Starting environment validation")

    errors = []

    # Check yt-dlp
    logging.debug("Checking for yt-dlp...")
    success, _, _ = run_command("yt-dlp --version")
    if not success:
        errors.append("yt-dlp not found. Install with: sudo pacman -S yt-dlp")
        logging.error("yt-dlp not found")
    else:
        print_success("yt-dlp found")
        logging.info("yt-dlp found")

    # Check vibe (skip if download-only mode)
    if not download_only:
        logging.debug("Checking for vibe...")
        success, _, _ = run_command("which vibe")
        if not success:
            errors.append("vibe not found. Install with: yay -S vibe-bin")
            logging.error("vibe not found")
        else:
            print_success("vibe found")
            logging.info("vibe found")

    # Check mediainfo (optional but recommended)
    logging.debug("Checking for mediainfo...")
    success, _, _ = run_command("mediainfo --version")
    if not success:
        print_warning("mediainfo not found (optional). Install with: sudo pacman -S mediainfo")
        print_info("Without mediainfo, timeout estimation for long videos may be inaccurate")
        logging.warning("mediainfo not found (optional)")
    else:
        print_success("mediainfo found")
        logging.info("mediainfo found")

    # Check vibe model (skip if download-only mode)
    if not download_only:
        logging.debug(f"Checking for vibe model at {VIBE_MODEL}...")
        if not VIBE_MODEL.exists():
            errors.append(f"Vibe model not found at: {VIBE_MODEL}")
            errors.append("Run vibe GUI once to download the model")
            logging.error(f"Vibe model not found at {VIBE_MODEL}")
        else:
            model_size = VIBE_MODEL.stat().st_size / (1024**3)  # GB
            print_success(f"Vibe model found ({model_size:.1f} GB)")
            logging.info(f"Vibe model found ({model_size:.1f} GB) at {VIBE_MODEL}")

    # Check directories
    logging.debug(f"Creating directories: {VIDEOS_DIR}, {WORK_DIR}")
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    print_success(f"Videos directory: {VIDEOS_DIR}")
    logging.info(f"Videos directory: {VIDEOS_DIR}")

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    print_success(f"Work directory: {WORK_DIR}")
    logging.info(f"Work directory: {WORK_DIR}")

    if errors:
        print_error("Environment validation failed:")
        for error in errors:
            print(f"  • {error}")
            logging.error(f"Validation error: {error}")
        logging.error("Environment validation FAILED")
        return False

    print_success("Environment validation passed")
    logging.info("Environment validation PASSED")
    return True

# ============================================================================
# MAIN PROCESSING FUNCTIONS
# ============================================================================

def download_video(url, audio_only=False):
    """
    Download video from URL using yt-dlp.

    Args:
        url: Video URL
        audio_only: If True, download only audio (much smaller)

    Returns:
        tuple: (Path to video file or None, bool indicating if already existed, site name)
    """
    logging.info(f"[DOWNLOAD] Starting download - URL: {url}, audio_only: {audio_only}")

    if audio_only:
        print_step(1, "Downloading audio only...")
        print_info("Mode: Audio-only (faster, smaller file)")
    else:
        print_step(1, "Downloading video...")

    print_info(f"URL: {url}")

    # Detect site and get site-specific directory
    site = detect_site(url)
    print_info(f"Detected site: {site}")
    logging.debug(f"[DOWNLOAD] Detected site: {site}")

    site_dir = get_site_output_dir(site)
    print_info(f"Output directory: {site_dir}")

    # Get list of video/audio files before download
    video_extensions = {'.mp4', '.webm', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.m4v', '.m4a', '.opus'}
    videos_before = {f.name for f in site_dir.glob("*") if f.suffix.lower() in video_extensions}

    # Determine filename pattern based on platform
    # Instagram/Threads/TikTok: use ID + description (if available)
    # YouTube: use title (more descriptive)
    if site in ['instagram', 'threads', 'tiktok']:
        # Try to get description/caption, fall back to ID
        filename_pattern = "%(id)s.%(ext)s"
    else:
        filename_pattern = "%(title)s.%(ext)s"

    # Check for site-specific cookies file
    use_cookies = False
    cookie_file = SITE_COOKIES.get(site)

    if cookie_file and cookie_file.exists():
        use_cookies = True
        print_info(f"Using {site} cookies for authentication")

        # Check cookie age and warn if old
        age_days, is_old = check_cookie_age(cookie_file)
        if is_old:
            print_warning(f"Cookie file is {age_days} days old (threshold: {COOKIE_WARNING_DAYS} days)")
            print_warning(f"⚠️  {Colors.FAIL}COOKIES MAY HAVE EXPIRED - CONSIDER UPDATING{Colors.ENDC}")
            print_info(f"Cookie location: {cookie_file}")
        else:
            print_info(f"Cookie age: {age_days} days (OK)")

    if audio_only:
        # Download only audio (much smaller, faster)
        cmd = [
            "yt-dlp",
            "--restrict-filenames",
            "--download-archive", str(DOWNLOAD_ARCHIVE),
            "-f", "bestaudio/best",  # Audio only
            "-x",  # Extract audio
            "--audio-format", "best",  # Keep best audio format
            "-o", filename_pattern,
        ]
        if site == 'youtube':
            # Android client bypasses SABR streaming / 403 errors
            cmd.extend(["--extractor-args", "youtube:player_client=android,web"])
        if use_cookies:
            cmd.extend(["--cookies", str(cookie_file)])
        cmd.append(url)
    else:
        # Download video with 480p max quality
        cmd = [
            "yt-dlp",
            "--restrict-filenames",
            "--download-archive", str(DOWNLOAD_ARCHIVE),
            "-f", "bestvideo[height<=480]+bestaudio/best[height<=480]/best",  # Max 480p to save space
            "-o", filename_pattern,
        ]
        if site == 'youtube':
            # Android client bypasses SABR streaming / 403 errors
            cmd.extend(["--extractor-args", "youtube:player_client=android,web"])
        if use_cookies:
            cmd.extend(["--cookies", str(cookie_file)])
        cmd.append(url)

    start_time = time.time()
    logging.debug(f"[DOWNLOAD] Running yt-dlp with timeout=1200s")
    success, stdout, stderr = run_command(cmd, cwd=site_dir, timeout=1200)  # 20 min for large files
    elapsed = time.time() - start_time

    if not success:
        print_error("Download failed")
        print(f"Error: {stderr}")
        logging.error(f"[DOWNLOAD] Failed after {elapsed:.1f}s - Error: {stderr[:200]}")

        # Special error handling for unsupported sites
        if site == 'threads' and 'Unsupported URL' in stderr:
            print_warning("Threads is not yet supported by yt-dlp")
            print_info("Threads support is in development. Check yt-dlp updates: yt-dlp -U")
            print_info("Alternative: Download manually and use the transcript/summary features")
            logging.warning(f"[DOWNLOAD] Unsupported site: {site}")

        return None, False, site

    # Find the most recently created VIDEO file in site directory
    try:
        video_files = [f for f in site_dir.glob("*") if f.suffix.lower() in video_extensions]

        if not video_files:
            print_error("No video files found after download")
            return None, False, site

        # Sort by modification time and get the most recent
        video_file = sorted(video_files, key=lambda p: p.stat().st_mtime, reverse=True)[0]
        file_size = video_file.stat().st_size / (1024**2)  # MB

        # Check if file already existed
        already_existed = video_file.name in videos_before

        if already_existed:
            print_warning(f"Video already exists: {video_file.name}")
            print_info("Skipping download (file already present)")
            logging.info(f"[DOWNLOAD] Skipped (already exists): {video_file.resolve()}")
        else:
            print_success(f"Downloaded: {video_file.name}")
            print_info(f"Time: {elapsed:.1f}s")
            logging.info(f"[DOWNLOAD] Success in {elapsed:.1f}s: {video_file.resolve()} ({file_size:.1f} MB)")

        print_info(f"Size: {file_size:.1f} MB")

        return video_file, already_existed, site

    except Exception as e:
        print_error(f"Error finding downloaded file: {e}")
        logging.error(f"[DOWNLOAD] Exception: {e}")
        return None, False, site

def get_video_duration(video_file):
    """
    Get video duration in minutes using mediainfo.

    Args:
        video_file: Path to video file

    Returns:
        int: Duration in minutes, or None if unable to determine
    """
    try:
        # Check if mediainfo is available
        success, _, _ = run_command("mediainfo --version")
        if not success:
            return None

        # Get duration string from mediainfo
        cmd = ["mediainfo", "--Inform=General;%Duration/String%", str(video_file)]
        success, stdout, stderr = run_command(cmd, timeout=10)

        if not success or not stdout.strip():
            return None

        duration_str = stdout.strip()

        # Parse duration string (examples: "43 min 50 s", "1 h 23 min", "2 min 15 s", "55 s 915 ms")
        total_minutes = 0

        # Extract hours
        if 'h' in duration_str:
            hours_part = duration_str.split('h')[0].strip()
            try:
                total_minutes += int(hours_part.split()[-1]) * 60
            except (ValueError, IndexError):
                pass

        # Extract minutes
        if 'min' in duration_str:
            # Get the part with minutes
            if 'h' in duration_str:
                min_part = duration_str.split('h')[1].split('min')[0].strip()
            else:
                min_part = duration_str.split('min')[0].strip()
            try:
                total_minutes += int(min_part.split()[-1])
            except (ValueError, IndexError):
                pass

        # Handle seconds-only videos (e.g., "55 s 915 ms")
        # If no hours or minutes found, check for seconds and round up to 1 minute
        if total_minutes == 0 and 's' in duration_str and 'min' not in duration_str:
            try:
                # Extract seconds (before " s")
                seconds_part = duration_str.split('s')[0].strip()
                seconds = int(seconds_part.split()[-1])
                # Round up to at least 1 minute for short videos
                total_minutes = max(1, (seconds + 59) // 60)  # Round up
            except (ValueError, IndexError):
                pass

        return total_minutes if total_minutes > 0 else None

    except Exception as e:
        print_warning(f"Could not determine video duration: {e}")
        return None

def transcribe_video(video_file, force=False):
    """
    Transcribe video using vibe.

    Args:
        video_file: Path to video file
        force: Force re-transcription even if transcript exists

    Returns:
        Path: Path to transcript file, or None on error
    """
    logging.info(f"[TRANSCRIBE] Starting transcription - Video: {video_file.resolve()}, force: {force}")

    print_step(2, "Transcribing video...")
    print_info(f"Video: {video_file.name}")
    print_info(f"Location: {video_file.parent}")

    # Create transcript filename
    transcript_file = video_file.parent / f"{video_file.stem}-transcript.txt"

    # Check if transcript already exists
    if transcript_file.exists() and not force:
        print_warning(f"Transcript already exists: {transcript_file.name}")
        print_info("Skipping transcription (file already present)")

        # Get transcript info
        transcript_size = transcript_file.stat().st_size
        with open(transcript_file, 'r') as f:
            transcript_text = f.read()
            word_count = len(transcript_text.split())

        print_info(f"Size: {transcript_size} bytes")
        print_info(f"Words: {word_count}")
        logging.info(f"[TRANSCRIBE] Skipped (already exists): {transcript_file.resolve()} ({word_count} words)")

        return transcript_file

    # Get video duration to calculate appropriate timeout
    duration_minutes = get_video_duration(video_file)

    # Calculate dynamic timeout based on duration
    if duration_minutes:
        print_info(f"Duration: {duration_minutes} minutes")

        # Calculate timeout: base rule is ~2x duration + buffer
        if duration_minutes < 30:
            timeout = 1200  # 20 minutes
        elif duration_minutes < 60:
            timeout = 2400  # 40 minutes
        elif duration_minutes < 120:
            timeout = 4800  # 80 minutes
        else:
            timeout = 7200  # 2 hours
            print_warning(f"Long video detected ({duration_minutes} min). This may take a while...")

        print_info(f"Transcription timeout: {timeout//60} minutes")
    else:
        # Fallback to default timeout if duration unknown
        timeout = 2400  # 40 minutes default
        print_warning("Could not determine video duration, using default timeout")

    # ⚠️ CRITICAL: Use vibe ONLY - NO ffmpeg or other tools
    cmd = [
        "vibe",
        "--model", str(VIBE_MODEL),
        "--file", video_file.name,
        "--write", transcript_file.name,
        "--format", "txt",
        "--language", "auto"
    ]

    print_info("Using Whisper Large V3 Turbo model...")
    logging.debug(f"[TRANSCRIBE] Running vibe with timeout={timeout}s")

    # vibe is a GTK app and needs DISPLAY even in CLI mode.
    # Always set DISPLAY=:0 if not already set — without it vibe fails with
    # "Gtk-WARNING: cannot open display" even when called from the terminal.
    vibe_env = os.environ.copy()
    if not vibe_env.get('DISPLAY'):
        vibe_env['DISPLAY'] = ':0'
        logging.debug("[TRANSCRIBE] DISPLAY not set — forcing DISPLAY=:0 for vibe")

    start_time = time.time()
    success, stdout, stderr = run_command(cmd, cwd=video_file.parent, timeout=timeout, env=vibe_env)
    elapsed = time.time() - start_time

    if not success:
        print_error("Transcription failed")
        print(f"Error: {stderr}")
        logging.error(f"[TRANSCRIBE] Failed after {elapsed:.1f}s - Error: {stderr[:200]}")
        print_warning("Troubleshooting:")
        print("  1. Verify model exists:")
        print(f"     ls -lh {VIBE_MODEL}")
        print("  2. Check video has audio:")
        print(f"     ffprobe -v error -select_streams a:0 -show_entries stream=codec_name {video_file}")
        print("  3. Try running vibe GUI first")
        return None

    if not transcript_file.exists():
        print_error("Transcript file not created")
        logging.error(f"[TRANSCRIBE] Transcript file not created: {transcript_file}")
        return None

    # Get transcript info
    transcript_size = transcript_file.stat().st_size
    with open(transcript_file, 'r') as f:
        transcript_text = f.read()
        word_count = len(transcript_text.split())

    print_success(f"Transcribed: {transcript_file.name}")
    print_info(f"Size: {transcript_size} bytes")
    print_info(f"Words: {word_count}")
    print_info(f"Time: {elapsed:.1f}s")
    logging.info(f"[TRANSCRIBE] Success in {elapsed:.1f}s: {transcript_file.resolve()} ({word_count} words)")

    return transcript_file

def copy_transcript(transcript_file):
    """
    Copy transcript to work directory.

    Args:
        transcript_file: Path to transcript file

    Returns:
        Path: Path to copied transcript, or None on error
    """
    logging.info(f"[COPY] Copying transcript to work directory")
    print_step(3, "Copying transcript...")

    dest_file = WORK_DIR / transcript_file.name

    try:
        import shutil
        shutil.copy2(transcript_file, dest_file)

        print_success(f"Copied to: {dest_file}")
        logging.info(f"[COPY] Success: {dest_file.resolve()}")
        return dest_file

    except Exception as e:
        print_error(f"Copy failed: {e}")
        logging.error(f"[COPY] Failed: {e}")
        return None

def generate_summary(transcript_file, video_file, site='other'):
    """
    Generate summary from transcript using OpenCode agent.

    Args:
        transcript_file: Path to transcript file
        video_file: Path to original video file
        site: Site name (for Instagram, adds smart naming + hashtags)

    Returns:
        Path: Path to summary file, or None on error
    """
    logging.info(f"[SUMMARY] Starting AI summary generation for: {video_file.stem}")
    print_step(4, "Generating summary with AI analysis...")
    print_info("Using OpenCode transcript-analyzer agent...")

    # Read transcript to get word count for context
    try:
        with open(transcript_file, 'r') as f:
            transcript_text = f.read().strip()
        word_count = len(transcript_text.split())
    except Exception as e:
        print_error(f"Failed to read transcript: {e}")
        return None

    if not transcript_text:
        print_error("Transcript is empty")
        return None

    # Expected summary file location (initial)
    summary_file = WORK_DIR / f"{video_file.stem}-summarize.md"

    # Check if summary already exists (skip regeneration)
    if summary_file.exists():
        file_size = summary_file.stat().st_size
        if file_size > 100:  # At least 100 bytes (not empty)
            print_success(f"Summary already exists: {summary_file.name}")
            print_info(f"Size: {file_size} bytes")
            print_info("Skipping summary generation (use -f flag to force regenerate)")
            logging.info(f"[SUMMARY] Skipped (already exists): {summary_file.resolve()}")
            return summary_file

    # Build prompt for OpenCode agent with special handling for Instagram
    if site in ['instagram', 'threads', 'tiktok']:
        # For social media with ID-based filenames, ask AI to generate smart title
        prompt = f"""Analyze the video transcript and generate a comprehensive summary.

Video ID: {video_file.stem}
Video source: {site}
Transcript location: {transcript_file}
Output location: {summary_file}
Transcript contains: {word_count} words

IMPORTANT INSTRUCTIONS:
1. Read the transcript file and analyze the content
2. Create a comprehensive summary following your configured structure
3. At the END of the summary, add a section called "## Metadata" with:
   - Suggested filename: Create a SHORT descriptive filename (MAX 3-4 words, lowercase-with-hyphens) based on the main topic
   - Keep it concise and memorable (e.g., "python-tutorial", "ai-basics", "unix-history")
   - Hashtags: Generate 3-5 relevant hashtags for categorization (e.g., #ai #tutorial #productivity)
   - Video ID: {video_file.stem}

Format the metadata section exactly like this:
```
## Metadata
**Suggested Filename:** short-topic-name
**Hashtags:** #tag1 #tag2 #tag3
**Video ID:** {video_file.stem}
```

CRITICAL: Filename MUST be 3-4 words maximum, all lowercase, separated by hyphens only.

Save the summary to the specified output location."""
    else:
        # For YouTube, use regular summary (title is already good)
        prompt = f"""Analyze the video transcript and generate a comprehensive summary.

Video filename: {video_file.stem.replace('_', ' ')}
Transcript location: {transcript_file}
Output location: {summary_file}
Transcript contains: {word_count} words

Read the transcript file, perform deep analysis following your configured structure, and save the summary to the specified output location.

At the END of the summary, add relevant hashtags for categorization (3-5 hashtags based on the content, e.g., #python #webdev #tutorial)."""

    # Execute OpenCode agent
    cmd = [
        "opencode", "run",
        "--agent", "transcript-analyzer",
        prompt  # Positional argument, not --prompt
    ]

    print_info("Running AI analysis (this may take 30-60 seconds)...")
    logging.debug(f"[SUMMARY] Running OpenCode agent with timeout=600s")
    start_time = time.time()
    success, stdout, stderr = run_command(cmd, cwd=WORK_DIR, timeout=600)  # 10 min timeout
    elapsed = time.time() - start_time

    if not success:
        print_error("Failed to generate summary with OpenCode agent")
        if stderr:
            print_error(f"Error: {stderr[:500]}")  # Show first 500 chars
        logging.error(f"[SUMMARY] Failed after {elapsed:.1f}s - Error: {stderr[:200]}")
        return None

    # Verify summary file was created
    if not summary_file.exists():
        print_error(f"Summary file not created: {summary_file}")
        logging.error(f"[SUMMARY] Summary file not created: {summary_file}")
        return None

    summary_size = summary_file.stat().st_size / 1024  # KB
    print_success(f"Summary created: {summary_file.name}")
    print_info(f"Size: {summary_size:.1f} KB")
    logging.info(f"[SUMMARY] Success in {elapsed:.1f}s: {summary_file.resolve()} ({summary_size:.1f} KB)")

    # For Instagram/social media, optionally rename based on AI suggestion
    if site in ['instagram', 'threads', 'tiktok']:
        try:
            with open(summary_file, 'r') as f:
                summary_content = f.read()

            # Look for suggested filename in metadata section
            import re
            filename_match = re.search(r'\*\*Suggested Filename:\*\*\s*([a-z0-9][a-z0-9-]*[a-z0-9])', summary_content, re.IGNORECASE)

            if filename_match:
                suggested_name = filename_match.group(1).lower().strip()

                # Validate: limit to 4 words (3 hyphens max)
                word_count = suggested_name.count('-') + 1
                if word_count > 4:
                    # Truncate to first 4 words
                    parts = suggested_name.split('-')
                    suggested_name = '-'.join(parts[:4])
                    print_warning(f"Truncated long filename to: {suggested_name}")

                # Validate: max 50 characters total
                if len(suggested_name) > 50:
                    suggested_name = suggested_name[:50].rstrip('-')
                    print_warning(f"Truncated filename to 50 chars: {suggested_name}")

                new_summary_file = WORK_DIR / f"{suggested_name}-{video_file.stem}-summarize.md"

                # Rename if the suggestion is different
                if new_summary_file != summary_file:
                    summary_file.rename(new_summary_file)
                    print_success(f"Renamed summary: {new_summary_file.name}")
                    print_info(f"AI-generated filename based on content")
                    summary_file = new_summary_file
            else:
                print_warning("Could not extract suggested filename from AI response")
                print_info("Keeping original filename")
        except Exception as e:
            print_warning(f"Could not rename based on AI suggestion: {e}")
            print_info("Keeping original filename")

    return summary_file

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def get_playlist_urls(playlist_url, playlist_items=None):
    """
    Extract individual video URLs from a YouTube playlist or channel.

    Args:
        playlist_url: YouTube playlist or channel URL
        playlist_items: Optional item range/selection string (e.g. '1-10', '1,3,5')

    Returns:
        list: List of video URLs, or empty list on failure
    """
    logging.info(f"[PLAYLIST] Fetching URLs from: {playlist_url}")
    print_step(0, "Fetching playlist URLs...")
    print_info(f"Playlist: {playlist_url}")

    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "url",
        "--no-warnings",
        "--extractor-args", "youtube:player_client=android,web",
    ]

    if playlist_items:
        cmd.extend(["--playlist-items", playlist_items])
        print_info(f"Selecting items: {playlist_items}")

    # Use YouTube cookies if available
    cookie_file = SITE_COOKIES.get('youtube')
    if cookie_file and cookie_file.exists():
        cmd.extend(["--cookies", str(cookie_file)])
        age_days, is_old = check_cookie_age(cookie_file)
        if is_old:
            print_warning(f"YouTube cookie file is {age_days} days old — consider updating")

    cmd.append(playlist_url)

    logging.debug(f"[PLAYLIST] Running yt-dlp flat-playlist with timeout=120s")
    success, stdout, stderr = run_command(cmd, timeout=120)

    if not success:
        print_error(f"Failed to fetch playlist")
        print(f"Error: {stderr[:300]}")
        logging.error(f"[PLAYLIST] Failed: {stderr[:200]}")
        return []

    urls = [line.strip() for line in stdout.splitlines()
            if line.strip() and line.strip().startswith('http')]

    if not urls:
        print_error("No video URLs found in playlist")
        logging.error("[PLAYLIST] No URLs extracted from playlist output")
        return []

    print_success(f"Found {len(urls)} video(s) in playlist")
    logging.info(f"[PLAYLIST] Extracted {len(urls)} URLs")
    return urls


def process_single_video(url, audio_only=False, force=False, download_only=False):
    """
    Process a single video URL.

    Args:
        url: Video URL
        audio_only: Download audio only
        force: Force re-transcription even if transcript exists
        download_only: Download only, skip transcription and summary

    Returns:
        bool: Success status
    """
    overall_start = time.time()

    # Step 1: Download
    logging.info(f"Processing URL: {url}")
    video_file, already_existed, site = download_video(url, audio_only=audio_only)
    if not video_file:
        print_error("Failed to download video")
        logging.error(f"Download failed for: {url}")
        return False

    # If download-only mode, stop here
    if download_only:
        overall_elapsed = time.time() - overall_start
        print_header("Download Complete!")
        print_success("Video downloaded successfully (download-only mode)")
        print_info(f"Total time: {overall_elapsed:.1f}s")
        print(f"\n{Colors.BOLD}Output:{Colors.ENDC}")
        print(f"  📹 Video: {video_file}")

        # Log downloaded file
        logging.info(f"Downloaded (audio-only={audio_only}): {video_file.resolve()}")
        logging.info(f"Processing time: {overall_elapsed:.1f}s")

        return True

    # Step 2: Transcribe
    transcript_file = transcribe_video(video_file, force=force)
    if not transcript_file:
        print_error("Failed to transcribe video")
        return False

    # Step 3: Copy transcript
    transcript_copy = copy_transcript(transcript_file)
    if not transcript_copy:
        print_error("Failed to copy transcript")
        return False

    # Step 4: Generate summary (with site info for smart naming)
    summary_file = generate_summary(transcript_copy, video_file, site=site)
    if not summary_file:
        print_error("Failed to generate summary")
        return False

    # Success!
    overall_elapsed = time.time() - overall_start

    print_header("Processing Complete!")
    print_success("All steps completed successfully")
    print_info(f"Total time: {overall_elapsed:.1f}s")

    print(f"\n{Colors.BOLD}Output Files:{Colors.ENDC}")
    print(f"  📹 Video:      {video_file}")
    print(f"  📝 Transcript: {transcript_copy}")
    print(f"  📊 Summary:    {summary_file}")

    # Log all processed files with full paths (DEBUG LOG)
    logging.info(f"Processing completed successfully for: {url}")
    logging.info(f"  Video (audio-only={audio_only}): {video_file.resolve()}")
    logging.info(f"  Transcript: {transcript_copy.resolve()}")
    logging.info(f"  Summary: {summary_file.resolve()}")
    logging.info(f"  Total processing time: {overall_elapsed:.1f}s")
    logging.info("-" * 60)

    # Log to PROCESSED FILES LOG (clean file history)
    processed_logger = logging.getLogger('processed')
    processed_logger.info(f"URL: {url}")
    processed_logger.info(f"  📹 Video: {video_file.resolve()}")
    processed_logger.info(f"  📝 Transcript: {transcript_copy.resolve()}")
    processed_logger.info(f"  📊 Summary: {summary_file.resolve()}")
    processed_logger.info(f"  ⏱️  Time: {overall_elapsed:.1f}s")
    processed_logger.info("-" * 80)

    return True


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description=(
            "TVS - Text-Video-Summarizer\n"
            "Automatically downloads a video or audio from a URL, transcribes\n"
            "the speech using Whisper AI (via vibe), and generates a structured\n"
            "markdown summary using an OpenCode AI agent.\n\n"
            "Supported sites: YouTube, Instagram, TikTok, X/Twitter, Threads\n"
            "Output:  ~/Videos/<site>/<file>          — downloaded media\n"
            "         ~/Work/Kai/video/<file>-transcript.txt  — transcript\n"
            "         ~/Work/Kai/video/<file>-summarize.md    — AI summary"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Single video (recommended flags: -a for audio-only, -t for live output):
    python3.13 tvs.py -u "https://youtube.com/watch?v=dQw4w9WgXcQ" -a -t

  YouTube Shorts:
    python3.13 tvs.py -u "https://youtube.com/shorts/8YULk160fIw" -a -t

  Batch from file (one URL per line, # lines are comments):
    python3.13 tvs.py -l urls.txt -a -t

  Full playlist:
    python3.13 tvs.py -p "https://youtube.com/playlist?list=PLxxxxxx" -a -t

  Channel videos tab:
    python3.13 tvs.py -p "https://youtube.com/@channelname/videos" -a -t

  Playlist, first 10 videos only:
    python3.13 tvs.py -p "https://youtube.com/playlist?list=PLxxxxxx" --playlist-items 1-10 -a -t

  Download video file only, skip transcription and summary:
    python3.13 tvs.py -u "https://youtube.com/watch?v=dQw4w9WgXcQ" -d

  Force re-transcribe (overwrite existing transcript):
    python3.13 tvs.py -u "https://youtube.com/watch?v=dQw4w9WgXcQ" -a -t -f

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  yt-dlp     — video downloader       (sudo pacman -S yt-dlp)
  vibe       — Whisper transcription  (yay -S vibe-bin)
  opencode   — AI summary agent       (must have transcript-analyzer agent configured)
  model      — Whisper Large V3 Turbo (run vibe GUI once to download, ~1.5 GB)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
URL LIST FILE FORMAT  (used with -l/--list)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  https://youtube.com/watch?v=abc123
  # this line is a comment and will be skipped
  https://youtube.com/watch?v=def456

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLAYLIST ITEM SELECTION  (used with --playlist-items)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1-10       first 10 videos
  1,3,5      videos 1, 3 and 5 only
  2-5,8      videos 2 through 5, plus video 8
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-u', '--url',
        metavar='URL',
        help=(
            'Process a single video URL. Supports YouTube, YouTube Shorts, '
            'Instagram, TikTok, X/Twitter, and Threads. '
            'The full pipeline runs: download → transcribe → copy → summarize.'
        )
    )
    group.add_argument(
        '-l', '--list',
        metavar='FILE',
        help=(
            'Process multiple URLs from a text file (one URL per line). '
            'Blank lines and lines starting with # are ignored. '
            'Each video goes through the full pipeline. Failed videos are '
            'skipped and processing continues with the next URL.'
        )
    )
    group.add_argument(
        '-p', '--playlist',
        metavar='URL',
        help=(
            'Process all videos from a YouTube playlist or channel. '
            'Accepts playlist URLs (youtube.com/playlist?list=...) and '
            'channel URLs (youtube.com/@name/videos). '
            'Use --playlist-items to select a subset of videos.'
        )
    )

    parser.add_argument(
        '-a', '--audio-only',
        action='store_true',
        help=(
            'Download audio only instead of video. '
            'The file is ~10x smaller and downloads much faster. '
            'Transcription quality is identical since vibe only uses the audio track. '
            'Strongly recommended for all use cases.'
        )
    )

    parser.add_argument(
        '-t', '--terminal',
        action='store_true',
        help=(
            'Print output in real time (unbuffered). '
            'Without this flag, output may appear in large chunks due to Python buffering. '
            'Use this when running interactively so you can see live progress.'
        )
    )

    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help=(
            'Force re-transcription even if a transcript file already exists. '
            'By default TVS skips transcription when it detects an existing transcript '
            'to avoid wasting time. Use -f to overwrite it (e.g. after a failed or '
            'incomplete transcription run).'
        )
    )

    parser.add_argument(
        '-d', '--download-only',
        action='store_true',
        help=(
            'Download the media file and then stop — skip transcription and summary. '
            'Useful when you only need the raw video/audio file, or want to '
            'inspect the file before committing to the full pipeline.'
        )
    )

    parser.add_argument(
        '--playlist-items',
        metavar='ITEMS',
        help=(
            'Select specific videos from a playlist (only used with -p/--playlist). '
            'Accepts yt-dlp item syntax: a range ("1-10"), a comma-separated list '
            '("1,3,5"), or a combination ("2-5,8"). '
            'Item numbers are 1-based and follow playlist order.'
        )
    )

    args = parser.parse_args()

    # Enable unbuffered output if -t flag is used
    if args.terminal:
        # Reconfigure stdout to be unbuffered
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)

    # Setup logging
    debug_log, processed_log = setup_logging()

    # Print header
    print_header("TVS - Text-Video-Summarizer")
    print_info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Debug log: {debug_log}")
    print_info(f"Processed files log: {processed_log}")

    # Validate environment
    if not validate_environment(download_only=args.download_only):
        print_error("Environment validation failed. Please fix the issues above.")
        return 1

    # Determine processing mode
    if args.url:
        # Single video mode
        print_info("Mode: Single video")
        if args.audio_only:
            print_info("Quality: Audio-only (fast, small file)")
        else:
            print_info("Quality: 480p max (balanced)")

        success = process_single_video(args.url, audio_only=args.audio_only, force=args.force, download_only=args.download_only)

        if success:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✨ Summary is ready! ✨{Colors.ENDC}")
            logging.info("Session completed successfully")
            logging.info("="*60)
            return 0
        else:
            logging.error("Session failed")
            logging.info("="*60)
            return 1

    elif args.list:
        # Batch mode from file
        print_info(f"Mode: Batch processing from file")
        print_info(f"URL list: {args.list}")

        # Read URLs from file
        try:
            with open(args.list, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print_error(f"File not found: {args.list}")
            return 1
        except Exception as e:
            print_error(f"Error reading file: {e}")
            return 1

        # Parse URLs (skip blank lines and comments)
        urls = []
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            # Skip blank lines and comments
            if not line or line.startswith('#'):
                continue
            urls.append((line_num, line))

        if not urls:
            print_error("No URLs found in file")
            return 1

        print_info(f"Found {len(urls)} URL(s) to process")

        # Process each URL
        total_start = time.time()
        results = {'success': 0, 'failed': 0, 'skipped': 0}

        for idx, (line_num, url) in enumerate(urls, 1):
            print(f"\n{Colors.BOLD}{'─'*60}{Colors.ENDC}")
            print(f"{Colors.BOLD}Processing {idx}/{len(urls)} (line {line_num}){Colors.ENDC}")
            print(f"{Colors.BOLD}{'─'*60}{Colors.ENDC}\n")

            logging.info(f"Starting batch video {idx}/{len(urls)}: {url}")

            success = process_single_video(url, audio_only=args.audio_only, force=args.force, download_only=args.download_only)

            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
                logging.warning(f"Failed to process video {idx}/{len(urls)}: {url}")
                print_warning("Continuing with next video...")

        # Print batch summary
        total_elapsed = time.time() - total_start

        print_header("Batch Processing Complete!")
        print(f"\n{Colors.BOLD}Statistics:{Colors.ENDC}")
        print(f"  ✅ Successful: {Colors.OKGREEN}{results['success']}{Colors.ENDC}")
        print(f"  ❌ Failed:     {Colors.FAIL}{results['failed']}{Colors.ENDC}")
        print(f"  📊 Total:      {len(urls)}")
        print(f"  ⏱️  Time:       {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")

        if results['success'] > 0:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✨ {results['success']} video(s) processed successfully! ✨{Colors.ENDC}")

        # Log batch processing summary
        logging.info("="*60)
        logging.info("BATCH PROCESSING SUMMARY")
        logging.info(f"Total videos: {len(urls)}")
        logging.info(f"Successful: {results['success']}")
        logging.info(f"Failed: {results['failed']}")
        logging.info(f"Total time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
        logging.info("="*60)

        # Return 0 if at least one succeeded
        return 0 if results['success'] > 0 else 1

    elif args.playlist:
        # Playlist mode
        print_info("Mode: Playlist")
        print_info(f"Playlist URL: {args.playlist}")
        if args.playlist_items:
            print_info(f"Items: {args.playlist_items}")
        if args.audio_only:
            print_info("Quality: Audio-only (fast, small file)")
        else:
            print_info("Quality: 480p max (balanced)")

        # Fetch all URLs from the playlist
        urls = get_playlist_urls(args.playlist, playlist_items=args.playlist_items)
        if not urls:
            print_error("No videos found in playlist. Check the URL and try again.")
            logging.error(f"Playlist returned no URLs: {args.playlist}")
            return 1

        print_info(f"Processing {len(urls)} video(s) from playlist")
        logging.info(f"[PLAYLIST] Starting processing of {len(urls)} videos from: {args.playlist}")

        # Process each video (same logic as batch mode)
        total_start = time.time()
        results = {'success': 0, 'failed': 0}

        for idx, url in enumerate(urls, 1):
            print(f"\n{Colors.BOLD}{'─'*60}{Colors.ENDC}")
            print(f"{Colors.BOLD}Playlist video {idx}/{len(urls)}{Colors.ENDC}")
            print(f"{Colors.BOLD}{'─'*60}{Colors.ENDC}\n")

            logging.info(f"[PLAYLIST] Processing video {idx}/{len(urls)}: {url}")

            success = process_single_video(
                url,
                audio_only=args.audio_only,
                force=args.force,
                download_only=args.download_only
            )

            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
                logging.warning(f"[PLAYLIST] Failed video {idx}/{len(urls)}: {url}")
                print_warning("Continuing with next video...")

        total_elapsed = time.time() - total_start

        print_header("Playlist Processing Complete!")
        print(f"\n{Colors.BOLD}Statistics:{Colors.ENDC}")
        print(f"  ✅ Successful: {Colors.OKGREEN}{results['success']}{Colors.ENDC}")
        print(f"  ❌ Failed:     {Colors.FAIL}{results['failed']}{Colors.ENDC}")
        print(f"  📊 Total:      {len(urls)}")
        print(f"  ⏱️  Time:       {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")

        if results['success'] > 0:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✨ {results['success']} video(s) processed successfully! ✨{Colors.ENDC}")

        logging.info("="*60)
        logging.info("PLAYLIST PROCESSING SUMMARY")
        logging.info(f"Playlist: {args.playlist}")
        logging.info(f"Total videos: {len(urls)}")
        logging.info(f"Successful: {results['success']}")
        logging.info(f"Failed: {results['failed']}")
        logging.info(f"Total time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")
        logging.info("="*60)

        return 0 if results['success'] > 0 else 1

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  Interrupted by user{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
