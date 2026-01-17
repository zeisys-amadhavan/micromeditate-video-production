#!/usr/bin/env python3
"""
generate_timed_chants_v3.py

Generate timed chant audio using ElevenLabs TTS.

Each row of the chants CSV produces one breath cycle:
  inhale_speak (inhale_ms) + hold_silence (hold_ms) + exhale_speak (exhale_ms) + rest_silence (rest_ms)

CSV columns:
  inhale, exhale
Optional:
  repeat (integer; defaults to 1)

Improvements vs v2:
- Better error handling for network/DNS/proxy issues (httpx.ConnectError / socket.gaierror).
- Prints detected proxy env vars + suggests exact `unset ...` commands.
- Final MP3 export defaults to 320k (reduces MP3 pre-echo artifacts).
- WAV output supported (set --out something.wav) to verify true silence.
"""

import argparse
import csv
import os
import sys
import socket
from io import BytesIO
from typing import List, Tuple

import httpx
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
from pydub.silence import detect_nonsilent


PROXY_KEYS = [
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
    "http_proxy", "https_proxy", "all_proxy", "no_proxy",
]


def print_network_troubleshooting() -> None:
    print("\n=== Network/DNS troubleshooting ===", file=sys.stderr)
    print("DNS/proxy issue likely (httpx ConnectError / DNS resolution failure).", file=sys.stderr)

    found = {k: os.getenv(k) for k in PROXY_KEYS if os.getenv(k)}
    if found:
        print("\nDetected proxy-related environment variables:", file=sys.stderr)
        for k, v in found.items():
            print(f"  {k}={v}", file=sys.stderr)

        print("\nTry temporarily disabling proxies in THIS terminal session:", file=sys.stderr)
        print("  unset HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY http_proxy https_proxy all_proxy no_proxy", file=sys.stderr)
    else:
        print("\nNo proxy env vars detected in your shell.", file=sys.stderr)

    print("\nQuick tests you can run:", file=sys.stderr)
    print("  python3.9 -c \"import socket; print(socket.gethostbyname('api.elevenlabs.io'))\"", file=sys.stderr)
    print("  curl -I https://api.elevenlabs.io", file=sys.stderr)
    print("\nIf those fail, try:", file=sys.stderr)
    print("  - disconnect VPN / corporate Wi-Fi and retry", file=sys.stderr)
    print("  - try a phone hotspot", file=sys.stderr)
    print("==================================\n", file=sys.stderr)


def clean_tts_tail(seg: AudioSegment, label: str = "") -> AudioSegment:
    """Trim junk/noise after spoken content and fade out to true silence."""
    if len(seg) == 0:
        return seg

    silence_thresh = max(-45, seg.dBFS - 20)
    ranges = detect_nonsilent(seg, min_silence_len=180, silence_thresh=silence_thresh)

    if not ranges:
        return AudioSegment.silent(duration=0)

    end_ms = min(len(seg), ranges[-1][1] + 60)
    return seg[:end_ms].fade_out(120)


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
        missing = {"inhale", "exhale"} - headers
        if missing:
            raise ValueError(f"CSV missing required columns: {sorted(missing)}")

        for i, row in enumerate(reader, start=2):
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


def tts_segment(
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
    """
    Fetch TTS bytes from ElevenLabs and return as a pydub AudioSegment.

    Raises:
      httpx.ConnectError / socket.gaierror if there are network/DNS issues.
    """
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

    raw_bytes = b"".join(chunk for chunk in audio_iter if chunk)

    outfmt = output_format.lower()
    if outfmt.startswith("mp3"):
        fmt = "mp3"
    elif outfmt.startswith("pcm") or outfmt.startswith("wav"):
        fmt = "wav"
    else:
        fmt = "mp3"

    seg = AudioSegment.from_file(BytesIO(raw_bytes), format=fmt)
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
        inhale_seg = tts_segment(
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

        exhale_seg = tts_segment(
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

    p.add_argument("--api-key", help="ElevenLabs API key (overrides env var if provided).")
    p.add_argument(
        "--api-key-env",
        default="ELEVENLABS_API_KEY",
        help="Name of environment variable containing the ElevenLabs API key (default: ELEVENLABS_API_KEY).",
    )

    p.add_argument("--chants-csv", required=True, help="Path to CSV with columns inhale, exhale (optional repeat).")

    p.add_argument("--inhale-ms", type=int, required=True, help="Inhale speak duration in ms.")
    p.add_argument("--hold-ms", type=int, required=True, help="Hold (silence) duration in ms.")
    p.add_argument("--exhale-ms", type=int, required=True, help="Exhale speak duration in ms.")
    p.add_argument("--rest-ms", type=int, required=True, help="Rest (silence) duration in ms.")

    p.add_argument("--voice-id", required=True, help="ElevenLabs voice ID to use.")

    p.add_argument("--out", required=True, help="Output path (must end with .mp3 or .wav).")
    p.add_argument(
        "--mp3-bitrate",
        default="320k",
        help="MP3 bitrate when --out ends with .mp3 (default: 320k).",
    )

    p.add_argument("--model-id", default="eleven_multilingual_v2")
    p.add_argument("--language-code", default="hi")
    p.add_argument("--output-format", default="mp3_44100_128")
    p.add_argument("--apply-text-normalization", default="off", choices=["auto", "on", "off"])

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
        print("ERROR: Missing ElevenLabs API key.", file=sys.stderr)
        return 2

    for name in ["inhale_ms", "hold_ms", "exhale_ms", "rest_ms"]:
        if getattr(args, name) < 0:
            print(f"ERROR: {name} must be >= 0", file=sys.stderr)
            return 2

    chants = load_chants_csv(args.chants_csv)
    if not chants:
        print("ERROR: No chants found in CSV.", file=sys.stderr)
        return 2

    client = ElevenLabs(api_key=api_key)

    try:
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
    except (httpx.ConnectError, socket.gaierror) as e:
        print(f"\nERROR: Unable to connect to ElevenLabs: {e}", file=sys.stderr)
        print_network_troubleshooting()
        return 3
    except httpx.HTTPError as e:
        # Covers timeouts, protocol errors, etc.
        print(f"\nERROR: HTTP error while contacting ElevenLabs: {e}", file=sys.stderr)
        print_network_troubleshooting()
        return 3

    out_lower = args.out.lower()
    if out_lower.endswith(".wav"):
        out.export(args.out, format="wav")
    elif out_lower.endswith(".mp3"):
        out.export(args.out, format="mp3", bitrate=args.mp3_bitrate)
    else:
        print("ERROR: --out must end with .mp3 or .wav", file=sys.stderr)
        return 2

    print(f"Saved: {args.out}  (duration_ms={len(out)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
