"""Git-visual segment v5 (v4 + text/pacing revision): marble-track
model in ONE continuous space at 2560x1440. v5 changes vs v4: TEXT
ONLY, per ledger/briefs/study-video-textpacing.md (Agent B) - plainer,
shorter copy everywhere (popup = title + <=2 short lines, headlines
<=6 words, body <=10 words, <=2 new lines per beat, one short source
tag per scene), and every text block's dwell set by THE RULE:
smallest 0.5 s-grid multiple >= max(1.5 s, 0.5 s + words/2.5). Popup
holds therefore grow (2.3 s -> rule dwell); the head marble simply
WAITS on its node - no event moves: every marble position is still
a pure function of the same clock that lights its event (chase:
head_x; replay: cursor_rank), gates/windows/topology/packaging are
v4's, shifted later in wall time by the bought dwell (SHIFT). Sync
re-measured by measure_sync5.py; copy/dwell audited by audit_text5.py.

2560x1440 @ 30 fps, video/style.py fonts/palette, 0.5 s / 120 BPM grid.
Every camera move renders the scene parametrically at output scale
(vector projection + native-size text) - max crop-upscale factor 1.0.
Handoffs (VALUES unchanged, now 1440p): open pure white (255,255,255);
end near-black source (3,4,9) -> (2,3,8) after encode (= outro2).
Data: history.json (real git history at a73e97d), gate2_numbers.json
(regen at a73e97d), KissFFT study JSONs, video/data.py IAS15 digests
+ figure-8 ICs (orbit integrated in float64, labelled illustration;
the hash rows are the proof). Frames stream to ffmpeg; never buffered.

Run: $MSF_PYTHON render_gitvisual5.py --still 12.0 --out stills5/test.png
     $MSF_PYTHON render_gitvisual5.py --out gitvisual5.mp4
"""
from __future__ import annotations

import argparse, json, math, subprocess, sys, time
from pathlib import Path
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "video"))
import style as S  # noqa: E402
import data as VDATA  # noqa: E402
import scenes as VSC  # noqa: E402  (simulate_fig8 only; drawing is ours)

W, H, FPS = 2560, 1440, 30
Q = 4.0 / 3.0  # 1080p design units -> 1440p px
# TOTAL is defined after the popup dwell computation (v5: 102.0 s)
NEAR_BLACK = (3, 4, 9)
WHITE = (255, 255, 255)
DEEP = {
    "lead / main": (29, 78, 216), "parcels": (8, 145, 178), "verifiers": (190, 24, 93),
    "plants": (217, 119, 6), "gates": (5, 150, 105), "studies": (124, 58, 237),
    "escalations": (220, 38, 38),
}
TEXT_DARK = (24, 28, 44)
GREY_NODE = (168, 174, 190)
HIST = json.loads((HERE / "history.json").read_text(encoding="utf-8"))
COMMITS, MERGES, NODES = HIST["commits"], HIST["merges"], HIST["node_events"]
IAS_RANK = next(m["rank"] for m in MERGES if m["short"] == "d9718cf")   # 44, true beat
G1_RANK = next(m["rank"] for m in MERGES if m["short"] == HIST["gate_anchors"]["gate1_kissfft_merge"])
G2_RANK = next(m["rank"] for m in MERGES if m["short"] == HIST["gate_anchors"]["gate2_metrics_merge"])
LAST_RANK = HIST["commit_count_all"] - 1
_spec = json.loads((HERE / "spectrum_n256.json").read_text())
_inp = json.loads((HERE / "input_n256.json").read_text())
SPEC, WAVE_RE = _spec["mag"], _inp["re"]
G2N = json.loads((HERE / "gate2_numbers.json").read_text(encoding="utf-8"))
IAS15 = VDATA.ias15_digests()          # asserts 2001 rows + step0/2000 pins
FIG8 = VSC.simulate_fig8(int(8 * FPS) + 2, VDATA.FIG8_T_FINAL)  # [frame,3,2]

# ---------- v5 text/pacing: popup copy + THE RULE ----------
# Popup copy overrides history.json node_events title/lines on screen
# only (history.json stays the shared v1-v4 data file; its full
# per-popup sources live in polish5-report.md now). Same seven real
# examples, same numbers, plain register: title + <=2 short lines.
POPUP5 = [
    ("PARCEL", ["173 binary32 routines", "one file: msf32.c"]),
    ("ESCALATION", ["tiny results packed wrong", "fixes: 53acb1a / b37fb12"]),
    ("VERIFIER", ["SHA-256 too short", "56 characters, needs 64"]),
    ("PLANTS", ["9/10 planted bugs caught", "one miss, harmless"]),
    ("GATES", ["52,168 quick + 1,117,504 standard tests",
               "chip matches computer exactly"]),
    ("STUDY", ["try in scratch first", "two studies wait ahead"]),
    ("LEAD MERGE", ["finished work joins main", "first merge: 2843792"]),
]
# One short source tag per scene (full sourcing in the report).
SRC_CHASE = "src: project RECORD + git log"
SRC_REPLAY = "src: git log @ a73e97d"

def word_count(s):
    return len(s.split())

def rule_dwell(words):
    """THE RULE: smallest 0.5 s-grid multiple >= max(1.5, 0.5+words/2.5)."""
    return math.ceil(max(1.5, 0.5 + words / 2.5) * 2.0) / 2.0

POPUP_WORDS = [word_count(t) + sum(word_count(ln) for ln in lines)
               for t, lines in POPUP5]
POPUP_DWELL = [rule_dwell(w) for w in POPUP_WORDS]
# Chase arrivals: first node as v4 (6.5 s), 1.0 s travel legs as v4,
# holds = rule dwell (the marble waits on its node; lighting is still
# gated on head_x, so the event itself cannot move).
ARRIVALS = []
_a = 6.5
for _dw in POPUP_DWELL:
    ARRIVALS.append(_a)
    _a += _dw + 1.0
T_BRIDGE = ARRIVALS[-1] + POPUP_DWELL[-1]          # 42.5 (v4: 28.6)
T_REPLAY = math.ceil((T_BRIDGE + 2.4) * 2.0) / 2.0  # 45.0 (v4: 31.0)
BRIDGE_DUR = T_REPLAY - T_BRIDGE                    # 2.5 (v4: 2.4)
SHIFT = T_REPLAY - 31.0                             # 14.0
T_BOX = 79.0 + SHIFT                                # 93.0
T_FADE = 86.0 + SHIFT                               # 100.0
TOTAL = 88.0 + SHIFT                                # 102.0

def px(v):
    return int(round(v * Q))

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def ss(x):
    """Smootherstep: zero velocity AND acceleration at both ends."""
    x = clamp(x)
    return x * x * x * (x * (x * 6 - 15) + 10)

def text(d, xy, s, kind, size, color, anchor=None):
    d.text(xy, s, font=S.font(kind, px(size)), fill=color, anchor=anchor)

def beat_pulse(t):
    ph = (t % 0.5) / 0.5
    return math.exp(-4.0 * ph)

