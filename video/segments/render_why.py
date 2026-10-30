"""study-video-why: 16 s 'why a custom softfloat' segment, 2560x1440 @ 30 fps.

Designed for SLOT B (right after the messenger intro, on the white plane):
opens and closes on the intro's pure-white hold frame, so it is also
slot-A safe. All motion is parametric (coordinates/font sizes scaled at
draw time); no bitmap is ever crop-upscaled. 120 BPM grid (BEAT=0.5 s).

Claims: only what muse-softfloat/docs/studies/SF-0.md states (its S3
citations included), SF-1/SF-2 for workload requirements, RECORD for
what shipped. See options-facts.md for per-claim pointers.

Run: $MSF_PYTHON render_why.py   (MSF_PYTHON = workspace .venv python)
Frames stream to ffmpeg one at a time (memory ceiling: one frame).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
VIDEO = HERE.parent.parent / "video"
sys.path.insert(0, str(VIDEO))
import style as S  # noqa: E402
import imageio_ffmpeg  # noqa: E402

W, H, FPS = 2560, 1440, 30
DUR = 16.0
NFRAMES = int(DUR * FPS)  # 480
K = 1440 / 1080  # type scale vs video/style.py's 1080p sizes

WHITE = (255, 255, 255)
INKD = (13, 18, 38)
DIMD = (92, 102, 132)
FAINTD = (170, 178, 200)
CARD = (238, 242, 250)
BORDER = (196, 205, 226)
GREEND = (4, 140, 90)
REDD = (198, 38, 54)
AMBERD = (172, 108, 0)
CYAND = (0, 128, 168)
VIOLETD = (108, 68, 208)
PINKD = (196, 48, 118)
QUEST = (140, 148, 172)

CHECK, CROSS, QM = "\u2713", "\u2717", "?"


def F(kind: str, size: float):
    return S.font(kind, int(size * K))


def text(d: ImageDraw.ImageDraw, xy, s, kind, size, fill, anchor="mm"):
    d.text(xy, s, font=F(kind, size), fill=fill, anchor=anchor)


def card(d, box, scale=1.0, fill=CARD, outline=BORDER, width=3):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hw, hh = (x1 - x0) / 2 * scale, (y1 - y0) / 2 * scale
    d.rounded_rectangle([cx - hw, cy - hh, cx + hw, cy + hh], radius=28 * scale,
                        fill=fill, outline=outline, width=max(1, int(width * scale)))


def pop(t: float, t0: float) -> float:
    """ease_out_back pop-in scale, 0 before t0."""
    if t < t0:
        return 0.0
    return S.ease_out_back(min(1.0, (t - t0) / 0.35))


def fade(t: float, t0: float, dur=0.25) -> float:
    if t < t0:
        return 0.0
    return S.ease_in_out(min(1.0, (t - t0) / dur))


def stamp(d, cx, cy, s, color, t, t0):
    a = pop(t, t0)
    if a <= 0:
        return
    f = F("black", 44 * a)
    tw = d.textlength(s, font=f)
    pad = 26 * a
    d.rounded_rectangle([cx - tw / 2 - pad, cy - 52 * a, cx + tw / 2 + pad, cy + 52 * a],
                        radius=16 * a, outline=color, width=max(1, int(6 * a)))
    d.text((cx, cy), s, font=f, fill=color, anchor="mm")


def header(d, t, big, small, color=INKD):
    text(d, (W / 2, 150), big, "black", 84, color)
    if small:
        text(d, (W / 2, 248), small, "body", 38, DIMD)


WORKLOADS = [
    ("IAS15", "orbital integrator", CYAND,
     ["binary64 bit-identical,", "desktop = chip,", "every bit, every step"]),
    ("INTERVAL GEOMETRY", "guaranteed enclosures", VIOLETD,
     ["directed rounding on demand:", "round down / round up,", "chosen per call"]),
    ("KISSFFT \u2014 FORK B", "exact-angle FFT", PINKD,
     ["sinPi / cosPi twiddles", "generated at runtime,", "correctly rounded"]),
]


def draw_sym(d, x, y, sym, color, size=54, anchor="l"):
    """Vector check/cross (Arial Black lacks U+2713/2717); ? as text."""
    if sym == QM:
        anc = "lm" if anchor == "l" else "mm"
        d.text((x, y), QM, font=F("black", size), fill=color, anchor=anc)
        return
    r = size * K * 0.34
    cx = x + r if anchor == "l" else x
    wdt = max(3, int(size * K * 0.13))
    if sym.startswith(CHECK):
        d.line([cx - r, y + 2, cx - r * 0.3, y + r * 0.75], fill=color, width=wdt)
        d.line([cx - r * 0.3, y + r * 0.75, cx + r, y - r * 0.8], fill=color, width=wdt)
        if sym.endswith("*"):
            d.text((cx + r + 8, y - r * 0.4), "*", font=F("black", size * 0.7),
                   fill=color, anchor="mm")
    else:  # CROSS
        d.line([cx - r * 0.8, y - r * 0.8, cx + r * 0.8, y + r * 0.8], fill=color, width=wdt)
        d.line([cx - r * 0.8, y + r * 0.8, cx + r * 0.8, y - r * 0.8], fill=color, width=wdt)

SPEC = [
    "rounding attributes: all four, + tiesToAway",
    "exception flags: invalid \u00b7 div-by-zero \u00b7 overflow \u00b7 underflow \u00b7 inexact",
    "subnormals kept \u2014 never flushed to zero",
    "NaN payloads preserved through arithmetic",
    "formats: binary16 + binary32 + binary64",
    "correctly rounded \u2014 FMA, sqrt, sinPi/cosPi, hard cases",
    "augmented add / sub / mul: head + exact tail",
]
SPEC_SHORT = ["rounding attrs", "5 flags", "subnormals", "NaN payloads",
              "b16+b32+b64", "correct rounding", "augmented ops"]


def scene_title(d, t):
    a = fade(t, 0.5)
    if a <= 0:
        return
    c = S.blend(WHITE, INKD, a)
    text(d, (W / 2, 600), "WHY NOT USE WHAT", "black", 150, c)
    text(d, (W / 2, 790), "ALREADY SHIPS?", "black", 150, c)
    text(d, (W / 2, 960),
         "The RP2040 has no FPU \u2014 every float is software. Three workloads go shopping.",
         "body", 40, S.blend(WHITE, DIMD, a))


def scene_workloads(d, t):
    header(d, t, "FIRST: THE WORKLOADS", "what actually has to run on the chip")
    boxes = [(140, 420, 820, 1120), (940, 420, 1620, 1120), (1740, 420, 2420, 1120)]
    for i, ((name, sub, col, lines), box) in enumerate(zip(WORKLOADS, boxes)):
        t0 = 1.5 + i * 1.0
        a = pop(t, t0)
        if a <= 0:
            continue
        card(d, box, scale=a)
        if a > 0.6:
            cx = (box[0] + box[2]) / 2
            text(d, (cx, 545), name, "black", 42, col)
            text(d, (cx, 615), sub, "body", 32, DIMD)
            d.line([box[0] + 60, 675, box[2] - 60, 675], fill=BORDER, width=3)
            text(d, (cx, 765), "NEEDS:", "bold", 30, DIMD)
            for k, ln in enumerate(lines):
                text(d, (cx, 860 + k * 62), ln, "body", 34, INKD)


def scene_spec(d, t):
    header(d, t, "TOGETHER, THAT'S A JOB SPEC", "the IEEE 754-2019 semantics the three workloads stand on")
    x0, y0 = 330, 380
    for i, row in enumerate(SPEC):
        a = fade(t, 4.5 + i * 0.18)
        if a <= 0:
            continue
        y = y0 + i * 138
        col = S.blend(WHITE, INKD, a)
        draw_sym(d, x0, y, CHECK, S.blend(WHITE, GREEND, a), size=60)
        text(d, (x0 + 110, y), row, "body", 44, col, anchor="lm")


def option_card(d, t, t0, kicker, title, rows, foot, stamp_s, stamp_c, stamp_t):
    a = pop(t, t0)
    if a <= 0:
        return
    box = (430, 400, 2130, 1170)
    card(d, box, scale=a)
    if a <= 0.6:
        return
    text(d, (W / 2, 150), kicker, "black", 56, DIMD)
    text(d, (W / 2, 235), title, "black", 76, INKD)
    for i, (sym, col, s) in enumerate(rows):
        ra = fade(t, t0 + 0.35 + i * 0.28)
        if ra <= 0:
            continue
        y = 500 + i * 122
        draw_sym(d, 600, y, sym, S.blend(CARD, col, ra), size=62)
        text(d, (720, y), s, "body", 43, S.blend(CARD, INKD, ra), anchor="lm")
    if foot:
        fa = fade(t, t0 + 0.35 + len(rows) * 0.28)
        if fa > 0:
            text(d, (560, 1095), foot, "body", 31, S.blend(CARD, DIMD, fa), anchor="lm")
    stamp(d, 1820, 975, stamp_s, stamp_c, t, stamp_t)


def scene_opt1(d, t):
    rows = [
        (CHECK, GREEND, "five basic ops correctly rounded *  (+ \u2212 \u00d7 \u00f7 \u221a)"),
        (CROSS, REDD, "subnormals flushed to zero \u2014 in and out"),
        (CROSS, REDD, "NaNs rendered as infinities \u2014 payloads gone"),
        (CROSS, REDD, "one rounding mode: ties-to-even. No directed modes"),
        (CROSS, REDD, "exception flags: none exist"),
    ]
    option_card(d, t, 6.0, "OPTION 1 \u2014 THE DEFAULT",
                "SDK \u2018pico\u2019 flavour \u2192 bootrom",
                rows, "* subject to those flush rules (RP2040 datasheet, via SF-0 \u00a78)",
                "ELIMINATED", REDD, 7.55)


def scene_opt2(d, t):
    rows = [
        (QM, QUEST, "directed rounding?  not measured"),
        (QM, QUEST, "exception flags?  not measured"),
        (QM, QUEST, "NaN payloads? subnormals? binary16?  not measured"),
        (CROSS, REDD, "compiler FMA contraction varies by target (SF-0 \u00a79)"),
    ]
    option_card(d, t, 8.0, "OPTION 2 \u2014 THE FALL-THROUGH",
                "SDK \u2018compiler\u2019 flavour \u2192 libgcc",
                rows, "SF-0 gated none of it \u2014 unmeasured semantics can't carry a proof",
                "NOT MEASURED", AMBERD, 9.55)


def scene_opt3(d, t):
    a = pop(t, 10.0)
    if a <= 0:
        return
    box = (430, 430, 2130, 1080)
    card(d, box, scale=a)
    if a <= 0.6:
        return
    text(d, (W / 2, 180), "OPTION 3", "black", 56, DIMD)
    text(d, (W / 2, 270), "SDK \u2018none\u2019 flavour", "black", 76, INKD)
    text(d, (W / 2, 640), 'panic("float support is disabled")', "mono", 52, REDD)
    text(d, (W / 2, 780), "every float entry point is this stub", "body", 40, DIMD)
    stamp(d, W / 2, 950, "NO FLOATS AT ALL", REDD, t, 10.55)


def scene_lineup(d, t):
    # Parametric zoom 1.0 -> 1.30 about the matrix centre (draw-time scale).
    zt = S.ease_in_out(min(1.0, max(0.0, (t - 11.3) / 1.7)))
    s = 1.0 + 0.22 * zt
    cx0, cy0 = 1500, 800

    def X(x):
        return cx0 + (x - cx0) * s

    def Y(y):
        return cy0 + (y - cy0) * s

    header(d, t, "THE LINEUP vs THE SPEC", "only what SF-0 actually measured or stated \u2014 ? means not measured")
    cols = [("BOOTROM", 1420), ("LIBGCC", 1760), ("CUSTOM", 2100)]
    boot = [CROSS, CROSS, CROSS, CROSS, QM, CHECK + "*", QM]
    lib = [QM] * 7
    settled = t >= 13.5
    cust = [CHECK] * 7 if settled else [QM] * 7
    grid = [boot, lib, cust]
    y0 = 520
    for j, (name, x) in enumerate(cols):
        col = GREEND if (j == 2 and settled) else INKD
        d.text((X(x), Y(y0 - 95)), name, font=F("black", 38 * s), fill=col, anchor="mm")
    for i, label in enumerate(SPEC_SHORT):
        y = y0 + i * 100
        ra = fade(t, 11.0 + i * 0.07)
        if ra <= 0:
            continue
        d.text((X(1150), Y(y)), label, font=F("body", 38 * s),
               fill=S.blend(WHITE, INKD, ra), anchor="rm")
        for j in range(3):
            sym = grid[j][i]
            col = GREEND if sym.startswith(CHECK) else (REDD if sym == CROSS else QUEST)
            if j == 0 and sym.startswith(CHECK):
                col = AMBERD
            draw_sym(d, X(cols[j][1]), Y(y), sym, S.blend(WHITE, col, ra),
                     size=56 * s, anchor="c")
    fa = fade(t, 11.6)
    if fa > 0:
        d.text((X(1420), Y(y0 + 7 * 100 + 25)), "* five basic ops, under the flush rules",
               font=F("body", 28 * s), fill=S.blend(WHITE, DIMD, fa), anchor="mm")


def scene_settle(d, t):
    a = pop(t, 13.5)
    if a <= 0:
        return
    box = (330, 330, 2230, 1140)
    card(d, box, scale=a, fill=(232, 248, 240), outline=GREEND, width=5)
    if a <= 0.6:
        return
    text(d, (W / 2, 170), "SO BUILD THE FOURTH OPTION", "black", 60, DIMD)
    text(d, (W / 2, 500), "MUSE-SOFTFLOAT", "black", 120, INKD)
    lines = [
        (640, "IEEE 754-2019 \u00b7 binary16 / 32 / 64 \u00b7 849 instantiations", 46),
        (740, "five rounding attributes \u00b7 five exact flags \u00b7 payloads preserved", 42),
        (835, "subnormals kept \u00b7 augmented ops \u00b7 correctly rounded, hard cases in", 42),
        (970, "proven bit-identical on RP2040 silicon", 50),
    ]
    for i, (y, s_, size) in enumerate(lines):
        la = fade(t, 13.85 + i * 0.22)
        if la <= 0:
            continue
        col = GREEND if i == len(lines) - 1 else INKD
        kind = "black" if i == len(lines) - 1 else "body"
        text(d, (W / 2, y), s_, kind, size, S.blend((232, 248, 240), col, la))


def frame(t: float) -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    if t < 1.5:
        scene_title(d, t)
    elif t < 4.5:
        scene_workloads(d, t)
    elif t < 6.0:
        scene_spec(d, t)
    elif t < 8.0:
        scene_opt1(d, t)
    elif t < 10.0:
        scene_opt2(d, t)
    elif t < 11.0:
        scene_opt3(d, t)
    elif t < 13.5:
        scene_lineup(d, t)
    else:
        scene_settle(d, t)
    if t >= 15.0:  # settle back onto the white plane; 0.75 s static hold out
        a = S.ease_in_out(min(1.0, (t - 15.0) / 0.25))
        white = Image.new("RGB", (W, H), WHITE)
        img = Image.blend(img, white, a)
    return img


def main() -> int:
    out = HERE / "why-1440p.mp4"
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-force_key_frames", "expr:eq(n,460)",
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
    twin = HERE / "why-1080p.mp4"  # welcome downscale twin (1440p is the deliverable)
    r2 = subprocess.run([exe, "-y", "-hide_banner", "-loglevel", "error",
                         "-i", str(out), "-vf", "scale=1920:1080",
                         "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                         "-crf", "16", str(twin)])
    print(f"twin rc={r2.returncode} -> {twin} ({twin.stat().st_size if twin.exists() else 0} bytes)")
    return r2.returncode


if __name__ == "__main__":
    raise SystemExit(main())
