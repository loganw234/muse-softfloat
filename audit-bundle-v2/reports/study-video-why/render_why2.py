"""study-video-why v2: 32.0 s slowed comparison, 2560x1440 @ 30 fps.

Re-timing of render_why.py (v1, 16 s) purely for reading time: same
SF-0-sourced claim pool and discipline (options-facts.md), reveals
now sequential with per-block dwell on the 120 BPM 0.5 s grid (dwell
rule stated in report-v2.md), type slightly larger, plus one sourced
concrete consequence line per doomed option (labelled 'e.g.'; direct
consequences of the same SF-0/S3 statements, no new measurement).
Opens and closes on pure white. Parametric zoom only.

Run: $MSF_PYTHON render_why2.py   (MSF_PYTHON = workspace .venv python)
Frames stream to ffmpeg one at a time (memory ceiling: one frame).
v1 artifacts (why-1440p.mp4 etc.) are not touched.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render_why as B  # noqa: E402
import imageio_ffmpeg  # noqa: E402

S = B.S
W, H, FPS = B.W, B.H, B.FPS
DUR = 32.0
NFRAMES = int(DUR * FPS)  # 960
WHITE, INKD, DIMD, CARD = B.WHITE, B.INKD, B.DIMD, B.CARD
GREEND, REDD, AMBERD, QUEST, BORDER = B.GREEND, B.REDD, B.AMBERD, B.QUEST, B.BORDER
CHECK, CROSS, QM = B.CHECK, B.CROSS, B.QM
text, card, pop, fade, header, stamp = B.text, B.card, B.pop, B.fade, B.header, B.stamp
draw_sym = B.draw_sym


def scene_title(d, t):
    a = fade(t, 0.5)
    if a <= 0:
        return
    c = S.blend(WHITE, INKD, a)
    text(d, (W / 2, 600), "WHY NOT USE WHAT", "black", 150, c)
    text(d, (W / 2, 790), "ALREADY SHIPS?", "black", 150, c)
    b = fade(t, 1.0)
    if b > 0:
        text(d, (W / 2, 960),
             "The RP2040 has no FPU \u2014 every float is software. Three workloads go shopping.",
             "body", 42, S.blend(WHITE, DIMD, b))


def scene_workloads(d, t):
    header(d, t, "FIRST: THE WORKLOADS", "what actually has to run on the chip")
    boxes = [(140, 420, 820, 1120), (940, 420, 1620, 1120), (1740, 420, 2420, 1120)]
    for i, ((name, sub, col, lines), box) in enumerate(zip(B.WORKLOADS, boxes)):
        a = pop(t, 2.5 + i * 2.0)  # one card per 2.0 s dwell
        if a <= 0:
            continue
        card(d, box, scale=a)
        if a > 0.6:
            cx = (box[0] + box[2]) / 2
            text(d, (cx, 545), name, "black", 44, col)
            text(d, (cx, 615), sub, "body", 33, DIMD)
            d.line([box[0] + 60, 675, box[2] - 60, 675], fill=BORDER, width=3)
            text(d, (cx, 765), "NEEDS:", "bold", 31, DIMD)
            for k, ln in enumerate(lines):
                text(d, (cx, 865 + k * 66), ln, "body", 36, INKD)


def scene_spec(d, t):
    header(d, t, "TOGETHER, THAT'S A JOB SPEC",
           "the IEEE 754-2019 semantics the three workloads stand on")
    x0, y0 = 300, 380
    for i, row in enumerate(B.SPEC):
        a = fade(t, 8.5 + i * 0.5)  # one row per beat, then a full-block hold
        if a <= 0:
            continue
        y = y0 + i * 140
        draw_sym(d, x0, y, CHECK, S.blend(WHITE, GREEND, a), size=62)
        text(d, (x0 + 115, y), row, "body", 46, S.blend(WHITE, INKD, a), anchor="lm")


def option_card(d, t, t0, kicker, title, rows, example, foot, stamp_s, stamp_c, stamp_t):
    """Rows reveal one per 1.0 s (each lacks line gets its own dwell)."""
    a = pop(t, t0)
    if a <= 0:
        return
    box = (400, 380, 2160, 1200)
    card(d, box, scale=a)
    if a <= 0.6:
        return
    text(d, (W / 2, 140), kicker, "black", 56, DIMD)
    text(d, (W / 2, 228), title, "black", 78, INKD)
    for i, (sym, col, s) in enumerate(rows):
        ra = fade(t, t0 + 0.5 + i * 1.0)
        if ra <= 0:
            continue
        y = 480 + i * 110
        draw_sym(d, 560, y, sym, S.blend(CARD, col, ra), size=64)
        text(d, (685, y), s, "body", 45, S.blend(CARD, INKD, ra), anchor="lm")
    y_ex = 480 + len(rows) * 110 + 8
    ea = fade(t, t0 + 0.5 + len(rows) * 1.0 - 0.5)
    if example and ea > 0:
        text(d, (560, y_ex), example, "body", 36, S.blend(CARD, REDD, ea), anchor="lm")
    fa = ea
    if foot and fa > 0:
        text(d, (560, y_ex + 72), foot, "body", 31, S.blend(CARD, DIMD, fa), anchor="lm")
    stamp(d, 1840, 1128, stamp_s, stamp_c, t, stamp_t)


def scene_opt1(d, t):
    rows = [
        (CHECK, GREEND, "five basic ops correctly rounded *  (+ \u2212 \u00d7 \u00f7 \u221a)"),
        (CROSS, REDD, "subnormals flushed to zero \u2014 in and out"),
        (CROSS, REDD, "NaNs rendered as infinities \u2014 payloads gone"),
        (CROSS, REDD, "one rounding mode: ties-to-even. No directed modes"),
        (CROSS, REDD, "exception flags: none exist"),
    ]
    option_card(
        d, t, 12.5, "OPTION 1 \u2014 THE DEFAULT", "SDK \u2018pico\u2019 flavour \u2192 bootrom",
        rows,
        "e.g. a tiny subnormal result \u2192 0, silently.",
        "* five basic ops, under the flush rules (SF-0 \u00a78)",
        "ELIMINATED", REDD, 18.5)


def scene_opt2(d, t):
    rows = [
        (QM, QUEST, "directed rounding?  not measured"),
        (QM, QUEST, "exception flags?  not measured"),
        (QM, QUEST, "NaN payloads? subnormals? binary16?  not measured"),
        (CROSS, REDD, "compiler FMA contraction varies by target (SF-0 \u00a79)"),
    ]
    option_card(
        d, t, 19.0, "OPTION 2 \u2014 THE FALL-THROUGH", "SDK \u2018compiler\u2019 flavour \u2192 libgcc",
        rows,
        "e.g. a\u00d7b+c may fuse on one target, not another \u2014 different bits.",
        "SF-0 gated none of it \u2014 unmeasured semantics can't carry a proof",
        "NOT MEASURED", AMBERD, 24.0)


def scene_opt3(d, t):
    a = pop(t, 24.5)
    if a <= 0:
        return
    card(d, (400, 410, 2160, 1110), scale=a)
    if a <= 0.6:
        return
    text(d, (W / 2, 165), "OPTION 3", "black", 56, DIMD)
    text(d, (W / 2, 258), "SDK \u2018none\u2019 flavour", "black", 78, INKD)
    b = fade(t, 25.0)
    if b > 0:
        text(d, (W / 2, 620), 'panic("float support is disabled")', "mono", 54,
             S.blend(CARD, REDD, b))
    c = fade(t, 25.5)
    if c > 0:
        text(d, (W / 2, 760), "every float entry point is this stub", "body", 42,
             S.blend(CARD, DIMD, c))
        text(d, (W / 2, 845), "e.g. the first  a + b  in any workload never returns.",
             "body", 38, S.blend(CARD, REDD, c))
    stamp(d, W / 2, 985, "NO FLOATS AT ALL", REDD, t, 26.0)


def scene_lineup(d, t):
    zt = S.ease_in_out(min(1.0, max(0.0, (t - 26.5) / 1.0)))
    s = 1.0 + 0.22 * zt
    cx0, cy0 = 1500, 800
    X = lambda x: cx0 + (x - cx0) * s  # noqa: E731
    Y = lambda y: cy0 + (y - cy0) * s  # noqa: E731
    header(d, t, "THE LINEUP vs THE SPEC",
           "only what SF-0 actually measured or stated \u2014 ? means not measured")
    cols = [("BOOTROM", 1420), ("LIBGCC", 1760), ("CUSTOM", 2100)]
    boot = [CROSS, CROSS, CROSS, CROSS, QM, CHECK + "*", QM]
    grid = [boot, [QM] * 7, [QM] * 7]
    y0 = 520
    for j, (name, x) in enumerate(cols):
        d.text((X(x), Y(y0 - 95)), name, font=B.F("black", 40 * s), fill=INKD, anchor="mm")
    for i, label in enumerate(B.SPEC_SHORT):
        ra = fade(t, 26.5 + i * 0.15)
        if ra <= 0:
            continue
        y = y0 + i * 100
        d.text((X(1150), Y(y)), label, font=B.F("body", 40 * s),
               fill=S.blend(WHITE, INKD, ra), anchor="rm")
        for j in range(3):
            sym = grid[j][i]
            col = GREEND if sym.startswith(CHECK) else (REDD if sym == CROSS else QUEST)
            if j == 0 and sym.startswith(CHECK):
                col = AMBERD
            draw_sym(d, X(cols[j][1]), Y(y), sym, S.blend(WHITE, col, ra),
                     size=58 * s, anchor="c")
    fa = fade(t, 27.0)
    if fa > 0:
        d.text((X(1420), Y(y0 + 725)), "* five basic ops, under the flush rules",
               font=B.F("body", 29 * s), fill=S.blend(WHITE, DIMD, fa), anchor="mm")


def scene_settle(d, t):
    a = pop(t, 28.0)
    if a <= 0:
        return
    card(d, (330, 330, 2230, 1140), scale=a, fill=(232, 248, 240),
         outline=GREEND, width=5)
    if a <= 0.6:
        return
    text(d, (W / 2, 170), "SO BUILD THE FOURTH OPTION", "black", 60, DIMD)
    text(d, (W / 2, 500), "MUSE-SOFTFLOAT", "black", 120, INKD)
    lines = [
        (640, "IEEE 754-2019 \u00b7 binary16 / 32 / 64 \u00b7 849 instantiations", 48),
        (740, "five rounding attributes \u00b7 five exact flags \u00b7 payloads preserved", 44),
        (835, "subnormals kept \u00b7 augmented ops \u00b7 correctly rounded, hard cases in", 44),
        (970, "proven bit-identical on RP2040 silicon", 52),
    ]
    at = [28.5, 29.0, 29.0, 29.5]  # middle pair lands as one block; punchline dwells 1.5 s
    for i, (y, s_, size) in enumerate(lines):
        la = fade(t, at[i])
        if la <= 0:
            continue
        col = GREEND if i == len(lines) - 1 else INKD
        kind = "black" if i == len(lines) - 1 else "body"
        text(d, (W / 2, y), s_, kind, size, S.blend((232, 248, 240), col, la))


def frame(t: float) -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    if t < 2.5:
        scene_title(d, t)
    elif t < 8.5:
        scene_workloads(d, t)
    elif t < 12.5:
        scene_spec(d, t)
    elif t < 19.0:
        scene_opt1(d, t)
    elif t < 24.5:
        scene_opt2(d, t)
    elif t < 26.5:
        scene_opt3(d, t)
    elif t < 28.0:
        scene_lineup(d, t)
    else:
        scene_settle(d, t)
    if t >= 31.0:  # fade out; 0.75 s exact-white hold (git hand-off)
        a = S.ease_in_out(min(1.0, (t - 31.0) / 0.25))
        img = Image.blend(img, Image.new("RGB", (W, H), WHITE), a)
    return img


def main() -> int:
    out = HERE / "why2-1440p.mp4"
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-force_key_frames", "expr:eq(n,938)",
           "-crf", "12", "-preset", "medium", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    for i in range(NFRAMES):
        proc.stdin.write(frame(i / FPS).tobytes())
        if i % 90 == 0:
            print(f"frame {i}/{NFRAMES}", flush=True)
    proc.stdin.close()
    rc = proc.wait()
    print(f"ffmpeg rc={rc} -> {out} ({out.stat().st_size if out.exists() else 0} bytes)")
    if rc != 0:
        return rc
    twin = HERE / "why2-1080p.mp4"
    r2 = subprocess.run([exe, "-y", "-hide_banner", "-loglevel", "error",
                         "-i", str(out), "-vf", "scale=1920:1080",
                         "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                         "-crf", "16", str(twin)])
    print(f"twin rc={r2.returncode} -> {twin} ({twin.stat().st_size if twin.exists() else 0} bytes)")
    return r2.returncode


if __name__ == "__main__":
    raise SystemExit(main())