def glow_poly(d, pts, core, width=7, pulse=0.0):
    if len(pts) < 2:
        return
    width = px(width)
    grow = int(px(3) * pulse)
    halo = tuple(int(c + (255 - c) * 0.5) for c in core)
    d.line(pts, fill=halo + (55,), width=width + px(16) + grow, joint="curve")
    d.line(pts, fill=halo + (110,), width=width + px(7) + grow, joint="curve")
    d.line(pts, fill=tuple(core) + (255,), width=max(2, width), joint="curve")
    d.line(pts, fill=tuple(int(c + (255 - c) * 0.65) for c in core) + (255,),
           width=max(2, width // 3), joint="curve")

# ---------- perspective camera (world: X progression, Y lateral, Z up) ----------
class Cam:
    def __init__(self, pos, target, roll=0.0, focal=None, up_hint=(0.0, 0.0, 1.0)):
        self.pos = np.array(pos, float); self.tgt = np.array(target, float)
        self.focal = float(focal if focal is not None else px(1250))
        f = self.tgt - self.pos; f /= np.linalg.norm(f)
        up0 = np.array(up_hint, float)
        if abs(np.dot(f, up0)) > 0.98:
            up0 = np.array([0.0, 1.0, 0.0])
        r = np.cross(f, up0); r /= np.linalg.norm(r)
        u = np.cross(r, f)
        if roll:
            c, s = math.cos(roll), math.sin(roll)
            r, u = r * c + u * s, u * c - r * s
        self.f, self.r, self.u = f, r, u

    def proj(self, pts):
        p = np.atleast_2d(np.asarray(pts, float)) - self.pos
        x, y, z = p @ self.r, p @ self.u, p @ self.f
        zc = np.where(np.abs(z) < 1e-6, 1e-6, z)
        sx = W / 2 + self.focal * x / zc
        sy = H / 2 - self.focal * y / zc
        return np.stack([sx, sy], 1), z, self.focal / zc

    def one(self, p3):
        sc, dep, scl = self.proj(np.array([p3], float))
        return (float(sc[0, 0]), float(sc[0, 1])), float(dep[0]), float(scl[0])

def proj_line(d, cam, pts3, core, width=7, pulse=0.0, ghost=False, alpha=None):
    if len(pts3) < 2:
        return
    sc, dep, scl = cam.proj(np.array(pts3, float))
    ok = [(float(sc[i, 0]), float(sc[i, 1])) for i in range(len(sc)) if dep[i] > 40]
    if len(ok) < 2:
        return
    med = float(np.median(scl[dep > 40])) if np.any(dep > 40) else 1.0
    wdt = max(2, int(px(width) * clamp(med, 0.25, 1.15)))
    if ghost or alpha is not None:
        d.line(ok, fill=tuple(core) + (60 if alpha is None else alpha,), width=wdt, joint="curve")
    else:
        # glow_poly already applies px(); feed it design-unit width back-scaled
        glow_poly(d, ok, core, max(2.0, width * clamp(med, 0.25, 1.15)), pulse)

def draw_marble(d, cam, p3, core, r_world=26.0, pulse=0.0, bed_z=None, shadow=(24, 30, 50)):
    """A marble: shaded sphere (screen circle scaled by 1/depth) + bed shadow.
    Shadow is a SOLID pre-blended colour (RGBA->RGB would resurrect alpha)."""
    (sx, sy), dep, scl = cam.one(p3)
    if dep <= 40:
        return None
    r = clamp(r_world * scl, 3.0, px(36)) + px(2.0) * pulse
    if bed_z is not None:
        (bx, by), bdep, _ = cam.one((p3[0], p3[1], bed_z))
        if bdep > 40:
            d.ellipse([bx - r * 0.9, by - r * 0.30, bx + r * 0.9, by + r * 0.30],
                      fill=tuple(shadow) + (255,))
    d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=tuple(core) + (255,))
    hx, hy = sx - r * 0.38, sy - r * 0.42
    d.ellipse([hx - r * 0.34, hy - r * 0.34, hx + r * 0.34, hy + r * 0.34],
              fill=tuple(int(c + (255 - c) * 0.78) for c in core) + (255,))
    d.ellipse([sx - r, sy - r, sx + r, sy + r], outline=(255, 255, 255, 90), width=2)
    return (sx, sy, r)

# ---------- chase (teaching diagram; v2 beats, marble head, same world) ----------
NODE_X = [820, 1520, 2220, 2920, 3620, 4320, 5020]
NODE_DY = [-320, 330, -320, 330, -320, 330, -320]
KEYS = [(1.0, 110.0), (3.0, 520.0), (ARRIVALS[0], float(NODE_X[0])),
        (ARRIVALS[0] + POPUP_DWELL[0], float(NODE_X[0]))]
for _i, _nx in enumerate(NODE_X[1:], start=1):
    KEYS.append((ARRIVALS[_i], float(_nx)))
    KEYS.append((ARRIVALS[_i] + POPUP_DWELL[_i], float(_nx)))
KEYS.append((T_REPLAY, 5480.0))  # final leg runs into the bridge (no cut)

def head_x(t):
    if t <= KEYS[0][0]:
        return KEYS[0][1]
    for (t0, x0), (t1, x1) in zip(KEYS, KEYS[1:]):
        if t <= t1:
            return x0 + (x1 - x0) * ss((t - t0) / max(1e-9, t1 - t0))
    return KEYS[-1][1]

def node_arrival(i):
    return ARRIVALS[i]

def lift_u(t):
    return ss((t - 3.0) / 3.5)

def trail_z(x, t):
    return lift_u(t) * 130.0

def chase_cam(t):
    hx = head_x(t); u = lift_u(t)
    hz = trail_z(hx, t)
    flat_off = np.array([-420.0, 0.0, 1900.0])
    chase_off = np.array([-980.0, -760.0, 500.0])
    off = flat_off * (1 - u) + chase_off * u
    close = 0.0
    for i in range(len(NODES)):
        a = node_arrival(i)
        close = max(close, ss((t - (a - 0.5)) / 0.7) * (1 - ss((t - (a + POPUP_DWELL[i] - 0.4)) / 0.6)))
    off = off * (1.0 - 0.20 * close * u)
    pos = np.array([hx, 0.0, hz]) + off
    look = np.array([hx + 120.0 + 260.0 * u, 0.0, hz * 0.85])
    for i in range(len(NODES)):
        a = node_arrival(i)
        wgt = ss((t - (a - 0.4)) / 0.6) * (1 - ss((t - (a + POPUP_DWELL[i] - 0.3)) / 0.5))
        if wgt > 0:
            node_p = np.array([NODE_X[i], NODE_DY[i], hz + 110.0 * u])
            look = look * (1 - 0.45 * wgt) + node_p * (0.45 * wgt)
    roll = u * 0.10 * math.sin(t * 0.55)
    up = np.array([0.0, 1.0 - u, u])
    return Cam(pos, look, roll=roll, focal=px(1150.0 + 350.0 * (1 - u)), up_hint=up)

def branch_pts3(i, t):
    nx, dy, u = NODE_X[i], NODE_DY[i], lift_u(t)
    z0 = trail_z(nx, t)
    return [(nx - 340, 0.0, z0), (nx - 190, dy * 0.5, z0 + 60 * u),
            (nx - 60, dy * 0.9, z0 + 100 * u), (nx, dy, z0 + 110 * u)]

def clip_branch(pts, hx):
    x_fork, x_node = pts[0][0], pts[-1][0]
    f = clamp((hx - x_fork) / max(1.0, x_node - x_fork))
    if f <= 0:
        return []
    out = [pts[0]]
    segs = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total, acc = sum(segs), 0.0
    for (a, b), ln in zip(zip(pts, pts[1:]), segs):
        if acc + ln <= f * total:
            out.append(b); acc += ln
        else:
            r = (f * total - acc) / ln if ln else 0
            out.append(tuple(a[k] + (b[k] - a[k]) * r for k in range(3)))
            break
    return out

def interp_poly(pts, f):
    """Point at fraction f of polyline arc length."""
    if not pts:
        return None
    if len(pts) == 1 or f <= 0:
        return pts[0]
    segs = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(segs) or 1.0
    want, acc = clamp(f) * total, 0.0
    for (a, b), ln in zip(zip(pts, pts[1:]), segs):
        if acc + ln >= want:
            r = (want - acc) / ln if ln else 0.0
            return tuple(a[k] + (b[k] - a[k]) * r for k in range(3))
        acc += ln
    return pts[-1]

def draw_popup(img, i, sx, sy, alpha_p):
    node = NODES[i]; col = DEEP[node["system"]]
    title, lines = POPUP5[i]  # v5 copy; history.json lines stay in reports
    pw, ph = px(780), px(74 + 38 * len(lines) + 10)
    px_ = int(min(max(sx - px(140), px(490)), W - pw - px(40)))
    py_ = int(sy - ph - px(60)) if NODE_DY[i] < 0 else int(sy + px(60))
    py_ = max(px(140), min(py_, H - ph - px(70)))
    py_ += int((1 - S.ease_out_back(alpha_p)) * -px(16))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([px_ + px(9), py_ + px(12), px_ + pw + px(9), py_ + ph + px(12)],
                        px(18), fill=(100, 115, 155, 90))
    d.rounded_rectangle([px_, py_, px_ + pw, py_ + ph], px(18),
                        fill=(255, 255, 255, 250), outline=col, width=px(4))
    d.line([(sx, sy), (px_ + px(70), py_ + ph if NODE_DY[i] < 0 else py_)], fill=col, width=px(3))
    text(d, (px_ + px(28), py_ + px(18)), title, "black", 34, col)
    for j, ln in enumerate(lines):
        text(d, (px_ + px(28), py_ + px(66 + 38 * j)), ln, "body", 27, TEXT_DARK)
    # v5: no per-popup src stamp - one scene tag (SRC_CHASE) instead

def draw_legend(img):
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0 = px(44), px(40)
    rows = list(DEEP.items())
    pw, ph = px(430), px(52 + 36 * len(rows))
    d.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], px(14), fill=(255, 255, 255, 235),
                        outline=(190, 196, 214), width=2)
    text(d, (x0 + px(22), y0 + px(12)), "LEGEND - SYSTEMS", "mono", 22, (110, 90, 10))
    for j, (name, col) in enumerate(rows):
        cy = y0 + px(56 + 36 * j)
        d.rounded_rectangle([x0 + px(22), cy - px(9), x0 + px(62), cy + px(9)], px(8), fill=col)
        text(d, (x0 + px(78), cy - px(14)), name, "body", 25, TEXT_DARK)

# ---------- backgrounds (pre-rendered once at output scale) ----------
def _vgrad(top, bot):
    g = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None, None]
    arr = (np.array(top, np.float32)[None, None, :] * (1 - g)
           + np.array(bot, np.float32)[None, None, :] * g).astype(np.uint8)
    return Image.fromarray(np.repeat(arr, W, axis=1), "RGB")

_WHITE_BG = _vgrad((255, 255, 255), (236, 240, 250))
_DARK_BG = _vgrad(S.BG2, S.BG)

def base_bg(dark_u):
    if dark_u <= 0.0:
        return _WHITE_BG.copy()
    if dark_u >= 1.0:
        return _DARK_BG.copy()
    return Image.blend(_WHITE_BG, _DARK_BG, dark_u)

def dark_u_at(t):
    return ss((t - T_BRIDGE) / BRIDGE_DUR)

