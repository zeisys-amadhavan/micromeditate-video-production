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
python3 -m pip install elevenlabs pydub
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

Give it as a text file in the same directory.

```bash
--api-key "$(cat eleven_labs_key.txt)" \
```


---

## Run

Example: 4‑4‑4‑4 breathing cycle

```bash
python3 generate_timed_chants.py --api-key "$(cat eleven_labs_key.txt)" --chants-csv chants.csv   --voice-id nPczCjzI2devNBz1zQrb   --inhale-ms 4000   --hold-ms 4000   --exhale-ms 4000   --rest-ms 4000   --out chants.mp3
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

# Simple ElevenLabs Test

This script is a **minimal sanity check** for ElevenLabs Text-to-Speech.
It verifies:

- API key is valid
- Network/DNS connectivity works
- Local audio playback works

If this script plays audio correctly, your ElevenLabs setup is working.

---

## Prerequisites

```bash
pip install elevenlabs
```

---

## Run the test

```bash
python3 test.py   --api-key "$(cat eleven_labs_key.txt)"   --text "The first move is what sets everything in motion."   --voice-id JBFqnCBsd6RMkjVDRZzb   --model-id eleven_multilingual_v2   --output-format mp3_44100_128
