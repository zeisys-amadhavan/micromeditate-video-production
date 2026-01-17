# ElevenLabs Timed Chant Generator (macOS)

This repository contains Python scripts used to generate **precisely timed spoken chants** using the ElevenLabs Text-to-Speech API.  
It is designed for **meditation, breath cadence, and mantra loops**, where timing accuracy matters more than expressive speech.

---

## System this was built on

- Operating System: macOS 26.2
- Build: 25C56
- Python: 3.9.6
- pip: 25.3

---

## Why this exists

Most TTS tools optimize for natural speech.
Meditation audio needs exact timing, silence control, and loop-safe output.

This repo enforces:
- Breath-cycle timing
- Deterministic silence
- Cleanup of ElevenLabs tail artifacts
- Repeatable batch generation

---

## Repository contents

### generate_voice.py
Generates a single spoken phrase for testing voice and pronunciation.

### generate_hindivoice.py
Same as above, tuned for Hindi / Sanskrit / Indic phonetics.

### generate_timedchants.py
Core script that enforces timing rules:

- Inhale: 4000 ms
- Hold silence: 4000 ms
- Exhale + post-silence: max 8000 ms

Ensures loop-safe audio without stray sounds.

### Shiva Names.csv
CSV input for batch chant generation.

### elevenlabs.txt
Early notes and API examples.
Rotate keys before sharing.

---

## Setup (macOS Terminal)

```bash
python3 --version
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install elevenlabs pydub
```

(Optional)
```bash
export ELEVENLABS_API_KEY="your_api_key_here"
```

---

## Running the scripts

```bash
python generate_voice.py
python generate_hindivoice.py
python generate_timedchants.py
```

---

## Design philosophy

- Silence is intentional
- Timing > expressiveness
- Loopability is required
- Minimal post-processing

---

## Final note

This code is strict on purpose.
It exists to produce reliable, breath-synced, loopable meditation audio.
