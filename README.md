Generate a timed breath–chant MP3 using ElevenLabs TTS.

Works with:
- macOS Terminal
- Python 3.9.6
- pip 25.3

---

## Prerequisites

### 1. Install FFmpeg (required by pydub)

```bash
brew install ffmpeg
```

### 2. Install Python packages

```bash
python3.9 -m pip install elevenlabs pydub
```

---

## CSV format

CSV **must be UTF‑8** and contain these columns:

- `inhale` (spoken during inhale)
- `exhale` (spoken during exhale)
- `repeat` (optional, integer, defaults to 1)

Example `chants.csv`:

```csv
inhale,exhale,repeat
Om namo,śivāya namaḥ,1
Om namo,maheśvarāya namaḥ,1
Om namo,śambhave namaḥ,2
```

---

## API key

Use **one** of the following:

### Option A — environment variable (recommended)

```bash
export ELEVENLABS_API_KEY="sk-..."
```

### Option B — custom env var name

```bash
export MY_ELEVEN_KEY="sk-..."
```

Pass its name with `--api-key-env MY_ELEVEN_KEY`

### Option C — command line (highest priority)

```bash
--api-key sk-...
```

Precedence:
```
--api-key > --api-key-env > ELEVENLABS_API_KEY
```

---

## Run

Example: 4‑4‑4‑4 breathing cycle

```bash
python3.9 generate_timed_chants.py   --chants-csv chants.csv   --voice-id nPczCjzI2devNBz1zQrb   --inhale-ms 4000   --hold-ms 4000   --exhale-ms 4000   --rest-ms 4000   --out Brian_timed.mp3
```

---

## Command‑line arguments

Required:
- `--chants-csv`
- `--voice-id`
- `--inhale-ms`
- `--hold-ms`
- `--exhale-ms`
- `--rest-ms`
- `--out`

Optional:
- `--api-key`
- `--api-key-env` (default: `ELEVENLABS_API_KEY`)
- `--model-id`
- `--language-code`
- `--stability`
- `--similarity-boost`
- `--style`
- `--no-speaker-boost`

---

## Output

A single MP3 file at the path passed to `--out`.
The script prints the total duration (ms) when finished.
