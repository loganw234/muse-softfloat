"""Rough-draft intro/outro scenes: phone messenger chat, programmatic only.

1920x1080 @ 30fps, cuts on the 120 BPM / 0.5 s beat grid (video/style.py).
INTRO (4.0 s): phone flies in, typing dots, sent message types out,
camera zooms into the final period -> flat white plane (handoff frame).
OUTRO (6.0 s): near-black, typing dots emerge, pull back to the phone,
reply message types out.
"""
from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
VIDEO = HERE.parent.parent / "video"
sys.path.insert(0, str(VIDEO))
import style as S  # noqa: E402
import imageio_ffmpeg  # noqa: E402

W, H, FPS = S.W, S.H, S.FPS

INTRO_MSG = "Hey Muse, I've got an idea..."
REPLY_1 = "Always. Here is the headline:"
REPLY_2 = (
    "Full IEEE 754 softfloat for the RP2040 \u2014 849 of 849 "
    "(783 Clause 5 + 66 Tier 2 across b16/b32/b64, H=20). "
    "IAS15 bit-identical on all 6 chips (2,001/2,001 state hashes), "
    "KissFFT 12/12 configs, 411,213 vectors in the merge gate. "
    "Method: small parcels, each met by a verifier that only disconfirms "
    "\u2014 114/120 plants caught (pinned bc807e6)."
)

BLUE = (29, 101, 242)
GREY = (44, 48, 66)
DOT = (150, 160, 185)
NEAR_BLACK = (3, 4, 9)
WHITE = (255, 255, 255)

PHONE = dict(x0=690, x1=1230, y0=70, y1=1010)


def stage(t: float):
    import numpy as np
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


def wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
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


def bubble(draw: ImageDraw.ImageDraw, img: Image.Image, lines: list[str],
           font, fill, right: bool, top: int, max_w: int = 380,
           pad_x: int = 22, pad_y: int = 14) -> tuple[int, int, int]:
    ascent, descent = font.getmetrics()
    lh = ascent + descent + 6
    widths = [draw.textlength(s, font=font) for s in lines]
    bw = int(max(widths)) + pad_x * 2
    bh = lh * len(lines) + pad_y * 2 - 6
    x0p, x1p = PHONE["x0"] + 34, PHONE["x1"] - 34
    if right:
        x1, x0 = x1p, x1p - bw
    else:
        x0, x1 = x0p, x0p + bw
    y0, y1 = top, top + bh
    draw.rounded_rectangle([x0, y0, x1, y1], radius=26, fill=fill)
    for i, s in enumerate(lines):
        draw.text((x0 + pad_x, y0 + pad_y + i * lh), s, font=font,
                  fill=(255, 255, 255))
    return x0, y0, y1


def draw_phone(base_t: float, sent_chars: int | None, typing: bool,
               reply1: bool, reply2_chars: int | None,
               dots_t: float) -> tuple[Image.Image, tuple, tuple]:
    img = stage(base_t)
    d = ImageDraw.Draw(img)
    x0, x1, y0, y1 = PHONE["x0"], PHONE["x1"], PHONE["y0"], PHONE["y1"]
    d.rounded_rectangle([x0 - 14, y0 - 14, x1 + 14, y1 + 14], radius=54,
                        fill=(24, 27, 44), outline=(60, 70, 100), width=3)
    d.rounded_rectangle([x0, y0, x1, y1], radius=42, fill=(13, 16, 28))
    f_status = S.font("body", 24)
    d.text((x0 + 30, y0 + 16), "9:41", font=f_status, fill=S.DIM)
    d.rounded_rectangle([x1 - 90, y0 + 22, x1 - 30, y0 + 40], radius=8,
                        outline=S.DIM, width=2)
    d.rectangle([x1 - 84, y0 + 27, x1 - 62, y0 + 35], fill=S.DIM)
    f_head = S.font("bold", 32)
    d.text((x0 + 30, y0 + 62), "<", font=f_head, fill=S.DIM)
    d.ellipse([x0 + 80, y0 + 60, x0 + 128, y0 + 108], fill=S.CYAN)
    f_av = S.font("black", 30)
    d.text((x0 + 93, y0 + 64), "M", font=f_av, fill=(9, 11, 20))
    d.text((x0 + 142, y0 + 58), "Muse", font=S.font("bold", 30), fill=S.INK)
    d.ellipse([x0 + 142, y0 + 96, x0 + 154, y0 + 108], fill=S.GREEN)
    d.text((x0 + 162, y0 + 92), "online", font=S.font("body", 22), fill=S.DIM)
    d.line([x0 + 20, y0 + 128, x1 - 20, y0 + 128], fill=(40, 46, 70), width=2)
    f_msg = S.font("body", 27)
    y = y0 + 160
    period_xy = (x1 - 60, y + 20)
    if sent_chars is not None:
        shown = INTRO_MSG[:sent_chars]
        lines = [shown] if shown else [""]
        ascent, _descent = f_msg.getmetrics()
        bx0, by0, by1 = bubble(d, img, lines, f_msg, BLUE, True, y)
        if shown:
            before = INTRO_MSG[:sent_chars - 1] if sent_chars else ""
            last = shown[-1:]
            tx = bx0 + 22
            ty = by0 + 14
            x_before = d.textlength(before, font=f_msg)
            w_last = max(4, d.textlength(last, font=f_msg))
            period_xy = (tx + x_before + w_last / 2, ty + ascent / 2)
        y = by1 + 24
    typing_xy = (x0 + 34 + 70, y + 30)
    if typing:
        n = 3
        bw_ = 150
        tx0 = x0 + 34
        d.rounded_rectangle([tx0, y, tx0 + bw_, y + 60], radius=26, fill=GREY)
        for i in range(n):
            cx = tx0 + 38 + i * 38
            cy = y + 30 + math.sin(dots_t * 9 + i * 2.1) * 6
            d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=DOT)
        y += 84
    if reply1:
        l1 = wrap(d, REPLY_1, f_msg, 380)
        _bx0, _by0, by1 = bubble(d, img, l1, f_msg, GREY, False, y)
        y = by1 + 24
    if reply2_chars is not None:
        f_reply = S.font("body", 22)
        full_lines = wrap(d, REPLY_2, f_reply, 380)
        shown_lines: list[str] = []
        budget = reply2_chars
        for ln in full_lines:
            if budget <= 0:
                break
            shown_lines.append(ln[:budget])
            budget -= len(ln)
        bubble(d, img, shown_lines if shown_lines else [""], f_reply,
               GREY, False, y, max_w=380)
    f_in = S.font("body", 24)
    d.rounded_rectangle([x0 + 24, y1 - 78, x1 - 96, y1 - 24], radius=27,
                        outline=(60, 70, 100), width=2)
    d.text((x0 + 52, y1 - 66), "Message...", font=f_in, fill=S.FAINT)
    d.ellipse([x1 - 76, y1 - 74, x1 - 28, y1 - 28], fill=BLUE)
    d.text((x1 - 66, y1 - 70), "^", font=S.font("bold", 26),
           fill=(255, 255, 255))
    return img, period_xy, typing_xy


