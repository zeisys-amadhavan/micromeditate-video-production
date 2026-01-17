# ElevenLabs cadence / timed-chant generators

These scripts generate repeatable, loop-friendly voice audio using the ElevenLabs Text-to-Speech API.

Main use-cases:

- **Voice bakeoff**: generate the same line in multiple ElevenLabs voices to quickly compare tone and clarity.
- **Hindi / multilingual TTS**: force the TTS engine into the intended language mode.
- **Timed chant cadence**: generate chants that land cleanly on a timing grid (e.g., 4 seconds speak + 4 seconds silence) for breath-cycle videos.

## Repo contents

### `generate_voice.py`
**Why:** Quick sanity check and voice comparison.

**What it does:**
- Iterates over a list of voice IDs.
- Generates the same English sentence for each voice.
- Writes `Sarah.mp3`, `George.mp3`, etc.

**When to use:**
- Picking a voice (clarity, warmth, pronunciation) before generating a full chant set.

---

### `generate_hindivoice.py`
**Why:** ElevenLabs can behave differently depending on language mode; this forces Hindi (or more broadly, multilingual) behavior.

**What it does:**
- Same concept as `generate_voice.py`, but sets `language_code="hi"`.
- Useful when your text is in Hindi (or transliterated Sanskrit/Hindi) and you want consistent pronunciation.

**When to use:**
- Testing which voice handles Hindi/transliteration best.

---

### `generate_timedchants.py`
**Why:** For micro-meditation videos, you often need audio that aligns to a strict grid so loops feel seamless (no drift, no “extra tail noise”).

**What it does:**
- Uses ONLY one chosen voice (currently Brian).
- For each chant pair `(inhale_text, exhale_text)`, it builds a cycle:
  1. **Inhale spoken segment** padded or trimmed to `SPEECH_MS` (default **4000 ms**)
  2. **Hold / pause1** silent segment of `SILENCE_MS` (default **4000 ms**)
  3. **Exhale spoken segment** (variable length)
  4. **Rest / pause2** added so that **(exhale + pause2) never exceeds `EXHALE_PHASE_MS`** (default **8000 ms**)

- Includes a cleanup step (`clean_tts_tail`) to reduce “garbled sounds” or hallucinated tails after the spoken content by:
  - Detecting the last non-silent region
  - Trimming after it
  - Applying a short fade-out

**Output:**
- Writes `Brian_timed.mp3` (or `<VoiceName>_timed.mp3`).

**When to use:**
- Generating a chant track that loops cleanly on a 16-second breath cycle (4 + 4 + 8).

---

### `Shiva Names.csv`
A simple list of Shiva names (one per line). It can be used as input when you eventually refactor `generate_timedchants.py` to read chants from a CSV instead of a hard-coded Python list.

---

### `elevenlabs.txt`
Contains an API key and a curl example.

**Recommendation:** do not commit secrets. Delete this file from any public repo, and rotate any keys it contains.

## Setup

### 1) Python environment
Recommended: Python 3.10+

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

### 2) Install dependencies

These scripts use:
- `elevenlabs` (official/SDK-style client)
- `pydub` (audio slicing/padding)

```bash
pip install elevenlabs pydub
```

### 3) Install FFmpeg (required by pydub)

Pydub relies on FFmpeg to read/write MP3.

- macOS (Homebrew):
  ```bash
  brew install ffmpeg
  ```
- Ubuntu/Debian:
  ```bash
  sudo apt-get update && sudo apt-get install -y ffmpeg
  ```

Verify:
```bash
ffmpeg -version
```

## API key handling (important)

Right now the scripts instantiate the client like:

```python
client = ElevenLabs(api_key="...")
```

That works, but it is risky (easy to leak keys).

### Recommended pattern (future-proof)

1) Set an environment variable:

```bash
export ELEVENLABS_API_KEY="YOUR_KEY_HERE"
```

2) In the scripts, replace the hard-coded key with:

```python
import os
client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
```

If this repo ever becomes public, rotate any exposed keys immediately.

## How to run

From the repo folder:

### Voice bakeoff (English)
```bash
python generate_voice.py
```
Creates `Sarah.mp3`, `George.mp3`, etc.

### Voice bakeoff (Hindi mode)
```bash
python generate_hindivoice.py
```
Creates the same set of MP3s, but using `language_code="hi"`.

### Timed chant cadence track
```bash
python generate_timedchants.py
```
Creates `Brian_timed.mp3` (a stitched track with strict timing rules).

## Customization knobs

### Change timing
In `generate_timedchants.py`:

- `SPEECH_MS` (default 4000): inhale spoken segment length
- `SILENCE_MS` (default 4000): hold/pause1 length
- `EXHALE_PHASE_MS` (default 8000): max (exhale + pause2)

If you want a classic 4-4-4-4 cycle instead of 4-4-8, you would change `EXHALE_PHASE_MS` to 4000 and add a separate rest.

### Change voices
- For multi-voice testing, edit the `voices = [...]` list.
- For cadence production, keep the list to a single voice to ensure a consistent feel.

### Reduce tail artifacts further
If you still hear garbage syllables after exhale:
- Increase `min_silence_len` in `detect_nonsilent` (e.g., 250-400)
- Make `silence_thresh` more aggressive (e.g., `seg.dBFS - 25` but keep a clamp)
- Add a tiny crossfade when concatenating segments (pydub supports crossfade)

## Troubleshooting

### "FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'"
FFmpeg is not installed or not on PATH. Install it (see Setup) and re-open your terminal.

### MP3 export works but audio has tiny clicks at cuts
- Increase fade-out in `clean_tts_tail` (e.g., from 120 ms to 200 ms)
- Add a very small fade-in on the next segment (10-30 ms)

### ElevenLabs client raises errors for optional params
Some SDK versions may not support all parameters.
- In `generate_timedchants.py`, remove `apply_text_normalization="off"` or the `voice_settings` block if the SDK complains.

## Suggested next refactor (nice-to-have)

- Read chant text from `Shiva Names.csv` (or a richer CSV with inhale/exhale columns).
- Centralize configuration (voice_id, timings, output folder) in a single config file.
- Add a `requirements.txt` and a `Makefile` target like `make timed`.

---

If you want, I can also:
- convert the hard-coded API keys to environment variables across all scripts,
- add CSV input support for chants,
- and add an output folder structure (e.g., `out/voices/`, `out/timed/`).
