# TVS Walker Integration: Implementation Tasks

**Project:** Integrate TVS (Text-Video-Summarizer) with Omarchy's Walker launcher
**Integration Method:** Walker prefix mode using `#` symbol
**Detail Level:** Very detailed with copy-pasteable code
**Created:** 2025-11-04
**Status:** Ready for Implementation

---

## 📋 Overview

This document provides step-by-step instructions to integrate TVS with Walker, allowing you to:

1. Type `#` in Walker to activate TVS mode
2. Paste/type a video URL
3. See interactive options: Full Process, Download Only, Audio + Transcript, etc.
4. Process videos directly from Walker with flags support

**Example Usage:**
```
# in Walker → Shows usage help
#https://youtube.com/watch?v=abc → Shows options
#https://youtube.com/watch?v=abc -a → Direct processing with audio-only
```

**Key Features:**
- ✅ `#` prefix mode in Walker
- ✅ Interactive options displayed as Walker results
- ✅ Flag support: `-a` (audio-only), `-d` (download-only), `-f` (force)
- ✅ Error handling and validation
- ✅ Smart URL detection from clipboard
- ✅ Duplicate detection
- ✅ Full rollback/uninstall support

---

## ✅ Prerequisites

Before starting, verify these exist:

1. **TVS Script:** `~/tools/automation/tvs/tvs.py` (main script)
2. **Walker Installed:** `walker --version` should work
3. **Walker Config:** `~/.config/walker/config.toml` exists
4. **Required Tools:**
   - `yt-dlp` (video downloader)
   - `vibe` (transcription)
   - `opencode` (summary generation)
   - `wl-paste` (clipboard access)
   - `notify-send` (notifications)

**Quick Check:**
```bash
cd ~/tools/automation/tvs/
ls -la tvs.py
walker --version
which yt-dlp vibe opencode wl-paste notify-send
```

All commands should succeed. If any fail, install missing dependencies first.

---

## 📦 Implementation Phases

### Phase 1: Modify TVS Core (Add Download-Only Flag)
### Phase 2: Create Walker Provider Script
### Phase 3: Configure Walker Integration
### Phase 4: Test and Verify
### Phase 5: Error Handling & Polish
### Rollback: Uninstall Instructions

---

# Phase 1: Modify TVS Core

## Task 1.1: Add `-d` (Download-Only) Flag to tvs.py

**Purpose:** Allow TVS to download videos without transcription/summarization.

**File:** `~/tools/automation/tvs/tvs.py`

**Location:** Add flag to argument parser (around line 514)

### Step 1.1.1: Add the Argument

Find the argument parser section in `main()` function (line ~509-518). After the `-f, --force` argument, add:

```python
parser.add_argument(
    '-d', '--download-only',
    action='store_true',
    help='Download video only (skip transcription and summary)'
)
```

**Exact location:** After line 517 (the `--force` argument), before `args = parser.parse_args()`

### Step 1.1.2: Modify process_single_video() Function

Find the `process_single_video()` function (line ~416). Update its signature and logic:

**Current signature (line 416):**
```python
def process_single_video(url, audio_only=False, force=False):
```

**New signature:**
```python
def process_single_video(url, audio_only=False, force=False, download_only=False):
```

**Update the docstring (line ~417-426):**
```python
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
```

### Step 1.1.3: Add Download-Only Logic

After the download step (around line 434), add conditional logic:

**Find this section (line ~431-434):**
```python
# Step 1: Download
video_file, already_existed = download_video(url, audio_only=audio_only)
if not video_file:
    print_error("Failed to download video")
    return False
```

**Add after line 434:**
```python
# If download-only mode, stop here
if download_only:
    overall_elapsed = time.time() - overall_start
    print_header("Download Complete!")
    print_success("Video downloaded successfully (download-only mode)")
    print_info(f"Total time: {overall_elapsed:.1f}s")
    print(f"\n{Colors.BOLD}Output:{Colors.ENDC}")
    print(f"  📹 Video: {video_file}")
    return True
```

### Step 1.1.4: Update Function Calls to process_single_video()

**Find all calls to process_single_video() and add download_only parameter:**

