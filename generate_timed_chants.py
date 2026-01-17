#!/usr/bin/env python3
"""
generate_timed_chants.py

Generate timed chant audio using ElevenLabs TTS.

Each row of the chants CSV produces one breath cycle:
  inhale_speak (inhale_ms) + hold_silence (hold_ms) + exhale_speak (exhale_ms) + rest_silence (rest_ms)

The CSV must include columns:
  inhale, exhale
Optional columns:
  repeat (integer; defaults to 1)

Examples:
  # Using default env var ELEVENLABS_API_KEY
  export ELEVENLABS_API_KEY="sk-..."
  python3 generate_timed_chants.py \
    --chants-csv chants.csv \
    --voice-id nPczCjzI2devNBz1zQrb \
    --inhale-ms 4000 --hold-ms 4000 --exhale-ms 4000 --rest-ms 4000 \
    --out Brian_timed.mp3

  # Using a custom env var name
  export MY_ELEVEN_KEY="sk-..."
  python3 generate_timed_chants.py \
    --api-key-env MY_ELEVEN_KEY \
    --chants-csv chants.csv \
    --voice-id nPczCjzI2devNBz1zQrb \
    --inhale-ms 4000 --hold-ms 4000 --exhale-ms 4000 --rest-ms 4000 \
    --out Brian_timed.mp3

  # Passing the key directly (highest priority)
  python3 generate_timed_chants.py \
    --api-key "sk-..." \
    --chants-csv chants.csv \
    --voice-id nPczCjzI2devNBz1zQrb \
    --inhale-ms 4000 --hold-ms 4000 --exhale-ms 4000 --rest-ms 4000 \
    --out Brian_timed.mp3
"""

import argparse
import csv
import os
import sys
from io import BytesIO
from typing import List, Tuple

from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
from pydub.silence import detect_nonsilent


def clean_tts_tail(seg: AudioSegment, label: str = "") -> AudioSegment:
    """
    Trim junk/noise after the spoken content.
    Keeps audio up to the last detected non-silent region, then fades out to true silence.
    """
    if len(seg) == 0:
        return seg

    # Dynamic threshold: treat anything ~20dB quieter than average as "silence" (clamped)
    silence_thresh = max(-45, seg.dBFS - 20)

    ranges = detect_nonsilent(seg, min_silence_len=180, silence_thresh=silence_thresh)

    if not ranges:
        return AudioSegment.silent(duration=0)

    end_ms = min(len(seg), ranges[-1][1] + 60)
    cleaned = seg[:end_ms].fade_out(120)
    return cleaned


def fit_to(seg: AudioSegment, target_ms: int, label: str = "") -> AudioSegment:
    if target_ms < 0:
        raise ValueError("target_ms must be >= 0")

    if len(seg) > target_ms:
        print(f"WARNING: '{label}' was {len(seg)}ms > {target_ms}ms, trimming.")
        return seg[:target_ms]
    return seg + AudioSegment.silent(duration=(target_ms - len(seg)))


def load_chants_csv(path: str) -> List[Tuple[str, str]]:
    chants: List[Tuple[str, str]] = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row.")

        headers = {h.strip() for h in reader.fieldnames if h}
        required = {"inhale", "exhale"}
        missing = required - headers
        if missing:
            raise ValueError(f"CSV missing required columns: {sorted(missing)}")

        for i, row in enumerate(reader, start=2):  # header is line 1
            inhale = (row.get("inhale") or "").strip()
            exhale = (row.get("exhale") or "").strip()
            if not inhale or not exhale:
                raise ValueError(f"Row {i}: inhale/exhale cannot be empty.")

            repeat_raw = (row.get("repeat") or "").strip()
            repeat = 1
            if repeat_raw:
                try:
                    repeat = int(repeat_raw)
                except ValueError:
                    raise ValueError(f"Row {i}: repeat must be an integer (got '{repeat_raw}').")
                if repeat < 1:
                    raise ValueError(f"Row {i}: repeat must be >= 1 (got {repeat}).")

            for _ in range(repeat):
                chants.append((inhale, exhale))

    return chants


def tts_mp3_segment(
    client: ElevenLabs,
    text: str,
    voice_id: str,
    model_id: str,
    language_code: str,
    output_format: str,
    apply_text_normalization: str,
    stability: float,
    similarity_boost: float,
    style: float,
    use_speaker_boost: bool,
) -> AudioSegment:
    audio_iter = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        language_code=language_code,
        output_format=output_format,
        apply_text_normalization=apply_text_normalization,
        voice_settings={
            "stability": stability,
            "similarity_boost": similarity_boost,
            "style": style,
            "use_speaker_boost": use_speaker_boost,
        },
    )

    mp3_bytes = b"".join(chunk for chunk in audio_iter if chunk)
    seg = AudioSegment.from_file(BytesIO(mp3_bytes), format="mp3")
    return clean_tts_tail(seg, label=text)


