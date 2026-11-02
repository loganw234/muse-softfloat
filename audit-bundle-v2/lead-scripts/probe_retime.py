import re, subprocess, sys
from pathlib import Path
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
SEG = Path("worktrees/w6-filmretime/video/segments")
OUT = Path("scratch/lead/retime_stills")
OUT.mkdir(parents=True, exist_ok=True)
names = ["intro3.mp4", "idea2-1440p.mp4", "why3-1440p.mp4", "gitvisual7.mp4", "outro3.mp4"]
total = 0.0
for n in names:
    p = subprocess.run([FF, "-i", str(SEG / n)], capture_output=True, text=True)
    err = p.stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    v = re.search(r"Video:.*?(\d+x\d+).*?(\d+(?:\.\d+)?) fps", err)
    audio = "Audio:" in err
    print(f"{n:20s} {dur:7.2f}s  {v.group(1)} @{v.group(2)}fps  audio={audio}")
    total += dur
print(f"native total {total:.2f}s -> at 124 BPM {total * 120 / 124:.2f}s (cap 180)")

grabs = [("why3-1440p.mp4", 1.0, "why_1s.png"), ("why3-1440p.mp4", 3.0, "why_3s.png"),
         ("intro3.mp4", 5.2, "intro_middive.png"), ("idea2-1440p.mp4", 24.0, "idea_question.png"),
         ("outro3.mp4", 11.0, "outro_end.png"), ("gitvisual7.mp4", 60.0, "git_gate.png")]
for n, t, out in grabs:
    subprocess.run([FF, "-y", "-ss", str(t), "-i", str(SEG / n), "-frames:v", "1",
                    str(OUT / out)], capture_output=True)
    print("grab", out)
