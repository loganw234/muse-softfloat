"""Grab one frame per sampled cue midpoint for the truth check."""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

WS = Path(__file__).resolve().parent.parent.parent
WT = WS / "worktrees" / "w6-captions"
MP4 = WT / "video" / "out" / "assembly_v6.mp4"
OUT = Path(__file__).resolve().parent / "probe_frames"

sys.path.insert(0, str(WT / "video" / "segments"))
sys.path.insert(0, str(WT / "video"))
import captions as C  # noqa: E402

SAMPLES = [1, 6, 12, 19, 34, 41, 49, 54, 59, 62, 66, 69, 70, 72, 77]

exe = imageio_ffmpeg.get_ffmpeg_exe()
OUT.mkdir(parents=True, exist_ok=True)
cues = C.build_cues()
for n in SAMPLES:
    c = cues[n - 1]
    mid = (C._ms(c.start) + C._ms(c.end)) / 2 / 1000
    out = OUT / f"cue{n:02d}_{mid:06.2f}.png"
    subprocess.run([exe, "-y", "-hide_banner", "-loglevel", "error",
                    "-ss", f"{mid:.3f}", "-i", str(MP4),
                    "-frames:v", "1", "-vf", "scale=1920:1080",
                    str(out)], check=True)
    print(f"cue {n:02d} t={mid:.3f}s -> {out.name}")
