# split_mov.py (macOS) — Lossless MOV splitter

Split a `.mov` video into **N parts** from macOS Terminal with **no quality loss** (no re-encoding).
Output segments are renamed as:

- `video-A.mov`
- `video-B.mov`
- `video-C.mov`
- …

This script uses FFmpeg with **stream copy** (`-c copy`) so the original video/audio streams are preserved.

---

## What you get

- ✅ Splits a `.mov` into **N parts**
- ✅ **No re-encode** → **no reduction in quality**
- ✅ Keeps all streams (`-map 0`) (video + audio, etc.)
- ✅ Output naming: `-A`, `-B`, `-C` … (A–Z)

---

## Requirements

- macOS
- Python 3.8+ (system Python is fine)
- FFmpeg (provides `ffmpeg` and `ffprobe`)

---

## Step 1 — Check if FFmpeg is installed

Run:

```bash
which ffmpeg
which ffprobe
```

If you see paths like `/opt/homebrew/bin/ffmpeg` or `/usr/local/bin/ffmpeg`, you’re good.
If you see `ffmpeg not found` / `ffprobe not found`, install FFmpeg below.

---

## Step 2 — Install FFmpeg (via Homebrew)

### 2A) Install Homebrew (only if you don’t already have it)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, Homebrew may ask you to run something like:

```bash
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Run that line if it appears.

Verify Homebrew:

```bash
brew --version
```

### 2B) Install FFmpeg

```bash
brew install ffmpeg
```

Verify:

```bash
which ffmpeg
which ffprobe

ffmpeg -version
ffprobe -version
```

---

## Step 3 — If `ffmpeg` still shows “not found” (PATH fix)

Sometimes Homebrew installs correctly but your shell PATH isn’t updated.

### Apple Silicon Macs (M1/M2/M3)

```bash
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile
```

### Intel Macs

```bash
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile
```

Now re-check:

```bash
which ffmpeg
which ffprobe
```

---

## Step 4 — Run the script

### 4A) Make it executable (first time only)

From the repo directory:

```bash
chmod +x split_mov.py
```

### 4B) Run

Syntax:

```bash
./split_mov.py "/full/path/to/video.mov" N
```

Example (split into 12 parts):

```bash
./split_mov.py "/Users/you/Videos/meditation.mov" 12
```

Output directory will be created automatically:

```
meditation_parts/
  meditation-A.mov
  meditation-B.mov
  ...
  meditation-L.mov
```

---

## Notes (important)

### 1) Keyframe boundaries (why parts may not be perfectly equal)

This tool uses **no re-encoding**. When streams are copied (`-c copy`), FFmpeg can only cut cleanly on **keyframes**.
That means:

- You will get **N parts**
- But segment durations may be **slightly uneven** (usually small drift)
- This is the tradeoff for **zero quality loss**

If you need perfectly equal durations, you must re-encode (not what this tool does).

### 2) Limit: A–Z naming (max 26 parts)

This repo’s default naming scheme supports **up to 26 parts** (`A` to `Z`).
If you need more (e.g., `AA`, `AB`, ...), extend the renaming logic.

---

## Quick Troubleshooting

### Error: `FileNotFoundError: ffprobe` or `ffmpeg not found`

- Install FFmpeg (Step 2)
- Fix PATH (Step 3)
- Confirm with:

```bash
which ffmpeg
which ffprobe
```

### Error: “Permission denied” when running script

Run:

```bash
chmod +x split_mov.py
```

Or run via Python:

```bash
python3 split_mov.py "/path/to/video.mov" 12
```

---

## What the script does under the hood (high level)

1. Uses `ffprobe` to read the video duration
2. Computes `segment_time = duration / N`
3. Runs FFmpeg segment muxer with `-c copy`:
   - No re-encode
   - No quality changes
4. Renames `tmp_000.mov` → `-A.mov`, `tmp_001.mov` → `-B.mov`, etc.

---

## License

Choose whatever you prefer (MIT is common). If you haven’t added one yet, add a `LICENSE` file.
