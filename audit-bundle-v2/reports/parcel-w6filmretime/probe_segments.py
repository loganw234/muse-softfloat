import json, re, subprocess, sys
from collections import Counter
from pathlib import Path
import imageio_ffmpeg
from PIL import Image
SEG = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-filmretime\video\segments")
OUT = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-w6filmretime")
FF = imageio_ffmpeg.get_ffmpeg_exe()
FILES = ["intro3.mp4", "idea2-1440p.mp4", "why3-1440p.mp4", "gitvisual7.mp4", "outro3.mp4"]
EXP = [7.0, 26.0, 32.0, 108.0, 12.0]
rows = []
for name, exp in zip(FILES, EXP):
    p = SEG / name
    r = subprocess.run([FF, "-hide_banner", "-i", str(p)], capture_output=True, text=True)
    err = r.stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    dur = int(m.group(1))*3600 + int(m.group(2))*60 + float(m.group(3))
    ms = re.search(r"Stream.*Video:.*?, (\d+x\d+).*?(\d+(?:\.\d+)?) fps", err)
    fc = subprocess.run([FF, "-hide_banner", "-i", str(p), "-map", "0:v:0", "-c", "copy", "-f", "null", "-"],
                        capture_output=True, text=True)
    fm = re.findall(r"frame=\s*(\d+)", fc.stderr)
    frames = int(fm[-1]) if fm else None
    rows.append(dict(file=name, expected=exp, duration=dur, res=ms.group(1) if ms else None,
                     fps=float(ms.group(2)) if ms else None, frames=frames,
                     frames_over_30=round(frames/30, 3) if frames else None, bytes=p.stat().st_size))
    print(rows[-1], flush=True)
print("sum durations(ffmpeg header) =", round(sum(r_["duration"] for r_ in rows), 3))
print("sum expected =", sum(EXP), " sum frames/30 =", round(sum(r_["frames"] for r_ in rows)/30, 3))
(OUT / "segment_probe.json").write_text(json.dumps(rows, indent=1))

def grab(name, t, fn):
    f = OUT / fn
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-ss", str(t), "-i", str(SEG/name),
                    "-frames:v", "1", str(f)], check=True)
    im = Image.open(f).convert("RGB")
    px = list(im.getdata())
    dom, cnt = Counter(px).most_common(1)[0]
    print(f"{fn} {name}@{t}s size={im.size} dominant={dom} {cnt}/{len(px)} corner={im.getpixel((5,5))} center={im.getpixel((1280,720))}")
    return im

grab("intro3.mp4", 6.9, "probe_intro_last.png")
grab("intro3.mp4", 5.2, "probe_intro_middive.png")
grab("outro3.mp4", 0.0, "probe_outro_first.png")
grab("outro3.mp4", 11.5, "probe_outro_last.png")
grab("idea2-1440p.mp4", 24.0, "probe_idea_question.png")
grab("why3-1440p.mp4", 0.2, "probe_why_02.png")
grab("why3-1440p.mp4", 2.0, "probe_why_spec.png")
grab("why3-1440p.mp4", 31.9, "probe_why_last.png")
grab("gitvisual7.mp4", 0.5, "probe_git_first.png")
grab("gitvisual7.mp4", 61.0, "probe_git_gate1.png")
grab("gitvisual7.mp4", 107.9, "probe_git_last.png")
