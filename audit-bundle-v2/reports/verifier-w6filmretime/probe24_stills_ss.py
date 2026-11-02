"""Probes 2+4: stills/joins + SS default vs measurements vs shipped MP4."""
import subprocess, sys
import numpy as np
from PIL import Image
sys.path.insert(0, "worktrees/verify6-filmretime/video/segments")
sys.path.insert(0, "worktrees/verify6-filmretime/video")

COPY = "worktrees/verify6-filmretime/video/segments"
FF = ".venv/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v1.exe"
FF = ".venv/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"
OUT = "scratch/verifier-w6filmretime"

def grab(mp4, t, dest):
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error",
                    "-ss", str(t), "-i", f"{COPY}/{mp4}",
                    "-frames:v", "1", dest], check=True)
    return Image.open(dest).convert("RGB")

def dom(im, q=8):
    a = np.asarray(im).reshape(-1, 3)
    c = (a // q * q + q // 2).mean(axis=0)
    return tuple(int(v) for v in a.mean(axis=0)), tuple(int(v) for v in
        np.median(a, axis=0))

jobs = [("why3-1440p.mp4", 0.2, f"{OUT}/p2_why_t02.png"),
        ("why3-1440p.mp4", 1.0, f"{OUT}/p2_why_t10.png"),
        ("why3-1440p.mp4", 3.0, f"{OUT}/p2_why_t30.png"),
        ("idea2-1440p.mp4", 22.0, f"{OUT}/p2_idea_t220.png"),
        ("idea2-1440p.mp4", 25.5, f"{OUT}/p2_idea_t255.png"),
        ("intro3.mp4", 6.9, f"{OUT}/p4_intro_last.png"),
        ("outro3.mp4", 0.05, f"{OUT}/p4_outro_first.png"),
        ("intro3.mp4", 5.4, f"{OUT}/p4_intro_mid550.png")]
for mp4, t, d in jobs:
    im = grab(mp4, t, d)
    print(d.split("/")[-1], "mean=", tuple(int(v) for v in
          np.asarray(im).mean(axis=(0, 1))), "size=", im.size)

# SS defaults vs measurements3.json
import json, os
import intro_outro as io
print("default SS (no env override):", repr(os.environ.get("MSF_SS")),
      "-> module SS =", io.SS, "canvas =", (io.W, io.H))
m = json.loads(open(f"{COPY}/measurements3.json").read())
print("measurements3: ss =", m["ss"], "internal =", m["internal_resolution"],
      "K =", m["scale_K"])

def mid_dive(ss):
    with io.canvas(ss):
        period = io.measure_period()
        plate = period["plate"]
        tgt = (period["raster_centroid"][0] + 0.5,
               period["raster_centroid"][1] + 0.5)
        final_w = max(1.2, min(period["ink"]["w"],
                               period["ink"]["h"] * 16 / 9) * 0.55)
        t = 5.4
        u = min(1.0, (t - 4.5) / 2.0)
        center, cw = io.intro_cam(u, tgt, final_w, plate.width, plate.height)
        img, _, _ = io.camera(plate, center, cw, plate.width, plate.height,
                              io.OW, io.OH)
        return img.convert("RGB"), cw, center

def edge_metric(im):
    g = np.asarray(im.convert("L"), dtype=np.float64)
    lap = (4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1]
           - g[1:-1, :-2] - g[1:-1, 2:])
    return float((lap ** 2).mean())

ship = Image.open(f"{OUT}/p4_intro_mid550.png")
print("shipped mid-dive edge energy:", round(edge_metric(ship), 2))
for ss in (1, 2):
    im, cw, ce = mid_dive(ss)
    im.save(f"{OUT}/p4_mid_ss{ss}.png")
    a, b = np.asarray(im).astype(float), np.asarray(ship).astype(float)
    mse = float(((a - b) ** 2).mean())
    print(f"SS={ss}: crop_w={round(cw,1)} center={[round(c,1) for c in ce]} "
          f"edge={round(edge_metric(im),2)} MSE-vs-shipped={round(mse,1)}")
