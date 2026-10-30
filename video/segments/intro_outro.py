"""v3 text/pacing pass: intro3/outro3 at NATIVE 2560x1440 @ 30 fps.

Parametric rescale of render_v2.py's 1920x1080 design by K=4/3 on
every coordinate, size and font (design values below are 1080p units,
scaled by sc()); the period centroid and camera clamps are RE-MEASURED
at 1440p (measurements3.json). Handoff frame VALUES unchanged: intro
ends on source white (255,255,255), outro opens on source near-black
(3,4,9). Copy/timing per ledger/briefs/study-video-textpacing.md
THE RULE (dwell from word count; see BLOCKS_INTRO/BLOCKS_OUTRO).
Frames stream to ffmpeg one at a time (v2 buffered; at 1440p that
would break the memory ceiling). v1/v2 artifacts never written.
Run: $MSF_PYTHON intro_outro.py
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
VIDEO = HERE.parent.parent / "video"
sys.path.insert(0, str(VIDEO))
import style as S  # noqa: E402
import imageio_ffmpeg  # noqa: E402

W, H, FPS = 2560, 1440, 30
K = W / 1920.0  # 1.333... design scale 1080p -> 1440p


def sc(v: float) -> int:
    return int(round(v * K))


def F(kind: str, size: float):
    return S.font(kind, sc(size))


INTRO_MSG = "Hey Muse, I've got an idea..."
REPLY_1 = "Done \u2014 it held up."
REPLY_2 = "Identical on all 6 boards."
LP_TITLE = "HUMAN : AI SPLIT"
LP_PROJ = "PROJECT 1,196,128,770 tokens"
LP_OWNER = "OWNER ~1,928 typed (est.)"
LP_NOTE = "true bar <1 px wide"
LP_RATIO = "\u2248 1 : 620,000"
LP_TAG = "Billed vs typed tokens (est.)"
STATS = [
    ("849 / 849", "versions across 3 sizes"),
    ("411,213", "checks before merging"),
    ("6 boards", "IAS15 \u00b7 2,001/2,001 checks"),
]
PANEL_T = [3.5, 4.0, 4.5, 5.0, 5.5, 6.0]  # LP1 LP2 LP3 S1 S2 S3

BLUE = (29, 101, 242)
GREY = (44, 48, 66)
DOT = (150, 160, 185)
NEAR_BLACK = (3, 4, 9)
WHITE = (255, 255, 255)
FRAME_C = (W / 2 - 0.5, H / 2 - 0.5)
FRAME_CC = (W / 2, H / 2)
CENTER_LEAD = 0.45
INTRO_DUR, OUTRO_DUR = 7.0, 8.5

PHONE_I = dict(x0=sc(690), x1=sc(1230), y0=sc(70), y1=sc(1010))
PHONE_O = dict(x0=sc(880), x1=sc(1420), y0=sc(70), y1=sc(1010))
OUTRO_TYPING_TOP = PHONE_O["y0"] + sc(310)

# audit blocks: (name, t_full, t_gone, lines); typed text t0 = full text
BLOCKS_INTRO = [("intro-msg (typed 1.0-1.5)", 1.5, 4.5, [INTRO_MSG])]
BLOCKS_OUTRO = [
    ("reply-1", 2.5, OUTRO_DUR, [REPLY_1]),
    ("reply-2 (typed 3.0-4.0)", 4.0, OUTRO_DUR, [REPLY_2]),
    ("panel-left-1", PANEL_T[0], OUTRO_DUR, [LP_TITLE, LP_PROJ]),
    ("panel-left-2", PANEL_T[1], OUTRO_DUR, [LP_OWNER, LP_NOTE]),
    ("panel-left-3", PANEL_T[2], OUTRO_DUR, [LP_RATIO, LP_TAG]),
    ("stat-1", PANEL_T[3], OUTRO_DUR, list(STATS[0])),
    ("stat-2", PANEL_T[4], OUTRO_DUR, list(STATS[1])),
    ("stat-3", PANEL_T[5], OUTRO_DUR, list(STATS[2])),
]


def smootherstep(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * x * (x * (x * 6 - 15) + 10)


def stage(t: float) -> Image.Image:
    grad = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None, None]
    top = np.array(S.BG2, dtype=np.float32)[None, None, :]
    bot = np.array(S.BG, dtype=np.float32)[None, None, :]
    arr = (top * (1 - grad) + bot * grad).astype(np.uint8)
    arr = np.repeat(arr, W, axis=1)
    img = Image.fromarray(arr, "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    step = sc(64)
    ox = int((t * sc(24)) % step)
    r = sc(2)
    for x in range(-step + ox, W, step):
        for y in range(sc(32), H, step):
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 18))
    return img.convert("RGB")


def wrap(draw, text_, font, max_w):
    words, lines, cur = text_.split(" "), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def bubble(draw, ph, lines, font, fill, right, top):
    pad_x, pad_y = sc(22), sc(14)
    ascent, descent = font.getmetrics()
    lh = ascent + descent + sc(6)
    widths = [draw.textlength(s, font=font) for s in lines]
    bw = int(max(widths)) + pad_x * 2 if widths else pad_x * 2
    bh = lh * len(lines) + pad_y * 2 - sc(6)
    x0p, x1p = ph["x0"] + sc(34), ph["x1"] - sc(34)
    if right:
        x1, x0 = x1p, x1p - bw
    else:
        x0, x1 = x0p, x0p + bw
    y0, y1 = top, top + bh
    draw.rounded_rectangle([x0, y0, x1, y1], radius=sc(26), fill=fill)
    for i, s in enumerate(lines):
        draw.text((x0 + pad_x, y0 + pad_y + i * lh), s, font=font,
                  fill=(255, 255, 255))
    return dict(x0=x0, y0=y0, x1=x1, y1=y1, tx=x0 + pad_x, ty=y0 + pad_y, lh=lh)


def phone_chrome(d, ph):
    x0, x1, y0, y1 = ph["x0"], ph["x1"], ph["y0"], ph["y1"]
    d.rounded_rectangle([x0 - sc(14), y0 - sc(14), x1 + sc(14), y1 + sc(14)],
                        radius=sc(54), fill=(24, 27, 44),
                        outline=(60, 70, 100), width=sc(3))
    d.rounded_rectangle([x0, y0, x1, y1], radius=sc(42), fill=(13, 16, 28))
    d.text((x0 + sc(30), y0 + sc(16)), "9:41", font=F("body", 24), fill=S.DIM)
    d.rounded_rectangle([x1 - sc(90), y0 + sc(22), x1 - sc(30), y0 + sc(40)],
                        radius=sc(8), outline=S.DIM, width=sc(2))
    d.rectangle([x1 - sc(84), y0 + sc(27), x1 - sc(62), y0 + sc(35)], fill=S.DIM)
    d.text((x0 + sc(30), y0 + sc(62)), "<", font=F("bold", 32), fill=S.DIM)
    d.ellipse([x0 + sc(80), y0 + sc(60), x0 + sc(128), y0 + sc(108)], fill=S.CYAN)
    d.text((x0 + sc(93), y0 + sc(64)), "M", font=F("black", 30), fill=(9, 11, 20))
    d.text((x0 + sc(142), y0 + sc(58)), "Muse", font=F("bold", 30), fill=S.INK)
    d.ellipse([x0 + sc(142), y0 + sc(96), x0 + sc(154), y0 + sc(108)], fill=S.GREEN)
    d.text((x0 + sc(162), y0 + sc(92)), "online", font=F("body", 22), fill=S.DIM)
    d.line([x0 + sc(20), y0 + sc(128), x1 - sc(20), y0 + sc(128)],
           fill=(40, 46, 70), width=sc(2))
    d.rounded_rectangle([x0 + sc(24), y1 - sc(78), x1 - sc(96), y1 - sc(24)],
                        radius=sc(27), outline=(60, 70, 100), width=sc(2))
    d.text((x0 + sc(52), y1 - sc(66)), "Message...", font=F("body", 24),
           fill=S.FAINT)
    d.ellipse([x1 - sc(76), y1 - sc(74), x1 - sc(28), y1 - sc(28)], fill=BLUE)
    d.text((x1 - sc(66), y1 - sc(70)), "^", font=F("bold", 26),
           fill=(255, 255, 255))


def typing_bubble(d, ph, top, dots_t):
    tx0 = ph["x0"] + sc(34)
    d.rounded_rectangle([tx0, top, tx0 + sc(150), top + sc(60)],
                        radius=sc(26), fill=GREY)
    centers = []
    for i in range(3):
        cx = tx0 + sc(38) + i * sc(38)
        cy = top + sc(30) + math.sin(dots_t * 9 + i * 2.1) * sc(6)
        centers.append((cx, cy))
        r = sc(10)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=DOT)
    return dict(x0=tx0, y0=top, x1=tx0 + sc(150), y1=top + sc(60),
                centroid=(tx0 + sc(76), top + sc(30)), centers=centers)


def components(mask: np.ndarray):
    h, w = mask.shape
    seen = np.zeros_like(mask)
    out = []
    for sy in range(h):
        for sx in range(w):
            if mask[sy, sx] and not seen[sy, sx]:
                q = deque([(sy, sx)])
                seen[sy, sx] = True
                ys, xs = [], []
                while q:
                    y, x = q.popleft()
                    ys.append(y)
                    xs.append(x)
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] \
                                and not seen[ny, nx]:
                            seen[ny, nx] = True
                            q.append((ny, nx))
                out.append((np.array(ys), np.array(xs)))
    return out


def draw_intro_scene(t, sent_chars, typing):
    img = stage(t)
    d = ImageDraw.Draw(img)
    phone_chrome(d, PHONE_I)
    f_msg = F("body", 27)
    y = PHONE_I["y0"] + sc(160)
    info = {}
    if sent_chars is not None:
        shown = INTRO_MSG[:sent_chars]
        info = bubble(d, PHONE_I, [shown] if shown else [""], f_msg,
                      BLUE, True, y)
        y = info["y1"] + sc(24)
    if typing:
        typing_bubble(d, PHONE_I, y, t)
    return img, info


def measure_period():
    """Raster-measure final '.' ink centroid at 1440p (re-measured)."""
    plate, info = draw_intro_scene(4.5, len(INTRO_MSG), False)
    f_msg = F("body", 27)
    d = ImageDraw.Draw(plate)
    arr = np.asarray(plate).astype(np.int32)
    x0, y0, x1, y1 = info["x0"], info["y0"], info["x1"], info["y1"]
    crop = arr[y0:y1, x0:x1]
    mask = crop[:, :, 0] > 150
    comps = components(mask)
    small = []
    for ys, xs in comps:
        hgt = ys.max() - ys.min() + 1
        wid = xs.max() - xs.min() + 1
        if hgt <= sc(12) and wid <= sc(12) and ys.min() > mask.shape[0] // 2:
            small.append((ys, xs))
    small.sort(key=lambda c: c[1].max())
    ys, xs = small[-1]
    wts = crop[ys, xs, 0].astype(np.float64) - 29.0
    cx = float((xs * wts).sum() / wts.sum()) + x0
    cy = float((ys * wts).sum() / wts.sum()) + y0
    ink = dict(w=int(xs.max() - xs.min() + 1), h=int(ys.max() - ys.min() + 1),
               bbox=[int(xs.min() + x0), int(ys.min() + y0),
                     int(xs.max() + x0), int(ys.max() + y0)], px=int(len(xs)))
    tx, ty = info["tx"], info["ty"]
    adv_before = d.textlength(INTRO_MSG[:-1], font=f_msg)
    adv_full = d.textlength(INTRO_MSG, font=f_msg)
    gx = tx + adv_before
    bb = d.textbbox((gx, ty), ".", font=f_msg)
    met = ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)
    ascent, _ = f_msg.getmetrics()
    v1 = (tx + adv_before + max(4, d.textlength(".", font=f_msg)) / 2,
          ty + ascent / 2)
    return dict(raster_centroid=[round(cx, 2), round(cy, 2)], ink=ink,
                n_dot_components=len(small),
                metrics_centroid=[round(met[0], 2), round(met[1], 2)],
                v1_formula=[round(v1[0], 2), round(v1[1], 2)],
                raster_minus_metrics=[round(cx - met[0], 2),
                                       round(cy - met[1], 2)],
                raster_minus_v1=[round(cx - v1[0], 2), round(cy - v1[1], 2)],
                adv_full=round(float(adv_full), 1),
                bubble=info, plate=plate)


def camera(img, center, crop_w):
    crop_w = min(float(crop_w), float(W))
    crop_h = crop_w * H / W
    cx = min(max(center[0], crop_w / 2), W - crop_w / 2)
    cy = min(max(center[1], crop_h / 2), H - crop_h / 2)
    box = (max(0.0, cx - crop_w / 2), max(0.0, cy - crop_h / 2),
           min(float(W), cx + crop_w / 2), min(float(H), cy + crop_h / 2))
    return img.resize((W, H), Image.BILINEAR, box=box), (cx, cy), box


def intro_cam(u, target, final_w):
    ce = smootherstep(u / CENTER_LEAD)
    center = (S.lerp(FRAME_CC[0], target[0], ce),
              S.lerp(FRAME_CC[1], target[1], ce))
    cw = math.exp(S.lerp(math.log(W), math.log(final_w), smootherstep(u)))
    return center, cw


def clamp_check(target, final_w, reverse, samples=401):
    worst = 0.0
    for i in range(samples):
        u = i / (samples - 1)
        cu = 1 - u if reverse else u
        center, cw = intro_cam(cu, target, final_w)
        ch = cw * H / W
        for c, lo, hi in ((center[0], cw / 2, W - cw / 2),
                          (center[1], ch / 2, H - ch / 2)):
            worst = max(worst, lo - c, c - hi, 0.0)
    return worst


def encode_start(out):
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo",
           "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def encode_end(proc, out):
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg failed")
    print(f"wrote {out} ({out.stat().st_size} bytes)", flush=True)


def render_intro(period, final_w):
    """7.0 s: enter, dots 0.5-1.0, type 1.0-1.5, HOLD to 4.5 (rule
    dwell 3.0 s at full text), dive 4.5-6.5, white 6.5-7.0."""
    target = tuple(period["target_cont"])
    plate = period["plate"]
    n = int(INTRO_DUR * FPS)
    proof, cam_log = None, []
    want = 100 * K
    proc = encode_start(HERE / "intro3.mp4")
    for i in range(n):
        t = i / FPS
        if t >= 6.5:
            img = Image.new("RGB", (W, H), WHITE)
        elif t < 4.5:
            sent, typing = None, False
            if t >= 1.0:
                k = min(1.0, (t - 1.0) / 0.5)
                sent = len(INTRO_MSG) if k >= 1.0 else max(1, int(len(INTRO_MSG) * k))
            elif t >= 0.5:
                typing = True
            img, _ = draw_intro_scene(t, sent, typing)
            if t < 0.5:
                k = S.ease_out_cubic(t / 0.5)
                s_ = 0.94 + 0.06 * k
                small = img.resize((int(W * s_), int(H * s_)), Image.BILINEAR)
                canvas = stage(t)
                canvas.paste(small, ((W - small.width) // 2,
                                     (H - small.height) // 2))
                img = Image.blend(stage(t), canvas, 0.35 + 0.65 * k)
            img = img.convert("RGB")
        else:
            u = min(1.0, (t - 4.5) / 2.0)
            center, cw = intro_cam(u, target, final_w)
            img, used_c, _box = camera(plate, center, cw)
            cam_log.append((t, cw, used_c))
            if proof is None or abs(cw - want) < abs(proof[1] - want):
                proof = (img.copy(), cw, t, used_c)
            img = img.convert("RGB")
        proc.stdin.write(img.tobytes())
        if i % 60 == 0:
            print(f"intro frame {i}/{n}", flush=True)
    encode_end(proc, HERE / "intro3.mp4")
    return proof, cam_log


def analyze_proof(proof):
    img, cw, t, _c = proof
    img.save(HERE / "still3_period_midzoom.png")
    # centre-window component search (period is centred by design)
    ox, oy = W // 2 - 500, H // 2 - 500
    win = img.crop((ox, oy, ox + 1000, oy + 1000))
    arr = np.asarray(win).astype(np.int32)
    mask = arr.min(axis=2) > 175
    best = None
    for ys, xs in components(mask):
        if len(xs) < 70:
            continue
        wts = arr[ys, xs].min(axis=1).astype(np.float64)
        cx = float((xs * wts).sum() / wts.sum()) + ox
        cy = float((ys * wts).sum() / wts.sum()) + oy
        dist = math.hypot(cx - FRAME_C[0], cy - FRAME_C[1])
        if best is None or dist < best[0]:
            best = (dist, cx, cy, len(xs))
    _d, cx, cy, npx = best
    over = img.copy()
    d = ImageDraw.Draw(over)
    d.line([FRAME_C[0], 0, FRAME_C[0], H], fill=(255, 60, 60), width=sc(3))
    d.line([0, FRAME_C[1], W, FRAME_C[1]], fill=(255, 60, 60), width=sc(3))
    rr = sc(46)
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(60, 255, 120),
              width=sc(4))
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(60, 255, 120))
    over.save(HERE / "still3_period_proof.png")
    return dict(t=round(t, 3), crop_w=round(cw, 1),
                measured_centroid=[round(cx, 1), round(cy, 1)],
                frame_center=list(FRAME_C),
                error_px=[round(cx - FRAME_C[0], 1), round(cy - FRAME_C[1], 1)],
                error_abs=round(math.hypot(cx - FRAME_C[0],
                                            cy - FRAME_C[1]), 1),
                component_px=int(npx))


# ---------------- outro ----------------

def bar_bubble(d, x0, y0, x1, y1, fill, bars, bar_fill):
    d.rounded_rectangle([x0, y0, x1, y1], radius=sc(22), fill=fill)
    y = y0 + sc(15)
    for bw in bars:
        d.rounded_rectangle([x0 + sc(20), y, x0 + sc(20) + bw, y + sc(9)],
                            radius=sc(4), fill=bar_fill)
        y += sc(17)


def draw_outro_scene(t, typing, reply1, reply2_chars):
    img = stage(t)
    d = ImageDraw.Draw(img)
    ph = PHONE_O
    phone_chrome(d, ph)
    x0, x1, y0 = ph["x0"], ph["x1"], ph["y0"]
    d.rounded_rectangle([x1 - sc(294), y0 + sc(118), x1 - sc(34), y0 + sc(148)],
                        radius=sc(12), fill=BLUE)
    d.line([x0 + sc(20), y0 + sc(128), x1 - sc(20), y0 + sc(128)],
           fill=(40, 46, 70), width=sc(2))
    bar_bubble(d, x0 + sc(34), y0 + sc(162), x0 + sc(334), y0 + sc(222),
               (38, 42, 58), [sc(200), sc(150), sc(230)], (84, 94, 122))
    bar_bubble(d, x1 - sc(244), y0 + sc(236), x1 - sc(34), y0 + sc(284),
               (24, 80, 190), [sc(140), sc(100)], (120, 170, 245))
    y = OUTRO_TYPING_TOP
    dots = None
    if typing:
        dots = typing_bubble(d, ph, y, t)
    f_msg = F("body", 27)
    if reply1:
        l1 = wrap(d, REPLY_1, f_msg, sc(380))
        b1 = bubble(d, ph, l1, f_msg, GREY, False, y)
        y = b1["y1"] + sc(20)
    if reply2_chars is not None:
        f_r = F("body", 24)
        full = wrap(d, REPLY_2, f_r, sc(380))
        shown, budget = [], reply2_chars
        for ln in full:
            if budget <= 0:
                break
            shown.append(ln[:budget])
            budget -= len(ln) + 1
        bubble(d, ph, shown if shown else [""], f_r, GREY, False, y)
    return img, dots


def card_bg(d, x0, y0, x1, y1, accent):
    d.rounded_rectangle([x0, y0, x1, y1], radius=sc(18), fill=(16, 20, 36, 238),
                        outline=(60, 70, 100, 255), width=sc(2))
    d.rounded_rectangle([x0, y0, x0 + sc(10), y1], radius=sc(5),
                        fill=accent + (255,))


def make_panel_layers():
    """Six RGBA stage layers: left card in 3 reading stages + 3 stats."""
    layers = []
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    card_bg(d, sc(60), sc(270), sc(820), sc(730), S.CYAN)
    d.text((sc(96), sc(298)), LP_TITLE, font=F("bold", 27), fill=S.CYAN + (255,))
    d.text((sc(96), sc(346)), LP_PROJ, font=F("mono", 28), fill=S.INK + (255,))
    d.rounded_rectangle([sc(96), sc(392), sc(784), sc(426)], radius=sc(8),
                        fill=S.CYAN + (255,))
    layers.append(lay)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text((sc(96), sc(446)), LP_OWNER, font=F("mono", 28), fill=S.AMBER + (255,))
    d.rectangle([sc(96), sc(492), sc(96) + sc(3), sc(526)], fill=S.AMBER + (255,))
    d.text((sc(112), sc(494)), LP_NOTE, font=F("body", 22), fill=S.DIM + (255,))
    layers.append(lay)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.text((sc(96), sc(540)), LP_RATIO, font=F("black", 58), fill=S.INK + (255,))
    d.text((sc(96), sc(650)), LP_TAG, font=F("body", 22), fill=S.DIM + (255,))
    layers.append(lay)
    accs = [S.GREEN, S.AMBER, S.VIOLET]
    for i, ((big, small), acc) in enumerate(zip(STATS, accs)):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        y0 = 230 + i * 205
        card_bg(d, sc(1460), sc(y0), sc(1860), sc(y0 + 165), acc)
        d.text((sc(1500), sc(y0 + 28)), big, font=F("black", 54),
               fill=S.INK + (255,))
        d.text((sc(1500), sc(y0 + 102)), small, font=F("body", 25),
               fill=S.DIM + (255,))
        layers.append(lay)
    return layers


def paste_panel(base, layer, p, from_left):
    if p <= 0:
        return base
    off = int((1 - p) * (-sc(18) if from_left else sc(18)))
    lay = layer.copy()
    a = lay.getchannel("A").point(lambda v: int(v * min(1.0, p)))
    lay.putalpha(a)
    base.paste(lay, (off, 0), lay)
    return base


def panel_p(t, start):
    return S.ease_out_cubic((t - start) / 0.5) if t >= start else 0.0


def measure_dots():
    img, dots = draw_outro_scene(1.5, True, False, None)
    arr = np.asarray(img).astype(np.int32)
    x0, y0, x1, y1 = dots["x0"], dots["y0"], dots["x1"], dots["y1"]
    crop = arr[y0:y1, x0:x1]
    mask = crop[:, :, 0] > 100
    ys, xs = np.nonzero(mask)
    wts = crop[ys, xs, 0].astype(np.float64)
    rc = [round(float((xs * wts).sum() / wts.sum()) + x0, 1),
          round(float((ys * wts).sum() / wts.sum()) + y0, 1)]
    return dict(layout_centroid=list(dots["centroid"]), raster_centroid=rc,
                bubble=[x0, y0, x1, y1])


def render_outro(dots_target):
    """8.5 s: dark->dots, reverse pull-back to 2.5, reply1 2.5,
    reply2 typed 3.0-4.0, panel stages 3.5..6.0, hold to 8.5."""
    panels = make_panel_layers()
    n = int(OUTRO_DUR * FPS)
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    full2_lines = wrap(tmp, REPLY_2, F("body", 24), sc(380))
    r1_lines = wrap(tmp, REPLY_1, F("body", 27), sc(380))
    assert len(full2_lines) == 1 and len(r1_lines) == 1, (full2_lines, r1_lines)
    full2 = " ".join(full2_lines)
    proc = encode_start(HERE / "outro3.mp4")
    for i in range(n):
        t = i / FPS
        typing = t < 2.5
        r1 = t >= 2.5
        r2 = None
        if t >= 3.0:
            k = min(1.0, (t - 3.0) / 1.0)
            r2 = len(full2) if k >= 1.0 else max(1, int(len(full2) * k))
        img, _ = draw_outro_scene(t, typing, r1, r2)
        if t < 2.5:
            u = min(1.0, max(0.0, (t - 0.5) / 2.0))
            center, cw = intro_cam(1 - u, dots_target, 200.0 * K)
            img, _c, _b = camera(img, center, cw)
            if t < 0.5:
                dark = Image.new("RGB", (W, H), NEAR_BLACK)
                img = Image.blend(dark, img, S.ease_out_cubic(t / 0.5))
        else:
            for j, lay in enumerate(panels):
                img = paste_panel(img, lay, panel_p(t, PANEL_T[j]), j < 3)
        proc.stdin.write(img.convert("RGB").tobytes())
        if i % 60 == 0:
            print(f"outro frame {i}/{n}", flush=True)
    encode_end(proc, HERE / "outro3.mp4")
    return dict(reply2_wrapped=full2_lines, reply1_wrapped=r1_lines)


def cam_smoothness(cam_log):
    steps = [math.log(cam_log[i + 1][1]) - math.log(cam_log[i][1])
             for i in range(len(cam_log) - 1)]
    dstep = [abs(steps[i + 1] - steps[i]) for i in range(len(steps) - 1)]
    speeds = [math.hypot(cam_log[i + 1][2][0] - cam_log[i][2][0],
                         cam_log[i + 1][2][1] - cam_log[i][2][1]) * FPS
              for i in range(len(cam_log) - 1)]
    return dict(max_abs_dlog_step_per_frame=round(max(dstep), 5),
                first_log_step=round(steps[0], 5),
                last_log_step=round(steps[-1], 5),
                peak_center_speed_px_s=round(max(speeds), 1),
                first_center_speed_px_s=round(speeds[0], 1),
                last_center_speed_px_s=round(speeds[-1], 1))


if __name__ == "__main__":
    period = measure_period()
    plate = period.pop("plate")
    ink = period["ink"]
    final_w = max(1.2, min(ink["w"], ink["h"] * 16 / 9) * 0.55)
    period["final_crop_w"] = round(final_w, 2)
    period.pop("bubble")
    b = period["ink"]["bbox"]
    crop = plate.crop((b[0] - sc(260), b[1] - sc(70), b[2] + sc(60), b[3] + sc(70)))
    big = crop.resize((crop.width * 3, crop.height * 3), Image.NEAREST)
    bd = ImageDraw.Draw(big)
    for pt, col in ((period["raster_centroid"], (255, 60, 60)),
                    (period["v1_formula"], (255, 220, 60))):
        px, py = (pt[0] - (b[0] - sc(260))) * 3, (pt[1] - (b[1] - sc(70))) * 3
        bd.line([px - 26, py, px + 26, py], fill=col, width=3)
        bd.line([px, py - 26, px, py + 26], fill=col, width=3)
    big.save(HERE / "still3_period_bubble.png")
    target = (period["raster_centroid"][0] + 0.5,
              period["raster_centroid"][1] + 0.5)
    period["target_cont"] = [round(target[0], 2), round(target[1], 2)]
    period["intro_clamp_max_px"] = round(clamp_check(target, final_w, False), 3)
    print(json.dumps(period, indent=1))
    period["plate"] = plate
    proof, cam_log = render_intro(period, final_w)
    period.pop("plate")
    proof_m = analyze_proof(proof)
    print(json.dumps(proof_m, indent=1))
    dots = measure_dots()
    dots_t = (dots["raster_centroid"][0] + 0.5, dots["raster_centroid"][1] + 0.5)
    dots["target_cont"] = [round(dots_t[0], 2), round(dots_t[1], 2)]
    dots["outro_clamp_max_px"] = round(clamp_check(dots_t, 200.0 * K, True), 3)
    print(json.dumps(dots, indent=1))
    wrapped = render_outro(dots_t)
    smooth = cam_smoothness(cam_log)
    samples = [dict(t=round(t, 2), crop_w=round(cw, 1),
                    center=[round(c[0], 1), round(c[1], 1)])
               for (t, cw, c) in cam_log[::10]]
    meas = dict(resolution=[W, H], scale_K=round(K, 4),
                period=period, proof=proof_m, dots=dots, smooth=smooth,
                cam_samples=samples, wrapped=wrapped,
                reply_chars=dict(r1=len(REPLY_1), r2=len(REPLY_2),
                                 total=len(REPLY_1) + len(REPLY_2)))
    (HERE / "measurements3.json").write_text(json.dumps(meas, indent=1))
    (HERE / "intro_msg3.txt").write_text(INTRO_MSG + "\n")
    (HERE / "outro_msg3.txt").write_text(REPLY_1 + "\n\n" + REPLY_2 + "\n")
    print("done")