def draw_chase_world(img, t, cam, fade=1.0):
    """Teaching tracks + head marble + splitting branch marbles. fade<1 in bridge."""
    u = lift_u(t); hx = head_x(t); pulse = beat_pulse(t)
    d = ImageDraw.Draw(img, "RGBA")
    light = dark_u_at(t) < 0.5
    mshadow = (198, 205, 224) if light else (24, 30, 50)
    grid = (185, 194, 218) if light else (70, 80, 110)
    gx0 = int((hx - 2600) // 400 * 400)
    for gx in range(gx0, int(hx + 2800), 400):
        proj_line(d, cam, [(gx, -900, 0), (gx, 900, 0)], grid, 2, ghost=True)
    for gy in (-900, -450, 0, 450, 900):
        proj_line(d, cam, [(hx - 2600, gy, 0), (hx + 2800, gy, 0)], grid, 2, ghost=True)
    xs = np.linspace(90, 5600, 120)
    main3 = [(float(x), 0.0, trail_z(x, t)) for x in xs]
    shadow = [(float(x), 0.0, 0.0) for x in xs if x <= hx]
    proj_line(d, cam, shadow, grid, 6, ghost=True)
    lit = [p for p in main3 if p[0] <= hx] + [(hx, 0.0, trail_z(hx, t))]
    ghost = [p for p in main3 if p[0] > hx]
    spine = DEEP["lead / main"] if light else (96, 165, 250)
    proj_line(d, cam, ghost, spine, 4, ghost=True)
    active, node_scr = None, {}
    for i in range(len(NODES)):
        col = DEEP[NODES[i]["system"]]
        bp = branch_pts3(i, t)
        proj_line(d, cam, bp, col, 4, ghost=True)
        clipped = clip_branch(bp, hx)
        proj_line(d, cam, clipped, col, 6, pulse)
        # split marble: rides the branch while the head traverses
        # fork->node, then parks exactly ON the node it lit (v4 sync:
        # the marble end of the lit branch IS the lighting clock)
        if len(clipped) >= 2:
            draw_marble(d, cam, clipped[-1], col, 22.0, pulse * 0.5, bed_z=0.0, shadow=mshadow)
        if i == len(NODES) - 1:
            nx, dy = NODE_X[i], NODE_DY[i]
            rejoin = [(nx, dy, trail_z(nx, t) + 110 * u),
                      (nx + 160, dy * 0.4, trail_z(nx, t) + 50 * u),
                      (nx + 290, 0.0, trail_z(nx, t))]
            if hx > nx:
                proj_line(d, cam, rejoin, spine, 6, pulse)
        (sx, sy), dep, scl = cam.one(bp[-1])
        if dep <= 40:
            continue
        node_scr[i] = (sx, sy)
        r = clamp(px(17) * scl, 3, px(26))
        # v4 sync: the node lights on head_x (the marble's own clock),
        # the same frame the split marble arrives - not on wall time.
        # KEYS make head_x(node_arrival(i)) == NODE_X[i] exactly, so
        # popup/camera timing keyed to node_arrival stays consistent.
        if hx >= NODE_X[i]:
            age = t - node_arrival(i)
            pop = S.ease_out_back(clamp(age / 0.45)) if age >= 0 else 1.0
            rr = r * (0.6 + 0.55 * pop) + px(2.5) * pulse
            d.ellipse([sx - rr - px(9), sy - rr - px(9), sx + rr + px(9), sy + rr + px(9)],
                      outline=tuple(col) + (int(130 * fade),), width=px(3))
            d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], fill=tuple(col) + (255,))
            d.ellipse([sx - rr * 0.4, sy - rr * 0.4, sx + rr * 0.4, sy + rr * 0.4],
                      fill=tuple(int(c + (255 - c) * 0.7) for c in col) + (255,))
            if t < node_arrival(i) + POPUP_DWELL[i]:
                active = i
        else:
            d.ellipse([sx - r, sy - r, sx + r, sy + r], outline=GREY_NODE + (220,), width=px(4))
    proj_line(d, cam, lit, spine, 8, pulse)
    draw_marble(d, cam, (hx, 0.0, trail_z(hx, t)), spine, 30.0, pulse, bed_z=0.0, shadow=mshadow)
    return active, node_scr

# ---------- replay world: real topology as a climbing marble track ----------
X0R = 5600.0           # rank 0 sits just beyond the chase trail: one space
DX, DY, DZ = 85.0, 165.0, 17.0
Z0R = 130.0
BOX_RANK = LAST_RANK + 16.0

def R3(rank, slot):
    return (X0R + rank * DX, slot * DY, Z0R + rank * DZ)

def lane_color(branch):
    if branch.startswith("w1-"):
        return S.CYAN
    if branch.startswith("w2-"):
        return (45, 212, 191)
    if branch.startswith(("w3-", "w-ias15")):
        return S.AMBER
    if branch.startswith("wave4-"):
        return S.VIOLET
    if branch.startswith("wave5-"):
        return S.PINK
    return (96, 165, 250)

_LANES = {}
def assign_lanes():
    if _LANES:
        return _LANES
    taken = []
    cycle, order = [-1, 1, -2, 2, -3, 3, -1, 2, -2, 1], [-1, 1, -2, 2, -3, 3, -4, 4]
    for k, m in enumerate([m for m in MERGES if m["target"] == "main"]):
        first = cycle[k % len(cycle)]
        for slot in [first] + [s for s in order if s != first]:
            if not any(s == slot and not (m["rank"] < a - 1 or m["merge_base_rank"] > b + 1)
                       for s, a, b in taken):
                _LANES[m["short"]] = slot
                taken.append((slot, m["merge_base_rank"], m["rank"])); break
    return _LANES

def lane_pts_rs(m):
    """Lane polyline in (rank, slot): fork at true merge-base, true merge rank.

    v4 fix: keep the polyline monotonic in rank. Two Wave-1 lanes
    (2843792, 06fdec8) carry exclusive commits whose TIME ranks
    precede the merge-base rank; v1-v3 then built a backwards first
    segment and slot_at snapped the marble straight to full lane
    offset just after the base (~101 px jump, measured). Elbows are
    now clamped inside (base, merge) and only in-span chain ranks
    become vertices; out-of-span exclusive dots draw on the spine
    side of the elbow via slot_at clamping (rank-axis artifact, S1).
    """
    slot = float(assign_lanes()[m["short"]])
    chain = sorted(float(r) for r in m["exclusive_ranks"])
    base_r, merge_r = float(m["merge_base_rank"]), float(m["rank"])
    mid = (base_r + merge_r) / 2
    ex0 = min(base_r + 2.0, chain[0], mid) if chain else min(base_r + 2.0, mid)
    ex1 = max(merge_r - 2.0, chain[-1], mid) if chain else max(merge_r - 2.0, mid)
    ex0 = clamp(ex0, base_r + 0.25, mid)
    ex1 = clamp(ex1, mid, merge_r - 0.25)
    inner = [(r, slot) for r in chain if ex0 <= r <= ex1]
    return [(base_r, 0.0), (ex0, slot)] + inner + [(ex1, slot), (merge_r, 0.0)]

def slot_at(pts_rs, rank):
    if rank <= pts_rs[0][0]:
        return pts_rs[0][1]
    for (r0, s0), (r1, s1) in zip(pts_rs, pts_rs[1:]):
        if rank <= r1:
            f = (rank - r0) / max(1e-9, r1 - r0)
            return s0 + (s1 - s0) * f
    return pts_rs[-1][1]

def clip_rs(pts_rs, rlo, rhi):
    """(rank,slot) polyline clipped to [rlo, rhi] with interpolated ends."""
    out = []
    for (r0, s0), (r1, s1) in zip(pts_rs, pts_rs[1:]):
        a, b = max(r0, rlo), min(r1, rhi)
        if b < a:
            continue
        for r in (a, b):
            f = (r - r0) / max(1e-9, r1 - r0)
            p = (r, s0 + (s1 - s0) * f)
            if not out or abs(out[-1][0] - p[0]) > 1e-6:
                out.append(p)
    return out

# timeline: cursor rank + gate windows (all boundaries on the 0.5 s grid)
GATES = [
    {"id": "ias15", "rank": float(IAS_RANK), "t0": 39.0 + SHIFT, "t1": 47.0 + SHIFT,
     "title": "IAS15 RUNS ON THE CHIP",
     "sub": "merge d9718cf - the stream waits",
     "src": "src: project record, Wave 3"},
    {"id": "kissfft", "rank": float(G1_RANK), "t0": 52.0 + SHIFT, "t1": 60.0 + SHIFT,
     "title": "KISSFFT STUDY",
     "sub": "merge 32bbd93 - the stream waits",
     "src": "src: KissFFT study report"},
    {"id": "tokens", "rank": float(G2_RANK), "t0": 67.0 + SHIFT, "t1": 75.0 + SHIFT,
     "title": "TOKENS, RECOUNTED",
     "sub": "metrics merge a1a888f (chosen anchor)",
     "src": "src: usage.jsonl @ a73e97d"},
]
LEGS = [(T_REPLAY, 39.0 + SHIFT, 0.0, float(IAS_RANK)),
        (47.0 + SHIFT, 52.0 + SHIFT, float(IAS_RANK), float(G1_RANK)),
        (60.0 + SHIFT, 67.0 + SHIFT, float(G1_RANK), float(G2_RANK)),
        (75.0 + SHIFT, T_BOX, float(G2_RANK), float(LAST_RANK))]

