import re, subprocess, sys, time
from pathlib import Path
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
SRC = "scratch/lead/music/assembly_v6_musicA_stretch.mp4"
OUT = Path("scratch/lead/music/assembly_v6_musicA_stretch_4k.mp4")

def probe(path):
    p = subprocess.run([FF, "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", p.stderr)
    dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    v = re.search(r"Video:.*? (\d{3,4}x\d{3,4})[ ,].*?(\d+(?:\.\d+)?) fps", p.stderr)
    return dur, v.group(1), v.group(2), "Audio:" in p.stderr

t0 = time.time()
cmd = [FF, "-y", "-i", SRC, "-vf", "scale=3840:2160:flags=lanczos",
       "-c:v", "libx264", "-preset", "medium", "-crf", "19",
       "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart",
       "-metadata", "title=Muse-Softfloat film + Sunflower Dance (A stretch to fit, 4K personal copy)",
       str(OUT)]
p = subprocess.run(cmd, capture_output=True, text=True)
if p.returncode != 0:
    sys.exit("encode FAIL\n" + p.stderr[-1000:])
d, res, fps, audio = probe(OUT)
print(f"4K: {OUT} {d:.3f}s {res}@{fps} audio={audio} "
      f"{OUT.stat().st_size} bytes wall={time.time() - t0:.0f}s")
grab = Path("scratch/lead/music/still_4k_100s.png")
subprocess.run([FF, "-y", "-ss", "100", "-i", str(OUT), "-frames:v", "1",
                str(grab)], capture_output=True)
print("still:", grab)
