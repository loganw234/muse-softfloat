"""Verify a rendered MP4 without ffprobe (none on PATH / none bundled).

Uses the bundled ffmpeg itself: `-i` banner for duration/codec/size, a full
decode to null for the exact frame count, and -ss grabs for stills.
Usage: ..\\..\\.venv\\Scripts\\python.exe probe.py out/proof.mp4 --stills dir --at 1.5 7 16 25
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg


def ffmpeg_exe() -> str:
    return imageio_ffmpeg.get_ffmpeg_exe()


def probe(path: Path) -> dict:
    exe = ffmpeg_exe()
    r = subprocess.run([exe, "-hide_banner", "-i", str(path)],
                       capture_output=True, text=True)
    info = r.stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info)
    dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else None
    stream = re.search(r"Stream .*: Video: (\S+).*?(\d{3,5})x(\d{3,5}).*?([\d.]+) fps", info)
    dec = subprocess.run([exe, "-hide_banner", "-v", "info", "-i", str(path),
                          "-f", "null", "-"], capture_output=True, text=True)
    frames = re.findall(r"frame=\s*(\d+)", dec.stderr)
    return {
        "file": str(path),
        "bytes": path.stat().st_size,
        "duration_s": dur,
        "codec": stream.group(1).rstrip(",") if stream else None,
        "width": int(stream.group(2)) if stream else None,
        "height": int(stream.group(3)) if stream else None,
        "fps": float(stream.group(4)) if stream else None,
        "decoded_frames": int(frames[-1]) if frames else None,
        "decode_rc": dec.returncode,
    }


def stills(path: Path, outdir: Path, times: list[float]) -> list[Path]:
    exe = ffmpeg_exe()
    outdir.mkdir(parents=True, exist_ok=True)
    made = []
    for t in times:
        out = outdir / f"still_{t:05.1f}s.png"
        subprocess.run([exe, "-y", "-hide_banner", "-loglevel", "error",
                        "-ss", str(t), "-i", str(path), "-frames:v", "1", str(out)],
                       check=True)
        made.append(out)
    return made


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mp4")
    ap.add_argument("--stills", help="directory for still grabs")
    ap.add_argument("--at", nargs="+", type=float, default=[1.5, 7.0, 16.0, 25.0])
    a = ap.parse_args()
    p = Path(a.mp4)
    if not p.exists():
        print(f"missing: {p}", file=sys.stderr)
        raise SystemExit(1)
    for k, v in probe(p).items():
        print(f"{k}: {v}")
    if a.stills:
        for s in stills(p, Path(a.stills), a.at):
            print(f"still: {s}")