def cursor_rank(t):
    if t < T_REPLAY:
        return 0.0
    for g in GATES:
        if g["t0"] <= t < g["t1"]:
            # v4 sync: the stream waits exactly ON the gate rank, so
            # the head marble sits on the gate-line node for the whole
            # window (v3 held half a rank short of the line)
            return g["rank"]
    for (ta, tb, ra, rb) in LEGS:
        if ta <= t < tb:
            return ra + (rb - ra) * ss((t - ta) / (tb - ta))
    return float(LAST_RANK)

def gate_at(t):
    for g in GATES:
        if g["t0"] <= t < g["t1"]:
            return g, t - g["t0"]
    return None, 0.0

def replay_cam(t, cur):
    """Closer angled chase of the cursor: behind-side-above, looking up-ramp.
    Near (old) sits low in frame, far (new) high: marbles travel UP-screen."""
    cx, cz = X0R + cur * DX, Z0R + cur * DZ
    sway = 60.0 * math.sin(t * 0.35)
    pos = np.array([cx - 1900.0, -1080.0 + sway, cz + 1050.0])
    tgt = np.array([cx + 900.0, 130.0, cz + 330.0])
    if t >= T_BOX:  # box dolly: ease toward the box on the same spine
        bx, bz = X0R + BOX_RANK * DX, Z0R + BOX_RANK * DZ
        u = ss((t - T_BOX) / 3.0)
        pos = pos * (1 - u) + np.array([bx - 2100.0, -1350.0, bz + 1000.0]) * u
        tgt = tgt * (1 - u) + np.array([bx, 0.0, bz + 220.0]) * u
    return Cam(pos, tgt, roll=0.05 * math.sin(t * 0.4), focal=px(1200))

def master_cam(t):
    if t < T_BRIDGE:
        return chase_cam(t)
    if t < T_REPLAY:  # bridge: one continuous flight chase -> replay angle
        u = ss((t - T_BRIDGE) / BRIDGE_DUR)
        a, b = chase_cam(t), replay_cam(t, 0.0)
        pos = a.pos * (1 - u) + b.pos * u
        tgt = a.tgt * (1 - u) + b.tgt * u
        return Cam(pos, tgt, focal=px(1150 + 150 * u))
    return replay_cam(t, cursor_rank(t))

# corrections/sendbacks: real commits (history.json) + RECORD/ledger sources.
# lane = merge short whose lane carries the event, "" = main spine.
SENDBACKS = [
    {"rank": 7.0, "lane": "", "label": "SENDBACK FIX 4cdb912",
     "sub": "error-value branch fixed"},
    {"rank": 12.0, "lane": "2843792", "label": "TININESS FIX RETURNS",
     "sub": "both rechecked: READY"},
    {"rank": 38.0, "lane": "", "label": "LEAD FIX 83622cf",
     "sub": "runner width fixed"},
    {"rank": 99.0, "lane": "7772da7", "label": "DEFECT FIX 048aa29",
     "sub": "exp2 edges hardened"},
    {"rank": 114.0, "lane": "97d1cbe", "label": "VERIFIER SENDBACK a41f026",
     "sub": "now 64 characters"},
]
SB_LABEL_TAIL = 14.0  # ranks a sendback label stays readable past its rank
SB_LABEL_DIM = 4.0    # ranks it then persists dimmed (old text may persist)

def sb_slot(sb):
    if not sb["lane"]:
        return 0.0
    return float(assign_lanes()[sb["lane"]])

def loop_pts3(sb):
    """Loop-back detour in world space: forward, up and BACK, stamped, rejoin."""
    R, sl = sb["rank"], sb_slot(sb)
    a, b = R3(R - 1.0, sl), R3(R + 3.0, sl)
    top = ((a[0] + b[0]) / 2 - 0.8 * DX, a[1], max(a[2], b[2]) + 175.0)
    back = (a[0] - 0.4 * DX, a[1], a[2] + 90.0)
    return [a, back, top, (b[0] - 0.5 * DX, b[1], b[2] + 80.0), b]

LOOP_SPAN = 4.0  # ranks of cursor travel per sendback loop ride

def sb_phase(sb, cur):
    """0..1 while cursor crosses [rank-1, rank+3] - the exact ranks
    the loop joins and rejoins (v4: one window for marble, stamp
    and label; v3 stamped on a 6-rank window the marble did not use)."""
    lo, hi = sb["rank"] - 1.0, sb["rank"] - 1.0 + LOOP_SPAN
    if cur < lo or cur > hi:
        return None
    return clamp((cur - lo) / (hi - lo))

def sb_apex_frac(sb):
    """Arc-length fraction of the loop apex (where the stamp lands)."""
    pts = loop_pts3(sb)
    segs = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    return sum(segs[:2]) / max(1e-9, sum(segs))

def draw_badge(d, sx, sy, txt, col, scale=1.0, angle_deg=0.0):
    """Small stamped pill (axis-aligned; angle only offsets the stamp jitter)."""
    f = S.font("mono", max(10, px(int(21 * scale))))
    w_ = int(d.textlength(txt, font=f)) + px(24)
    h_ = px(int(38 * scale))
    jx = int(math.sin(math.radians(angle_deg)) * px(3))
    d.rounded_rectangle([sx - w_ / 2 + jx, sy - h_ / 2, sx + w_ / 2 + jx, sy + h_ / 2],
                        px(9), fill=(10, 14, 28, 235), outline=tuple(col), width=max(2, px(3)))
    d.text((sx + jx, sy), txt, font=f, fill=tuple(col), anchor="mm")
    return w_, h_

def draw_check(d, sx, sy, r, col=S.GREEN):
    d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(6, 40, 26, 245),
              outline=tuple(col), width=max(2, px(4)))
    d.line([(sx - r * 0.55, sy + r * 0.05), (sx - r * 0.12, sy + r * 0.45),
            (sx + r * 0.6, sy - r * 0.42)], fill=tuple(col), width=max(3, px(6)), joint="curve")

_LANE_PTS = {}
def all_lane_pts():
    if not _LANE_PTS:
        for m in MERGES:
            if m["target"] == "main":
                _LANE_PTS[m["short"]] = lane_pts_rs(m)
    return _LANE_PTS

