import re, subprocess
from pathlib import Path
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
OUT = Path("scratch/lead/assembly_stills")
OUT.mkdir(parents=True, exist_ok=True)
mp4 = "muse-softfloat/video/out/assembly_v6.mp4"
p = subprocess.run([FF, "-i", mp4], capture_output=True, text=True)
err = p.stderr
m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
v = re.search(r"Video:.*? (\d{3,4}x\d{3,4})[ ,].*?(\d+(?:\.\d+)?) fps", err)
print(f"assembly {dur:.2f}s  {v.group(1)} @{v.group(2)}fps  audio={'Audio:' in err}")
print(f"size {Path(mp4).stat().st_size} bytes")

# scaled cut times: cumulative native * 120/124 -> 6.77, 31.94, 62.90, 167.42
bounds = [7.0, 33.0, 65.0, 173.0]
scaled = [b * 120.0 / 124.0 for b in bounds]
print("scaled cuts:", [f"{s:.2f}" for s in scaled])
grabs = []
for i, s in enumerate(scaled):
    grabs.append((s - 0.4, f"join{i}_before.png"))
    grabs.append((s + 0.4, f"join{i}_after.png"))
grabs += [(5.0, "intro_dive.png"), (28.0, "dup_zone.png"), (100.0, "git_mid.png"),
          (176.0, "outro_panels.png")]
for t, out in grabs:
    subprocess.run([FF, "-y", "-ss", f"{t:.2f}", "-i", mp4, "-frames:v", "1",
                    str(OUT / out)], capture_output=True)
    print(f"grab {t:7.2f}s -> {out}")
