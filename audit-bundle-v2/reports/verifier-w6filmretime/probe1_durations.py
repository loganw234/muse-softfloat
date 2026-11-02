"""Probe 1: durations, resolution, fps, audio, frame counts vs SEGMENTS + tempo math."""
import json, subprocess, sys
from pathlib import Path

COPY = Path("worktrees/verify6-filmretime/video/segments")
FF = Path(".venv/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe")

def probe(mp4):
    p = COPY / mp4
    r = subprocess.run([str(FF), "-hide_banner", "-i", str(p)],
                       capture_output=True, text=True)
    err = r.stderr
    # count frames
    r2 = subprocess.run(
        [str(FF), "-hide_banner", "-loglevel", "error", "-i", str(p),
         "-map", "0:v:0", "-c", "copy", "-f", "null", "-"],
        capture_output=True, text=True)
    return err

names = ["intro3.mp4", "idea2-1440p.mp4", "why3-1440p.mp4",
         "gitvisual7.mp4", "outro3.mp4"]
import re
for n in names:
    err = probe(n)
    dur = re.search(r"Duration: (\S+),", err).group(1)
    vs = re.search(r"Stream #0:0.*Video: (\w+).*?(\d+x\d+),.*?(\d+) fps", err)
    audio = "Audio" in err
    # frame count via packets
    r3 = subprocess.run(
        [str(FF), "-hide_banner", "-loglevel", "error", "-i", str(COPY / n),
         "-map", "0:v:0", "-f", "null", "-"],
        capture_output=True, text=True)
    m = re.search(r"frame=\s*(\d+)", r3.stderr)
    print(f"{n}: duration={dur} video={vs.group(2) if vs else '?'} "
          f"fps={vs.group(3) if vs else '?'} audio={audio} "
          f"frames_decoded={m.group(1) if m else '?'} size={(COPY/n).stat().st_size}")

# SEGMENTS arithmetic as written in assemble.py
SEG = [("intro_outro.py", "intro3.mp4", 7.0),
       ("idea.py", "idea2-1440p.mp4", 26.0),
       ("why.py", "why3-1440p.mp4", 29.0),
       ("gitvisual.py", "gitvisual7.mp4", 108.0),
       ("intro_outro.py", "outro3.mp4", 12.0)]
native_seg = sum(d for _, _, d in SEG)
print("SEGMENTS native sum =", native_seg)
print("tempo as coded = 120.0/120.0 =", 120.0 / 120.0)
print("scaled total as coded =", native_seg * (120.0 / 120.0))
print("scaled total if 120/124 (docstring) =", round(native_seg * 120.0 / 124.0, 3))
print("actual MP4 sum = 7+26+32+108+12 =", 7 + 26 + 32 + 108 + 12)
print("actual scaled 185*120/124 =", round(185 * 120.0 / 124.0, 3))
print("cap 180: coded-product-under-cap =", (185 * 1.0) < 180)
