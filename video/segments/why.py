"""study-video-why v3 (text/pacing pass): why3-1440p.mp4, 2560x1440 @ 30.

Revised copy per ledger/briefs/study-video-textpacing.md THE RULE
(dwell from word count; headlines <= 6 w; body <= 10 w; <= 2 new
lines/beat; plain language; one short source tag per scene).
Same SF-0 claim pool/discipline (options-facts.md unchanged);
not-measured stays not-measured. The v2 lineup matrix scene is CUT:
it restated spec+option rows cell-for-cell (no unique claim) and
its dwell cost could not be bought honestly (see textrev report).
Writes ONLY why3-1440p.mp4; all v1/v2 artifacts untouched.
Opens/closes pure white. Frames stream one at a time.
BLOCKS is the audit source of truth. Run: $MSF_PYTHON render_why3.py
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
# Production trim (2026-10-29, owner): the workloads scene duplicated
# the idea segment's three workload cards. It is deleted; everything
# after the title runs SHIFT seconds earlier via frame()'s time map.
SHIFT = 4.5  # E_WORK(8.0) - E_TITLE(3.5) in the untrimmed timeline
DUR = 33.5 - SHIFT  # 29.0
NFRAMES = int(DUR * FPS)  # 870
WHITE, INKD, DIMD, CARD = B.WHITE, B.INKD, B.DIMD, B.CARD
GREEND, REDD, AMBERD, QUEST, BORDER = B.GREEND, B.REDD, B.AMBERD, B.QUEST, B.BORDER
CYAND, VIOLETD, PINKD = B.CYAND, B.VIOLETD, B.PINKD
CHECK, CROSS, QM = B.CHECK, B.CROSS, B.QM
text, card, pop, fade, header, stamp = B.text, B.card, B.pop, B.fade, B.header, B.stamp
draw_sym = B.draw_sym

# ---- copy ----
T_H = ("WHY NOT USE WHAT", "ALREADY SHIPS?")
T_SUB = "RP2040: no maths hardware (FPU)"
HD_WORK = ("FIRST: THE WORKLOADS", "what must run on the chip")
WORK = [
    ("IAS15", CYAND, "Desktop bits (binary64)"),
    ("INTERVAL GEOMETRY", VIOLETD, "Down / up per end"),
    ("KISSFFT \u2014 FORK B", PINKD, "Correctly rounded sinPi/cosPi"),
]
HD_SPEC = ("TOGETHER: A JOB SPEC", "what the three jobs need (IEEE 754-2019)")
SPEC3 = [
    "All five rounding choices",
    "Five warning flags, always exact",
    "Tiny numbers never zeroed (subnormals)",
    "Error values keep their details",
    "Three number sizes (binary16/32/64)",
    "Correctly rounded, even hard cases",
    "Exact leftovers (augmented)",
]
O1_HEAD = ("OPTION 1 \u2014 THE DEFAULT", "SDK \u2018pico\u2019 flavour \u2192 bootrom")
O1_ROWS = [
    (CHECK, GREEND, "Five basic sums correctly rounded"),
    (CROSS, REDD, "Tiny results silently become zero"),
    (CROSS, REDD, "Error values turn into infinity"),
    (CROSS, REDD, "One rounding choice only (ties-to-even)"),
    (CROSS, REDD, "No warning flags exist"),
]
O1_TAG = "(SF-0 \u00a78)"
O1_STAMP = "ELIMINATED"
O2_HEAD = ("OPTION 2 \u2014 THE FALL-THROUGH", "SDK \u2018compiler\u2019 flavour \u2192 libgcc")
O2_ROWS = [
    (QM, QUEST, "Rounding directions? Not measured"),
    (QM, QUEST, "Warning flags? Not measured"),
    (QM, QUEST, "Errors, tiny numbers, small size? Unmeasured"),
    (CROSS, REDD, "Same code, different bits per target"),
]
O2_EX = "e.g. a\u00d7b+c differs by target."
O2_FOOT = "Unmeasured proves nothing (SF-0)"
O2_STAMP = "NOT MEASURED"
O3_HEAD = ("OPTION 3", "SDK \u2018none\u2019 flavour")
O3_PANIC = 'panic("float support is disabled")'
O3_SUB = "Every number call stops here"
O3_STAMP = "NO FLOATS AT ALL"
ST_KICK = "SO BUILD THE FOURTH OPTION"
ST_TITLE = "MUSE-SOFTFLOAT"
ST_LINES = [
    "Three sizes \u00b7 849 versions (IEEE 754-2019)",
    "Five roundings, five exact warnings",
    "Tiny kept \u00b7 leftovers exact \u00b7 correctly rounded",
    "Proven bit-identical on the chip",
]

# ---- timeline ----
E_TITLE, E_WORK, E_SPEC = 3.5, 8.0, 13.5
E_O1, E_O2, E_O3 = 18.5, 24.0, 28.0
FADE_T = 32.5

# BLOCKS: audit truth in TRIMMED segment time (post-title blocks are the
# untrimmed times minus SHIFT; the workloads scene is deleted - see top).
def _sh(blocks):
    return [(s, a - SHIFT, b - SHIFT, lines) for (s, a, b, lines) in blocks]


BLOCKS = [
    ("title", 0.5, E_TITLE, list(T_H)),
    ("title", 1.0, E_TITLE, [T_SUB]),
] + _sh([
    ("spec", 8.0, E_SPEC, list(HD_SPEC)),
] + [("spec", 8.5 + i * 0.5, E_SPEC, [r]) for i, r in enumerate(SPEC3)] + [
    ("opt1", 13.5, E_O1, list(O1_HEAD)),
] + [("opt1", 14.0 + i * 0.5, E_O1, [r[2]]) for i, r in enumerate(O1_ROWS)] + [
    ("opt1", 16.5, E_O1, [O1_TAG]),
    ("opt1", 17.0, E_O1, [O1_STAMP]),
    ("opt2", 18.5, E_O2, list(O2_HEAD)),
] + [("opt2", 19.0 + i * 0.5, E_O2, [r[2]]) for i, r in enumerate(O2_ROWS)] + [
    ("opt2", 21.0, E_O2, [O2_EX]),
    ("opt2", 21.5, E_O2, [O2_FOOT]),
    ("opt2", 22.5, E_O2, [O2_STAMP]),
    ("opt3", 24.0, E_O3, list(O3_HEAD)),
    ("opt3", 24.5, E_O3, [O3_PANIC]),
    ("opt3", 25.0, E_O3, [O3_SUB]),
    ("opt3", 25.5, E_O3, [O3_STAMP]),
    ("settle", 28.0, FADE_T, [ST_KICK, ST_TITLE]),
    ("settle", 28.5, FADE_T, [ST_LINES[0]]),
    ("settle", 29.0, FADE_T, [ST_LINES[1]]),
    ("settle", 29.5, FADE_T, [ST_LINES[2]]),
    ("settle", 30.0, FADE_T, [ST_LINES[3]]),
])


def scene_title(d, t):
    a = fade(t, 0.5)
    if a <= 0:
        return
    c = S.blend(WHITE, INKD, a)
    text(d, (W / 2, 600), T_H[0], "black", 150, c)
    text(d, (W / 2, 790), T_H[1], "black", 150, c)
    b = fade(t, 1.0)
    if b > 0:
        text(d, (W / 2, 960), T_SUB, "body", 42, S.blend(WHITE, DIMD, b))


def scene_workloads(d, t):
    header(d, t, *HD_WORK)
    boxes = [(140, 420, 820, 1120), (940, 420, 1620, 1120), (1740, 420, 2420, 1120)]
    for i, ((name, col, needs), box) in enumerate(zip(WORK, boxes)):
        a = pop(t, 4.0 + i * 0.5)
        if a <= 0:
            continue
        card(d, box, scale=a)
        if a > 0.6:
            cx = (box[0] + box[2]) / 2
            text(d, (cx, 580), name, "black", 44, col)
            d.line([box[0] + 60, 660, box[2] - 60, 660], fill=BORDER, width=3)
            text(d, (cx, 820), needs, "body", 28, INKD)


def scene_spec(d, t):
    header(d, t, *HD_SPEC)
    x0, y0 = 300, 380
    for i, row in enumerate(SPEC3):
        a = fade(t, 8.5 + i * 0.5)
        if a <= 0:
            continue
        y = y0 + i * 140
        draw_sym(d, x0, y, CHECK, S.blend(WHITE, GREEND, a), size=62)
        text(d, (x0 + 115, y), row, "body", 46, S.blend(WHITE, INKD, a), anchor="lm")


def option_card(d, t, t0, head, rows, extra, stamp_s, stamp_c, stamp_t):
    """extra: [(t_abs, s, size, color)] lines under the rows."""
    a = pop(t, t0)
    if a <= 0:
        return
    card(d, (400, 380, 2160, 1200), scale=a)
    if a <= 0.6:
        return
    text(d, (W / 2, 140), head[0], "black", 56, DIMD)
    text(d, (W / 2, 228), head[1], "black", 78, INKD)
    for i, (sym, col, s) in enumerate(rows):
        ra = fade(t, t0 + 0.5 + i * 0.5)
        if ra <= 0:
            continue
        y = 480 + i * 110
        draw_sym(d, 560, y, sym, S.blend(CARD, col, ra), size=64)
        text(d, (685, y), s, "body", 45, S.blend(CARD, INKD, ra), anchor="lm")
    y_ex = 480 + len(rows) * 110 + 8
    for k, (tt, s, size, col) in enumerate(extra):
        ea = fade(t, tt)
        if ea > 0:
            text(d, (560, y_ex + k * 72), s, "body", size,
                 S.blend(CARD, col, ea), anchor="lm")
    stamp(d, 1840, 1128, stamp_s, stamp_c, t, stamp_t)


def scene_opt1(d, t):
    option_card(d, t, 13.5, O1_HEAD, O1_ROWS,
                [(16.5, O1_TAG, 31, DIMD)], O1_STAMP, REDD, 17.0)


def scene_opt2(d, t):
    option_card(d, t, 18.5, O2_HEAD, O2_ROWS,
                [(21.0, O2_EX, 36, REDD), (21.5, O2_FOOT, 31, DIMD)],
                O2_STAMP, AMBERD, 22.5)


def scene_opt3(d, t):
    a = pop(t, 24.0)
    if a <= 0:
        return
    card(d, (400, 410, 2160, 1110), scale=a)
    if a <= 0.6:
        return
    text(d, (W / 2, 165), O3_HEAD[0], "black", 56, DIMD)
    text(d, (W / 2, 258), O3_HEAD[1], "black", 78, INKD)
    b = fade(t, 24.5)
    if b > 0:
        text(d, (W / 2, 620), O3_PANIC, "mono", 54, S.blend(CARD, REDD, b))
    c = fade(t, 25.0)
    if c > 0:
        text(d, (W / 2, 760), O3_SUB, "body", 42, S.blend(CARD, DIMD, c))
    stamp(d, W / 2, 985, O3_STAMP, REDD, t, 25.5)


def scene_settle(d, t):
    a = pop(t, 28.0)
    if a <= 0:
        return
    card(d, (330, 330, 2230, 1140), scale=a, fill=(232, 248, 240),
         outline=GREEND, width=5)
    if a <= 0.6:
        return
    text(d, (W / 2, 170), ST_KICK, "black", 60, DIMD)
    text(d, (W / 2, 500), ST_TITLE, "black", 120, INKD)
    ys = [640, 740, 835, 970]
    sizes = [48, 44, 44, 52]
    for i, (y, s_, size) in enumerate(zip(ys, ST_LINES, sizes)):
        la = fade(t, 28.5 + i * 0.5)
        if la <= 0:
            continue
        col = GREEND if i == len(ST_LINES) - 1 else INKD
        kind = "black" if i == len(ST_LINES) - 1 else "body"
        text(d, (W / 2, y), s_, kind, size, S.blend((232, 248, 240), col, la))


def frame(t: float) -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    if t < E_TITLE:
        scene_title(d, t)
        return img
    ts = t + SHIFT  # untrimmed-timeline time for all later scenes
    if ts < E_SPEC:
        scene_spec(d, ts)
    elif ts < E_O1:
        scene_opt1(d, ts)
    elif ts < E_O2:
        scene_opt2(d, ts)
    elif ts < E_O3:
        scene_opt3(d, ts)
    else:
        scene_settle(d, ts)
    if ts >= FADE_T:
        a = S.ease_in_out(min(1.0, (ts - FADE_T) / 0.25))
        img = Image.blend(img, Image.new("RGB", (W, H), WHITE), a)
    return img


def main() -> int:
    out = HERE / "why3-1440p.mp4"
    first_white = int((FADE_T - SHIFT + 0.25) * FPS) + 1
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [exe, "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-force_key_frames", f"expr:eq(n,{first_white})",
           "-crf", "12", "-preset", "medium", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    for i in range(NFRAMES):
        proc.stdin.write(frame(i / FPS).tobytes())
        if i % 120 == 0:
            print(f"frame {i}/{NFRAMES}", flush=True)
    proc.stdin.close()
    rc = proc.wait()
    print(f"ffmpeg rc={rc} -> {out} ({out.stat().st_size if out.exists() else 0} bytes)")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
