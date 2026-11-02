"""study-video-idea: 14.5 s 'idea breakdown' segment, 2560x1440 @ 30 fps.

Sits between the messenger intro and the why comparison: opens AND
closes on pure white (intro hand-off in, comparison hand-off out).
All motion parametric (draw-time coords/font sizes); no bitmap
crop-upscale. 120 BPM grid (BEAT=0.5 s); reveals sequential with
reading dwell (rule in report.md).

Facts only from README/RECORD/SF-0/SF-1/SF-2 at muse-softfloat a73e97d
(per-claim sources in report.md). The number-line is a definitional
illustration of correct rounding (SF-0 2.3), labelled illustrative;
no measurement is implied by it.

Run: $MSF_PYTHON render_idea.py   (MSF_PYTHON = workspace .venv python)
Frames stream to ffmpeg one at a time (memory ceiling: one frame).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
WHY = HERE.parent / "study-video-why"
sys.path.insert(0, str(WHY))
import render_why as B  # noqa: E402  (shared one-hand helpers/palette)
import imageio_ffmpeg  # noqa: E402

S = B.S
W, H, FPS = B.W, B.H, B.FPS
DUR = 14.5
NFRAMES = int(DUR * FPS)  # 435
WHITE, INKD, DIMD = B.WHITE, B.INKD, B.DIMD
GREEND, REDD, CYAND, VIOLETD, PINKD, BORDER = (
    B.GREEND, B.REDD, B.CYAND, B.VIOLETD, B.PINKD, B.BORDER)
text, card, pop, fade, header = B.text, B.card, B.pop, B.fade, B.header


def scene_idea(d, t):
    header(d, t, "THE IDEA", "one sentence, then what it demands")
    box = (330, 360, 2230, 1160)
    a = pop(t, 0.5)
    if a <= 0:
        return
    card(d, box, scale=a)
    if a <= 0.6:
        return
    lines = [
        (0.5, 520, "A software IEEE 754 floating-point library", "black", 58, INKD),
        (1.0, 630, "for the RP2040 \u2014 a chip with no FPU,", "black", 58, INKD),
        (1.5, 740, "where every float is already software \u2014", "body", 46, DIMD),
        (2.0, 880, "so real science code runs bit-identically:", "bold", 50, INKD),
        (2.5, 985, "same source on desktop and chip, same bits out.", "body", 46, GREEND),
    ]
    for t0, y, s, kind, size, col in lines:
        la = fade(t, t0)
        if la > 0:
            text(d, (W / 2, y), s, kind, size, S.blend(B.CARD, col, la))


def scene_correct(d, t):
    header(d, t, "WHAT \u201cCORRECT\u201d MEANS HERE",
           "every result the correctly rounded one \u2014 every flag exact")
    # Number line: two neighbouring representable values, exact result between.
    x0, x1, y = 430, 2130, 700
    xa, xb = 780, 1780          # neighbour ticks
    xe = 1080                    # exact (infinitely precise) result: nearer xa
    a1 = fade(t, 3.0)
    if a1 > 0:
        lc = S.blend(WHITE, INKD, a1)
        d.line([x0, y, x1, y], fill=lc, width=6)
        for x, lab in ((xa, "representable\nvalue A"), (xb, "next value\nA + 1 ULP")):
            d.line([x, y - 46, x, y + 46], fill=lc, width=6)
            for k, part in enumerate(lab.split("\n")):
                text(d, (x, y + 130 + k * 58), part, "body", 38,
                     S.blend(WHITE, DIMD, a1))
        if t < 5.0:  # prompt clears the band before the verdict labels land
            text(d, (W / 2, 430), "one operation, done exactly \u2014 where must it land?",
                 "body", 44, S.blend(WHITE, DIMD, a1))
    a2 = pop(t, 4.0)
    if a2 > 0:  # exact result dot
        r = 26 * a2
        d.ellipse([xe - r, y - r, xe + r, y + r], fill=VIOLETD)
        if a2 > 0.6:
            text(d, (xe, y - 150), "exact result", "bold", 42, VIOLETD)
            text(d, (xe, y - 95), "(infinitely precise)", "body", 32, DIMD)
    a3 = fade(t, 5.0)
    if a3 > 0:  # arrow lands on A; B marked as the wrong neighbour
        gc = S.blend(WHITE, GREEND, a3)
        ay = y - 210
        d.line([xe, ay + 60, xe, ay], fill=gc, width=8)
        d.line([xe, ay, xa + 30, ay], fill=gc, width=8)
        d.polygon([(xa - 8, ay), (xa + 34, ay - 20), (xa + 34, ay + 20)], fill=gc)
        text(d, ((xe + xa) / 2, ay - 62), "correctly rounded \u2192 A", "black", 44, gc)
        rc = S.blend(WHITE, REDD, a3)
        B.draw_sym(d, xb, y - 200, B.CROSS, rc, size=64, anchor="c")
        text(d, (xb, y - 285), "a neighbour is a wrong answer", "body", 38, rc)
    a4 = fade(t, 5.5)
    if a4 > 0:
        text(d, (W / 2, 1120),
             "not close \u2014 exact: right value, right flags, every time  (illustrative)",
             "bold", 44, S.blend(WHITE, INKD, a4))


def scene_prove(d, t):
    header(d, t, "WHAT WILL PROVE IT", "three real workloads, run on the chip")
    boxes = [(140, 420, 820, 1120), (940, 420, 1620, 1120), (1740, 420, 2420, 1120)]
    cards = [
        ("IAS15", "orbital integrator", CYAND,
         ["binary64, bit-identical", "desktop = chip,", "every bit, every step"]),
        ("INTERVAL GEOMETRY", "guaranteed enclosures", VIOLETD,
         ["directed rounding:", "down for one end,", "up for the other"]),
        ("KISSFFT \u2014 FORK B", "exact-angle FFT", PINKD,
         ["sinPi / cosPi twiddles", "made at runtime,", "correctly rounded"]),
    ]
    for i, ((name, sub, col, lines), box) in enumerate(zip(cards, boxes)):
        a = pop(t, 6.5 + i * 1.0)
        if a <= 0:
            continue
        card(d, box, scale=a)
        if a > 0.6:
            cx = (box[0] + box[2]) / 2
            text(d, (cx, 545), name, "black", 44, col)
            text(d, (cx, 615), sub, "body", 33, DIMD)
            d.line([box[0] + 60, 675, box[2] - 60, 675], fill=BORDER, width=3)
            for k, ln in enumerate(lines):
                text(d, (cx, 800 + k * 70), ln, "body", 36, INKD)


def scene_method(d, t):
    header(d, t, "HOW IT GETS BUILT", "the short version \u2014 the film shows the rest")
    rows = [
        (10.0, CYAND, "1", "briefed agents build it, parcel by parcel"),
        (10.5, VIOLETD, "2", "every piece independently verified \u2014"),
        (11.0, PINKD, "3", "a verifier whose only job is to disconfirm"),
    ]
    for i, (t0, col, num, s) in enumerate(rows):
        a = fade(t, t0)
        if a <= 0:
            continue
        y = 520 + i * 170
        d.ellipse([560, y - 52, 664, y + 52], fill=S.blend(WHITE, col, a))
        text(d, (612, y), num, "black", 52, WHITE)
        text(d, (720, y), s, "body", 48, S.blend(WHITE, INKD, a), anchor="lm")
    a = fade(t, 11.5)
    if a > 0:
        text(d, (W / 2, 1120), "watch it land, commit by commit, in a minute.",
             "body", 40, S.blend(WHITE, DIMD, a))


def scene_question(d, t):
    a = fade(t, 12.0)
    if a <= 0:
        return
    c = S.blend(WHITE, INKD, a)
    text(d, (W / 2, 560), "BUT FIRST \u2014", "black", 64, S.blend(WHITE, DIMD, a))
    text(d, (W / 2, 720), "WHY NOT USE WHAT", "black", 150, c)
    text(d, (W / 2, 910), "ALREADY SHIPS?", "black", 150, c)


def frame(t: float) -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    if t < 3.0:
        if t >= 0.5:
            scene_idea(d, t)
    elif t < 6.5:
        scene_correct(d, t)
    elif t < 10.0:
        scene_prove(d, t)
    elif t < 12.0:
        scene_method(d, t)
    else:
        scene_question(d, t)
    if t >= 13.5:  # fade to the white join; 0.75 s exact-white hold out
        a = S.ease_in_out(min(1.0, (t - 13.5) / 0.25))
        img = Image.blend(img, Image.new("RGB", (W, H), WHITE), a)
    return img


def main() -> int:
    out = HERE / "idea-1440p.mp4"
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-force_key_frames", "expr:eq(n,415)",
           "-crf", "12", "-preset", "medium", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    for i in range(NFRAMES):
        proc.stdin.write(frame(i / FPS).tobytes())
        if i % 60 == 0:
            print(f"frame {i}/{NFRAMES}", flush=True)
    proc.stdin.close()
    rc = proc.wait()
    print(f"ffmpeg rc={rc} -> {out} ({out.stat().st_size if out.exists() else 0} bytes)")
    if rc != 0:
        return rc
    twin = HERE / "idea-1080p.mp4"
    r2 = subprocess.run([exe, "-y", "-hide_banner", "-loglevel", "error",
                         "-i", str(out), "-vf", "scale=1920:1080",
                         "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                         "-crf", "16", str(twin)])
    print(f"twin rc={r2.returncode} -> {twin} ({twin.stat().st_size if twin.exists() else 0} bytes)")
    return r2.returncode


if __name__ == "__main__":
    raise SystemExit(main())
