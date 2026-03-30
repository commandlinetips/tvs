# STT-Only Flag Design

## Problem

The opencode-telegram-bot uses a remote Whisper-compatible API (OpenAI/Groq) for voice note transcription, incurring API costs. TVS already has local mlx-whisper transcription working reliably. We need a way for the bot to call TVS's STT pipeline directly on a local audio file, without running the full download-transcribe-summarize pipeline.

## Solution

Add a `--stt` flag to tvs.py that accepts a local audio/video file path, transcribes it using the existing mlx-whisper pipeline, and outputs the transcript text to stdout.

## CLI Interface

```bash
python3.13 tvs.py --stt <path-to-audio-file>
```

- Accepts any audio/video format that ffmpeg can handle (ogg, mp3, wav, m4a, webm, mp4, etc.)
- Only the raw transcript text is printed to stdout
- All status/diagnostic output goes to stderr
- Exit code 0 on success, 1 on failure
- Auto-cleans intermediate files (converted WAV, whisper output .txt)
- Extra flags (`-a`, `-t`, `-f`, `-d`, `-o`) are silently ignored in STT mode

## Architecture

### Stdout Isolation

`convert_audio_for_whisper()` and `run_command()` both use `print()` / `print_info()` / `print_error()` which write to stdout. In STT mode, stdout must contain ONLY the transcript text.

**Solution**: In `transcribe_file_stt()`, temporarily redirect `sys.stdout` to `sys.stderr` before calling any existing helper functions, then restore it before printing the transcript:

```python
sys.stdout = sys.stderr
converted_audio = convert_audio_for_whisper(audio_file)
sys.stdout = sys.__stdout__
```

This ensures all diagnostic output goes to stderr while the transcript output remains clean on stdout.

### Logging Without setup_logging()

`setup_logging()` is skipped in STT mode (no log files created). `run_command()` calls `logging.error()` on failures, which will use Python's lastResort handler → stderr. `logging.info()` / `logging.debug()` will be silently dropped (root logger defaults to WARNING). This is intentional and acceptable.

### New function: `transcribe_file_stt(file_path)`

Located in the "Main Processing Functions" section of tvs.py. Completely standalone — does not depend on logging setup, environment validation, or the existing pipeline functions.

Steps:
1. Validate the input file exists
2. Check ffmpeg is available (needed for audio conversion)
3. Check mlx-whisper binary exists at `MLX_WHISPER_BIN`
4. Redirect stdout → stderr, call `convert_audio_for_whisper()` to produce mono 16kHz WAV, restore stdout
5. Redirect stdout → stderr, build and run the mlx-whisper command (same arguments as `transcribe_video()`), restore stdout
6. Read the whisper output `.txt` file
7. Print transcript text to **stdout** (`sys.stdout.write()`)
8. Delete the intermediate WAV file and whisper output `.txt` file
9. Return the transcript string (or None on error)

Intermediate files (`{stem}_mono16k.wav`, `{stem}_mono16k.txt`) are created in the same directory as the input file. This is fine for `/tmp` inputs from the bot.

### Changes to `main()`

- Add `--stt` to the existing mutually exclusive argument group (alongside `-u` and `-l`)
- Update the validation guard on line 1242: change `if not args.url and not args.list:` to `if not args.url and not args.list and not args.stt:`
- When `--stt` is used:
  - Skip `setup_logging()` — no log files created
  - Skip `validate_environment()` — checks are done inside `transcribe_file_stt()`
  - Skip all header/progress printing
  - Call `transcribe_file_stt()` directly
  - Return 0 or 1 based on result
- All diagnostic messages in STT mode print to **stderr** (not stdout) so they don't pollute the transcript output

### What stays the same

- `convert_audio_for_whisper()` — reused as-is (stdout redirected around calls)
- `MLX_WHISPER_BIN`, `MLX_WHISPER_MODEL` constants — reused as-is
- `run_command()` — reused as-is
- No changes to `transcribe_video()`, `download_video()`, or any other existing function

## Error Handling

| Condition | Behavior |
|-----------|----------|
| File not found | stderr message, exit 1 |
| ffmpeg not found | stderr message, exit 1 |
| mlx-whisper binary missing | stderr message, exit 1 |
| ffmpeg conversion fails | stderr message, exit 1 |
| mlx-whisper transcription fails | stderr message, exit 1 |
| Empty transcript | stderr warning, exit 1 |
| Timeout | 300s default (same minimum as existing pipeline), stderr message, exit 1 |

Timeout is 300s (5 minutes). This matches the minimum timeout in the existing `transcribe_video()` and is sufficient for voice notes and short audio. For very long audio files, the caller can handle timeout at the subprocess level.

## Cleanup

After successful transcription, delete:
- `{stem}_mono16k.wav` — the intermediate mono WAV file
- `{stem}_mono16k.txt` — the whisper output file (if still present)

Cleanup is best-effort — failures to delete are logged to stderr but don't cause exit 1.

## Bot Integration (future, out of scope)

The bot will call tvs.py as a subprocess:

```typescript
const { stdout } = await execFileAsync("python3.13", [
    "/path/to/tvs.py",
    "--stt", "/tmp/voice-note.ogg"
], { timeout: 120_000 });
const transcript = stdout.trim();
```

Bot-side changes are not part of this plan.

## Examples

```bash
# Transcribe a voice note
python3.13 tvs.py --stt /tmp/voice-note.ogg
# Output (stdout): "Hello, this is a test message"

# Transcribe an mp3 file
python3.13 tvs.py --stt /path/to/interview.mp3
# Output (stdout): "So today we're going to talk about..."

# Error case
python3.13 tvs.py --stt /nonexistent/file.ogg
# Output (stderr): "[-] File not found: /nonexistent/file.ogg"
# Exit code: 1
```