def draw_replay_world(img, t, cam, cur, gate=None, gate_lt=0.0):
    d = ImageDraw.Draw(img, "RGBA")
    pulse = beat_pulse(t)
    rlo, rhi = cur - 18.0, cur + 48.0   # close window: the tree is implied
    # track bed: cross ties + lane guides following the ramp
    for r in range(max(0, int(rlo) // 4 * 4), min(LAST_RANK + 16, int(rhi) + 1), 4):
        proj_line(d, cam, [R3(r, -4.6), R3(r, 4.6)], (70, 80, 110), 2, ghost=True)
    for sl in (-4, -2, 0, 2, 4):
        proj_line(d, cam, [R3(max(rlo, 0), sl), R3(min(rhi, BOX_RANK), sl)], (52, 62, 92), 2, ghost=True)
    # day separators (first commit of each day, S7)
    seen = {}
    for c in COMMITS:
        seen.setdefault(c["date"][:10], c["rank"])
    for day, r in seen.items():
        if rlo <= r <= rhi:
            proj_line(d, cam, [R3(r, -4.6), R3(r, 4.6)], (120, 130, 165), 2, alpha=80)
            (lx, ly), dep, _ = cam.one(R3(r, -4.6))
            if dep > 40:
                text(d, (lx + px(8), ly - px(12)), day[5:], "mono_reg", 20, (120, 130, 160, 255), anchor="la")
    lanes = all_lane_pts()
    by_short = {m["short"]: m for m in MERGES if m["target"] == "main"}
    # ghost future + lit past per lane
    for short, pts in lanes.items():
        m = by_short[short]; col = lane_color(m["branch"])
        gp = [R3(r, s) for r, s in clip_rs(pts, max(rlo, cur), rhi)]
        proj_line(d, cam, gp, col, 4, ghost=True)
        lp = [R3(r, s) for r, s in clip_rs(pts, rlo, min(cur, float(m["rank"])))]
        proj_line(d, cam, lp, col, 5, pulse * 0.5)
        for r in m["exclusive_ranks"]:
            if rlo <= r <= cur:
                (sx, sy), dep, scl = cam.one(R3(r, slot_at(pts, r)))
                if dep > 40:
                    rr = clamp(9.0 * scl, 2.0, px(9))
                    d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], fill=tuple(col) + (255,))
    # spine: ghost ahead to the box, lit behind cursor
    proj_line(d, cam, [R3(max(cur, 0), 0), R3(min(rhi, BOX_RANK), 0)], (147, 197, 253), 4, ghost=True)
    proj_line(d, cam, [R3(max(rlo, 0), 0), R3(max(min(cur, LAST_RANK), 0), 0)], (147, 197, 253), 6, pulse * 0.4)
    for c in COMMITS:
        if c["on_main_first_parent"] and not c["is_merge"] and rlo <= c["rank"] <= cur:
            (sx, sy), dep, scl = cam.one(R3(c["rank"], 0))
            if dep > 40:
                rr = clamp(7.0 * scl, 1.5, px(7))
                d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], fill=S.DIM + (255,))
    # lead-fix re-gate connectors (true second-parent edges, S3)
    by_branch = {m["branch"]: m for m in MERGES if m["target"] == "main"}
    for m in MERGES:
        if m["target"] == "main" or m["rank"] > cur or not (rlo <= m["rank"] <= rhi):
            continue
        host = by_branch.get(m["target_branch"])
        if not host:
            continue
        p2 = next(c["rank"] for c in COMMITS if c["hash"] == m["second_parent"])
        proj_line(d, cam, [R3(p2, 0), R3(m["rank"], assign_lanes()[host["short"]])], S.RED, 3, alpha=230)
    # merge pops (green) + persistent dots
    for m in MERGES:
        if m["target"] == "main" and m["rank"] <= cur and rlo <= m["rank"] <= rhi:
            (sx, sy), dep, scl = cam.one(R3(m["rank"], 0))
            if dep <= 40:
                continue
            fresh = clamp(1.0 - (cur - m["rank"]) / 6.0)
            if fresh > 0:
                rr = px(10) + (1 - fresh) * px(34)
                d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], outline=S.GREEN + (int(170 * fresh),), width=px(3))
            rr = clamp(15.0 * scl, 3.0, px(13))
            d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], fill=S.GREEN + (255,))
            d.ellipse([sx - rr * 0.45, sy - rr * 0.45, sx + rr * 0.45, sy + rr * 0.45], fill=(6, 40, 26, 255))
    # gate lines + persistent green checks for passed gates
    for g in GATES:
        gr = g["rank"]
        if not (rlo - 6 <= gr <= rhi):
            continue
        passed = t >= g["t1"] or (gate is g and gate_lt >= 6.5)
        col = S.GREEN if passed else S.AMBER
        proj_line(d, cam, [R3(gr, -4.6), R3(gr, 4.6)], col, 5, alpha=235)
        if passed:
            gp = R3(gr, 0.0); gp = (gp[0], gp[1], gp[2] + 90.0)
            (sx, sy), dep, scl = cam.one(gp)
            if dep > 40:
                draw_check(d, sx, sy, clamp(34.0 * scl, px(12), px(30)))
    # ---- marbles: spine stream + one per active lane (split/rejoin) ----
    # v4 sync model: marble_pos is a PURE function of (rank, slot) -
    # no time term, no gate bob, no ride-height offset - so a marble
    # at cursor rank r projects onto the node center of rank r. The
    # BPM pulse only breathes the drawn radius, never the center.
    def marble_pos(rank, slot):
        return R3(rank, slot)
    sb_active = {}
    for sb in SENDBACKS:
        ph = sb_phase(sb, cur)
        if ph is not None:
            sb_active[id(sb)] = ph
    for back in (18.0, 12.0, 6.0):  # trailing spine marbles (box scene owns them later)
        r = cur - back
        if r >= 0 and t < T_BOX:
            draw_marble(d, cam, marble_pos(r, 0.0), (96, 165, 250), 22.0, 0.0, bed_z=Z0R + r * DZ)
    for short, pts in lanes.items():
        m = by_short[short]
        if float(m["merge_base_rank"]) <= cur < float(m["rank"]):
            col = lane_color(m["branch"])
            # sendback detour overrides the straight ride on its lane
            detour = None
            for sb in SENDBACKS:
                if sb["lane"] == short and id(sb) in sb_active:
                    detour = sb
            if detour is not None:
                lp3 = loop_pts3(detour)
                p = interp_poly(lp3, sb_active[id(detour)])
                draw_marble(d, cam, p, col, 26.0, pulse, bed_z=Z0R + cur * DZ)
            else:
                draw_marble(d, cam, marble_pos(cur, slot_at(pts, cur)), col, 26.0, pulse * 0.6,
                            bed_z=Z0R + cur * DZ)
    # spine sendback detour for the head marble (loop ends coincide
    # with the straight ride at both ends, so entry/exit are seamless)
    head_p = marble_pos(cur, 0.0)
    for sb in SENDBACKS:
        if sb["lane"] == "" and id(sb) in sb_active:
            head_p = interp_poly(loop_pts3(sb), sb_active[id(sb)])
    if t < T_BOX:
        draw_marble(d, cam, head_p, S.AMBER, 34.0, pulse, bed_z=Z0R + cur * DZ)
    # sendback loops + stamps + labels (after marbles so badges read on top)
    for sb in SENDBACKS:
        if not (rlo <= sb["rank"] <= rhi):
            continue
        lp3 = loop_pts3(sb)
        done = cur > sb["rank"] - 1.0 + LOOP_SPAN
        proj_line(d, cam, lp3, S.RED if not done else (160, 90, 90), 3,
                  ghost=False, alpha=None) if id(sb) in sb_active else \
            proj_line(d, cam, lp3, S.RED, 3, alpha=70)
        apex = lp3[2]
        (ax, ay), dep, scl = cam.one(apex)
        ax = clamp(ax, px(430), W - px(430))  # keep the label block on-frame
        if dep <= 40:
            continue
        ph = sb_active.get(id(sb))
        apex_rank = sb["rank"] - 1.0 + sb_apex_frac(sb) * LOOP_SPAN
        # v5 dwell: the (shorter) label stays readable, then persists
        # dimmed - text only; the marble/stamp still ride the cursor.
        # Hidden while a gate window is up (one reading load at a time).
        label_end = sb["rank"] + SB_LABEL_TAIL + SB_LABEL_DIM
        if apex_rank <= cur <= label_end and gate is None:
            # the stamp lands the exact frame the marble crests the apex
            pop = S.ease_out_back(clamp((cur - apex_rank) / 0.6))
            dimmed = cur > sb["rank"] + SB_LABEL_TAIL
            ink = S.FAINT if dimmed else S.INK
            sub_c = S.FAINT if dimmed else S.DIM
            ly = ay - px(150)
            text(d, (ax, ly), sb["label"], "black", 25, ink, anchor="ma")
            text(d, (ax, ly + px(36)), sb["sub"], "body", 21, sub_c, anchor="ma")
            if not dimmed:
                draw_badge(d, ax, ay - px(36), "FIXED - REJOINS", S.RED, 0.7 + 0.3 * pop, -6.0)
        elif done:
            draw_check(d, ax, ay, clamp(22.0 * scl, px(8), px(18)), col=(248, 150, 150))
    # branch labels near their merge (billboards, S9)
    for short, pts in lanes.items():
        m = by_short[short]
        if float(m["merge_base_rank"]) <= cur <= float(m["rank"]) + 16 and rlo <= m["rank"] <= rhi:
            (sx, sy), dep, _ = cam.one(R3(min(cur, float(m["rank"])), slot_at(pts, min(cur, float(m["rank"])))))
            if dep > 40:
                anch = "ra" if sx < W / 2 else "la"
                xo = -px(36) if anch == "ra" else px(36)
                text(d, (sx + xo, sy - px(64)), m["branch"], "mono_reg", 21,
                     lane_color(m["branch"]) + (255,), anchor=anch)

# ---------- gate windows (rise from the track plane; no scene exit) ----------
WIN_FULL = (px(255), px(150), px(1665), px(855))  # design 1920-wide -> 1440p px

