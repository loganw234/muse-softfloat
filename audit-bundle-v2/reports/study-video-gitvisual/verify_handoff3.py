"""Verify handoff frames on the rendered MP4 stills + outro2 first frame."""
import subprocess
from pathlib import Path
import imageio_ffmpeg
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
for name in ("still_000.5s.png", "still_087.5s.png"):
    a = np.asarray(Image.open(HERE / "stills3" / name).convert("RGB"))
    u, c = np.unique(a.reshape(-1, 3), axis=0, return_counts=True)
    order = np.argsort(-c)
    print(name, "px", a.shape[0] * a.shape[1], "unique_colors", len(u),
          "top", [(u[i].tolist(), int(c[i])) for i in order[:3]])
exe = imageio_ffmpeg.get_ffmpeg_exe()
out = HERE / "stills3" / "_outro2_first.png"
subprocess.run([exe, "-y", "-hide_banner", "-loglevel", "error", "-i",
                str(ROOT / "scratch/study-video-intro/outro2.mp4"), "-frames:v", "1", str(out)], check=True)
a = np.asarray(Image.open(out).convert("RGB"))
u, c = np.unique(a.reshape(-1, 3), axis=0, return_counts=True)
print("outro2 first frame: unique", len(u), "dominant", u[int(np.argmax(c))].tolist(),
      "share", round(float(c.max() / c.sum()), 4))
out.unlink()
