# AGENTS.md

## Project

TVS (Text-Video-Summarizer) — single-file Python 3.13 CLI. Downloads, transcribes, and summarizes videos from YouTube, Instagram, TikTok, X/Twitter.

**All logic lives in `tvs.py`. Do not split into modules.**

## Commands

```bash
python3.13 tvs.py -u "URL" -a -t              # Audio-only download + transcribe + summarize
python3.13 tvs.py -u "URL" -a -t -d            # Download only
python3.13 tvs.py -u "URL" -a -t -f            # Force re-transcription
python3.13 tvs.py --list urls.txt -a -t        # Batch from file (# for comments)
python3.13 tvs.py -u "URL" -a -t -o /path      # Custom output dir for transcripts/summaries
```

No automated test suite. No ruff/mypy/black installed. Verification is manual against real URLs.

## Architecture

```
URL → download_video() → transcribe_video() → copy_transcript() → generate_summary()
        yt-dlp             mlx-whisper            shutil            OpenCode
```

- **Transcription**: mlx-whisper (`mlx-community/distil-whisper-large-v3`), binary lives at `/Users/khaled/cc-project/insanely-fast-whisper/.venv/bin/mlx_whisper`
- **Summarization**: calls OpenCode `transcript-analyzer` agent via subprocess
- Cookies (for IG, TikTok, X) in `cookies/<platform>/`, warns if >30 days old

## Key functions

| Function | Line | Purpose |
|----------|------|---------|
| `run_command()` | ~271 | Subprocess wrapper, returns `(success, stdout, stderr)` |
| `validate_environment()` | ~332 | Checks yt-dlp, ffmpeg, mediainfo, mlx-whisper |
| `download_video()` | ~414 | yt-dlp download with platform-specific cookie injection |
| `transcribe_video()` | ~792 | mlx-whisper transcription with ffmpeg audio pre-processing |
| `generate_summary()` | ~1076 | OpenCode subprocess call for AI summary |
| `process_single_video()` | ~1259 | Orchestrates the full pipeline |

## Code conventions

- **Imports**: stdlib only at top level; `shutil`, `tempfile`, `re` imported locally inside functions
- **Constants**: `UPPER_SNAKE_CASE` at top of file after imports
- **Paths**: always `pathlib.Path`, relative to `SCRIPT_DIR = Path(__file__).parent.resolve()`
- **Sections**: separated by `# ===...` (80-char) banner lines — CONFIG, UTILITY FUNCTIONS, VALIDATION, DOWNLOAD, TRANSCRIPTION, SUMMARY, MAIN
- **Error pattern**: `print_error()` for user + `logging.error()` for debug log; return `None` on failure
- **Output helpers**: `print_header()`, `print_step()`, `print_success()`, `print_error()`, `print_warning()`, `print_info()`
- **Docstrings**: triple-quoted with Args/Returns sections
- **No type hints currently used** (acceptable to add)

## CLI flags

| Flag | Description |
|------|-------------|
| `-u, --url` | Single video URL |
| `-l, --list` | URL list file |
| `-a, --audio-only` | Download audio only (10x faster) |
| `-t, --terminal` | Live terminal output |
| `-f, --force` | Force re-transcription |
| `-d, --download-only` | Skip transcription/summary |
| `-o, --output` | Custom transcript/summary output dir |