def build_timed_track(
    client: ElevenLabs,
    chants: List[Tuple[str, str]],
    voice_id: str,
    inhale_ms: int,
    hold_ms: int,
    exhale_ms: int,
    rest_ms: int,
    model_id: str,
    language_code: str,
    output_format: str,
    apply_text_normalization: str,
    stability: float,
    similarity_boost: float,
    style: float,
    use_speaker_boost: bool,
) -> AudioSegment:
    out = AudioSegment.silent(duration=0)

    for inhale_text, exhale_text in chants:
        inhale_seg = tts_mp3_segment(
            client=client,
            text=inhale_text,
            voice_id=voice_id,
            model_id=model_id,
            language_code=language_code,
            output_format=output_format,
            apply_text_normalization=apply_text_normalization,
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            use_speaker_boost=use_speaker_boost,
        )
        inhale_seg = fit_to(inhale_seg, inhale_ms, label=f"inhale: {inhale_text}")
        hold_seg = AudioSegment.silent(duration=hold_ms)

        exhale_seg = tts_mp3_segment(
            client=client,
            text=exhale_text,
            voice_id=voice_id,
            model_id=model_id,
            language_code=language_code,
            output_format=output_format,
            apply_text_normalization=apply_text_normalization,
            stability=stability,
            similarity_boost=similarity_boost,
            style=style,
            use_speaker_boost=use_speaker_boost,
        )
        exhale_seg = fit_to(exhale_seg, exhale_ms, label=f"exhale: {exhale_text}")
        rest_seg = AudioSegment.silent(duration=rest_ms)

        out += inhale_seg + hold_seg + exhale_seg + rest_seg

    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate timed chant audio with ElevenLabs TTS.")

    # API key: accept either direct key or env var name (default ELEVENLABS_API_KEY)
    p.add_argument("--api-key", help="ElevenLabs API key (overrides env var if provided).")
    p.add_argument(
        "--api-key-env",
        default="ELEVENLABS_API_KEY",
        help="Name of environment variable containing the ElevenLabs API key (default: ELEVENLABS_API_KEY).",
    )

    p.add_argument("--chants-csv", required=True,
                   help="Path to CSV with columns inhale, exhale (optional repeat).")

    # Timing
    p.add_argument("--inhale-ms", type=int, required=True, help="Inhale speak duration in ms.")
    p.add_argument("--hold-ms", type=int, required=True, help="Hold (silence) duration in ms.")
    p.add_argument("--exhale-ms", type=int, required=True, help="Exhale speak duration in ms.")
    p.add_argument("--rest-ms", type=int, required=True, help="Rest (silence) duration in ms.")

    # Voice
    p.add_argument("--voice-id", required=True, help="ElevenLabs voice ID to use.")

    # Output
    p.add_argument("--out", required=True, help="Output MP3 path.")

    # TTS options (defaults match your earlier script)
    p.add_argument("--model-id", default="eleven_multilingual_v2")
    p.add_argument("--language-code", default="hi")
    p.add_argument("--output-format", default="mp3_44100_128")
    p.add_argument("--apply-text-normalization", default="off", choices=["auto", "on", "off"])

    # Voice settings
    p.add_argument("--stability", type=float, default=0.90)
    p.add_argument("--similarity-boost", type=float, default=0.75)
    p.add_argument("--style", type=float, default=0.0)
    p.add_argument("--use-speaker-boost", dest="use_speaker_boost", action="store_true", default=True)
    p.add_argument("--no-speaker-boost", dest="use_speaker_boost", action="store_false")

    return p.parse_args()


def main() -> int:
    args = parse_args()

    api_key = args.api_key or os.getenv(args.api_key_env)
    if not api_key:
        print(
            "ERROR: Missing ElevenLabs API key.\n"
            "Provide one using:\n"
            "  --api-key <KEY>\n"
            "or export an environment variable and (optionally) pass its name via:\n"
            "  --api-key-env <ENV_VAR_NAME>\n"
            f"(Current --api-key-env is '{args.api_key_env}')",
            file=sys.stderr,
        )
        return 2

    for name in ["inhale_ms", "hold_ms", "exhale_ms", "rest_ms"]:
        v = getattr(args, name)
        if v < 0:
            print(f"ERROR: {name} must be >= 0 (got {v}).", file=sys.stderr)
            return 2

    chants = load_chants_csv(args.chants_csv)
    if not chants:
        print("ERROR: No chants found in CSV.", file=sys.stderr)
        return 2

    client = ElevenLabs(api_key=api_key)

    out = build_timed_track(
        client=client,
        chants=chants,
        voice_id=args.voice_id,
        inhale_ms=args.inhale_ms,
        hold_ms=args.hold_ms,
        exhale_ms=args.exhale_ms,
        rest_ms=args.rest_ms,
        model_id=args.model_id,
        language_code=args.language_code,
        output_format=args.output_format,
        apply_text_normalization=args.apply_text_normalization,
        stability=args.stability,
        similarity_boost=args.similarity_boost,
        style=args.style,
        use_speaker_boost=args.use_speaker_boost,
    )

    out.export(args.out, format="mp3", bitrate="128k")
    print(f"Saved: {args.out}  (duration_ms={len(out)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
