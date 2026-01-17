# generate_timed_chants.py — Timed Breath-Chant MP3 generator (ElevenLabs)

This script generates a single MP3 by looping through rows in a chants CSV.
Each row becomes one timed breath cycle:

**inhale (spoken)** → **hold (silence)** → **exhale (spoken)** → **rest (silence)**

It uses **ElevenLabs** for TTS and **pydub** to assemble the audio.

---

## Requirements

- Python 3.9+
- FFmpeg (required by `pydub` for MP3 decoding/encoding)
- ElevenLabs Python SDK
- pydub

---

## Install dependencies

### 1) Install FFmpeg

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

### 2) Install Python packages

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install elevenlabs pydub
```

---

## Prepare your chants CSV

Create a file like `chants.csv` with **UTF-8** encoding.

**Required columns:** `inhale`, `exhale`  
**Optional column:** `repeat` (integer; defaults to 1)

Example:

```csv
inhale,exhale,repeat
Om namo,śivāya namaḥ,1
Om namo,maheśvarāya namaḥ,1
Om namo,śambhave namaḥ,2
```

---

## API key options (CLI arg or exported env var)

The script supports BOTH:

### Option A — Export the default env var

```bash
export ELEVENLABS_API_KEY="sk-..."
```

Then run without `--api-key`.

### Option B — Export a custom env var name

```bash
export MY_ELEVEN_KEY="sk-..."
```

Then pass its name:

```bash
python3 generate_timed_chants.py --api-key-env MY_ELEVEN_KEY ...
```

### Option C — Pass directly on the command line (highest priority)

```bash
python3 generate_timed_chants.py --api-key "sk-..." ...
```

**Precedence:** `--api-key` > `--api-key-env` > `ELEVENLABS_API_KEY`

---

## Run the script

Example (4-4-4-4 cycle):

```bash
python3 generate_timed_chants.py \
  --chants-csv chants.csv \
  --voice-id nPczCjzI2devNBz1zQrb \
  --inhale-ms 4000 --hold-ms 4000 --exhale-ms 4000 --rest-ms 4000 \
  --out Brian_timed.mp3
```

---

## All options

```bash
python3 generate_timed_chants.py --help
```

Key flags:

- `--api-key` (optional)
- `--api-key-env` (optional; default `ELEVENLABS_API_KEY`)
- `--chants-csv` (required)
- `--voice-id` (required)
- `--inhale-ms --hold-ms --exhale-ms --rest-ms` (required)
- `--out` (required)
- Optional TTS tuning:
  - `--model-id`
  - `--language-code`
  - `--stability`
  - `--similarity-boost`
  - `--style`
  - `--no-speaker-boost`

---

## Notes / troubleshooting

- If you see errors like `ffmpeg not found`, install FFmpeg and confirm it’s on your PATH:
  ```bash
  which ffmpeg
  ```
- If your MP3 sounds like it has “garbage tails,” this script already trims trailing noise and fades out the end of each spoken segment.

---

## Output

The output is a single MP3 at the path you pass in `--out`:

- Example: `Brian_timed.mp3`

The script prints the total duration in milliseconds when done.
