"""Grab midpoint frames for the verifier's truth sample (own script)."""
import subprocess
from pathlib import Path
import imageio_ffmpeg

BASE = Path("C:/Users/logan/source/repos/Muse-Softfloat")
MP4 = BASE / "worktrees/verify6-captions/video/out/assembly_v6.mp4"
OUT = BASE / "scratch/verifier-w6captions/frames"
OUT.mkdir(parents=True, exist_ok=True)
exe = imageio_ffmpeg.get_ffmpeg_exe()

# (cue_no, mid_seconds) — 15 cues, all five segments, incl first + outro
SAMPLE = [
    (1, 2.904), (2, 8.000), (6, 10.403), (12, 15.967), (19, 21.774),
    (24, 26.371), (27, 32.661), (41, 43.548), (49, 50.322),
    (59, 71.129), (63, 93.145), (66, 121.936), (69, 160.190),
    (70, 170.565), (77, 177.821),
]
for n, t in SAMPLE:
    out = OUT / f"cue{n:02d}_t{t:.3f}.png"
    r = subprocess.run([exe, "-y", "-hide_banner", "-loglevel", "error",
                        "-ss", f"{t:.3f}", "-i", str(MP4),
                        "-frames:v", "1", str(out)],
                       capture_output=True, text=True)
    if r.returncode != 0 or not out.exists():
        print(f"FAIL cue {n}: {r.stderr[-500:]}")
    else:
        print(f"cue {n:02d} t={t:.3f} -> {out.name} ({out.stat().st_size} bytes)")
