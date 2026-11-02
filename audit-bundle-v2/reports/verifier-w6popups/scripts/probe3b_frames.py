"""Probe3b: extract one frame per card at copy-code mid-dwell from the committed mp4."""
import subprocess, sys
from pathlib import Path
import imageio_ffmpeg
DUP = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
ff = imageio_ffmpeg.get_ffmpeg_exe()
mp4 = DUP / "video/segments/gitvisual7.mp4"
# copy-code mid-dwells: ARRIVALS + DWELL/2
mids = [8.5, 14.0, 19.75, 25.25, 31.25, 37.75, 44.0]
names = ["parcels", "escalations", "verifiers", "plants", "gates", "studies", "main"]
for t, n in zip(mids, names):
    out = OUT / f"mp4frame_{n}_{t}.png"
    p = subprocess.run([ff, "-y", "-v", "error", "-ss", str(t), "-i", str(mp4),
                        "-frames:v", "1", str(out)], capture_output=True, text=True)
    print(t, n, out.name, "OK" if out.exists() else f"FAIL {p.stderr[:200]}")
