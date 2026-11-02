"""v2 polish pass: intro2/outro2. Measured period targeting, eased cameras.

INTRO2 (5.0 s): enter, typing dots, sent message, 1-beat breath, smootherstep
log-scale dive dead-center into the final period ink -> pure white hold.
OUTRO2 (6.0 s): near-black, typing dots emerge zoomed-in, time-reversed
camera pull-back into a composed off-center phone frame, short reply,
side graphics sequenced on beats. 1920x1080 @ 30 fps, 120 BPM grid.
Never writes v1 artifacts.
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

W, H, FPS = S.W, S.H, S.FPS
INTRO_MSG = "Hey Muse, I've got an idea..."
REPLY_1 = "Done \u2014 it held up."
REPLY_2 = (
    "849/849 ops across b16/b32/b64. 411,213 vectors in the gate, "
    "IAS15 identical on all 6 boards. Small parcels; verifiers that "
    "only disconfirm."
)
BLUE = (29, 101, 242)
GREY = (44, 48, 66)
DOT = (150, 160, 185)
NEAR_BLACK = (3, 4, 9)
WHITE = (255, 255, 255)
FRAME_C = (W / 2 - 0.5, H / 2 - 0.5)   # pixel-index coords (measurement)
FRAME_CC = (W / 2, H / 2)              # continuous coords (resize box)
CENTER_LEAD = 0.45

PHONE_I = dict(x0=690, x1=1230, y0=70, y1=1010)   # intro: centered (v1)
PHONE_O = dict(x0=880, x1=1420, y0=70, y1=1010)   # outro: deliberate right


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
    ox = int((t * 24) % 64)
    for x in range(-64 + ox, W, 64):
        for y in range(32, H, 64):
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 255, 255, 18))
    return img.convert("RGB")


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(" "), [], ""
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


def bubble(draw, ph, lines, font, fill, right, top, pad_x=22, pad_y=14):
    ascent, descent = font.getmetrics()
    lh = ascent + descent + 6
    widths = [draw.textlength(s, font=font) for s in lines]
    bw = int(max(widths)) + pad_x * 2 if widths else pad_x * 2
    bh = lh * len(lines) + pad_y * 2 - 6
    x0p, x1p = ph["x0"] + 34, ph["x1"] - 34
    if right:
        x1, x0 = x1p, x1p - bw
    else:
        x0, x1 = x0p, x0p + bw
    y0, y1 = top, top + bh
    draw.rounded_rectangle([x0, y0, x1, y1], radius=26, fill=fill)
    for i, s in enumerate(lines):
        draw.text((x0 + pad_x, y0 + pad_y + i * lh), s, font=font,
                  fill=(255, 255, 255))
    return dict(x0=x0, y0=y0, x1=x1, y1=y1, tx=x0 + pad_x, ty=y0 + pad_y, lh=lh)


def phone_chrome(d, ph):
    x0, x1, y0, y1 = ph["x0"], ph["x1"], ph["y0"], ph["y1"]
    d.rounded_rectangle([x0 - 14, y0 - 14, x1 + 14, y1 + 14], radius=54,
                        fill=(24, 27, 44), outline=(60, 70, 100), width=3)
    d.rounded_rectangle([x0, y0, x1, y1], radius=42, fill=(13, 16, 28))
    d.text((x0 + 30, y0 + 16), "9:41", font=S.font("body", 24), fill=S.DIM)
    d.rounded_rectangle([x1 - 90, y0 + 22, x1 - 30, y0 + 40], radius=8,
                        outline=S.DIM, width=2)
    d.rectangle([x1 - 84, y0 + 27, x1 - 62, y0 + 35], fill=S.DIM)
    d.text((x0 + 30, y0 + 62), "<", font=S.font("bold", 32), fill=S.DIM)
    d.ellipse([x0 + 80, y0 + 60, x0 + 128, y0 + 108], fill=S.CYAN)
    d.text((x0 + 93, y0 + 64), "M", font=S.font("black", 30), fill=(9, 11, 20))
    d.text((x0 + 142, y0 + 58), "Muse", font=S.font("bold", 30), fill=S.INK)
    d.ellipse([x0 + 142, y0 + 96, x0 + 154, y0 + 108], fill=S.GREEN)
    d.text((x0 + 162, y0 + 92), "online", font=S.font("body", 22), fill=S.DIM)
    d.line([x0 + 20, y0 + 128, x1 - 20, y0 + 128], fill=(40, 46, 70), width=2)
    d.rounded_rectangle([x0 + 24, y1 - 78, x1 - 96, y1 - 24], radius=27,
                        outline=(60, 70, 100), width=2)
    d.text((x0 + 52, y1 - 66), "Message...", font=S.font("body", 24),
           fill=S.FAINT)
    d.ellipse([x1 - 76, y1 - 74, x1 - 28, y1 - 28], fill=BLUE)
    d.text((x1 - 66, y1 - 70), "^", font=S.font("bold", 26),
           fill=(255, 255, 255))


def typing_bubble(d, ph, top, dots_t):
    tx0 = ph["x0"] + 34
    d.rounded_rectangle([tx0, top, tx0 + 150, top + 60], radius=26, fill=GREY)
    centers = []
    for i in range(3):
        cx = tx0 + 38 + i * 38
        cy = top + 30 + math.sin(dots_t * 9 + i * 2.1) * 6
        centers.append((cx, cy))
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=DOT)
    return dict(x0=tx0, y0=top, x1=tx0 + 150, y1=top + 60,
                centroid=(tx0 + 76, top + 30), centers=centers)


def components(mask: np.ndarray):
    """4-connected components of a boolean mask -> list of (ys, xs)."""
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
    f_msg = S.font("body", 27)
    y = PHONE_I["y0"] + 160
    info = {}
    if sent_chars is not None:
        shown = INTRO_MSG[:sent_chars]
        info = bubble(d, PHONE_I, [shown] if shown else [""], f_msg,
                      BLUE, True, y)
        y = info["y1"] + 24
    if typing:
        typing_bubble(d, PHONE_I, y, t)
    return img, info


def measure_period():
    """Raster-measure the final '.' ink centroid on the full-message plate.

    Cross-checked against font metrics and the v1 formula. Returns dict.
    """
    plate, info = draw_intro_scene(2.0, len(INTRO_MSG), False)
    f_msg = S.font("body", 27)
    d = ImageDraw.Draw(plate)
    arr = np.asarray(plate).astype(np.int32)
    x0, y0, x1, y1 = info["x0"], info["y0"], info["x1"], info["y1"]
    crop = arr[y0:y1, x0:x1]
    mask = crop[:, :, 0] > 150  # white text ink (blue bubble R=29)
    comps = components(mask)
    small = []
    for ys, xs in comps:
        hgt = ys.max() - ys.min() + 1
        wid = xs.max() - xs.min() + 1
        if hgt <= 12 and wid <= 12 and ys.min() > mask.shape[0] // 2:
            small.append((ys, xs))
    small.sort(key=lambda c: c[1].max())
    ys, xs = small[-1]
    wts = crop[ys, xs, 0].astype(np.float64) - 29.0
    cx = float((xs * wts).sum() / wts.sum()) + x0
    cy = float((ys * wts).sum() / wts.sum()) + y0
    ink = dict(w=int(xs.max() - xs.min() + 1), h=int(ys.max() - ys.min() + 1),
               bbox=[int(xs.min() + x0), int(ys.min() + y0),
                     int(xs.max() + x0), int(ys.max() + y0)], px=int(len(xs)))
    # metrics cross-check: advance split at the last glyph + its ink bbox
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
                bubble=info, plate=plate)


def camera(img, center, crop_w):
    """Subpixel crop-zoom: float box centered on `center`, clamped in-frame."""
    crop_w = min(float(crop_w), float(W))
    crop_h = crop_w * H / W
    cx = min(max(center[0], crop_w / 2), W - crop_w / 2)
    cy = min(max(center[1], crop_h / 2), H - crop_h / 2)
    box = (max(0.0, cx - crop_w / 2), max(0.0, cy - crop_h / 2),
           min(float(W), cx + crop_w / 2), min(float(H), cy + crop_h / 2))
    return img.resize((W, H), Image.BILINEAR, box=box), (cx, cy), box


def intro_cam(u, target, final_w):
    """(center, crop_w) at dive progress u in [0,1]."""
    ce = smootherstep(u / CENTER_LEAD)
    center = (S.lerp(FRAME_CC[0], target[0], ce),
              S.lerp(FRAME_CC[1], target[1], ce))
    cw = math.exp(S.lerp(math.log(W), math.log(final_w), smootherstep(u)))
    return center, cw


def clamp_check(target, final_w, reverse, samples=401):
    """Max clamp adjustment the camera path would need (0 = never clamps)."""
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


def encode(frames, out):
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "error", "-f", "rawvideo",
           "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in frames:
        proc.stdin.write(f.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg failed")


def render_intro(period, final_w):
    target = tuple(period["target_cont"])
    plate = period["plate"]
    n = int(5.0 * FPS)
    frames, proof, cam_log = [], None, []
    for i in range(n):
        t = i / FPS
        if t >= 4.5:
            frames.append(Image.new("RGB", (W, H), WHITE))
            continue
        if t < 2.5:
            sent, typing = None, False
            if t >= 1.5:
                k = min(1.0, (t - 1.5) / 0.5)
                sent = max(1, int(len(INTRO_MSG) * k))
                if k >= 1.0:
                    sent = len(INTRO_MSG)
            elif t >= 0.5:
                typing = True
            img, _ = draw_intro_scene(t, sent, typing)
            if t < 0.5:  # gentle enter: 0.94 -> 1.0 scale, fade in
                k = S.ease_out_cubic(t / 0.5)
                sc = 0.94 + 0.06 * k
                small = img.resize((int(W * sc), int(H * sc)), Image.BILINEAR)
                canvas = stage(t)
                canvas.paste(small, ((W - small.width) // 2,
                                     (H - small.height) // 2))
                img = Image.blend(stage(t), canvas, 0.35 + 0.65 * k)
            frames.append(img.convert("RGB"))
        else:  # 2.5-4.5 dive (breath was 2.0-2.5 static hold)
            u = min(1.0, (t - 2.5) / 2.0)
            center, cw = intro_cam(u, target, final_w)
            img, used_c, _box = camera(plate, center, cw)
            cam_log.append((t, cw, used_c))
            if proof is None or abs(cw - 100) < abs(proof[1] - 100):
                proof = (img.copy(), cw, t, used_c)
            frames.append(img.convert("RGB"))
    encode(frames, HERE / "intro2.mp4")
    return proof, cam_log


def analyze_proof(proof):
    img, cw, t, _c = proof
    img.save(HERE / "still2_period_midzoom.png")
    arr = np.asarray(img).astype(np.int32)
    mask = arr.min(axis=2) > 175
    best = None
    for ys, xs in components(mask):
        if len(xs) < 40:
            continue
        wts = arr[ys, xs].min(axis=1).astype(np.float64)
        cx = float((xs * wts).sum() / wts.sum())
        cy = float((ys * wts).sum() / wts.sum())
        dist = math.hypot(cx - FRAME_C[0], cy - FRAME_C[1])
        if best is None or dist < best[0]:
            best = (dist, cx, cy, len(xs))
    _d, cx, cy, npx = best
    over = img.copy()
    d = ImageDraw.Draw(over)
    d.line([FRAME_C[0], 0, FRAME_C[0], H], fill=(255, 60, 60), width=3)
    d.line([0, FRAME_C[1], W, FRAME_C[1]], fill=(255, 60, 60), width=3)
    d.ellipse([cx - 46, cy - 46, cx + 46, cy + 46], outline=(60, 255, 120),
              width=4)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(60, 255, 120))
    over.save(HERE / "still2_period_proof.png")
    return dict(t=round(t, 3), crop_w=round(cw, 1),
                measured_centroid=[round(cx, 1), round(cy, 1)],
                frame_center=list(FRAME_C),
                error_px=[round(cx - FRAME_C[0], 1), round(cy - FRAME_C[1], 1)],
                error_abs=round(math.hypot(cx - FRAME_C[0],
                                            cy - FRAME_C[1]), 1),
                component_px=int(npx))


# ---------------- outro ----------------

OUTRO_TYPING_TOP = PHONE_O["y0"] + 310  # dots cy = 410


def bar_bubble(d, x0, y0, x1, y1, fill, bars, bar_fill):
    d.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=fill)
    y = y0 + 15
    for bw in bars:
        d.rounded_rectangle([x0 + 20, y, x0 + 20 + bw, y + 9], radius=4,
                            fill=bar_fill)
        y += 17


def draw_outro_scene(t, typing, reply1, reply2_chars):
    img = stage(t)
    d = ImageDraw.Draw(img)
    ph = PHONE_O
    phone_chrome(d, ph)
    x0, x1, y0 = ph["x0"], ph["x1"], ph["y0"]
    # scrolled history: user bubble cropped by the header, faint exchanges
    d.rounded_rectangle([x1 - 294, y0 + 118, x1 - 34, y0 + 148], radius=12,
                        fill=BLUE)
    d.line([x0 + 20, y0 + 128, x1 - 20, y0 + 128], fill=(40, 46, 70), width=2)
    bar_bubble(d, x0 + 34, y0 + 162, x0 + 334, y0 + 222, (38, 42, 58),
               [200, 150, 230], (84, 94, 122))
    bar_bubble(d, x1 - 244, y0 + 236, x1 - 34, y0 + 284, (24, 80, 190),
               [140, 100], (120, 170, 245))
    y = OUTRO_TYPING_TOP
    dots = None
    if typing:
        dots = typing_bubble(d, ph, y, t)
    f_msg = S.font("body", 27)
    if reply1:
        l1 = wrap(d, REPLY_1, f_msg, 380)
        b1 = bubble(d, ph, l1, f_msg, GREY, False, y)
        y = b1["y1"] + 20
    if reply2_chars is not None:
        f_r = S.font("body", 24)
        full = wrap(d, REPLY_2, f_r, 380)
        shown, budget = [], reply2_chars
        for ln in full:
            if budget <= 0:
                break
            shown.append(ln[:budget])
            budget -= len(ln) + 1
        bubble(d, ph, shown if shown else [""], f_r, GREY, False, y)
    return img, dots


def card_bg(d, x0, y0, x1, y1, accent):
    d.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=(16, 20, 36, 238),
                        outline=(60, 70, 100, 255), width=2)
    d.rounded_rectangle([x0, y0, x0 + 10, y1], radius=5, fill=accent + (255,))


def make_panels():
    """Four pre-rendered RGBA layers: left split card + 3 right stat cards."""
    layers = []
    # left: human:AI split, refreshed metrics, definitions on-frame
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    card_bg(d, 60, 270, 820, 730, S.CYAN)
    d.text((96, 298), "HUMAN : AI \u2014 THE WORK SPLIT", font=S.font("bold", 27),
           fill=S.CYAN + (255,))
    d.text((96, 346), "PROJECT BILLED   1,196,128,770 tokens",
           font=S.font("mono", 28), fill=S.INK + (255,))
    d.rounded_rectangle([96, 392, 784, 426], radius=8, fill=S.CYAN + (255,))
    d.text((96, 446), "OWNER TYPED   ~1,928 tokens (est.)",
           font=S.font("mono", 28), fill=S.AMBER + (255,))
    d.rectangle([96, 492, 99, 526], fill=S.AMBER + (255,))
    d.text((112, 494), "1 px is too wide \u2014 shown 3 px",
           font=S.font("body", 22), fill=S.DIM + (255,))
    d.text((96, 540), "\u2248 1 : 620,000", font=S.font("black", 58),
           fill=S.INK + (255,))
    defs = ("Owner: chars/4 \u00b130% over 40 typed prompts (tokens study, "
            "2026-10-28). Project: API-billed input+output from "
            "docs/metrics/usage.jsonl @ a73e97d (93 rows, waves 0\u20135); "
            "cached is inside input, not added.")
    ly = 626
    for ln in wrap(d, defs, S.font("body", 19), 688):
        d.text((96, ly), ln, font=S.font("body", 19), fill=S.DIM + (255,))
        ly += 24
    layers.append(lay)
    stats = [
        ("849 / 849", "instantiations \u00b7 b16/b32/b64", S.GREEN),
        ("411,213", "vectors in the merge gate", S.AMBER),
        ("6 boards", "IAS15 \u00b7 2,001/2,001 state hashes", S.VIOLET),
    ]
    for i, (big, small, acc) in enumerate(stats):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        y0 = 230 + i * 205
        card_bg(d, 1460, y0, 1860, y0 + 165, acc)
        d.text((1500, y0 + 28), big, font=S.font("black", 54),
               fill=S.INK + (255,))
        d.text((1500, y0 + 102), small, font=S.font("body", 25),
               fill=S.DIM + (255,))
        layers.append(lay)
    return layers


def paste_panel(base, layer, p, from_left):
    if p <= 0:
        return base
    off = int((1 - p) * (-18 if from_left else 18))
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
    panels = make_panels()
    n = int(6.0 * FPS)
    frames = []
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    full2 = " ".join(wrap(tmp, REPLY_2, S.font("body", 24), 380))
    for i in range(n):
        t = i / FPS
        typing = t < 3.0
        r1 = t >= 3.0
        r2 = None
        if t >= 3.5:
            k = min(1.0, (t - 3.5) / 1.5)
            r2 = len(full2) if k >= 1.0 else max(1, int(len(full2) * k))
        img, _ = draw_outro_scene(t, typing, r1, r2)
        if t < 2.5:  # reverse camera: intro curve run backwards
            u = min(1.0, max(0.0, (t - 0.5) / 2.0))
            center, cw = intro_cam(1 - u, dots_target, 200.0)
            img, _c, _b = camera(img, center, cw)
            if t < 0.5:
                dark = Image.new("RGB", (W, H), NEAR_BLACK)
                img = Image.blend(dark, img, S.ease_out_cubic(t / 0.5))
        else:
            img = paste_panel(img, panels[0], panel_p(t, 3.5), True)
            img = paste_panel(img, panels[1], panel_p(t, 4.0), False)
            img = paste_panel(img, panels[2], panel_p(t, 4.5), False)
            img = paste_panel(img, panels[3], panel_p(t, 5.0), False)
        frames.append(img.convert("RGB"))
    encode(frames, HERE / "outro2.mp4")


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
    # annotated bubble crop: red cross = raster centroid, yellow = v1 point
    b = period["ink"]["bbox"]
    crop = plate.crop((b[0] - 260, b[1] - 70, b[2] + 60, b[3] + 70))
    big = crop.resize((crop.width * 4, crop.height * 4), Image.NEAREST)
    bd = ImageDraw.Draw(big)
    for pt, col in ((period["raster_centroid"], (255, 60, 60)),
                    (period["v1_formula"], (255, 220, 60))):
        px, py = (pt[0] - (b[0] - 260)) * 4, (pt[1] - (b[1] - 70)) * 4
        bd.line([px - 26, py, px + 26, py], fill=col, width=3)
        bd.line([px, py - 26, px, py + 26], fill=col, width=3)
    big.save(HERE / "still2_period_bubble.png")
    # continuous coords for resize box: pixel index i spans [i, i+1]
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
    dots["outro_clamp_max_px"] = round(clamp_check(dots_t, 200.0, True), 3)
    print(json.dumps(dots, indent=1))
    render_outro(dots_t)
    smooth = cam_smoothness(cam_log)
    samples = [dict(t=round(t, 2), crop_w=round(cw, 1),
                    center=[round(c[0], 1), round(c[1], 1)])
               for (t, cw, c) in cam_log[::10]]
    meas = dict(period=period, proof=proof_m, dots=dots, smooth=smooth,
                cam_samples=samples,
                reply_chars=dict(r1=len(REPLY_1), r2=len(REPLY_2),
                                 total=len(REPLY_1) + len(REPLY_2)))
    (HERE / "measurements2.json").write_text(json.dumps(meas, indent=1))
    (HERE / "intro_msg2.txt").write_text(INTRO_MSG + "\n")
    (HERE / "outro_msg2.txt").write_text(REPLY_1 + "\n\n" + REPLY_2 + "\n")
    print("done")