def draw_picos_mini(d, t, state, x0, y0, cw, ch, sc=1.0):
    """Six Pico mockups in a 2x3 grid inside the window (v2 idiom, scaled)."""
    for k in range(6):
        bx, by = x0 + (k % 2) * (cw + px(18) * sc), y0 + (k // 2) * (ch + px(30) * sc)
        genuine = (k == 0)
        d.rounded_rectangle([bx, by, bx + cw, by + ch], px(12), fill=(14, 64, 40),
                            outline=(60, 160, 105), width=max(2, px(2)))
        d.rectangle([bx + cw * 0.39, by - 2, bx + cw * 0.61, by + ch * 0.13], fill=(150, 158, 175))
        d.rectangle([bx + cw * 0.35, by + ch * 0.33, bx + cw * 0.65, by + ch * 0.79],
                    fill=(22, 26, 38), outline=(90, 100, 125))
        d.text((bx + cw / 2, by + ch * 0.56), "RP2040", font=S.font("mono", max(8, int(px(15) * sc))),
               fill=S.DIM, anchor="mm")
        on = True if state == "pass" else (math.sin(t * 6.2 + k * 1.7) > (-0.6 if genuine else 0.05))
        led = (70, 255, 150) if on else (28, 80, 52)
        if genuine:
            d.rectangle([bx + cw * 0.12, by + ch * 0.20, bx + cw * 0.18, by + ch * 0.31], fill=led)
            lbl = "Pico - GP25 LED"
        else:
            lr = ch * 0.10
            d.ellipse([bx + cw * 0.15 - lr, by + ch * 0.26 - lr, bx + cw * 0.15 + lr, by + ch * 0.26 + lr],
                      fill=led, outline=(200, 255, 225) if on else (70, 90, 80), width=2)
            lbl = "RP2040-Zero - WS2812"
        if on:
            gr = ch * 0.16 + (px(6) * beat_pulse(t) if state == "pass" else 0)
            cx_, cy_ = bx + cw * 0.15, by + ch * 0.26
            d.ellipse([cx_ - gr, cy_ - gr, cx_ + gr, cy_ + gr], outline=(70, 255, 150, 90), width=2)
        d.text((bx + 2, by + ch + px(4) * sc), lbl, font=S.font("mono_reg", max(8, int(px(15) * sc))), fill=S.DIM)

def viz_kissfft(d, rect, lt, sc):
    x0, y0, x1, y1 = rect
    # local text helper: sizes in design units * window scale sc (parametric)
    def T(xy, s, kind, size, color, anchor=None):
        d.text(xy, s, font=S.font(kind, max(9, int(px(size) * sc))), fill=color, anchor=anchor)
    T((x0, y0), "sound wave in, spectrum out", "mono_reg", 19, S.AMBER)
    T((x0, y0 + (y1 - y0) * 0.045), "(picture only - not KissFFT output)",
      "mono_reg", 17, S.DIM)
    wy = y0 + (y1 - y0) * 0.22
    if lt > 0:
        n = int(len(WAVE_RE) * clamp(lt / 1.8))
        pts = [(x0 + i * (x1 - x0) / len(WAVE_RE), wy - v * px(52) * sc)
               for i, v in enumerate(WAVE_RE[:max(2, n)])]
        d.line(pts, fill=S.CYAN + (255,), width=max(2, px(2)))
    # v5: input caption dropped (the stamp now lands earlier and would
    # cover it mid-dwell); N=256 detail lives in polish5-report.md
    cx, cy, r = x0 + (x1 - x0) * 0.20, y0 + (y1 - y0) * 0.66, (y1 - y0) * 0.20
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=S.FAINT, width=2)
    for k in range(max(0, int(256 * clamp((lt - 1.8) / 1.8)))):
        a = -2 * math.pi * k / 256
        pxx, pyy = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([pxx - 2, pyy - 2, pxx + 2, pyy + 2], fill=S.VIOLET)
    if lt > 2.7:
        T((cx, cy + r + px(10) * sc), "exact twiddle factors", "mono_reg", 19, S.DIM, anchor="ma")
    bx0, by1 = x0 + (x1 - x0) * 0.44, y1 - px(30) * sc
    bw = (x1 - bx0) / 128
    mx = max(SPEC[:128]) or 1
    for k in range(max(0, int(128 * clamp((lt - 3.6) / 2.7)))):
        hgt = (SPEC[k] / mx) * (y1 - y0) * 0.38
        d.rectangle([bx0 + k * bw, by1 - hgt, bx0 + (k + 1) * bw - 1, by1], fill=S.GREEN)
    if lt > 4.5:
        T((bx0, by1 + px(6) * sc), "spectrum, bin by bin", "mono_reg", 19, S.DIM)
    if lt >= 3.6:  # v5: earlier than v4's 6.3 so the stamp gets its dwell
        d.rounded_rectangle([x0 + (x1 - x0) * 0.08, y0 + (y1 - y0) * 0.315,
                             x1 - (x1 - x0) * 0.08, y0 + (y1 - y0) * 0.435], px(10),
                            fill=(6, 40, 26, 240), outline=S.GREEN, width=max(2, px(2)))
        T(((x0 + x1) / 2, y0 + (y1 - y0) * 0.335), "12 / 12 SETUPS CHECKED",
          "black", 30, S.GREEN, anchor="ma")
        T(((x0 + x1) / 2, y0 + (y1 - y0) * 0.40), "check-values recorded",
          "mono_reg", 18, S.DIM, anchor="ma")

def viz_tokens(d, rect, lt, sc):
    x0, y0, x1, y1 = rect
    def T(xy, s, kind, size, color, anchor=None):
        d.text(xy, s, font=S.font(kind, max(9, int(px(size) * sc))), fill=color, anchor=anchor)
    billed, inp, outp = G2N["project_billed_in_plus_out"], G2N["input_tokens"], G2N["output_tokens"]
    T((x0, y0), "recounted at a73e97d", "mono_reg", 19, S.AMBER)
    p = S.ease_out_cubic(clamp(lt / 2.4))
    T((x0, y0 + (y1 - y0) * 0.07), f"{int(billed * p):,}", "mono", 58, S.INK)
    if lt > 0.6:
        T((x0, y0 + (y1 - y0) * 0.20), "billed = input + output (93 rows)",
          "body", 22, S.DIM)
    if lt > 1.2:
        T((x0, y0 + (y1 - y0) * 0.255),
          f"input {inp:,} + output {outp:,}",
          "mono_reg", 19, S.FAINT)
        T((x0, y0 + (y1 - y0) * 0.295),
          f"cached {G2N['cached_tokens_inside_input']:,} sits inside input",
          "mono_reg", 19, S.FAINT)
    by = y0 + (y1 - y0) * 0.33
    d.rectangle([x0, by, x0 + (x1 - x0) * p, by + (y1 - y0) * 0.09], fill=S.CYAN)
    d.rectangle([x0, by, x0 + 2, by + (y1 - y0) * 0.09], fill=S.AMBER)
    if lt > 1.8:
        T((x0, by + (y1 - y0) * 0.11), "you typed ~1,928 tokens (amber, to scale)",
          "body", 21, S.AMBER)
    if lt > 2.5:
        zp = S.ease_out_back(clamp((lt - 2.5) / 1.1))
        zx, zy = x0 + (x1 - x0) * 0.20, y0 + (y1 - y0) * 0.52
        zw, zh = (x1 - x0) * 0.52 * max(0.05, zp), (y1 - y0) * 0.27 * max(0.05, zp)
        d.rectangle([x0 - 4, by - 6, x0 + 12, by + (y1 - y0) * 0.09 + 6], outline=S.AMBER, width=2)
        d.line([(x0 + 12, by + (y1 - y0) * 0.09 + 6), (zx, zy)], fill=S.AMBER, width=2)
        d.rounded_rectangle([zx, zy, zx + zw, zy + zh], px(9), fill=(20, 18, 10, 245),
                            outline=S.AMBER, width=max(2, px(2)))
        if zp > 0.6:
            T((zx + px(18) * sc, zy + px(10) * sc), "x500,000 ZOOM", "mono", 21, S.AMBER)
            T((zx + px(18) * sc, zy + px(40) * sc), "YOU: ~1,928 tokens", "black", 27, S.INK)
            if lt > 4.2:  # third line is its own later beat
                T((zx + px(18) * sc, zy + px(76) * sc), "40 prompts, 7,713 characters", "body", 21, S.DIM)
            d.rectangle([zx + px(18) * sc, zy + zh * 0.74, zx + px(18) * sc + zw * 0.39 * zp,
                         zy + zh * 0.74 + px(16) * sc], fill=S.AMBER)
    if lt > 2.6:  # v5: earlier than v4's 4.8 so the lines get their dwell
        T((x0, y1 - (y1 - y0) * 0.13),
          f"~1 : {G2N['ratio_billed_per_owner_token']:,} - {G2N['messages']:,} messages",
          "black", 27, S.GREEN)
        T((x0, y1 - (y1 - y0) * 0.075),
          f"your share: {G2N['human_share_pct']:.5f}%", "body", 21, S.GREEN)

def viz_ias15(d, rect, lt, sc, t):
    x0, y0, x1, y1 = rect
    def T(xy, s, kind, size, color, anchor=None):
        d.text(xy, s, font=S.font(kind, max(9, int(px(size) * sc))), fill=color, anchor=anchor)
    # left: figure-8 orbit (real ICs, float64 illustration - hashes are the proof)
    ocx, ocy = x0 + (x1 - x0) * 0.24, y0 + (y1 - y0) * 0.42
    oscale = (x1 - x0) * 0.16
    frame = min(len(FIG8) - 1, int(lt * FPS))
    trail = 110
    for b in range(3):
        col = S.ACCENTS[b]
        lo = max(0, frame - trail)
        pts = [(ocx + float(FIG8[i, b, 0]) * oscale, ocy - float(FIG8[i, b, 1]) * oscale)
               for i in range(lo, frame + 1)]
        for i in range(len(pts) - 1):
            a = int(210 * (i / max(1, len(pts) - 1)) ** 1.6)
            if a > 8:
                d.line([pts[i], pts[i + 1]], fill=tuple(col) + (a,), width=max(2, px(2)))
        if pts:
            bx_, by_ = pts[-1]
            d.ellipse([bx_ - px(6) * sc, by_ - px(6) * sc, bx_ + px(6) * sc, by_ + px(6) * sc], fill=S.INK)
    T((x0, y0), "figure-8 orbit (picture)", "mono_reg", 19, S.AMBER)
    if lt > 0.5:
        T((x0, y0 + (y1 - y0) * 0.045), "real start, drawn on desktop", "mono_reg", 17, S.DIM)
    if lt > 1.6:
        T((x0, y0 + (y1 - y0) * 0.72), "check-values at right are the proof", "body", 20, S.DIM)
    if lt > 4.0:
        T((x0, y0 + (y1 - y0) * 0.85), "IAS15 on the chip, via muse-softfloat", "mono_reg", 18, S.FAINT)
    # right: hash rows (sc_hashlock idiom) - real H_state digests
    hx0 = x0 + (x1 - x0) * 0.50
    if lt > 0.4:
        T((hx0, y0), "state check-values: desktop == chip", "mono_reg", 19, S.AMBER)
    steps = IAS15["steps_shown"]
    all_done, done_at = True, 0.0
    for i, step in enumerate(steps):
        ry = y0 + (y1 - y0) * (0.12 + i * 0.20)
        at = 0.4 + i * 1.0  # v5: tighter than v4 so rows+stamp get dwell
        h = IAS15["native"][step][0]
        if lt > at - 0.2:
            T((hx0, ry), f"STEP {step:,}", "mono", 24, S.AMBER)
        shown = int(len(h) * S.ease_out_cubic(clamp((lt - at) / 0.8)))
        txt = h[:shown] + ("_" if 0 < shown < len(h) else "")
        T((hx0, ry + (y1 - y0) * 0.055), txt[:32], "mono", 20, S.GREEN)
        if shown > 32:
            T((hx0, ry + (y1 - y0) * 0.105), txt[32:], "mono", 20, S.GREEN)
        if shown >= len(h) and lt > at:
            T((x1, ry), "desktop == RP2040", "bold", 20, S.GREEN, anchor="ra")
            done_at = max(done_at, at + 0.8)
        else:
            all_done = False
    if all_done and lt > done_at + 0.3 and done_at > 0:
        p_ = S.ease_out_back(clamp((lt - done_at - 0.3) / 0.35))
        sy0 = y0 + (y1 - y0) * 0.74
        d.rounded_rectangle([hx0, sy0, x1, sy0 + (y1 - y0) * 0.13], px(12),
                            outline=S.GREEN, width=max(2, px(3)))
        T(((hx0 + x1) / 2, sy0 + (y1 - y0) * 0.028), "2,001 / 2,001 IDENTICAL", "black", 28, S.GREEN, anchor="ma")
        T(((hx0 + x1) / 2, sy0 + (y1 - y0) * 0.078), "desktop == chip", "black", 24, S.GREEN, anchor="ma")

