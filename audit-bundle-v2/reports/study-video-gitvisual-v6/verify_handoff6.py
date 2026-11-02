"""Handoff verification for gitvisual6.mp4: container facts
(duration / size / fps) via ffprobe, then exact pixel census of the
two handoff frames - t=0.5 s must be pure white (255,255,255) and
t=101.5 s the near-black (2,3,8) after encode (= outro2's first
frame), the frozen v1-v5 VALUES. Mirrors verify_handoff5.py.

Run: $MSF_PYTHON verify_handoff6.py [gitvisual6.mp4]
"""
import json, subprocess, sys
from collections import Counter
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

HERE = Path(__file__).resolve().parent
MP4 = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "gitvisual6.mp4"
FF = imageio_ffmpeg.get_ffmpeg_exe()


def probe():
    cmd = [FF.replace("ffmpeg", "ffprobe"), "-v", "error", "-select_streams", "v:0",
           "-show_entries", "stream=width,height,r_frame_rate,nb_frames",
           "-show_entries", "format=duration,size", "-of", "json", str(MP4)]
    try:
        return json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
    except Exception:
        cmd = [FF, "-hide_banner", "-i", str(MP4), "-f", "null", "-"]
        err = subprocess.run(cmd, capture_output=True, text=True).stderr
        return {"ffmpeg_stderr_tail": "\n".join(err.strip().splitlines()[-3:])}


def frame(t, name):
    out = HERE / name
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-ss", str(t),
                    "-i", str(MP4), "-frames:v", "1", str(out)], check=True)
    im = Image.open(out).convert("RGB")
    c = Counter(im.getdata())
    total = im.width * im.height
    top = c.most_common(3)
    return {"t": t, "size": [im.width, im.height], "pixels": total,
            "unique_colours": len(c),
            "top": [[list(col), n] for col, n in top]}


res = {"file": MP4.name, "probe": probe(),
       "open_0.5s": frame(0.5, "handoff6_open.png"),
       "end_101.5s": frame(101.5, "handoff6_end.png")}
(HERE / "handoff6.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
o, e = res["open_0.5s"], res["end_101.5s"]
assert o["top"][0][0] == [255, 255, 255] and o["top"][0][1] == o["pixels"], "open not pure white"
assert e["top"][0][0] == [2, 3, 8], f"end colour {e['top'][0][0]} != (2,3,8)"
print("HANDOFF OK: open pure white, end (2,3,8)")
