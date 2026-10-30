"""study-video-idea v2 (text/pacing pass): idea2-1440p.mp4, 2560x1440 @ 30.

Revised copy per ledger/briefs/study-video-textpacing.md THE RULE:
dwell = smallest 0.5 s multiple >= max(1.5, 0.5 + words/2.5);
headlines <= 6 words; body lines <= 10 words; <= 2 new lines per
beat; plain language; same claims/sources/numbers (a73e97d, see
report.md claim table). Prior idea-1440p/1080p artifacts untouched;
this script writes ONLY idea2-1440p.mp4. Opens/closes pure white.
All motion parametric; frames stream to ffmpeg one at a time.

BLOCKS below is the audit source of truth (one entry per beat of new
text; words = whitespace tokens containing a letter/digit). Scene code
draws exactly these strings at exactly these times.
Run: $MSF_PYTHON render_idea2.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
WHY = HERE  # production: base lib lives beside this file
sys.path.insert(0, str(WHY))
import render_why as B  # noqa: E402
import imageio_ffmpeg  # noqa: E402

S = B.S
W, H, FPS = B.W, B.H, B.FPS
DUR = 22.5
NFRAMES = int(DUR * FPS)  # 675
WHITE, INKD, DIMD = B.WHITE, B.INKD, B.DIMD
GREEND, REDD, CYAND, VIOLETD, PINKD, BORDER = (
    B.GREEND, B.REDD, B.CYAND, B.VIOLETD, B.PINKD, B.BORDER)
text, card, pop, fade, header = B.text, B.card, B.pop, B.fade, B.header

# ---- copy (single source; scene code and BLOCKS both use these) ----
HD_IDEA = ("THE IDEA", "for the RP2040 chip")
IDEA_LINES = [
    "Precise number maths in software (IEEE 754)",
    "for a chip without maths hardware",
    "All maths there is software.",
    "Same answer everywhere.",
]
HD_COR = ("WHAT \u201cCORRECT\u201d MEANS", "the nearest answer, every time")
LAB_A = "value A"
LAB_B = "the next number the chip can hold"
DOT_LAB = ("exact answer", "(no rounding yet)")
ARROW_LAB = "correctly rounded \u2192 A"
CROSS_LAB = "A neighbour is wrong."
TAG_ILL = "(illustrative)"
COR_FOOT = "Exact, not close."
HD_PROVE = ("WHAT WILL PROVE IT", "three real jobs on the chip")
CARDS = [
    ("IAS15", "tracks planets", CYAND,
     ["Desktop bits, every step", "(binary64)"]),
    ("INTERVAL GEOMETRY", "answers with guarantees", VIOLETD,
     ["Down one end,", "up the other"]),
    ("KISSFFT \u2014 FORK B", "live signals", PINKD,
     ["Correctly rounded", "sinPi/cosPi"]),
]
HD_METH = ("HOW IT GETS BUILT", "the short version")
METH_ROWS = [
    "Agents build it piece by piece",
    "Each piece checked independently",
    "Verifiers try disproving it",
]
METH_FOOT = "Watch it land."
Q_KICK = "BUT FIRST \u2014"
Q_H1 = "WHY NOT USE WHAT"
Q_H2 = "ALREADY SHIPS?"

# ---- timeline (absolute seconds; scene ends) ----
T_IDEA, T_COR, T_PROVE, T_METH, T_Q = 0.5, 4.5, 9.5, 14.5, 18.5
FADE_T = 21.5

# (scene, t0, t_gone, lines) -- t_gone = scene cut (or fade start)
BLOCKS = [
    ("idea", 0.5, 4.5, list(HD_IDEA)),
    ("idea", 1.0, 4.5, [IDEA_LINES[0]]),
    ("idea", 1.5, 4.5, [IDEA_LINES[1]]),
    ("idea", 2.0, 4.5, [IDEA_LINES[2]]),
    ("idea", 2.5, 4.5, [IDEA_LINES[3]]),
    ("correct", 4.5, 9.5, list(HD_COR)),
    ("correct", 5.0, 9.5, [LAB_A, LAB_B]),
    ("correct", 6.0, 9.5, list(DOT_LAB)),
    ("correct", 6.5, 9.5, [ARROW_LAB]),
    ("correct", 7.0, 9.5, [CROSS_LAB, TAG_ILL]),
    ("correct", 7.5, 9.5, [COR_FOOT]),
    ("prove", 9.5, 14.5, list(HD_PROVE)),
    ("prove", 10.0, 14.5, [CARDS[0][0], CARDS[0][1]]),
    ("prove", 10.5, 14.5, list(CARDS[0][3])),
    ("prove", 11.0, 14.5, [CARDS[1][0], CARDS[1][1]]),
    ("prove", 11.5, 14.5, list(CARDS[1][3])),
    ("prove", 12.0, 14.5, [CARDS[2][0], CARDS[2][1]]),
    ("prove", 12.5, 14.5, list(CARDS[2][3])),
    ("method", 14.5, 18.5, list(HD_METH)),
    ("method", 15.0, 18.5, ["1", METH_ROWS[0]]),
    ("method", 15.5, 18.5, ["2", METH_ROWS[1]]),
    ("method", 16.0, 18.5, ["3", METH_ROWS[2]]),
    ("method", 16.5, 18.5, [METH_FOOT]),
    ("question", 18.5, 21.5, [Q_KICK, Q_H1]),
    ("question", 19.0, 21.5, [Q_H2]),
]


def scene_idea(d, t):
    header(d, t, *HD_IDEA)
    a = pop(t, 0.5)
    if a <= 0:
        return
    card(d, (330, 360, 2230, 1160), scale=a)
    if a <= 0.6:
        return
    style = [("black", 58, INKD), ("black", 54, INKD),
             ("body", 46, DIMD), ("bold", 50, GREEND)]
    for i, (s, (kind, size, col)) in enumerate(zip(IDEA_LINES, style)):
        la = fade(t, 1.0 + i * 0.5)
        if la > 0:
            text(d, (W / 2, 560 + i * 130), s, kind, size, S.blend(B.CARD, col, la))


def scene_correct(d, t):
    header(d, t, *HD_COR)
    x0, x1, y = 430, 2130, 700
    xa, xb, xe = 780, 1780, 1080
    a1 = fade(t, 5.0)
    if a1 > 0:
        lc = S.blend(WHITE, INKD, a1)
        d.line([x0, y, x1, y], fill=lc, width=6)
        for x in (xa, xb):
            d.line([x, y - 46, x, y + 46], fill=lc, width=6)
        text(d, (xa, y + 130), LAB_A, "body", 38, S.blend(WHITE, DIMD, a1))
        text(d, (xb, y + 130), LAB_B, "body", 34, S.blend(WHITE, DIMD, a1))
    a2 = pop(t, 6.0)
    if a2 > 0:
        r = 26 * a2
        d.ellipse([xe - r, y - r, xe + r, y + r], fill=VIOLETD)
        if a2 > 0.6:
            text(d, (xe, y - 150), DOT_LAB[0], "bold", 42, VIOLETD)
            text(d, (xe, y - 95), DOT_LAB[1], "body", 32, DIMD)
    a3 = fade(t, 6.5)
    if a3 > 0:
        gc = S.blend(WHITE, GREEND, a3)
        ay = y - 210
        d.line([xe, ay + 60, xe, ay], fill=gc, width=8)
        d.line([xe, ay, xa + 30, ay], fill=gc, width=8)
        d.polygon([(xa - 8, ay), (xa + 34, ay - 20), (xa + 34, ay + 20)], fill=gc)
        text(d, ((xe + xa) / 2, ay - 62), ARROW_LAB, "black", 44, gc)
    a4 = fade(t, 7.0)
    if a4 > 0:
        rc = S.blend(WHITE, REDD, a4)
        B.draw_sym(d, xb, y - 200, B.CROSS, rc, size=64, anchor="c")
        text(d, (xb, y - 285), CROSS_LAB, "body", 38, rc)
        text(d, (2050, 1120), TAG_ILL, "body", 28, S.blend(WHITE, DIMD, a4))
    a5 = fade(t, 7.5)
    if a5 > 0:
        text(d, (W / 2, 1120), COR_FOOT, "bold", 44, S.blend(WHITE, INKD, a5))


def scene_prove(d, t):
    header(d, t, *HD_PROVE)
    boxes = [(140, 420, 820, 1120), (940, 420, 1620, 1120), (1740, 420, 2420, 1120)]
    for i, ((name, sub, col, needs), box) in enumerate(zip(CARDS, boxes)):
        a = pop(t, 10.0 + i * 1.0)
        if a <= 0:
            continue
        card(d, box, scale=a)
        if a <= 0.6:
            continue
        cx = (box[0] + box[2]) / 2
        text(d, (cx, 545), name, "black", 44, col)
        text(d, (cx, 615), sub, "body", 33, DIMD)
        na = fade(t, 10.5 + i * 1.0)
        if na > 0:
            cc = S.blend(B.CARD, BORDER, na)
            d.line([box[0] + 60, 675, box[2] - 60, 675], fill=cc, width=3)
            for k, ln in enumerate(needs):
                text(d, (cx, 800 + k * 70), ln, "body", 36,
                     S.blend(B.CARD, INKD, na))


def scene_method(d, t):
    header(d, t, *HD_METH)
    cols = [CYAND, VIOLETD, PINKD]
    for i, (s, col) in enumerate(zip(METH_ROWS, cols)):
        a = fade(t, 15.0 + i * 0.5)
        if a <= 0:
            continue
        y = 520 + i * 170
        d.ellipse([560, y - 52, 664, y + 52], fill=S.blend(WHITE, col, a))
        text(d, (612, y), str(i + 1), "black", 52, WHITE)
        text(d, (720, y), s, "body", 48, S.blend(WHITE, INKD, a), anchor="lm")
    a = fade(t, 16.5)
    if a > 0:
        text(d, (W / 2, 1120), METH_FOOT, "body", 40, S.blend(WHITE, DIMD, a))


def scene_question(d, t):
    a = fade(t, 18.5)
    if a > 0:
        text(d, (W / 2, 560), Q_KICK, "black", 64, S.blend(WHITE, DIMD, a))
        text(d, (W / 2, 720), Q_H1, "black", 150, S.blend(WHITE, INKD, a))
    b = fade(t, 19.0)
    if b > 0:
        text(d, (W / 2, 910), Q_H2, "black", 150, S.blend(WHITE, INKD, b))


def frame(t: float) -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    if t >= T_IDEA and t < T_COR:
        scene_idea(d, t)
    elif t >= T_COR and t < T_PROVE:
        scene_correct(d, t)
    elif t >= T_PROVE and t < T_METH:
        scene_prove(d, t)
    elif t >= T_METH and t < T_Q:
        scene_method(d, t)
    elif t >= T_Q:
        scene_question(d, t)
    if t >= FADE_T:
        a = S.ease_in_out(min(1.0, (t - FADE_T) / 0.25))
        img = Image.blend(img, Image.new("RGB", (W, H), WHITE), a)
    return img


def main() -> int:
    out = HERE / "idea2-1440p.mp4"
    first_white = int((FADE_T + 0.25) * FPS) + 1  # first exact-white frame idx
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
        if i % 90 == 0:
            print(f"frame {i}/{NFRAMES}", flush=True)
    proc.stdin.close()
    rc = proc.wait()
    print(f"ffmpeg rc={rc} -> {out} ({out.stat().st_size if out.exists() else 0} bytes)")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