def draw_gate_window(img, t, cam, gate, lt):
    """Window rises FROM the gate line on the track plane, plays, then
    closes into the green check already drawn on the track. The world
    stays visible (dimmed) throughout - no scene exit."""
    gp = R3(gate["rank"], 0.0)
    (gx, gy), dep, _ = cam.one(gp)
    rise = ss(lt / 0.8)
    close = ss((lt - 7.2) / 0.8)
    open_u = rise * (1.0 - close)
    # darken (not erase) the world: blend manually - a translucent RGBA rect
    # would REPLACE pixels and convert("RGB") would resurrect it full-strength
    darkened = Image.blend(img.convert("RGB"), Image.new("RGB", (W, H), (4, 6, 14)),
                           0.38 * open_u).convert("RGBA")
    img.paste(darkened, (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    if open_u <= 0.01:
        return
    fx0, fy0, fx1, fy1 = WIN_FULL
    sw, sh = px(300), px(170)
    sx0, sy0 = gx - sw / 2, gy - sh - px(30)
    e = open_u
    wx0 = sx0 + (fx0 - sx0) * e; wy0 = sy0 + (fy0 - sy0) * e
    wx1 = (sx0 + sw) + (fx1 - (sx0 + sw)) * e; wy1 = (sy0 + sh) + (fy1 - (sy0 + sh)) * e
    sc = clamp(e, 0.12, 1.0)  # content scale: fonts drawn natively each frame
    d.rounded_rectangle([wx0 + px(8), wy0 + px(10), wx1 + px(8), wy1 + px(10)], px(16),
                        fill=(0, 0, 0, 110))
    d.rounded_rectangle([wx0, wy0, wx1, wy1], px(16), fill=(10, 14, 28, 248),
                        outline=S.AMBER, width=max(2, px(3)))
    bar = (wy1 - wy0) * 0.115
    d.rounded_rectangle([wx0, wy0, wx1, wy0 + bar], px(16), fill=(24, 30, 54, 255))
    d.rectangle([wx0, wy0 + bar - px(16), wx1, wy0 + bar], fill=(24, 30, 54, 255))
    d.text((wx0 + px(26) * sc, wy0 + bar * 0.14), gate["title"],
           font=S.font("black", max(11, int(px(36) * sc))), fill=S.INK)
    d.text((wx0 + px(26) * sc, wy0 + bar * 0.60), gate["sub"],
           font=S.font("mono", max(9, int(px(21) * sc))), fill=S.CYAN)
    # v5: the window's one short source tag, in the title bar
    d.text((wx1 - px(26) * sc, wy0 + bar * 0.34), gate["src"],
           font=S.font("mono_reg", max(9, int(px(17) * sc))), fill=S.FAINT, anchor="ra")
    done = lt >= 6.5
    state = "pass" if done else "working"
    cx0, cy0 = wx0 + px(30) * sc, wy0 + bar + px(22) * sc
    cx1, cy1 = wx1 - px(30) * sc, wy1 - px(78) * sc
    split = cx0 + (cx1 - cx0) * 0.66
    viz = (cx0, cy0, split - px(18) * sc, cy1)
    if gate["id"] == "ias15":
        viz_ias15(d, viz, lt, sc, t)
    elif gate["id"] == "kissfft":
        viz_kissfft(d, viz, lt, sc)
    else:
        viz_tokens(d, viz, lt, sc)
    if lt > 0.8:  # own beat, after the title bar (<=2 new lines/beat)
        d.text((split + px(6) * sc, cy0), "SIX BOARDS (mockup)",
               font=S.font("mono", max(9, int(px(19) * sc))), fill=S.AMBER)
    pw_ = ((cx1 - split) - px(18) * sc) / 2
    ph_ = ((cy1 - cy0 - px(34) * sc) - 2 * px(30) * sc) / 3
    draw_picos_mini(d, t, state, split + px(6) * sc, cy0 + px(34) * sc,
                    max(18.0, pw_), max(12.0, ph_), sc)
    # stem from the track plane into the window base (visible below the window)
    if gy > wy1:
        d.line([(gx, gy), ((wx0 + wx1) / 2, wy1)], fill=S.AMBER + (220,), width=max(2, px(4)))
        d.ellipse([gx - px(7), gy - px(7), gx + px(7), gy + px(7)], fill=S.AMBER + (255,))
    # footer: progress along the window base + PASS state
    fy = wy1 - px(38) * sc
    bh = max(3.0, px(7) * sc)
    d.rectangle([wx0 + px(26) * sc, fy - bh / 2, wx1 - px(26) * sc, fy + bh / 2], fill=(70, 84, 120, 255))
    run = clamp(lt / 6.5)
    d.rectangle([wx0 + px(26) * sc, fy - bh / 2,
                 wx0 + px(26) * sc + (wx1 - wx0 - px(52) * sc) * run, fy + bh / 2], fill=S.CYAN + (255,))
    if done:
        impact = math.exp(-9 * (lt - 6.5))
        # v5 dwell: PASS shows 1.5 s (6.5->8.0), so it is one word -
        # the six solid LEDs beside it say the rest
        d.text((wx0 + px(26) * sc, fy - px(32) * sc), "PASS",
               font=S.font("mono", max(9, int(px(21) * sc))), fill=S.GREEN, anchor="la")
        if impact > 0.02:
            rr = px(20) + (1 - impact) * px(70)
            rcx, rcy = wx0 + px(60) * sc, fy - px(70) * sc
            d.ellipse([rcx - rr, rcy - rr, rcx + rr, rcy + rr],
                      outline=S.GREEN + (int(190 * impact),), width=max(2, px(3)))
    if close > 0.55:  # collapsing into the check on the track
        pop = S.ease_out_back(clamp((close - 0.55) / 0.45))
        draw_check(d, (wx0 + wx1) / 2, (wy0 + wy1) / 2, px(44) * max(0.2, pop))

# ---------- box ending (in-world, on the spine past HEAD) ----------
# v4 packaging: EVERY legend system marble travels into the box, one
# by one (lead last), each a pure function of the box clock lt; as
# they land, the box front stamps what the process retains - only
# real artefacts of this repo: RECORD, the ledgers, the test
# vectors, the session metrics (usage.jsonl). The lid then shuts on
# its hinge arc and the neon dims to the near-black handoff (the
# t>86 fade in frame_at is untouched, values identical to v1-v3).
PACK_ORDER = ["parcels", "verifiers", "plants", "gates", "studies",
              "escalations", "lead / main"]
PACK_STAMPS = [(1, "RECORD"), (3, "LEDGERS"), (5, "VECTORS"), (7, "METRICS")]

def _bright(col, f=0.30):
    return tuple(int(c + (255 - c) * f) for c in col)

def pack_state(lt):
    """[(system, rank, hop, inside)] for the 7 packaging marbles."""
    out = []
    dest = BOX_RANK - 2.0
    for k, name in enumerate(PACK_ORDER):
        # front-most marble departs first, lead (back-most) last, so
        # the queue files in without marbles passing through each other
        start = float(LAST_RANK) - 3.0 * k
        p = ss(clamp((lt - 0.35 * k) / 2.6))
        r = start + (dest - start) * p
        hop, inside = 0.0, False
        # hop crests the front rim BEFORE the front plane (rank
        # BOX-330/85 ~= BOX-3.9) so the whole arc stays visible;
        # the marble is inside once it crosses that plane dropping
        if r > BOX_RANK - 9.0:
            f = clamp((r - (BOX_RANK - 9.0)) / 5.2)
            inside = f > 0.98
            hop = math.sin(min(f, 1.0) * math.pi) * 430.0 * 1.30
        out.append((name, r, hop, inside))
    return out

def draw_box(img, t, cam, cur):
    d = ImageDraw.Draw(img, "RGBA")
    lt = t - T_BOX
    bx, bz = X0R + BOX_RANK * DX, Z0R + BOX_RANK * DZ
    hw, hh, hd = 330.0, 430.0, 330.0  # half-width (Y), height (Z), half-depth (X)
    dim = clamp((lt - 5.8) / 1.4)
    boxcol = tuple(int(S.INK[i] * (1 - dim * 0.75)) for i in range(3))
    def P(x, y, z):
        (sx, sy), dep, _ = cam.one((x, y, z))
        return (sx, sy)
    front = [P(bx - hd, -hw, bz), P(bx - hd, hw, bz), P(bx - hd, hw, bz + hh), P(bx - hd, -hw, bz + hh)]
    side = [P(bx - hd, -hw, bz), P(bx + hd, -hw, bz), P(bx + hd, -hw, bz + hh), P(bx - hd, -hw, bz + hh)]
    top = [P(bx - hd, -hw, bz + hh), P(bx - hd, hw, bz + hh), P(bx + hd, hw, bz + hh), P(bx + hd, -hw, bz + hh)]
    d.polygon(side, fill=(18, 24, 46, 255), outline=boxcol, width=max(2, px(4)))
    shut = ss(clamp((lt - 5.0) / 1.3))  # lid waits until every marble is in
    if shut < 0.9:
        d.polygon(top, fill=(5, 8, 18, 255), outline=boxcol, width=max(2, px(3)))
    # front face BEFORE the marbles: every not-yet-inside marble is
    # still in front of that plane (inside flips as it crosses), so
    # painter order matches depth and the hop arc stays visible
    d.polygon(front, fill=(22, 28, 52, 255), outline=boxcol, width=max(3, px(5)))
    # the seven system marbles file in along the spine (back to front)
    packs = pack_state(lt)
    n_in = sum(1 for _n, _r, _h, ins in packs if ins)
    labels = []
    for k, (name, r, hop, inside) in enumerate(reversed(packs)):
        if inside:
            continue
        p = R3(r, 0.0)
        mcol = _bright(DEEP[name])
        got = draw_marble(d, cam, (p[0], p[1], p[2] + hop), mcol, 28.0,
                          beat_pulse(t) * (1 - dim), bed_z=p[2])
        if got and r < BOX_RANK - 8.0:
            # stagger alternate labels upward so the queue reads clean
            labels.append((got[0], got[1] - got[2] - px(10 + (k % 2) * 30), name, mcol))
    ang = (1 - shut) * 1.25
    lx = bx - hd + math.cos(ang) * 2 * hd
    lz = bz + hh + math.sin(ang) * 2 * hd * 0.72
    lid = [P(bx - hd, -hw, bz + hh), P(bx - hd, hw, bz + hh), P(lx, hw, lz), P(lx, -hw, lz)]
    d.polygon(lid, fill=(30, 38, 70, 255), outline=boxcol, width=max(3, px(5)))
    for sx, sy, name, mcol in labels:
        if dim < 0.9:
            text(d, (sx, sy), name, "mono", 19, mcol, anchor="ms")
    if dim < 0.9:
        (sx, sy), dep, _ = cam.one((bx - hd, 0.0, bz + hh * 0.62))
        text(d, (sx, sy), "muse-softfloat", "mono", 28, S.DIM, anchor="ma")
        (sx, sy), dep, _ = cam.one((bx - hd, 0.0, bz + hh * 0.36))
        kept = "  ".join(s for need, s in PACK_STAMPS if n_in >= need)
        if kept:
            text(d, (sx, sy), kept, "mono", 18, S.GREEN, anchor="ma")
        text(d, (px(48), px(42)), "3 - BOXED", "black", 44, S.INK)
        text(d, (px(48), px(98)), "every system packed away", "mono", 24, S.CYAN)
        text(d, (px(48), px(136)), f"marbles in: {n_in} / 7", "mono", 21, S.DIM)

# ---------- HUD ----------
def draw_hud(img, t, cur, gate):
    d = ImageDraw.Draw(img, "RGBA")
    merges_done = sum(1 for m in MERGES if m["target"] == "main" and m["rank"] <= cur)
    ci = max(0, min(LAST_RANK, int(cur))); c = COMMITS[ci]
    if t < T_REPLAY:
        beat = "same track, real history ahead" if t >= T_BRIDGE else "teaching diagram"
        title = "1 - THE CHASE" if t < T_BRIDGE else "1 > 2 - REAL HISTORY AHEAD"
    elif t < T_BOX:
        beat = ("next: IAS15 window" if t < GATES[0]["t1"] else
                "next: KissFFT window" if t < GATES[1]["t1"] else
                "next: tokens window" if t < GATES[2]["t1"] else "close: HEAD a73e97d")
        title = "2 - AS IT HAPPENED"
    else:
        return  # box draws its own titles
    ink = S.INK if dark_u_at(t) > 0.4 else TEXT_DARK
    sub = S.CYAN if dark_u_at(t) > 0.4 else DEEP["lead / main"]
    if t >= T_BRIDGE:  # during the chase the legend owns this corner (v2 idiom)
        text(d, (px(48), px(42)), title, "black", 42, ink)
        text(d, (px(48), px(96)),
             f"{beat}   commit {ci + 1}/{HIST['commit_count_all']}   merges {merges_done}/{HIST['merges_into_main']}",
             "mono", 25, sub)
        du_ = dark_u_at(t)
        strip = tuple(int((236, 240, 250)[i] * (1 - du_) + S.BG[i] * du_) for i in range(3))
        d.rectangle([0, H - px(104), W, H], fill=strip + (255,))
        text(d, (px(48), H - px(78)), f"{c['date'][:16].replace('T', ' ')}  {c['short']}  {c['subject'][:84]}",
             "mono_reg", 23, S.DIM if dark_u_at(t) > 0.4 else (90, 98, 120))
        # v5: replay scene's one short source tag + key, one line
        text(d, (W - px(48), H - px(44)),
             f"{SRC_REPLAY}  |  green = merge  |  red loop = fix",
             "mono_reg", 18, S.FAINT, anchor="ra")
        text(d, (W - px(48), px(56)), "NEWEST ^", "mono", 23, S.AMBER, anchor="ra")
        text(d, (W - px(48), H - px(150)), "OLDEST v", "mono", 23, S.FAINT, anchor="ra")

# ---------- dispatch ----------
def frame_at(t):
    if t < 1.0:
        return Image.new("RGB", (W, H), WHITE)
    du = dark_u_at(t)
    img = base_bg(du).convert("RGBA")
    cam = master_cam(t)
    cur = cursor_rank(t)
    gate, glt = gate_at(t)
    if t < T_REPLAY:
        active, node_scr = draw_chase_world(img, t, cam)
        if t >= T_BRIDGE:  # real tracks fade in ahead during the bridge
            draw_replay_world(img, t, cam, 0.0)
        if active is not None and active in node_scr and t < T_BRIDGE:
            p = clamp((t - (node_arrival(active) - 0.1)) / 0.35)
            sx, sy = node_scr[active]
            draw_popup(img, active, clamp(sx, px(60), W - px(60)), clamp(sy, px(80), H - px(80)), p)
        if t < T_BRIDGE:
            draw_legend(img)
            d = ImageDraw.Draw(img, "RGBA")
            u = lift_u(t)
            ph = "flat plane" if u < 0.02 else ("lifting into 3D..." if u < 0.98 else "marbles split at branches")
            d.rounded_rectangle([px(36), H - px(76), px(1100), H - px(24)], px(12), fill=(255, 255, 255, 215))
            text(d, (px(52), H - px(64)), f"1 - THE CHASE  |  {ph}",
                 "mono_reg", 23, (110, 118, 145))
            # v5: the chase scene's one short source tag
            text(d, (W - px(48), H - px(64)), SRC_CHASE, "mono_reg", 20, (120, 128, 150), anchor="ra")
    else:
        draw_replay_world(img, t, cam, cur, gate, glt)
        if t >= T_BOX:
            draw_box(img, t, cam, cur)
        if gate is not None:
            draw_gate_window(img, t, cam, gate, glt)
    draw_hud(img, t, cur, gate)
    out = img.convert("RGB")
    if t > T_FADE:
        out = Image.blend(out, Image.new("RGB", (W, H), NEAR_BLACK), clamp((t - T_FADE) / 1.0))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "gitvisual5.mp4"))
    ap.add_argument("--still", type=float)
    ap.add_argument("--crf", type=int, default=18)
    a = ap.parse_args()
    assign_lanes(); all_lane_pts()
    if a.still is not None:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        frame_at(a.still).save(a.out)
        print(f"still t={a.still}s -> {a.out}")
        return 0
    n = int(TOTAL * FPS)
    out = Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", str(a.crf),
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    print(f"rendering {n} frames ({TOTAL:.0f}s @ {FPS}fps, {W}x{H}) -> {out}", flush=True)
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(n):
            proc.stdin.write(frame_at(i / FPS).tobytes())
            if i % 300 == 0:
                print(f"  frame {i}/{n} [{time.time() - t0:.0f}s]", flush=True)
    finally:
        proc.stdin.close()
    rc = proc.wait()
    print(f"DONE rc={rc} {out} {out.stat().st_size / 1e6:.1f} MB wall {time.time() - t0:.0f}s")
    return rc

if __name__ == "__main__":
    raise SystemExit(main())
