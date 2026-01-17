#!/usr/bin/env python3
import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path
import string

def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        sys.stderr.write(p.stderr + "\n")
        raise SystemExit(p.returncode)

def ffprobe_duration_seconds(input_path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-print_format", "json",
        "-show_format",
        str(input_path),
    ]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        sys.stderr.write(p.stderr + "\n")
        raise SystemExit(p.returncode)

    data = json.loads(p.stdout)
    return float(data["format"]["duration"])

def main():
    ap = argparse.ArgumentParser(
        description="Split a .mov into N parts with NO re-encode and name as -A, -B, -C..."
    )
    ap.add_argument("input", help="Path to input .mov file")
    ap.add_argument("parts", type=int, help="Number of parts (max 26 for A–Z)")
    ap.add_argument("-o", "--outdir", default=None, help="Output directory")
    args = ap.parse_args()

    if args.parts > 26:
        raise SystemExit("This naming scheme supports up to 26 parts (A–Z).")

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    base = input_path.stem
    outdir = Path(args.outdir).expanduser().resolve() if args.outdir else (Path.cwd() / f"{base}_parts")
    outdir.mkdir(parents=True, exist_ok=True)

    duration = ffprobe_duration_seconds(input_path)
    segment_time = duration / args.parts

    temp_pattern = str(outdir / f"{base}_tmp_%03d.mov")

    # Split (lossless)
    run([
        "ffmpeg",
        "-y",
        "-i", str(input_path),
        "-map", "0",
        "-c", "copy",
        "-f", "segment",
        "-segment_time", f"{segment_time:.6f}",
        "-reset_timestamps", "1",
        temp_pattern,
    ])

    # Rename to -A, -B, -C...
    tmp_files = sorted(outdir.glob(f"{base}_tmp_*.mov"))
    letters = string.ascii_uppercase

    for i, f in enumerate(tmp_files):
        new_name = outdir / f"{base}-{letters[i]}.mov"
        f.rename(new_name)

    print(f"Done. Created {len(tmp_files)} files:")
    for i in range(len(tmp_files)):
        print(f"  {base}-{letters[i]}.mov")

if __name__ == "__main__":
    main()