**Call 1 (line ~546):**
```python
# OLD:
success = process_single_video(args.url, audio_only=args.audio_only, force=args.force)

# NEW:
success = process_single_video(args.url, audio_only=args.audio_only, force=args.force, download_only=args.download_only)
```

**Call 2 (line ~594):**
```python
# OLD:
success = process_single_video(url, audio_only=args.audio_only, force=args.force)

# NEW:
success = process_single_video(url, audio_only=args.audio_only, force=args.force, download_only=args.download_only)
```

### Step 1.1.5: Verify the Changes

**Test the new flag:**
```bash
cd ~/tools/automation/tvs/
python3.13 tvs.py -h | grep "download-only"
# Should show: -d, --download-only    Download video only (skip transcription and summary)

# Test with short video
python3.13 tvs.py -u "https://youtube.com/shorts/8YULk160fIw" -d -a -t
```

**Expected output:**
- ✅ Downloads video
- ✅ Shows "Download Complete!" message
- ✅ Stops without transcription/summary
- ✅ No errors

**Checkpoint:** `-d` flag works correctly ✓

---

# Phase 2: Create Walker Provider Script

## Task 2.1: Determine Script Location

**Question for you:** Where should the Walker provider script live?

**Options:**
1. `~/.local/bin/walker-tvs-provider` (standard user binaries)
2. `~/.local/share/omarchy/bin/omarchy-tvs-walker-provider` (Omarchy scripts)
3. `~/tools/automation/tvs/walker-tvs-provider` (with TVS project)

**Recommendation:** Option 1 (`~/.local/bin/`) - follows Omarchy patterns for user scripts, easy to find, in PATH.

**For this guide, I'll use:** `~/.local/bin/walker-tvs-provider`

**⚠️ PAUSE HERE: Confirm location before continuing**

---

## Task 2.2: Create Walker Provider Script

**File:** `~/.local/bin/walker-tvs-provider`

