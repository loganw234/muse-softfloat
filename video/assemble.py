"""Assemble the segment-based cut (v5) at 2560x1440.

Segments live in video/segments/ (production copies of the
study renderers; history in scratch/study-video-*). This
script renders each segment if its MP4 is missing, then
concatenates intro -> idea -> why -> gitvisual -> outro into
video/out/assembly_v5.mp4 and pixel-checks the joins.

Run from the workspace root with the project venv:
    .venv\\Scripts\\python.exe video\\assemble.py [--force]
"""
from __future__ import annotations

import subprocess
import sys
from collections import Counter
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SEG = HERE / "segments"
OUT = HERE / "out"
PY = sys.executable
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# (script, expected mp4, expected seconds)
SEGMENTS = [
    ("intro_outro.py", "intro3.mp4", 7.0),
    ("idea.py", "idea2-1440p.mp4", 22.5),
    ("why.py", "why3-1440p.mp4", 29.0),  # workloads scene trimmed (dup of idea)
    ("gitvisual.py", "gitvisual5.mp4", 102.0),
    ("intro_outro.py", "outro3.mp4", 8.5),  # same script renders both
]
ORDER = ["intro3.mp4", "idea2-1440p.mp4", "why3-1440p.mp4",
         "gitvisual5.mp4", "outro3.mp4"]


def render_missing(force: bool) -> None:
    done_scripts = set()
    for script, mp4, _dur in SEGMENTS:
        target = SEG / mp4
        if script in done_scripts:
            continue
        if target.exists() and not force:
            print(f"skip {mp4} (exists; --force to re-render)")
            continue
        done_scripts.add(script)
        cmd = [PY, str(SEG / script)]
        if script == "gitvisual.py":
            cmd += ["--out", str(SEG / "gitvisual5.mp4")]
        print("render:", " ".join(cmd))
        rc = subprocess.run(cmd, cwd=ROOT).returncode
        if rc != 0:
            raise SystemExit(f"{script} failed rc={rc}")


def main() -> int:
    force = "--force" in sys.argv
    OUT.mkdir(exist_ok=True)
    render_missing(force)
    inputs = []
    filters = []
    for i, name in enumerate(ORDER):
        inputs += ["-i", str(SEG / name)]
        filters.append(f"[{i}:v]setsar=1[v{i}]")
    fc = ";".join(filters) + ";" + "".join(f"[v{i}]" for i in range(len(ORDER))) \
        + f"concat=n={len(ORDER)}:v=1:a=0[v]"
    out = OUT / "assembly_v5.mp4"
    cmd = [FFMPEG, "-y", *inputs, "-filter_complex", fc, "-map", "[v]",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30", str(out)]
    print("concat ->", out)
    if subprocess.run(cmd).returncode != 0:
        raise SystemExit("ffmpeg concat failed")
    # join checks: segment boundaries at cumulative durations
    bounds = []
    t = 0.0
    durs = {mp4: dur for _s, mp4, dur in SEGMENTS}
    for name in ORDER[:-1]:
        t += durs[name]
        bounds.append(t)
    for b in bounds:
        for dt in (-0.1, 0.1):
            grab = OUT / f"_join_{b + dt:.1f}.png"
            subprocess.run([FFMPEG, "-y", "-ss", str(b + dt), "-i", str(out),
                            "-frames:v", "1", str(grab)],
                           capture_output=True)
            im = Image.open(grab).convert("RGB")
            px = im.get_flattened_data() if hasattr(im, "get_flattened_data") \
                else list(im.getdata())
            dom, cnt = Counter(px).most_common(1)[0]
            print(f"join {b + dt:7.1f}s dominant {dom} {cnt}/{len(px)}")
            grab.unlink()
    print("done:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
