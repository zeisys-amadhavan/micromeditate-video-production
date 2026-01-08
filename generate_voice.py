from elevenlabs.client import ElevenLabs
from elevenlabs.play import play  # (kept as-is, though not used below)

client = ElevenLabs(
    api_key="sk_9b47e2b1f1d5778b65d5bbadebd2824f581c1b5bd39787f5"  # <-- use your (new) key here (or env var)
)

voices = [
    ("Sarah",   "EXAVITQu4vr4xnSDxMaL"),
    ("George",  "JBFqnCBsd6RMkjVDRZzb"),
    ("Callum",  "N2lVS1w4EtoT3dr4eOWO"),
    ("Liam",    "TX3LPaxmHKxFdv7VOQHJ"),
    ("Alice",   "Xb7hH8MSUJpSbSDYk0k2"),
    ("Jessica", "cgSgspJ2msm6clMCkdW9"),
    ("Chris",   "iP95p4xoKVk53GoZ742B"),
    ("Brian",   "nPczCjzI2devNBz1zQrb"),
]

text = "The first move is what sets everything in motion."

for name, voice_id in voices:
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )

    output_path = f"{name}.mp3"
    with open(output_path, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)

    print(f"Saved: {output_path}")