**Purpose:**
- Accepts input from Walker (user's query after `#`)
- Parses URL and flags
- Returns JSON with interactive options
- Handles execution of selected option

### Step 2.2.1: Create the Script File

```bash
cat > ~/.local/bin/walker-tvs-provider << 'SCRIPT_END'
#!/bin/bash
# Walker TVS Provider
# Integrates TVS (Text-Video-Summarizer) with Walker launcher
# Usage: Called automatically by Walker when user types #
# Returns: JSON with Walker-compatible items

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

TVS_SCRIPT="/home/skull/tools/automation/tvs/tvs.py"
PYTHON_CMD="python3.13"
WORK_DIR="$HOME/Work/Kai/video"
VIDEOS_DIR="$HOME/Videos"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

# Send JSON to Walker
send_json() {
    echo "$1"
    exit 0
}

# Check if string is a valid URL
is_url() {
    local url="$1"
    [[ "$url" =~ ^https?:// ]]
}

# Extract video ID from URL (for duplicate detection)
extract_video_id() {
    local url="$1"
    # YouTube
    if [[ "$url" =~ youtube\.com/watch\?v=([^&]+) ]]; then
        echo "${BASH_REMATCH[1]}"
    elif [[ "$url" =~ youtu\.be/([^?]+) ]]; then
        echo "${BASH_REMATCH[1]}"
    elif [[ "$url" =~ youtube\.com/shorts/([^?]+) ]]; then
        echo "${BASH_REMATCH[1]}"
    # Twitter/X
    elif [[ "$url" =~ (twitter\.com|x\.com)/.*/status/([0-9]+) ]]; then
        echo "${BASH_REMATCH[2]}"
    # Generic: use last path component
    else
        echo "$url" | rev | cut -d'/' -f1 | rev | cut -d'?' -f1
    fi
}

# Check if video already processed
check_existing_summary() {
    local url="$1"
    local video_id
    video_id=$(extract_video_id "$url")

    # Search for existing summary
    find "$WORK_DIR" -name "*${video_id}*-summarize.md" 2>/dev/null | head -1
}

# Escape JSON strings
json_escape() {
    echo "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/$/\\n/g' | tr -d '\n'
}

# ============================================================================
# MAIN LOGIC
# ============================================================================

# Read query from Walker (stdin)
read -r QUERY || QUERY=""

# Remove leading # if present (Walker might pass it)
QUERY="${QUERY#\#}"
QUERY="${QUERY## }"  # Trim leading spaces

# Case 1: Empty query - show usage
if [[ -z "$QUERY" ]]; then
    send_json '{
        "items": [
            {
                "label": "📹 TVS - Text-Video-Summarizer",
                "sub": "Paste a video URL to process (YouTube, Twitter, etc.)",
                "exec": ""
            },
            {
                "label": "💡 Usage Examples",
                "sub": "#<URL> for options | #<URL> -a for audio-only",
                "exec": ""
            },
            {
                "label": "📋 Try Clipboard",
                "sub": "Paste from clipboard (Super+V)",
                "exec": ""
            }
        ]
    }'
fi

# Parse query for URL and flags
FLAGS=""
URL=""

# Simple parser: everything that starts with - is a flag, rest is URL
for word in $QUERY; do
    if [[ "$word" =~ ^- ]]; then
        FLAGS="$FLAGS $word"
    else
        URL="$word"
    fi
done

# Case 2: No URL found - try clipboard
if [[ -z "$URL" ]] || ! is_url "$URL"; then
    # Check clipboard
    CLIPBOARD=$(wl-paste 2>/dev/null || echo "")

    if is_url "$CLIPBOARD"; then
        URL="$CLIPBOARD"
        send_json "{
            \"items\": [
                {
                    \"label\": \"📋 Found URL in Clipboard\",
                    \"sub\": \"$URL\",
                    \"exec\": \"\"
                },
                {
                    \"label\": \"⚡ Process Now (Full Pipeline)\",
                    \"sub\": \"Download → Transcribe → Summarize\",
                    \"exec\": \"$PYTHON_CMD $TVS_SCRIPT -u '$URL' -a -t $FLAGS\"
                },
                {
                    \"label\": \"📥 Download Only\",
                    \"sub\": \"Download video without processing\",
                    \"exec\": \"$PYTHON_CMD $TVS_SCRIPT -u '$URL' -d -a -t $FLAGS\"
                }
            ]
        }"
    else
        send_json '{
            "items": [
                {
                    "label": "❌ Invalid Input",
                    "sub": "No valid URL found in query or clipboard",
                    "exec": ""
                },
                {
                    "label": "💡 Tip",
                    "sub": "Copy a video URL first, then type # in Walker",
                    "exec": ""
                }
            ]
        }'
    fi
fi

# Case 3: Valid URL - show processing options

# Check for existing summary (duplicate detection)
EXISTING_SUMMARY=$(check_existing_summary "$URL")

# Build JSON response
if [[ -n "$EXISTING_SUMMARY" ]]; then
    # Summary exists - offer to open or reprocess
    send_json "{
        \"items\": [
            {
                \"label\": \"⚠️  Already Processed\",
                \"sub\": \"This video was processed before\",
                \"exec\": \"\"
            },
            {
                \"label\": \"📖 Open Existing Summary\",
                \"sub\": \"$(basename "$EXISTING_SUMMARY")\",
                \"exec\": \"marktext '$EXISTING_SUMMARY'\"
            },
            {
                \"label\": \"🔄 Reprocess Video\",
                \"sub\": \"Force re-transcription and new summary\",
                \"exec\": \"$PYTHON_CMD $TVS_SCRIPT -u '$URL' -a -t -f $FLAGS\"
            },
            {
                \"label\": \"📥 Download Only\",
                \"sub\": \"Re-download video without processing\",
                \"exec\": \"$PYTHON_CMD $TVS_SCRIPT -u '$URL' -d -a -t $FLAGS\"
            }
        ]
    }"
else
    # New video - show standard options

    # If flags already provided, execute directly
    if [[ -n "$FLAGS" ]]; then
        send_json "{
            \"items\": [
                {
                    \"label\": \"⚡ Processing with flags: $FLAGS\",
                    \"sub\": \"$URL\",
                    \"exec\": \"$PYTHON_CMD $TVS_SCRIPT -u '$URL' -a -t $FLAGS\"
                }
            ]
        }"
    fi

    # Show interactive options
    send_json "{
        \"items\": [
            {
                \"label\": \"⚡ Full Process (Recommended)\",
                \"sub\": \"Download → Transcribe → Summarize (audio-only)\",
                \"exec\": \"$PYTHON_CMD $TVS_SCRIPT -u '$URL' -a -t\"
            },
            {
                \"label\": \"🔊 Audio + Transcript Only\",
                \"sub\": \"Download and transcribe (skip summary)\",
                \"exec\": \"$PYTHON_CMD $TVS_SCRIPT -u '$URL' -a -d -t\"
            },
            {
                \"label\": \"📥 Download Only\",
                \"sub\": \"Just download, no processing\",
                \"exec\": \"$PYTHON_CMD $TVS_SCRIPT -u '$URL' -d -a -t\"
            },
            {
                \"label\": \"🎬 Full Video (Not Audio-Only)\",
                \"sub\": \"Download video + full processing (slower, larger)\",
                \"exec\": \"$PYTHON_CMD $TVS_SCRIPT -u '$URL' -t\"
            },
            {
                \"label\": \"⚙️  Custom Flags\",
                \"sub\": \"Type flags manually: #<URL> -a -d -f\",
                \"exec\": \"\"
            }
        ]
    }"
fi

SCRIPT_END
```

### Step 2.2.2: Make Script Executable

```bash
chmod +x ~/.local/bin/walker-tvs-provider
```

### Step 2.2.3: Test the Script Manually

**Test 1: Empty input**
```bash
echo "" | ~/.local/bin/walker-tvs-provider
```
**Expected:** JSON with usage help

**Test 2: Valid URL**
```bash
echo "https://youtube.com/watch?v=dQw4w9WgXcQ" | ~/.local/bin/walker-tvs-provider
```
**Expected:** JSON with processing options

**Test 3: URL with flags**
```bash
echo "https://youtube.com/watch?v=dQw4w9WgXcQ -a -d" | ~/.local/bin/walker-tvs-provider
```
**Expected:** JSON with direct execution option

**Checkpoint:** Script produces valid JSON ✓

---

# Phase 3: Configure Walker Integration

## Task 3.1: Add TVS Prefix to Walker Config

**File:** `~/.config/walker/config.toml`

### Step 3.1.1: Backup Current Config

```bash
cp ~/.config/walker/config.toml ~/.config/walker/config.toml.backup-$(date +%Y%m%d-%H%M%S)
```

### Step 3.1.2: Add TVS Prefix

**Find the `[[providers.prefixes]]` section** (around line 133-155 in your config)

**After the last prefix (clipboard `$`), add:**

```toml
[[providers.prefixes]]
prefix = "#"
provider = "tvs"
```

**Exact location:** After line 155 (after the `$` clipboard prefix), before `[providers.actions]` section

### Step 3.1.3: Configure TVS Provider Actions

**Find the `[providers.actions]` section** (line ~157)

**Add TVS actions after the clipboard actions (after line 238):**

```toml
tvs = [
  { action = "run", default = true, bind = "Return" },
  { action = "cancel", bind = "Escape" },
]
```

**Note:** The `run` action executes the `exec` command from the JSON returned by the provider script.

### Step 3.1.4: Verify Walker Config Syntax

```bash
# Check for syntax errors
grep -A2 'prefix = "#"' ~/.config/walker/config.toml
# Should show:
# prefix = "#"
# provider = "tvs"

grep -A2 'tvs = \[' ~/.config/walker/config.toml
# Should show:
# tvs = [
#   { action = "run", default = true, bind = "Return" },
```

---

## Task 3.2: Configure Custom Provider in Walker

Walker needs to know how to call your custom provider script.

### Step 3.2.1: Add Custom Provider Configuration

**File:** `~/.config/walker/config.toml`

**Find the `[providers]` section** (around line 121-129)

**After the `max_results = 50` line, add:**

```toml
[providers.tvs]
command = "/home/skull/.local/bin/walker-tvs-provider"
```

**Alternative location:** Create a separate provider config file

**File:** `~/.config/walker/providers.toml` (create if doesn't exist)

```toml
[tvs]
command = "/home/skull/.local/bin/walker-tvs-provider"
```

**Then reference it in main config:**

In `~/.config/walker/config.toml`, add at top:
```toml
[providers]
include = "~/.config/walker/providers.toml"
```

**⚠️ Note:** Walker's custom provider support varies by version. If above doesn't work, the provider script might need to be invoked differently. Check Walker documentation or experiment.

---

## Task 3.3: Restart Walker Services

```bash
# Kill existing Walker processes
pkill walker

# Restart Walker service
setsid uwsm-app -- walker --gapplication-service &

# Wait for service to start
sleep 2

# Test launch
walker --width 644 --maxheight 300 --minheight 300
```

**Expected:** Walker opens with no errors

---

# Phase 4: Test and Verify

## Task 4.1: Test Basic TVS Mode

### Test 4.1.1: Empty # Query
1. Press `Super+Space` (launch Walker)
2. Type: `#`
3. Press `Enter` or wait

**Expected Result:**
- Walker shows: "📹 TVS - Text-Video-Summarizer"
- Shows usage help
- No errors

### Test 4.1.2: # with Invalid Input
1. Launch Walker
2. Type: `#not a url`

**Expected Result:**
- Shows "❌ Invalid Input"
- Suggests copying URL first

### Test 4.1.3: # with Valid URL
1. Launch Walker
2. Type: `#https://youtube.com/shorts/8YULk160fIw`
3. Wait for options to appear

**Expected Result:**
- Shows 5 options:
  - ⚡ Full Process (Recommended)
  - 🔊 Audio + Transcript Only
  - 📥 Download Only
  - 🎬 Full Video
  - ⚙️ Custom Flags
- No errors

### Test 4.1.4: Select and Execute Option
1. Launch Walker
2. Type: `#https://youtube.com/shorts/8YULk160fIw`
3. Select "📥 Download Only"
4. Press `Enter`

**Expected Result:**
- Walker closes
- Terminal window opens (if `-t` flag in exec command)
- TVS starts downloading
- Notifications appear
- Video downloads to `~/Videos/`
- No transcript/summary generated (download-only mode)

---

## Task 4.2: Test Clipboard Detection

### Test 4.2.1: # with URL in Clipboard
1. Copy URL: `echo "https://youtube.com/shorts/8YULk160fIw" | wl-copy`
2. Launch Walker
3. Type: `#` (without URL)

**Expected Result:**
- Shows "📋 Found URL in Clipboard"
- Shows URL from clipboard
- Offers processing options

---

## Task 4.3: Test Duplicate Detection

### Test 4.3.1: Process Same Video Twice
1. Process a video fully (creates summary)
2. Launch Walker again
3. Type same URL with `#`

**Expected Result:**
- Shows "⚠️ Already Processed"
- Offers "📖 Open Existing Summary"
- Offers "🔄 Reprocess Video" with `-f` flag

---

## Task 4.4: Test Flag Support

### Test 4.4.1: Direct Flags
1. Launch Walker
2. Type: `#https://youtube.com/shorts/8YULk160fIw -d -a`

**Expected Result:**
- Shows "⚡ Processing with flags: -d -a"
- Executes immediately when selected
- Downloads audio only, no transcription

---

# Phase 5: Error Handling & Polish

## Task 5.1: Add URL Validation

**File:** `~/.local/bin/walker-tvs-provider`

**Enhance the `is_url()` function** to check if URL is actually a video:

### Step 5.1.1: Add Video URL Validation

**Find the `is_url()` function** (around line 36)

**Replace with enhanced version:**

```bash
# Check if string is a valid video URL
is_url() {
    local url="$1"

    # Basic URL check
    if ! [[ "$url" =~ ^https?:// ]]; then
        return 1
    fi

    # Check if it's a supported video platform
    if [[ "$url" =~ (youtube\.com|youtu\.be|twitter\.com|x\.com|vimeo\.com|twitch\.tv) ]]; then
        return 0
    fi

    # For other URLs, try yt-dlp simulation (quick check)
    if command -v yt-dlp &> /dev/null; then
        if yt-dlp --simulate "$url" &> /dev/null; then
            return 0
        fi
    fi

    return 1
}
```

**Note:** This adds platform detection and optional yt-dlp validation.

---

## Task 5.2: Add Disk Space Check

**File:** `~/.local/bin/walker-tvs-provider`

**Add before showing options:**

### Step 5.2.1: Add Disk Space Warning

**After the URL validation, before showing options, add:**

```bash
# Check available disk space in Videos directory
AVAILABLE_SPACE=$(df "$VIDEOS_DIR" | awk 'NR==2 {print $4}')
AVAILABLE_GB=$((AVAILABLE_SPACE / 1024 / 1024))

if [[ $AVAILABLE_GB -lt 1 ]]; then
    send_json "{
        \"items\": [
            {
                \"label\": \"⚠️  Low Disk Space\",
                \"sub\": \"Only ${AVAILABLE_GB}GB available in ~/Videos/\",
                \"exec\": \"\"
            },
            {
                \"label\": \"🗑️  Clean Up Space\",
                \"sub\": \"Open file manager to free space\",
                \"exec\": \"dolphin $VIDEOS_DIR\"
            },
            {
                \"label\": \"⚠️  Continue Anyway\",
                \"sub\": \"Try downloading despite low space\",
                \"exec\": \"$PYTHON_CMD $TVS_SCRIPT -u '$URL' -a -t $FLAGS\"
            }
        ]
    }"
fi
```

**Note:** Warns if less than 1GB available, offers cleanup option.

---

## Task 5.3: Add Video Duration Warning

**File:** `~/.local/bin/walker-tvs-provider`

**Add video info fetching:**

### Step 5.3.1: Fetch Video Metadata

**After URL validation, add:**

```bash
# Get video info (duration, title)
if command -v yt-dlp &> /dev/null; then
    VIDEO_INFO=$(yt-dlp --print "%(duration)s|%(title)s" "$URL" 2>/dev/null || echo "0|Unknown")
    DURATION=$(echo "$VIDEO_INFO" | cut -d'|' -f1)
    TITLE=$(echo "$VIDEO_INFO" | cut -d'|' -f2)

    # Convert duration to minutes
    DURATION_MINUTES=$((DURATION / 60))

    # Warn for long videos (>2 hours)
    if [[ $DURATION_MINUTES -gt 120 ]]; then
        send_json "{
            \"items\": [
                {
                    \"label\": \"⏱️  Long Video Detected\",
                    \"sub\": \"$TITLE ($DURATION_MINUTES minutes)\",
                    \"exec\": \"\"
                },
                {
                    \"label\": \"⚡ Process Anyway (Full)\",
                    \"sub\": \"This may take 30-60 minutes\",
                    \"exec\": \"$PYTHON_CMD $TVS_SCRIPT -u '$URL' -a -t $FLAGS\"
                },
                {
                    \"label\": \"📥 Download Only (Faster)\",
                    \"sub\": \"Just download, process later\",
                    \"exec\": \"$PYTHON_CMD $TVS_SCRIPT -u '$URL' -d -a -t $FLAGS\"
                }
            ]
        }"
    fi
fi
```

**Note:** Warns for videos over 2 hours, suggests download-only for speed.

---

## Task 5.4: Add Concurrent Processing Lock

**Purpose:** Prevent multiple TVS processes from running simultaneously

### Step 5.4.1: Create Lock File System

**File:** `~/.local/bin/walker-tvs-provider`

**Add near the top (after CONFIGURATION section):**

```bash
# Lock file to prevent concurrent processing
LOCK_FILE="/tmp/tvs-walker-processing.lock"

# Check if another TVS process is running
if [[ -f "$LOCK_FILE" ]]; then
    # Read PID from lock file
    LOCK_PID=$(cat "$LOCK_FILE" 2>/dev/null || echo "0")

    # Check if that process is still running
    if kill -0 "$LOCK_PID" 2>/dev/null; then
        send_json '{
            "items": [
                {
                    "label": "⚠️  TVS Already Running",
                    "sub": "Another video is being processed",
                    "exec": ""
                },
                {
                    "label": "📊 Check Progress",
                    "sub": "Open terminal to see current processing",
                    "exec": "alacritty -e tail -f /tmp/tvs-latest.log"
                }
            ]
        }'
    else
        # Stale lock file, remove it
        rm "$LOCK_FILE"
    fi
fi
```

### Step 5.4.2: Update tvs.py to Create Lock File

**File:** `~/tools/automation/tvs/tvs.py`

**Add to main() function, after argument parsing:**

```python
# Create lock file to prevent concurrent runs
lock_file = Path("/tmp/tvs-walker-processing.lock")
if lock_file.exists():
    # Check if process is still running
    try:
        lock_pid = int(lock_file.read_text().strip())
        # If we can't signal it, it's dead
        os.kill(lock_pid, 0)
        print_error("Another TVS process is already running")
        print_info(f"PID: {lock_pid}")
        return 1
    except (ProcessLookupError, ValueError):
        # Process is dead, remove stale lock
        lock_file.unlink()

# Create lock file with our PID
lock_file.write_text(str(os.getpid()))

try:
    # ... existing main logic ...
    pass
finally:
    # Always remove lock file when done
    if lock_file.exists():
        lock_file.unlink()
```

**Add import at top of file:**
```python
import os
```

---

## Task 5.5: Improve Notification Messages

**File:** `~/.local/bin/walker-tvs-provider`

**Add rich notifications to the exec commands:**

### Step 5.5.1: Wrap Commands with Notifications

**Instead of directly calling tvs.py, wrap with notification:**

**Replace exec commands like:**
```json
"exec": "$PYTHON_CMD $TVS_SCRIPT -u '$URL' -a -t"
```

**With:**
```json
"exec": "notify-send -a 'TVS' '🎬 Processing Started' '$TITLE' -t 3000 && $PYTHON_CMD $TVS_SCRIPT -u '$URL' -a -t || notify-send -a 'TVS' -u critical '❌ Processing Failed' 'Check terminal for errors'"
```

**Note:** This adds start notification and failure notification.

---

# Rollback: Uninstall Instructions

## Complete Removal of TVS Walker Integration

If you want to remove the Walker integration completely:

### Step R.1: Remove Walker Provider Script

```bash
rm ~/.local/bin/walker-tvs-provider
```

### Step R.2: Restore Walker Config

```bash
# List available backups
ls -lt ~/.config/walker/config.toml.backup-*

# Restore from backup (choose timestamp)
cp ~/.config/walker/config.toml.backup-YYYYMMDD-HHMMSS ~/.config/walker/config.toml
```

**Or manually remove added sections:**

### Step R.2a: Remove TVS Prefix

**File:** `~/.config/walker/config.toml`

**Remove these lines (added in Task 3.1.2):**
```toml
[[providers.prefixes]]
prefix = "#"
provider = "tvs"
```

### Step R.2b: Remove TVS Actions

**File:** `~/.config/walker/config.toml`

**Remove these lines (added in Task 3.1.3):**
```toml
tvs = [
  { action = "run", default = true, bind = "Return" },
  { action = "cancel", bind = "Escape" },
]
```

### Step R.2c: Remove Custom Provider Config

**File:** `~/.config/walker/config.toml`

**Remove these lines (added in Task 3.2.1):**
```toml
[providers.tvs]
command = "/home/skull/.local/bin/walker-tvs-provider"
```

**Or delete:** `~/.config/walker/providers.toml` if created

### Step R.3: Revert tvs.py Changes

```bash
cd ~/tools/automation/tvs/

# If you have git:
git checkout tvs.py

# Or manually remove:
# - The -d/--download-only argument
# - The download_only parameter from process_single_video()
# - The download-only logic
# - Lock file logic
```

**Or restore from backup if created before changes**

### Step R.4: Restart Walker

```bash
pkill walker
sleep 2
setsid uwsm-app -- walker --gapplication-service &
```

### Step R.5: Verify Removal

```bash
# Should not find walker-tvs-provider
which walker-tvs-provider

# Should not show # prefix
grep 'prefix = "#"' ~/.config/walker/config.toml

# Walker should work normally
walker
# Type # and verify no TVS options appear
```

**Expected:** All traces of TVS integration removed, Walker works as before.

---

# Appendix: Troubleshooting

## Problem: Walker doesn't show TVS options when typing #

**Possible causes:**
1. Walker config syntax error
2. Provider script not executable
3. Walker not restarted
4. Script path incorrect

**Solutions:**
```bash
# Check config syntax
grep -A5 'prefix = "#"' ~/.config/walker/config.toml

# Check script exists and is executable
ls -la ~/.local/bin/walker-tvs-provider

# Restart Walker
pkill walker && setsid uwsm-app -- walker --gapplication-service &

# Test script directly
echo "https://youtube.com/watch?v=test" | ~/.local/bin/walker-tvs-provider
```

## Problem: "Command not found" when selecting option

**Cause:** `exec` command in JSON is incorrect

**Solution:** Check provider script output:
```bash
echo "#https://youtube.com/watch?v=test" | ~/.local/bin/walker-tvs-provider | jq .
```

Verify `exec` field contains valid command path.

## Problem: Duplicate detection not working

**Cause:** Summary file not found or path mismatch

**Solution:** Check WORK_DIR path:
```bash
# In walker-tvs-provider:
echo "$WORK_DIR"  # Should be /home/skull/Work/Kai/video

# Check for existing summaries:
ls -la "$HOME/Work/Kai/video/"*-summarize.md
```

## Problem: Options appear but nothing happens when selected

**Cause:** Walker not executing commands or terminal flag missing

**Solution:**
1. Check Walker actions configured correctly
2. Add `-t` flag to exec commands for terminal output
3. Check Walker logs: `journalctl -xeu walker`

## Problem: JSON parsing errors in Walker

**Cause:** Malformed JSON from provider script

**Solution:**
```bash
# Validate JSON output
echo "#test_url" | ~/.local/bin/walker-tvs-provider | jq .

# Should show no errors
# If errors, fix quoting/escaping in script
```

---

# Appendix: Advanced Customization

## Custom Option: Add "Process in Background"

**File:** `~/.local/bin/walker-tvs-provider`

**In the options JSON, add:**

```json
{
    "label": "🌙 Process in Background",
    "sub": "Run without terminal, get notification when done",
    "exec": "nohup $PYTHON_CMD $TVS_SCRIPT -u '$URL' -a > /tmp/tvs-bg.log 2>&1 & notify-send -a 'TVS' '🎬 Processing in Background' 'You will be notified when complete'"
}
```

## Custom Option: Add "Open Videos Folder"

```json
{
    "label": "📁 Open Videos Folder",
    "sub": "Browse downloaded videos",
    "exec": "dolphin $VIDEOS_DIR"
}
```

## Custom Option: Add "Show Recent Summaries"

```json
{
    "label": "📚 Recent Summaries",
    "sub": "Open work directory",
    "exec": "dolphin $WORK_DIR"
}
```

---

# Appendix: Integration with Other Tools

## Open Summary in Obsidian

**Add to exec command:**

```bash
"exec": "$PYTHON_CMD $TVS_SCRIPT -u '$URL' -a -t && obsidian://open?vault=MyVault&file=$(basename \"$WORK_DIR\"/*-summarize.md)"
```

## Copy Summary to Clipboard After Processing

```bash
"exec": "$PYTHON_CMD $TVS_SCRIPT -u '$URL' -a -t && wl-copy < \"$WORK_DIR\"/*-summarize.md && notify-send 'TVS' 'Summary copied to clipboard!'"
```

## Share Summary via Email

```bash
"exec": "$PYTHON_CMD $TVS_SCRIPT -u '$URL' -a -t && thunderbird -compose \"subject='Video Summary',body='$(cat \"$WORK_DIR\"/*-summarize.md)'\""
```

---

**END OF TASKS.MD**

**Document Created:** 2025-11-04
**Format:** Step-by-step implementation guide
**Detail Level:** Very detailed with copy-pasteable code
**Status:** Ready for implementation

**Next Steps:**
1. Confirm script location (`~/.local/bin/walker-tvs-provider`)
2. Start with Phase 1 (Add `-d` flag to tvs.py)
3. Proceed through phases sequentially
4. Test after each phase
5. Report issues or questions

**Estimated Time:**
- Phase 1: 20 minutes
- Phase 2: 30 minutes
- Phase 3: 15 minutes
- Phase 4: 30 minutes (testing)
- Phase 5: 45 minutes (polish)
- **Total:** ~2.5 hours for full implementation

Good luck with the implementation! 🚀
