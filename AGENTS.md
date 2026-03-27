# AGENTS.md

Guidelines for AI coding agents working in this repository.

## Project Overview

**TVS (Text-Video-Summarizer)** - A single-file Python CLI tool for downloading, transcribing, and summarizing videos from social media platforms (YouTube, Instagram, TikTok, X/Twitter).

## Build/Lint/Test Commands

```bash
# Run the tool (primary usage)
python3.13 tvs.py -u "URL" -a -t

# Download only mode
python3.13 tvs.py -u "URL" -a -t -d

# Force re-transcription
python3.13 tvs.py -u "URL" -a -t -f

# Batch processing
python3.13 tvs.py --list urls.txt -a -t

# Show color demo
python3.13 tvs.py --colors

# Show help
python3.13 tvs.py --help

# Type checking (if mypy installed)
mypy tvs.py --ignore-missing-imports

# Linting (if ruff installed)
ruff check tvs.py

# Format check (if black installed)
black --check tvs.py
```

Note: This project has no automated test suite. Testing is done manually by running the tool against real URLs.

## Requirements

- Python 3.13+
- `yt-dlp` - Video downloading
- `ffmpeg` - Audio conversion (mono 16kHz WAV)
- `mediainfo` - Video duration detection (optional)
- `conda` with `nemo` environment - NVIDIA NeMo for transcription
- `opencode` - Summary generation via `transcript-analyzer` agent

## Architecture

### Processing Pipeline

```
URL → download_video() → transcribe_video() → copy_transcript() → generate_summary()
        (yt-dlp)            (parakeet)           (shutil)          (OpenCode)
```

### Directory Structure

```
tvs/
├── tvs.py              # Main script (ALL logic in single file)
├── videos/             # Downloaded media (organized by platform)
│   ├── youtube/
│   ├── instagram/
│   ├── tiktok/
│   └── x/
├── transcripts/        # Transcripts and summaries (WORK_DIR)
├── logs/               # debug-DATE.log and processed-DATE.log
└── cookies/            # Platform cookies (optional)
```

## Code Style Guidelines

### Imports

```python
# Standard library imports only (alphabetically ordered)
import argparse
import subprocess
import sys
import os
import time
import logging
from pathlib import Path
from datetime import datetime
```

- Use stdlib only; no external pip packages in main script
- Import `shutil`, `tempfile`, `re` locally when needed (inside functions)
- Group: stdlib imports, then from imports

### File Structure

The script follows this section order (marked with `# ===` separators):

1. Shebang and module docstring
2. Imports
3. Configuration constants (ALL_CAPS)
4. Utility classes (e.g., `Colors`)
5. Utility functions
6. Validation functions
7. Main processing functions
8. Main function and entry point

### Naming Conventions

- **Constants**: `UPPER_SNAKE_CASE` (e.g., `VIDEOS_DIR`, `CONDA_PATH`, `SITE_COOKIES`)
- **Functions**: `snake_case` (e.g., `download_video`, `transcribe_video`)
- **Classes**: `PascalCase` (e.g., `Colors`)
- **Variables**: `snake_case` (e.g., `video_file`, `transcript_text`)
- **Private-ish functions**: No underscore prefix used; all functions are "public"

### Formatting

- Line length: ~100-120 characters (not strictly enforced)
- Indentation: 4 spaces
- String formatting: Use f-strings (e.g., `f"Processing: {url}"`)
- Section headers: `# ============...` with 60+ equals signs
- Empty lines: 2 blank lines between major sections

### Docstrings

```python
def function_name(arg1, arg2):
    """
    Brief description of function.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value
    """
```

- Use triple-quoted docstrings for all functions
- Include Args and Returns sections
- Keep descriptions concise

### Error Handling

```python
try:
    # Operation
    result = perform_operation()
except FileNotFoundError:
    print_error("File not found")
    logging.error("File not found")
    return None
except Exception as e:
    print_error(f"Unexpected error: {e}")
    logging.error(f"Exception: {e}")
    return None
```

- Use specific exceptions when possible
- Always use `print_error()` for user-facing errors
- Always use `logging.error()` for debug log
- Return `None` on failure, actual value on success
- Include troubleshooting hints in error messages

### Logging

```python
# Setup (done once in setup_logging())
logging.info("Starting operation")
logging.debug(f"Variable value: {var}")
logging.error(f"Failed: {error}")
```

- Use `logging.info()` for major operations
- Use `logging.debug()` for detailed diagnostics
- Use `logging.error()` for failures
- Use `logging.warning()` for non-fatal issues

### Terminal Output Functions

Use these helper functions for user output:

- `print_header(text)` - Major section header with colors
- `print_step(num, text)` - Step number and description
- `print_success(text)` - Success message (green with checkmark)
- `print_error(text)` - Error message (red with X)
- `print_warning(text)` - Warning message (yellow with warning icon)
- `print_info(text)` - Info message (cyan with info icon)

### Type Hints

Not currently used in the codebase, but acceptable to add:

```python
def download_video(url: str, audio_only: bool = False) -> tuple[Path | None, bool, str]:
```

### Path Handling

Always use `pathlib.Path`:

```python
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
video_file = SCRIPT_DIR / "videos" / "youtube" / "video.mp4"

# Check existence
if video_file.exists():
    ...

# Create directories
video_dir.mkdir(parents=True, exist_ok=True)

# Read/write files
content = video_file.read_text(encoding="utf-8")
video_file.write_text(content, encoding="utf-8")
```

### Subprocess Commands

Use the `run_command()` helper:

```python
def run_command(cmd, cwd=None, timeout=600, shell=False):
    """
    Run shell command and return output.
    Returns: tuple(success: bool, stdout: str, stderr: str)
    """
```

Example:
```python
success, stdout, stderr = run_command(["yt-dlp", "--version"])
if not success:
    print_error(f"Command failed: {stderr}")
```

## Key Functions Reference

| Function | Purpose | Location |
|----------|---------|----------|
| `download_video()` | Download via yt-dlp | Line ~358 |
| `transcribe_video()` | Transcribe with parakeet | Line ~617 |
| `generate_summary()` | AI summary via opencode | Line ~801 |
| `validate_environment()` | Check dependencies | Line ~273 |
| `run_command()` | Subprocess wrapper | Line ~232 |

## Configuration

Key constants at top of `tvs.py`:

- `PARAKEET_MODEL` - Path to local NeMo model
- `CONDA_PATH` - Conda executable path
- `CONDA_ENV` - Conda environment name (`nemo`)
- `SITE_COOKIES` - Dict of platform cookie paths
- `COOKIE_WARNING_DAYS` - Cookie age threshold (30)

## Making Changes

1. All logic lives in `tvs.py` - do not split into modules
2. Maintain the section structure with `# ===` separators
3. Add new functions in appropriate section
4. Update docstrings for any modified functions
5. Test manually with real URLs before committing
6. Keep backwards compatibility with existing CLI flags

## Platform Support

| Platform | Download | Smart Naming | Notes |
|----------|----------|--------------|-------|
| YouTube | Yes | No (uses title) | Most reliable |
| Instagram | Yes | Yes | Requires cookies |
| TikTok | Yes | Yes | Requires cookies |
| X/Twitter | Yes | No | Requires cookies |
| Threads | No | Yes | yt-dlp unsupported |