def encode(frames: list[Image.Image], out: Path):
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


def render_intro() -> tuple[Path, tuple]:
    frames: list[Image.Image] = []
    n = int(4.0 * FPS)
    full, period_xy, _ = draw_phone(2.0, len(INTRO_MSG), False, False, None, 0.0)
    for i in range(n):
        t = i / FPS
        if t < 3.5:
            sent = None
            typing = False
            if t >= 1.5:
                k = min(1.0, (t - 1.5) / 0.5)
                sent = max(1, int(len(INTRO_MSG) * k))
            elif t >= 0.5:
                typing = True
            img, period_xy, _ = draw_phone(t, sent, typing, False, None, t)
            if t >= 2.0:
                k = min(1.0, (t - 2.0) / 1.5)
                e = k * k
                cw = max(10, int(W * (1 - e) + 10 * e))
                ch = max(6, int(H * (1 - e) + 6 * e))
                cx = min(max(period_xy[0], cw / 2), W - cw / 2)
                cy = min(max(period_xy[1], ch / 2), H - ch / 2)
                crop = full.crop((int(cx - cw / 2), int(cy - ch / 2),
                                  int(cx + cw / 2), int(cy + ch / 2)))
                img = crop.resize((W, H), Image.BILINEAR)
            elif t < 0.5:
                k = S.ease_out_cubic(t / 0.5)
                small = img.resize((max(1, int(W * (0.7 + 0.3 * k))),
                                    max(1, int(H * (0.7 + 0.3 * k)))),
                                   Image.BILINEAR)
                canvas = stage(t)
                canvas.paste(small, ((W - small.width) // 2,
                                     (H - small.height) // 2))
                if k < 1.0:
                    img = Image.blend(stage(t), canvas, k)
                else:
                    img = canvas
        else:
            img = Image.new("RGB", (W, H), WHITE)
        frames.append(img.convert("RGB"))
    out = HERE / "intro.mp4"
    encode(frames, out)
    return out, period_xy


def render_outro():
    frames: list[Image.Image] = []
    n = int(6.0 * FPS)
    phone_typing, _, _ = draw_phone(1.5, len(INTRO_MSG), True, False, None, 1.5)
    for i in range(n):
        t = i / FPS
        if t < 1.0:
            k = S.ease_out_cubic(t / 1.0)
            img = Image.new("RGB", (W, H), NEAR_BLACK)
            d = ImageDraw.Draw(img)
            for j in range(3):
                r = int(10 + 26 * k)
                cx = W / 2 + (j - 1) * 90
                cy = H / 2 + math.sin(t * 9 + j * 2.1) * 10
                a = int(120 + 135 * k)
                d.ellipse([cx - r, cy - r, cx + r, cy + r],
                          fill=(150, 160, 185))
                _ = a
            frames.append(img)
        elif t < 2.5:
            k = S.ease_out_cubic((t - 1.0) / 1.5)
            scale = 1.6 - 0.6 * k
            sw, sh = int(W / scale), int(H / scale)
            cx, cy = W / 2, H / 2 - 40
            crop = phone_typing.crop((int(cx - sw / 2), int(cy - sh / 2),
                                      int(cx + sw / 2), int(cy + sh / 2)))
            img = crop.resize((W, H), Image.BILINEAR)
            if k < 1.0:
                dark = Image.new("RGB", (W, H), NEAR_BLACK)
                img = Image.blend(dark, img, k)
            frames.append(img)
        else:
            r1 = True
            r2 = None
            if t >= 3.0:
                k = min(1.0, (t - 3.0) / 2.0)
                tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
                full_lines = wrap(tmp, REPLY_2, S.font("body", 22), 380)
                full = " ".join(full_lines)
                r2 = max(1, int(len(full) * k))
                if k >= 1.0:
                    r2 = len(full)
            elif t < 2.5 + 0.5:
                r1 = (t - 2.5) > 0.15
            img, _, _ = draw_phone(t, len(INTRO_MSG), False, r1, r2, t)
            frames.append(img)
    out = HERE / "outro.mp4"
    encode(frames, out)
    return out


if __name__ == "__main__":
    p1, pxy = render_intro()
    print(f"intro -> {p1} period={pxy}")
    p2 = render_outro()
    print(f"outro -> {p2}")
