"""Decode the last 6 frames of why-1440p.mp4; count non-white px in each."""
import subprocess
from pathlib import Path
import imageio_ffmpeg
from PIL import Image

HERE = Path(__file__).resolve().parent
exe = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([exe, "-y", "-hide_banner", "-loglevel", "error",
                "-sseof", "-0.2", "-i", str(HERE / "why-1440p.mp4"),
                str(HERE / "stills" / "tail_%02d.png")], check=True)
for p in sorted((HERE / "stills").glob("tail_*.png")):
    im = Image.open(p).convert("RGB")
    px = list(im.getdata())
    print(p.name, "nonwhite =", sum(1 for q in px if q != (255, 255, 255)))
