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
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Directories
VIDEOS_DIR = Path.home() / "Videos"
WORK_DIR = Path.home() / "Work" / "Kai" / "video"

# Vibe configuration
VIBE_MODEL = Path.home() / ".local/share/github.com.thewh1teagle.vibe/ggml-large-v3-turbo.bin"

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

def run_command(cmd, cwd=None, timeout=600):
    """
    Run shell command and return output.

    Args:
        cmd: Command as list or string
        cwd: Working directory
        timeout: Timeout in seconds

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
            check=False
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

def validate_environment():
    """Validate that all required tools and paths exist."""
    print_step(0, "Validating environment...")

    errors = []

    # Check yt-dlp
    success, _, _ = run_command("yt-dlp --version")
    if not success:
        errors.append("yt-dlp not found. Install with: sudo pacman -S yt-dlp")
    else:
        print_success("yt-dlp found")

    # Check vibe
    success, _, _ = run_command("vibe --help")
    if not success:
        errors.append("vibe not found. Install with: yay -S vibe-bin")
    else:
        print_success("vibe found")

    # Check vibe model
    if not VIBE_MODEL.exists():
        errors.append(f"Vibe model not found at: {VIBE_MODEL}")
        errors.append("Run vibe GUI once to download the model")
    else:
        model_size = VIBE_MODEL.stat().st_size / (1024**3)  # GB
        print_success(f"Vibe model found ({model_size:.1f} GB)")

    # Check directories
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    print_success(f"Videos directory: {VIDEOS_DIR}")

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    print_success(f"Work directory: {WORK_DIR}")

    if errors:
        print_error("Environment validation failed:")
        for error in errors:
            print(f"  • {error}")
        return False

    print_success("Environment validation passed")
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
        tuple: (Path to video file or None, bool indicating if already existed)
    """
    if audio_only:
        print_step(1, "Downloading audio only...")
        print_info("Mode: Audio-only (faster, smaller file)")
    else:
        print_step(1, "Downloading video...")

    print_info(f"URL: {url}")

    # Get list of video/audio files before download
    video_extensions = {'.mp4', '.webm', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.m4v', '.m4a', '.opus'}
    videos_before = {f.name for f in VIDEOS_DIR.glob("*") if f.suffix.lower() in video_extensions}

    if audio_only:
        # Download only audio (much smaller, faster)
        cmd = [
            "yt-dlp",
            "--restrict-filenames",
            "-f", "bestaudio/best",  # Audio only
            "-x",  # Extract audio
            "--audio-format", "best",  # Keep best audio format
            "-o", "%(title)s.%(ext)s",
            url
        ]
    else:
        # Download video with 480p max quality
        cmd = [
            "yt-dlp",
            "--restrict-filenames",
            "-f", "bestvideo[height<=480]+bestaudio/best[height<=480]/best",  # Max 480p to save space
            "-o", "%(title)s.%(ext)s",
            url
        ]

    start_time = time.time()
    success, stdout, stderr = run_command(cmd, cwd=VIDEOS_DIR, timeout=1200)  # 20 min for large files
    elapsed = time.time() - start_time

    if not success:
        print_error("Download failed")
        print(f"Error: {stderr}")
        return None, False

    # Find the most recently created VIDEO file in Videos directory
    try:
        video_files = [f for f in VIDEOS_DIR.glob("*") if f.suffix.lower() in video_extensions]

        if not video_files:
            print_error("No video files found after download")
            return None, False

        # Sort by modification time and get the most recent
        video_file = sorted(video_files, key=lambda p: p.stat().st_mtime, reverse=True)[0]
        file_size = video_file.stat().st_size / (1024**2)  # MB

        # Check if file already existed
        already_existed = video_file.name in videos_before

        if already_existed:
            print_warning(f"Video already exists: {video_file.name}")
            print_info("Skipping download (file already present)")
        else:
            print_success(f"Downloaded: {video_file.name}")
            print_info(f"Time: {elapsed:.1f}s")

        print_info(f"Size: {file_size:.1f} MB")

        return video_file, already_existed

    except Exception as e:
        print_error(f"Error finding downloaded file: {e}")
        return None, False

def transcribe_video(video_file, force=False):
    """
    Transcribe video using vibe.

    Args:
        video_file: Path to video file
        force: Force re-transcription even if transcript exists

    Returns:
        Path: Path to transcript file, or None on error
    """
    print_step(2, "Transcribing video...")
    print_info(f"Video: {video_file.name}")

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

        return transcript_file

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

    start_time = time.time()
    success, stdout, stderr = run_command(cmd, cwd=VIDEOS_DIR, timeout=2400)  # 40 min for long videos
    elapsed = time.time() - start_time

    if not success:
        print_error("Transcription failed")
        print(f"Error: {stderr}")
        print_warning("Troubleshooting:")
        print("  1. Verify model exists:")
        print(f"     ls -lh {VIBE_MODEL}")
        print("  2. Check video has audio:")
        print(f"     ffprobe -v error -select_streams a:0 -show_entries stream=codec_name {video_file}")
        print("  3. Try running vibe GUI first")
        return None

    if not transcript_file.exists():
        print_error("Transcript file not created")
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

    return transcript_file

def copy_transcript(transcript_file):
    """
    Copy transcript to work directory.

    Args:
        transcript_file: Path to transcript file

    Returns:
        Path: Path to copied transcript, or None on error
    """
    print_step(3, "Copying transcript...")

    dest_file = WORK_DIR / transcript_file.name

    try:
        import shutil
        shutil.copy2(transcript_file, dest_file)

        print_success(f"Copied to: {dest_file}")
        return dest_file

    except Exception as e:
        print_error(f"Copy failed: {e}")
        return None

def generate_summary(transcript_file, video_file):
    """
    Generate summary from transcript using OpenCode agent.

    Args:
        transcript_file: Path to transcript file
        video_file: Path to original video file

    Returns:
        Path: Path to summary file, or None on error
    """
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

    # Expected summary file location
    summary_file = WORK_DIR / f"{video_file.stem}-summarize.md"

    # Build prompt for OpenCode agent
    prompt = f"""Analyze the video transcript and generate a comprehensive summary.

Video filename: {video_file.stem.replace('_', ' ')}
Transcript location: {transcript_file}
Output location: {summary_file}
Transcript contains: {word_count} words

Read the transcript file, perform deep analysis following your configured structure, and save the summary to the specified output location."""

    # Execute OpenCode agent
    cmd = [
        "opencode", "run",
        "--agent", "transcript-analyzer",
        prompt  # Positional argument, not --prompt
    ]

    print_info("Running AI analysis (this may take 30-60 seconds)...")
    success, stdout, stderr = run_command(cmd, cwd=WORK_DIR, timeout=600)  # 10 min timeout

    if not success:
        print_error("Failed to generate summary with OpenCode agent")
        if stderr:
            print_error(f"Error: {stderr[:500]}")  # Show first 500 chars
        return None

    # Verify summary file was created
    if not summary_file.exists():
        print_error(f"Summary file not created: {summary_file}")
        return None

    summary_size = summary_file.stat().st_size / 1024  # KB
    print_success(f"Summary created: {summary_file.name}")
    print_info(f"Size: {summary_size:.1f} KB")

    return summary_file

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def process_single_video(url, audio_only=False, force=False):
    """
    Process a single video URL.

    Args:
        url: Video URL
        audio_only: Download audio only
        force: Force re-transcription even if transcript exists

    Returns:
        bool: Success status
    """
    overall_start = time.time()

    # Step 1: Download
    video_file, already_existed = download_video(url, audio_only=audio_only)
    if not video_file:
        print_error("Failed to download video")
        return False

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

    # Step 4: Generate summary
    summary_file = generate_summary(transcript_copy, video_file)
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

    return True


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="TVS - Text-Video-Summarizer: Download, transcribe, and summarize videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single video
  python3.13 tvs.py -u https://youtube.com/watch?v=dQw4w9WgXcQ
  python3.13 tvs.py --url https://youtube.com/shorts/8YULk160fIw

  # Batch processing from file
  python3.13 tvs.py --list urls.txt

Notes:
  - Requires: yt-dlp, vibe
  - Vibe model must be downloaded (run vibe GUI once)
  - Videos saved to: ~/Videos/
  - Transcripts/summaries saved to: ~/Work/Kai/video/
  - URL list file format: one URL per line, blank lines and # comments ignored
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '-u', '--url',
        help='Single video URL (YouTube, etc.)'
    )
    group.add_argument(
        '-l', '--list',
        help='Text file containing list of URLs (one per line)'
    )

    parser.add_argument(
        '-a', '--audio-only',
        action='store_true',
        help='Download audio only (smaller file size, faster download)'
    )

    parser.add_argument(
        '-t', '--terminal',
        action='store_true',
        help='Show live output in terminal (no buffering, real-time updates)'
    )

    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Force re-transcription even if transcript already exists'
    )

    args = parser.parse_args()

    # Enable unbuffered output if -t flag is used
    if args.terminal:
        # Reconfigure stdout to be unbuffered
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)

    # Print header
    print_header("TVS - Text-Video-Summarizer")
    print_info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Validate environment
    if not validate_environment():
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

        success = process_single_video(args.url, audio_only=args.audio_only, force=args.force)

        if success:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✨ Summary is ready! ✨{Colors.ENDC}")
            return 0
        else:
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

            success = process_single_video(url, audio_only=args.audio_only, force=args.force)

            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
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

        # Return 0 if at least one succeeded
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
