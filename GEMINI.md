# TVS - Text-Video-Summarizer (Gemini CLI Guide)

This project is a standalone tool for downloading, transcribing, and summarizing videos from various platforms (YouTube, Instagram, TikTok, X, etc.).

## 🚀 Core Functionality
1. **Download**: Uses `yt-dlp` to fetch videos or audio.
2. **Transcribe**: Uses NVIDIA NeMo's `parakeet-tdt-0.6b-v3` model (running in a `nemo` conda environment).
3. **Summarize**: Generates Markdown summaries from transcripts.

## 📂 Project Structure
- `tvs.py`: Main entry point.
- `tvs-quick.sh`: Helper for processing URLs from the clipboard.
- `videos/`: Default download location.
- `transcripts/`: Stores `.txt` transcripts and `-summarize.md` summaries.
- `cookies/`: Site-specific cookies for authentication.
- `parakeet-tdt-0.6b-v3/`: Local storage for the transcription model.

## 🛠 Tech Stack
- **Python**: 3.13
- **Conda**: Required for the `nemo` environment.
- **FFmpeg**: Required for audio conversion (mono 16kHz WAV).
- **yt-dlp**: Required for downloading.

## 📍 Portability & Path Management
The project is designed to be fully portable. All internal paths are calculated relative to the script's location using `SCRIPT_DIR`.

- **Conda Discovery**: The tool dynamically searches for the `conda` executable in common system paths and via `which`.
- **Local Model**: It is configured to use the local `.nemo` file within the repository rather than downloading it from a hub.

## 📝 Recent Changes (March 25, 2026)
- **Path Hardcoding Removal**: Replaced all absolute `/Users/khaled/...` paths with dynamic `SCRIPT_DIR` references.
- **Local Model Integration**: Updated `tvs.py` to point `PARAKEET_MODEL` to the local `parakeet-tdt-0.6b-v3.nemo` file.
- **Dynamic Conda Path**: Implemented `get_conda_path()` in `tvs.py` to resolve the conda executable location at runtime.
- **Location-Independent Shell Script**: Updated `tvs-quick.sh` to dynamically resolve its own directory before calling `tvs.py`.
- **Dynamic Help Epilog**: The `--help` command now shows the actual resolved paths for saving videos and transcripts.
