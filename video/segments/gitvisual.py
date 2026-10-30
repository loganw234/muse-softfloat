"""Git-visual segment v7 (owner-directed redesign of v6/r2, per
ledger/briefs/study-video-gitvisual-v7.md): the replay becomes the
real PROCESS graph. v6/r2 showed merged git topology only (25 branch
lanes coloured by wave); the records say 93 agent episodes ran
through Wave 5 (docs/metrics/passes.jsonl: 94 rows = 93 lane
episodes + the lead spine episode). v7 draws one lane + one marble
per episode from process_graph.json (prep_process_graph.py, full
accounting: every passes row one episode, every plants verifier
attached or named unmapped), coloured by the introduction's DEEP
role legend EVERYWHERE (author=parcels teal, verifier=pink,
surveyor=studies purple, fixer=escalations red, lead=lead/main
blue; wave lane colouring deleted - waves survive only as day
separators). Author episodes ride the existing git lane geometry to
their merge (no double-draw); verifier lanes stop at their verdict
with plant ticks (orange, filled=caught, hollow=missed); surveyor
lanes terminate in a document node; fixer lanes are red returns to
their merge. A compact DEEP legend and an agent counter
(Waves 0-5, n/93) persist through the replay. Everything r2 fixed
stays fixed: chase replay camera, spine clipping, bridge
cross-fade, red persistence, falling opening + on-plate label,
interval epilogue gate, gate ranks [44, 69, 140], TOTAL 108.0 s (wave6 dwell),
open white, end near-black, sync = pure function of cursor_rank
(episode activity is a function of the same fractional rank - no
second clock).

2560x1440 @ 30 fps, video/style.py fonts/palette, 0.5 s / 120 BPM grid.
Run: $MSF_PYTHON gitvisual.py --still 12.0 --out stills7/test.png
     $MSF_PYTHON gitvisual.py --out gitvisual7.mp4
"""
from __future__ import annotations

import argparse, json, math, subprocess, sys, time
from pathlib import Path
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
# production layout: ROOT = muse-softfloat/ (HERE.parent.parent);
# the scratch study copy sat two levels below the workspace root,
# so resolve whichever layout is present (kept for study reuse).
if (HERE.parent.parent / "video" / "style.py").exists():
    ROOT = HERE.parent.parent
else:
    ROOT = HERE.parent.parent / "muse-softfloat"
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
LAST_RANK = HIST["commit_count_all"] - 1
_spec = json.loads((HERE / "spectrum_n256.json").read_text())
_inp = json.loads((HERE / "input_n256.json").read_text())
SPEC, WAVE_RE = _spec["mag"], _inp["re"]
# v6: Wave 6 epilogue sample (prep_augint_sample.py, exact arithmetic;
# stage-3 value cross-checked there against the catalogue oracle)
AUG = json.loads((HERE / "augint_sample.json").read_text(encoding="utf-8"))
IAS15 = VDATA.ias15_digests()          # asserts 2001 rows + step0/2000 pins
FIG8 = VSC.simulate_fig8(int(8 * FPS) + 2, VDATA.FIG8_T_FINAL)  # [frame,3,2]
# v7: the process graph (prep_process_graph.py; accounting inside).
# DEEP role colours are the ONLY lane colours in both halves.
PG = json.loads((HERE / "process_graph.json").read_text(encoding="utf-8"))
EPISODES = PG["episodes"]
LANE_EPS = [e for e in EPISODES if e["kind"] == "lane"]
ROLE_COL = {"lead": DEEP["lead / main"], "author": DEEP["parcels"],
            "verifier": DEEP["verifiers"], "surveyor": DEEP["studies"],
            "fixer": DEEP["escalations"]}
N_AGENTS = PG["accounting"]["lane_episodes"]  # 93 (lead spine excluded)
SLOT_MAX = max(abs(e["slot"]) for e in LANE_EPS)
GIT_OWNER = {e["git_lane"]: e for e in LANE_EPS if e.get("git_lane")}
# study labels: SF-0/1/2-class surveyors that gate a later parcel
# (Tier-2/SF-1 input studies, SF-2 input studies, SF-0 evidence).
# study-kissfft-visual / study-tokens-visual deliberately excluded:
# feasibility doodles for gates, not plan-gating studies.
STUDY_LABELS = {e["id"] for e in LANE_EPS if e["role"] == "surveyor" and (
    e["agent"].startswith(("study-tier2", "study-sf2")) or "SF-0" in e["work"])}

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
SRC_REPLAY = "src: git log @ a73e97d + metrics passes/plants"

def word_count(s):
    return len(s.split())

def rule_dwell(words):
    """THE RULE: smallest 0.5 s-grid multiple >= max(1.5, 0.5+words/2.5)."""
    return math.ceil(max(1.5, 0.5 + words / 2.5) * 2.0) / 2.0

POPUP_WORDS = [word_count(t) + sum(word_count(ln) for ln in lines)
               for t, lines in POPUP5]
POPUP_DWELL = [rule_dwell(w) + 0.5 for w in POPUP_WORDS]  # wave6 dwell +0.5 each
# Chase arrivals: first node as v4 (6.5 s), 1.0 s travel legs as v4,
# holds = rule dwell (the marble waits on its node; lighting is still
# gated on head_x, so the event itself cannot move).
ARRIVALS = []
_a = 6.5
for _dw in POPUP_DWELL:
    ARRIVALS.append(_a)
    _a += _dw + 1.0
T_BRIDGE = ARRIVALS[-1] + POPUP_DWELL[-1]          # 46.0 wave6 (v5: 42.5)
T_REPLAY = math.ceil((T_BRIDGE + 2.4) * 2.0) / 2.0  # 48.5 wave6 (v5: 45.0)
BRIDGE_DUR = T_REPLAY - T_BRIDGE                    # 2.5 (v4: 2.4)
BRIDGE_TAIL = 2.0   # r2: chase geometry fades OUT over 45.0-47.0 s
SHIFT = T_REPLAY - 31.0                             # 17.5 wave6 (v5: 14.0)
# r2 item 1: the r1 end parked 89->93 s at HEAD, then travelled
# 2.6 s before the first tip - 6.75 s of hang between the interval
# gate closing (89.0) and the first fall (95.75). Funded from that
# dead settle: opening scene starts 90.5 (1.5 s breath), the wider
# pack stagger (PACK_STAGGER below) spreads the drops 93.25-96.4,
# dimming moves to lt 6.8 (97.3). T_FADE/TOTAL unchanged.
T_BOX = 79.0 + SHIFT  # wave6: aug gate close + 1.5 (was 90.5)
T_FADE = T_BOX + 9.5  # wave6 (was 86.0+SHIFT=100.0)
TOTAL = T_FADE + 2.0  # wave6: 108.0 (was 102.0)

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
        self.roll = roll  # r2: bridge interpolates it (see master_cam)

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

NEAR_Z = 41.0

def proj_line(d, cam, pts3, core, width=7, pulse=0.0, ghost=False, alpha=None):
    """Project a 3D polyline, CLIPPING segments at the near plane.

    r2 item 4 root cause: the old filter simply dropped vertices
    with depth <= 40. A long line along the view direction drawn
    from two endpoints (the replay spine: rlo -> cursor) then
    vanished whole the moment its far-behind endpoint crossed
    behind the camera, even though most of the line was visible.
    Segments are now clipped in camera space at z = NEAR_Z, so the
    visible remainder always draws (possibly in several runs)."""
    if len(pts3) < 2:
        return
    p = np.array(pts3, float) - cam.pos
    cx, cy, cz = p @ cam.r, p @ cam.u, p @ cam.f
    runs, run = [], []
    for i in range(len(cx) - 1):
        a = np.array([cx[i], cy[i], cz[i]]); b = np.array([cx[i + 1], cy[i + 1], cz[i + 1]])
        if a[2] < NEAR_Z and b[2] < NEAR_Z:
            if len(run) >= 2:
                runs.append(run)
            run = []
            continue
        if a[2] < NEAR_Z:  # entering: clip start onto the near plane
            a = a + (b - a) * ((NEAR_Z - a[2]) / (b[2] - a[2]))
            if run:
                if len(run) >= 2:
                    runs.append(run)
                run = []
        if not run:
            run = [a]
        if b[2] < NEAR_Z:  # leaving: clip end onto the near plane
            b = a + (b - a) * ((NEAR_Z - a[2]) / (b[2] - a[2]))
            run.append(b)
            runs.append(run)
            run = []
        else:
            run.append(b)
    if len(run) >= 2:
        runs.append(run)
    for run in runs:
        arr = np.array(run)
        ok = [(float(W / 2 + cam.focal * q[0] / q[2]),
               float(H / 2 - cam.focal * q[1] / q[2])) for q in arr]
        med = float(np.median(cam.focal / arr[:, 2]))
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

# v7: wave lane colouring DELETED (r2's lane_color). Colour = DEEP
# role everywhere; waves survive only as day separators/background.
def assign_lanes():
    """Git lane slots from process_graph.json (prep replicates the
    r2 algorithm exactly; single source of truth for v7 geometry)."""
    return PG["git_slots"]

_EP_PTS = {}
def ep_pts_rs(ep):
    """Episode lane polyline in (rank, slot), monotonic in rank.
    Authors on a git lane reuse the git lane_pts_rs (no double-draw).
    Others: fork from the spine at draw_start, elbow to the episode
    slot, then by endpoint: merge -> back to slot 0 at draw_end;
    verdict/doc -> stay at slot (the lane STOPS; a node marks it).
    Sub-rank spans get proportional elbows; near-instant probes
    (span < 0.05 ranks, seconds long in the records) collapse to a
    short spur so the endpoint node still has a lane to sit on."""
    eid = ep["id"]
    if eid in _EP_PTS:
        return _EP_PTS[eid]
    if ep.get("git_lane"):
        m = next(m for m in MERGES if m["short"] == ep["git_lane"])
        pts = lane_pts_rs(m)
    else:
        s, e, slot = ep["draw_start"], ep["draw_end"], float(ep["slot"])
        span = max(0.0, e - s)
        elb = min(0.9, span / 3.0) if span > 0.05 else 0.02
        if ep["endpoint"] == "merge":
            pts = [(s, 0.0), (s + elb, slot), (e - elb, slot), (e, 0.0)]
        else:
            pts = [(s, 0.0), (s + elb, slot), (e, slot)]
        pts = sorted(pts)
        # keep strictly increasing rank for slot_at
        fixed = [pts[0]]
        for p in pts[1:]:
            if p[0] <= fixed[-1][0]:
                p = (fixed[-1][0] + 1e-4, p[1])
            fixed.append(p)
        pts = fixed
    _EP_PTS[eid] = pts
    return pts

FIX_BUMP = 110.0  # world-units height of the fixer return loop arc

def ep_zoff(ep, rank):
    """Fixer lanes are red RETURN LOOPS: the return elbow arcs up
    (raised loop in Z over the last stretch before rejoining at the
    merge rank). Pure function of rank; 0 at both ends of the arc,
    so spawn/return events stay exactly on the spine nodes."""
    if ep["role"] != "fixer" or ep["endpoint"] != "merge":
        return 0.0
    s, e = ep["draw_start"], ep["draw_end"]
    elb = min(0.9, max(0.0, e - s) / 3.0)
    lo = e - max(elb, 0.6)
    if rank <= lo or rank >= e:
        return 0.0
    return FIX_BUMP * math.sin(math.pi * (rank - lo) / (e - lo))

def ep_marble_pos(ep, cur):
    """Episode marble centre: PURE function of (episode lane, cursor
    rank) - the v4 sync model extended to episodes."""
    p = R3(cur, slot_at(ep_pts_rs(ep), cur))
    z = ep_zoff(ep, cur)
    return (p[0], p[1], p[2] + z) if z else p

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
# v6: the TOKENS window is gone. The augmented-interval gate is an
# EPILOGUE after the last frozen-history rank (history.json is frozen
# at a73e97d; the augint merge is Wave 6, later), reusing the tokens
# window's wall time (67-75+SHIFT): replay leg C now runs straight to
# HEAD, and the old leg D (75+SHIFT -> T_BOX) is the parked settle at
# HEAD - cursor_rank stays on LAST_RANK through both, so the gate hold
# sits exactly on its rank like every other gate.
GATES = [
    {"id": "ias15", "rank": float(IAS_RANK), "t0": 39.0 + SHIFT, "t1": 48.0 + SHIFT,
     "title": "IAS15 RUNS ON THE CHIP",
     "sub": "merge d9718cf - the stream waits",
     "src": "src: project record, Wave 3"},
    {"id": "kissfft", "rank": float(G1_RANK), "t0": 53.0 + SHIFT, "t1": 62.0 + SHIFT,
     "title": "KISSFFT STUDY",
     "sub": "merge 32bbd93 - the stream waits",
     "src": "src: KissFFT study report"},
    {"id": "augint", "rank": float(LAST_RANK), "t0": 69.0 + SHIFT, "t1": 77.5 + SHIFT,
     "title": "AUGMENTED INTERVALS",
     "sub": "epilogue - Wave 6, after HEAD",
     # r2 item 6: the interval proof ran on all six boards
     # 2026-10-30, all PASS (scratch/lead/interval_six_summary.txt)
     "src": "src: BOARD, Wave 6 - six boards"},
]
LEGS = [(T_REPLAY, 39.0 + SHIFT, 0.0, float(IAS_RANK)),
        (48.0 + SHIFT, 53.0 + SHIFT, float(IAS_RANK), float(G1_RANK)),
        (62.0 + SHIFT, 69.0 + SHIFT, float(G1_RANK), float(LAST_RANK))]

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
    """v6: the replay shot in the introduction's chase language (owner
    change 1). Same close-follow offset and look-ahead as chase_cam
    once lifted (-980,-760,+500, looking ~380 units ahead of the head
    marble, focal px(1150)), riding ON the climbing track: the offset
    is taken from the cursor point R3(cur,0), so the camera climbs DZ
    per rank with the head marble and the track ahead stays
    near-horizontal in frame instead of v5's distant up-ramp framing
    ((-1900,-1080,+1050) looking 900 ahead). The gate holds get the
    chase's node-arrival emphasis: a 20% close-in while a gate window
    is up, damped roll. Camera only - cursor_rank, gate holds, leg
    wall times and every marble position are unchanged."""
    cp = np.array(R3(cur, 0.0), float)
    close = 0.0
    for g in GATES:
        close = max(close, ss((t - (g["t0"] - 0.5)) / 0.7)
                    * (1 - ss((t - (g["t1"] - 0.4)) / 0.6)))
    off = np.array([-980.0, -760.0, 500.0]) * (1.0 - 0.20 * close)
    pos = cp + off
    tgt = cp + np.array([380.0, 0.0, 380.0 * DZ / DX - 55.0])
    if t >= T_BOX:  # opening dolly: ease to the end framing on the same spine
        oc = np.array(R3(BOX_RANK, 0.0), float)
        u = ss((t - T_BOX) / 3.0)
        pos = pos * (1 - u) + (oc + np.array([-1500.0, -1050.0, 850.0])) * u
        tgt = tgt * (1 - u) + (oc + np.array([0.0, 0.0, 40.0])) * u
    roll = 0.08 * math.sin(t * 0.5) * (1.0 - 0.6 * close)
    return Cam(pos, tgt, roll=roll, focal=px(1150))

def master_cam(t):
    if t < T_BRIDGE:
        return chase_cam(t)
    if t < T_REPLAY:  # bridge: one continuous flight chase -> replay angle
        u = ss((t - T_BRIDGE) / BRIDGE_DUR)
        a, b = chase_cam(t), replay_cam(t, 0.0)
        pos = a.pos * (1 - u) + b.pos * u
        tgt = a.tgt * (1 - u) + b.tgt * u
        # v6: both ends now speak chase (same focal) - constant focal
        # keeps the landing free of v5's small 1300->1200 focal step.
        # r2 item 3: interpolate ROLL too - r1 built the bridge Cam
        # with roll=0, so the whole frame snapped ~4 deg the frame
        # replay_cam's roll (0.08*sin(t/2) = -0.070 rad at 45 s)
        # switched on, and likewise dropped chase_cam's roll at 42.5.
        roll = a.roll * (1 - u) + b.roll * u
        return Cam(pos, tgt, roll=roll, focal=px(1150))
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
    # v6: window recentred on the cursor for the close chase framing
    # (v5's cur-18..cur+48 suited the distant up-ramp camera; total
    # span kept, so draw cost is unchanged)
    rlo, rhi = cur - 30.0, cur + 36.0   # close window: the tree is implied
    # track bed: cross ties + lane guides following the ramp (v7:
    # widened to the episode slot range the layout actually needed)
    bed = SLOT_MAX + 0.6
    for r in range(max(-4, int(rlo) // 4 * 4), min(LAST_RANK + 16, int(rhi) + 1), 4):
        proj_line(d, cam, [R3(r, -bed), R3(r, bed)], (70, 80, 110), 2, ghost=True)
    for sl in range(-SLOT_MAX, SLOT_MAX + 1, 2):
        proj_line(d, cam, [R3(max(rlo, -2.0), sl), R3(min(rhi, BOX_RANK), sl)], (52, 62, 92), 2, ghost=True)
    # day separators (first commit of each day, S7)
    seen = {}
    for c in COMMITS:
        seen.setdefault(c["date"][:10], c["rank"])
    for day, r in seen.items():
        if rlo <= r <= rhi:
            proj_line(d, cam, [R3(r, -bed), R3(r, bed)], (120, 130, 165), 2, alpha=80)
            (lx, ly), dep, _ = cam.one(R3(r, -bed))
            if dep > 40:
                text(d, (lx + px(8), ly - px(12)), day[5:], "mono_reg", 20, (120, 130, 160, 255), anchor="la")
    lanes = all_lane_pts()
    by_short = {m["short"]: m for m in MERGES if m["target"] == "main"}
    # v7 process graph: one lane per EPISODE, DEEP role colours.
    # Git lanes owned by an author episode are drawn HERE as that
    # episode (same geometry, no double-draw); the 6 lead-authored
    # git lanes with no author episode draw thin in lead blue.
    for short, pts in lanes.items():
        if short in GIT_OWNER:
            continue
        m = by_short[short]; col = ROLE_COL["lead"]
        gp = [R3(r, s) for r, s in clip_rs(pts, max(rlo, cur), rhi)]
        proj_line(d, cam, gp, col, 3, ghost=True)
        lp = [R3(r, s) for r, s in clip_rs(pts, rlo, min(cur, float(m["rank"])))]
        proj_line(d, cam, lp, col, 4, pulse * 0.4)
        for r in m["exclusive_ranks"]:
            if rlo <= r <= cur:
                (sx, sy), dep, scl = cam.one(R3(r, slot_at(pts, r)))
                if dep > 40:
                    rr = clamp(8.0 * scl, 2.0, px(8))
                    d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], fill=tuple(col) + (255,))
    for ep in LANE_EPS:
        if ep["draw_end"] < rlo or ep["draw_start"] > rhi:
            continue
        pts = ep_pts_rs(ep); col = ROLE_COL[ep["role"]]
        def _p3(rs_pts, ep=ep):
            out = []
            for r, s in rs_pts:
                p = R3(r, s); z = ep_zoff(ep, r)
                out.append((p[0], p[1], p[2] + z) if z else p)
            return out
        gp = _p3(clip_rs(pts, max(rlo, cur), rhi))
        proj_line(d, cam, gp, col, 3, ghost=True)
        # sample the lit part so the fixer return arc reads as a loop
        lit_rs = clip_rs(pts, rlo, min(cur, ep["draw_end"]))
        if ep["role"] == "fixer" and len(lit_rs) >= 2:
            dense, (ra, rb) = [], (lit_rs[0][0], lit_rs[-1][0])
            steps = max(2, int((rb - ra) / 0.25))
            for i_ in range(steps + 1):
                rr_ = ra + (rb - ra) * i_ / steps
                dense.append((rr_, slot_at(pts, rr_)))
            lit_rs = dense
        proj_line(d, cam, _p3(lit_rs), col, 5, pulse * 0.5)
        if ep.get("git_lane"):  # exclusive-commit dots on the git geometry
            for r in by_short[ep["git_lane"]]["exclusive_ranks"]:
                if rlo <= r <= cur:
                    (sx, sy), dep, scl = cam.one(R3(r, slot_at(pts, r)))
                    if dep > 40:
                        rr = clamp(9.0 * scl, 2.0, px(9))
                        d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], fill=tuple(col) + (255,))
    # episode endpoints: surveyor = document node (lane stops);
    # verifier = verdict node + plant ticks at the lane end
    for ep in LANE_EPS:
        if ep["endpoint"] == "merge" or not (rlo <= ep["draw_end"] <= rhi):
            continue
        p_end = R3(ep["draw_end"], float(ep["slot"]))
        (sx, sy), dep, scl = cam.one(p_end)
        if dep <= 40:
            continue
        col = ROLE_COL[ep["role"]]
        rr = clamp(13.0 * scl, 3.0, px(12))
        lit_end = cur >= ep["draw_end"]
        if ep["endpoint"] == "doc":
            # a small standing document: pale diamond, purple edge;
            # outline-only until the cursor reaches it (ghost future)
            if lit_end:
                d.polygon([(sx, sy - rr * 1.5), (sx + rr, sy), (sx, sy + rr * 1.5), (sx - rr, sy)],
                          fill=(232, 236, 248, 255), outline=tuple(col) + (255,))
            else:
                d.polygon([(sx, sy - rr * 1.5), (sx + rr, sy), (sx, sy + rr * 1.5), (sx - rr, sy)],
                          outline=tuple(col) + (160,))
        else:  # verdict
            if lit_end:
                d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], fill=tuple(col) + (255,))
                d.ellipse([sx - rr * 0.45, sy - rr * 0.45, sx + rr * 0.45, sy + rr * 0.45],
                          fill=(28, 8, 18, 255))
            else:
                d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], outline=tuple(col) + (150,), width=max(2, px(2)))
        if ep["endpoint"] == "verdict" and ep["plants"] and lit_end:
            # plant ticks: small orange marks fanning from the verdict
            # node along +rank, filled = caught, hollow = missed
            ocol = DEEP["plants"]
            for k, tk in enumerate(ep["plants"]):
                tp = R3(ep["draw_end"] + 0.28 + 0.30 * k, float(ep["slot"]))
                tp = (tp[0], tp[1], tp[2] + 30.0)
                (tx, ty), tdep, tscl = cam.one(tp)
                if tdep <= 40:
                    continue
                tr = clamp(10.0 * tscl, 2.5, px(10))
                if tk["grade"] == "caught":
                    d.rectangle([tx - tr, ty - tr, tx + tr, ty + tr], fill=tuple(ocol) + (255,))
                else:
                    d.rectangle([tx - tr, ty - tr, tx + tr, ty + tr],
                                outline=tuple(ocol) + (255,), width=max(2, px(3)))
    # spine: ghost ahead (to the opening's near rim once the end scene
    # owns the track - the track ends at the opening, not across it).
    # r2 item 4: sampled every 2 ranks (was two endpoints only, so
    # near-plane culling dropped the whole lit spine at chase
    # distance); lit behind the cursor, ghost ahead, whole replay.
    ghost_end = BOX_RANK - OPEN_HX / DX if t >= T_BOX else BOX_RANK
    def spine_pts(ra, rb):
        if rb <= ra:
            return []
        rs = [ra + 2.0 * i for i in range(int((rb - ra) / 2.0) + 1)]
        if rs[-1] < rb:
            rs.append(rb)
        return [R3(r, 0) for r in rs]
    # v7: spine in DEEP lead blue, extended to rank -2 for the
    # pre-root Wave 0 episodes (their forks precede the root commit)
    proj_line(d, cam, spine_pts(max(cur, -2.0), min(rhi, ghost_end)), ROLE_COL["lead"], 4, ghost=True)
    proj_line(d, cam, spine_pts(max(rlo, -2.0), min(cur, float(LAST_RANK))),
              ROLE_COL["lead"], 6, pulse * 0.4)
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
        proj_line(d, cam, [R3(p2, 0), R3(m["rank"], assign_lanes()[host["short"]])], DEEP["escalations"], 3, alpha=230)
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
        proj_line(d, cam, [R3(gr, -bed), R3(gr, bed)], col, 5, alpha=235)
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
    for back in (18.0, 12.0, 6.0):  # trailing spine marbles (opening scene owns them later)
        r = cur - back
        if r >= 0 and t < T_BOX:
            draw_marble(d, cam, marble_pos(r, 0.0), ROLE_COL["lead"], 22.0, 0.0, bed_z=Z0R + r * DZ)
    # v7: one travelling marble per ACTIVE episode (smaller than the
    # head marble), pure function of the cursor rank. Sendback
    # detours override the ride of the marble on their lane, as r2.
    for ep in LANE_EPS:
        if not (ep["draw_start"] <= cur < ep["draw_end"]) or t >= T_BOX:
            continue
        col = ROLE_COL[ep["role"]]
        detour = None
        lane_key = ep.get("git_lane")
        for sb in SENDBACKS:
            if sb["lane"] and sb["lane"] == lane_key and id(sb) in sb_active:
                detour = sb
        if detour is not None:
            p = interp_poly(loop_pts3(detour), sb_active[id(detour)])
            draw_marble(d, cam, p, col, 18.0, pulse, bed_z=Z0R + cur * DZ)
        else:
            draw_marble(d, cam, ep_marble_pos(ep, cur), col, 18.0, pulse * 0.6,
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
    sb_label_rects = []  # v6: branch labels must not overdraw these
    for sb in SENDBACKS:
        if not (rlo <= sb["rank"] <= rhi):
            continue
        lp3 = loop_pts3(sb)
        done = cur > sb["rank"] - 1.0 + LOOP_SPAN
        # r2 item 5: a completed loop keeps the SAME persistence as a
        # completed lane (full glow, width 5, pulse*0.5 - the lit-lane
        # call above); r1 drew inactive loops at alpha=70, width 3,
        # so every red loop faded to thin/dark the frame it finished.
        # Only a loop the cursor has not reached yet is a ghost.
        if done or id(sb) in sb_active:
            proj_line(d, cam, lp3, DEEP["escalations"], 5, pulse * 0.5)
        else:
            proj_line(d, cam, lp3, DEEP["escalations"], 3, alpha=70)
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
            # v6: keep the whole label block on-frame in the closer
            # chase framing (v5's fixed offset could crop at the edges)
            ly = clamp(ay - px(150), px(150), H - px(310))
            sb_label_rects.append((ax - px(330), ly - px(8), ax + px(330), ly + px(150)))
            # r2: dark backing so lanes/marbles behind can no longer
            # strike through the glyphs (r1: the "4cdb912" hash had
            # a lane + marble across it at 48.5 s). Draw-order fix.
            f1, f2 = S.font("black", px(25)), S.font("body", px(21))
            half = max(d.textlength(sb["label"], font=f1),
                       d.textlength(sb["sub"], font=f2)) / 2 + px(16)
            d.rounded_rectangle([ax - half, ly - px(10), ax + half, ly + px(80)],
                                px(10), fill=(5, 8, 16, 170 if dimmed else 218))
            text(d, (ax, ly), sb["label"], "black", 25, ink, anchor="ma")
            text(d, (ax, ly + px(36)), sb["sub"], "body", 21, sub_c, anchor="ma")
            if not dimmed:
                draw_badge(d, ax, ly + px(114), "FIXED - REJOINS", (248, 150, 150), 0.7 + 0.3 * pop, -6.0)
        elif done:
            draw_check(d, ax, ay, clamp(22.0 * scl, px(8), px(18)), col=(248, 150, 150))
    # branch labels near their merge (billboards, S9)
    for short, pts in lanes.items():
        m = by_short[short]
        if float(m["merge_base_rank"]) <= cur <= float(m["rank"]) + 16 and rlo <= m["rank"] <= rhi:
            (sx, sy), dep, _ = cam.one(R3(min(cur, float(m["rank"])), slot_at(pts, min(cur, float(m["rank"])))))
            if dep > 40:
                # v6: in the close chase framing a branch label can land
                # exactly on a sendback label block; the sendback text
                # wins (it is the timed reading load), the branch name
                # reappears as soon as the block moves off
                if any(rx0 <= sx <= rx1 and ry0 <= sy - px(64) <= ry1
                       for rx0, ry0, rx1, ry1 in sb_label_rects):
                    continue
                anch = "ra" if sx < W / 2 else "la"
                xo = -px(36) if anch == "ra" else px(36)
                # r2: same backing treatment for branch billboards
                bw_ = d.textlength(m["branch"], font=S.font("mono_reg", px(21)))
                bx0 = sx + xo - bw_ - px(10) if anch == "ra" else sx + xo - px(10)
                d.rounded_rectangle([bx0, sy - px(70), bx0 + bw_ + px(20), sy - px(34)],
                                    px(8), fill=(5, 8, 16, 195))
                _own = GIT_OWNER.get(short)
                _lc = ROLE_COL[_own["role"]] if _own else ROLE_COL["lead"]
                text(d, (sx + xo, sy - px(64)), m["branch"], "mono_reg", 21,
                     tuple(int(c + (255 - c) * 0.35) for c in _lc) + (255,), anchor=anch)
    # v7: study-node labels (SF-0/1/2 class only - sparse by design):
    # agent name at the document node while active and 8 ranks after
    if gate is None:
        study_rects = []
        for ep in LANE_EPS:
            if ep["id"] not in STUDY_LABELS:
                continue
            if not (ep["draw_start"] <= cur <= ep["draw_end"] + 8.0):
                continue
            if not (rlo <= ep["draw_end"] <= rhi):
                continue
            (sx, sy), dep, _ = cam.one(R3(ep["draw_end"], float(ep["slot"])))
            if dep <= 40 or not (px(80) < sx < W - px(80) and px(140) < sy < H - px(160)):
                continue
            if any(rx0 <= sx <= rx1 and ry0 <= sy - px(58) <= ry1
                   for rx0, ry0, rx1, ry1 in sb_label_rects):
                continue
            bw_ = d.textlength(ep["agent"], font=S.font("mono_reg", px(20)))
            rect = (sx - bw_ / 2 - px(10), sy - px(64), sx + bw_ / 2 + px(10), sy - px(30))
            if any(not (rect[2] < a[0] or rect[0] > a[2] or rect[3] < a[1] or rect[1] > a[3])
                   for a in study_rects):
                continue  # clustered studies: first label wins this frame
            study_rects.append(rect)
            d.rounded_rectangle(rect, px(8), fill=(5, 8, 16, 195))
            text(d, (sx, sy - px(58)), ep["agent"], "mono_reg", 20,
                 tuple(int(c + (255 - c) * 0.4) for c in ROLE_COL["surveyor"]) + (255,), anchor="ma")

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

def viz_augint(d, rect, lt, sc):
    """Wave 6 epilogue: one real catalogue row tightening stage by
    stage to the exact stage-3 sign. Bars are a labelled illustration
    on a signed-log scale around zero (the stage widths span ~9
    decades, so no linear scale can show all three); the stage-3
    value and verdict are exact (prep_augint_sample.py, cross-checked
    against the catalogue oracle row)."""
    x0, y0, x1, y1 = rect
    def T(xy, s, kind, size, color, anchor=None):
        d.text(xy, s, font=S.font(kind, max(9, int(px(size) * sc))), fill=color, anchor=anchor)
    s1, s2 = AUG["stage1_f32"], AUG["stage2_f64"]
    T((x0, y0), f"catalogue row {AUG['row_id']} of 710: one grazing ray", "mono_reg", 19, S.AMBER)
    if lt > 0.4:
        T((x0, y0 + (y1 - y0) * 0.055), "does it touch the sphere?", "body", 21, S.DIM)
    cx = (x0 + x1) / 2
    hw = (x1 - x0) * 0.34

    def sx(v):  # signed-log axis: sign * log10(1+|v|/v0), v0 = 1e-8
        return cx + math.copysign(math.log10(1.0 + abs(v) / 1e-8), v) / 11.21 * hw

    def bar(frac_y, lo, hi, col, grow, label, lo_s, hi_s):
        by = y0 + (y1 - y0) * frac_y
        bh = px(15) * sc
        xa, xb = sx(lo), sx(hi)
        xa, xb = cx + (xa - cx) * grow, cx + (xb - cx) * grow
        d.rounded_rectangle([xa, by - bh / 2, xb, by + bh / 2], px(6), fill=tuple(col) + (235,))
        d.line([(cx, by - bh), (cx, by + bh)], fill=S.INK + (255,), width=max(2, px(2)))
        T((x0, by - px(44) * sc), label, "mono", 20, col)
        if grow > 0.85:
            T((xa - px(10) * sc, by - px(12) * sc), lo_s, "mono_reg", 18, S.DIM, anchor="ra")
            T((xb + px(10) * sc, by - px(12) * sc), hi_s, "mono_reg", 18, S.DIM)
        return by

    if lt > 1.0:
        g = S.ease_out_cubic(clamp((lt - 1.0) / 0.7))
        bar(0.24, s1["lo"], s1["hi"], S.CYAN, g, "STAGE 1 - binary32",
            s1["lo_screen"], "+" + s1["hi_screen"])
    if lt > 1.7:
        T((cx, y0 + (y1 - y0) * 0.305), "crosses zero: no answer yet", "body", 20, S.DIM, anchor="ma")
    if lt > 3.2:
        g = S.ease_out_cubic(clamp((lt - 3.2) / 0.7))
        bar(0.42, s2["lo"], s2["hi"], S.VIOLET, g, "STAGE 2 - binary64",
            s2["lo_screen"], "+" + s2["hi_screen"])
    if lt > 3.9:
        T((cx, y0 + (y1 - y0) * 0.485), "tighter, still crosses zero", "body", 20, S.DIM, anchor="ma")
    if lt > 5.4:
        ex = AUG["exact_disc_float"]; mx = sx(ex)
        my = y0 + (y1 - y0) * 0.58
        pop = S.ease_out_back(clamp((lt - 5.4) / 0.4))
        rr = px(13) * sc * max(0.2, pop)
        d.line([(cx, my - px(20) * sc), (cx, my + px(20) * sc)], fill=S.INK + (255,), width=max(2, px(2)))
        d.ellipse([mx - rr, my - rr, mx + rr, my + rr], fill=S.GREEN + (255,))
        T((x0, my - px(13) * sc), "STAGE 3 - exact (augmented)", "mono", 20, S.GREEN)
        T((mx + px(22) * sc, my - px(13) * sc), AUG["exact_disc_screen"], "mono", 20, S.GREEN)
    if lt > 6.1:
        T((cx, y0 + (y1 - y0) * 0.665), "negative: a true MISS", "black", 26, S.GREEN, anchor="ma")
    if lt > 2.4:  # the sourced aggregates close the window (own beat)
        ay = y0 + (y1 - y0) * 0.76
        T((x0, ay), "710 / 710 rows - same answers", "black", 25, S.INK)
        T((x0, ay + (y1 - y0) * 0.065), "stage-3 calls: 283,314 -> 63,305", "mono", 21, S.CYAN)
        T((x0, ay + (y1 - y0) * 0.125), "all six boards: ae04caf0...c1422", "mono", 21, S.GREEN)
    if lt > 0.8:
        T((x1, y1 - px(6) * sc), "bars: illustration (log scale)", "mono_reg", 16, S.FAINT, anchor="rs")

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
    close = ss((lt - (gate["t1"] - gate["t0"] - 0.8)) / 0.8)  # wave6: dwell before close
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
        viz_augint(d, viz, lt, sc)
    # r2 item 6: "mockup" now describes the DRAWING only. On the
    # interval gate the panel states the six-board proof plainly
    # (all six PASS 2026-10-30, BOARD_SHA256 ae04caf0...c1422).
    # Pacing RULE: line 1 = 4 words (need 2.5 s), proof line = 5
    # words (need 2.5 s); both land at lt 0.8 as <=2 new lines and
    # stay to the window close (~7.2 s).
    is_aug = gate["id"] == "augint"
    if lt > 0.8:  # own beat, after the title bar (<=2 new lines/beat)
        d.text((split + px(6) * sc, cy0), "SIX BOARDS (drawing: mockup)",
               font=S.font("mono", max(9, int(px(19) * sc))), fill=S.AMBER)
        if is_aug:
            d.text((split + px(6) * sc, cy0 + px(27) * sc),
                   "all six PASS - interval proof",
                   font=S.font("mono", max(9, int(px(19) * sc))), fill=S.GREEN)
    head_h = px(61 if is_aug else 34) * sc
    pw_ = ((cx1 - split) - px(18) * sc) / 2
    ph_ = ((cy1 - cy0 - head_h) - 2 * px(30) * sc) / 3
    draw_picos_mini(d, t, state, split + px(6) * sc, cy0 + head_h,
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

# ---------- opening ending (in-world, on the spine past HEAD) ----------
# v6 (owner change 2): no box, no lid - an opening in the track plane
# at the same end position (BOX_RANK). EVERY legend system marble
# travels in one by one (lead last, same PACK_ORDER/labels as v5),
# tips over the near rim and falls in under gravity; as they land,
# the standing plate beyond the opening stamps what the process
# retains - only real artefacts of this repo: RECORD, the ledgers,
# the test vectors, the session metrics (usage.jsonl). What falls in
# is kept; nothing is scattered. The muse-softfloat label stands on
# the plate beside/above the opening through the fade to the
# near-black handoff (frame_at fade untouched). T_FADE / TOTAL are
# v5's; T_BOX moved 93.0 -> 90.5 in r2 (item 1, see report_r2.md).
PACK_ORDER = ["parcels", "verifiers", "plants", "gates", "studies",
              "escalations", "lead / main"]
PACK_STAMPS = [(1, "RECORD"), (3, "LEDGERS"), (5, "VECTORS"), (7, "METRICS")]
OPEN_HX, OPEN_HY, OPEN_DEPTH = 300.0, 320.0, 520.0  # half extents + shaft depth
FALL_G = 3400.0      # world units / s^2: plane -> shaft floor in ~0.55 s
TIP_T = 0.15         # s tipping over the rim before free fall
# r2 item 1: funded from the r1 89->93 s parked settle (T_BOX 90.5),
# the drops are SPACED wider instead of ending earlier: stagger
# 0.35 -> 0.55 s, travel stays 2.6 s. First rim 93.1, first fall
# 93.25 (r1: 95.75), last rim 96.4, all in ~96.7, dim lt 6.8.
PACK_STAGGER = 0.55
PACK_TRAVEL = 2.6
PACK_DIM_LT = 6.8    # lt at which the end dimming starts (r1: 5.8)

def _bright(col, f=0.30):
    return tuple(int(c + (255 - c) * f) for c in col)

def plane_z(x):
    """The (climbing) track plane: z of the spine at world x."""
    return Z0R + (x - X0R) * DZ / DX

def pack_state(lt):
    """[(system, rank, z_off, inside)] for the 7 packaging marbles.
    Pure functions of the end-scene clock lt: travel (PACK_STAGGER
    stagger, PACK_TRAVEL smootherstep legs) to the near rim, a 0.15 s tip
    just inside it, then free fall z_off = -(8 + FALL_G*dt^2/2) -
    believable gravity, accelerating, no bounce. inside flips once
    the marble is dropping below the plane (stamp counter)."""
    out = []
    rim = BOX_RANK - OPEN_HX / DX
    for k, name in enumerate(PACK_ORDER):
        # front-most marble departs first, lead (back-most) last, so
        # the queue files in without marbles passing through each other
        start = float(LAST_RANK) - 3.0 * k
        p = ss(clamp((lt - PACK_STAGGER * k) / PACK_TRAVEL))
        r = start + (rim - start) * p
        z_off, inside = 0.0, False
        tf = lt - (PACK_STAGGER * k + PACK_TRAVEL)  # since this marble reached the rim
        if tf > 0.0:
            if tf <= TIP_T:          # tip: ease just inside the rim, dipping
                u = tf / TIP_T
                r = rim + (90.0 / DX) * (u * u)
                z_off = -8.0 * u * u
            else:                    # free fall into the shaft
                dt = tf - TIP_T
                r = rim + 90.0 / DX
                z_off = -(8.0 + 0.5 * FALL_G * dt * dt)
                inside = z_off < -60.0
        out.append((name, r, z_off, inside))
    return out

# ---------- plate label: text IN the plate plane (r2 item 2) ----------
# r1 drew the label with screen-space text() at the projected plate
# centre: glyphs stayed screen-aligned (not on the slanted plate)
# and the stamps line, wider than the plate, crossed its border.
# r2 renders the two lines into a texture (font size shrunk until
# each line measurably fits its margins) and perspective-warps that
# texture onto an inset of the plate quad, so the text shares the
# plate's perspective and cannot cross the border by construction.
PLATE_TEX_W, PLATE_TEX_H = 1200, 440   # plate world 680x250 -> same aspect
PLATE_MARGIN_U = 70.0                  # tex px kept clear each side
PLATE_INSET_U, PLATE_INSET_V = 0.07, 0.12  # quad inset before warp

def plate_texture(n_in, dim):
    tex = Image.new("RGBA", (PLATE_TEX_W, PLATE_TEX_H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tex)
    lab = tuple(int(c * (1 - dim * 0.55) + 30 * dim) for c in S.INK) + (255,)
    grn = tuple(int(c * (1 - dim * 0.55)) for c in S.GREEN) + (255,)
    avail = PLATE_TEX_W - 2 * PLATE_MARGIN_U

    def fit_font(s, size):
        while size > 18 and td.textlength(s, font=S.font("mono", size)) > avail:
            size -= 2
        return S.font("mono", size)

    td.text((PLATE_TEX_W / 2, 66), "muse-softfloat",
            font=fit_font("muse-softfloat", 118), fill=lab, anchor="ma")
    kept = "  ".join(s for need, s in PACK_STAMPS if n_in >= need)
    if kept:
        td.text((PLATE_TEX_W / 2, 252), kept, font=fit_font(kept, 68),
                fill=grn, anchor="ma")
    return tex

def _persp_coeffs(src_quad, dst_quad):
    """PIL PERSPECTIVE coeffs mapping output px -> input px."""
    m = []
    for (x, y), (u, v) in zip(dst_quad, src_quad):
        m.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        m.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    rhs = np.array([c for uv in src_quad for c in uv], float)
    return np.linalg.solve(np.array(m, float), rhs)

def paste_on_quad(img, tex, quad_tl_tr_br_bl):
    """Warp tex onto the screen quad (TL,TR,BR,BL), bbox-local."""
    xs = [q[0] for q in quad_tl_tr_br_bl]; ys = [q[1] for q in quad_tl_tr_br_bl]
    bx, by = int(math.floor(min(xs))), int(math.floor(min(ys)))
    bw, bh = int(math.ceil(max(xs))) - bx + 1, int(math.ceil(max(ys))) - by + 1
    if bw < 4 or bh < 4:
        return
    src = [(0, 0), (tex.width, 0), (tex.width, tex.height), (0, tex.height)]
    a, b, c, dd, e, f, g, h = _persp_coeffs(src, quad_tl_tr_br_bl)
    den = g * bx + h * by + 1.0
    coeffs = (a / den, b / den, (a * bx + b * by + c) / den,
              dd / den, e / den, (dd * bx + e * by + f) / den,
              g / den, h / den)
    warped = tex.transform((bw, bh), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    mask = Image.new("L", tex.size, 255).transform(
        (bw, bh), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    arr = np.array(warped)
    arr[..., 3] = np.minimum(arr[..., 3], np.array(mask))
    img.alpha_composite(Image.fromarray(arr, "RGBA"), (bx, by))

def plate_quads(cam, lx):
    """(plate quad, inset text quad) as TL,TR,BR,BL screen points.
    The end camera looks along +X with up ~+Z, so screen-right is
    world -Y: texture-left must sit at world +Y or the text mirrors
    (caught on the first r2 still)."""
    def pt(y, dz):
        (sx, sy), _dep, _s = cam.one((lx, y, plane_z(lx) + dz))
        return np.array([sx, sy])
    tl, tr, br, bl = pt(340, 250), pt(-340, 250), pt(-340, 0), pt(340, 0)
    def bil(u, v):
        return tuple((tl * (1 - u) + tr * u) * (1 - v)
                     + (bl * (1 - u) + br * u) * v)
    iu, iv = PLATE_INSET_U, PLATE_INSET_V
    return ([tuple(tl), tuple(tr), tuple(br), tuple(bl)],
            [bil(iu, iv), bil(1 - iu, iv), bil(1 - iu, 1 - iv), bil(iu, 1 - iv)])

def draw_opening(img, t, cam, cur):
    """The opening in the track plane + falling marbles + label plate.
    Painter order is depth order for this camera (behind-side-above):
    label plate and shaft interior first, then marbles already below
    the plane (so the near slab can swallow them), then the slab
    frame around the hole, then marbles still on the plane."""
    d = ImageDraw.Draw(img, "RGBA")
    lt = t - T_BOX
    bx = X0R + BOX_RANK * DX
    dim = clamp((lt - PACK_DIM_LT) / 1.4)  # r2: starts after all 7 are in
    rimcol = tuple(int(S.INK[i] * (1 - dim * 0.75)) for i in range(3))
    def P(x, y, z):
        (sx, sy), dep, _ = cam.one((x, y, z))
        return (sx, sy)
    def Q(x, y, dz=0.0):
        return P(x, y, plane_z(x) + dz)
    x0, x1 = bx - OPEN_HX, bx + OPEN_HX          # hole extent in X
    sx0, sx1 = bx - 560.0, bx + 560.0            # slab extent in X
    sy = 560.0                                    # slab half-extent in Y
    packs = pack_state(lt)
    n_in = sum(1 for _n, _r, _z, ins in packs if ins)
    # label plate standing beyond the opening (farthest: drawn first;
    # clear of the slab so its face is never overdrawn)
    lx = bx + 650.0
    plate = [Q(lx, -340), Q(lx, 340), Q(lx, 340, 250), Q(lx, -340, 250)]
    d.polygon(plate, fill=(16, 22, 42, 255), outline=rimcol, width=max(2, px(4)))
    # shaft interior: far wall, side walls, floor (darkens with depth)
    d.polygon([Q(x1, -OPEN_HY), Q(x1, OPEN_HY), Q(x1, OPEN_HY, -OPEN_DEPTH),
               Q(x1, -OPEN_HY, -OPEN_DEPTH)], fill=(16, 21, 40, 255))
    for yy in (-OPEN_HY, OPEN_HY):
        d.polygon([Q(x0, yy), Q(x1, yy), Q(x1, yy, -OPEN_DEPTH),
                   Q(x0, yy, -OPEN_DEPTH)], fill=(11, 15, 30, 255))
    d.polygon([Q(x0, -OPEN_HY, -OPEN_DEPTH), Q(x1, -OPEN_HY, -OPEN_DEPTH),
               Q(x1, OPEN_HY, -OPEN_DEPTH), Q(x0, OPEN_HY, -OPEN_DEPTH)],
              fill=(14, 18, 34, 255))
    # what is already kept glints on the shaft floor (same colours)
    for k, (name, r, z_off, inside) in enumerate(packs):
        if inside and z_off <= -(OPEN_DEPTH - 60.0):
            fx = bx - 150.0 + (k % 4) * 100.0
            fy = -110.0 + (k // 4) * 170.0 + (k % 2) * 40.0
            draw_marble(d, cam, (fx, fy, plane_z(fx) - OPEN_DEPTH + 26.0),
                        _bright(DEEP[name], 0.35), 28.0, 0.0)
    # marbles below the plane, still falling (swallowed by slab next)
    for name, r, z_off, inside in packs:
        if z_off < -8.0 and z_off > -(OPEN_DEPTH - 60.0):
            p = R3(r, 0.0)
            draw_marble(d, cam, (p[0], p[1], p[2] + z_off), _bright(DEEP[name]),
                        28.0, beat_pulse(t) * (1 - dim))
    # slab frame around the hole (top follows the climbing plane)
    slab = (20, 26, 48, 255)
    d.polygon([Q(sx0, -sy), Q(x0, -sy), Q(x0, sy), Q(sx0, sy)], fill=slab)          # near
    d.polygon([Q(x1, -sy), Q(sx1, -sy), Q(sx1, sy), Q(x1, sy)], fill=slab)          # far
    d.polygon([Q(x0, -sy), Q(x1, -sy), Q(x1, -OPEN_HY), Q(x0, -OPEN_HY)], fill=slab)
    d.polygon([Q(x0, OPEN_HY), Q(x1, OPEN_HY), Q(x1, sy), Q(x0, sy)], fill=slab)
    d.polygon([Q(sx0, -sy), Q(sx1, -sy), Q(sx1, -sy, -80), Q(sx0, -sy, -80)],
              fill=(14, 18, 36, 255))                                                # side face
    d.polygon([Q(sx0, -sy), Q(sx0, sy), Q(sx0, sy, -80), Q(sx0, -sy, -80)],
              fill=(12, 16, 32, 255))                                                # front face
    rim = [Q(x0, -OPEN_HY), Q(x1, -OPEN_HY), Q(x1, OPEN_HY), Q(x0, OPEN_HY)]
    d.line(rim + [rim[0]], fill=tuple(rimcol) + (255,), width=max(2, px(4)), joint="curve")
    glow = tuple(int(c * (1 - dim * 0.8)) for c in S.CYAN)
    d.line(rim + [rim[0]], fill=glow + (150,), width=max(2, px(2)), joint="curve")
    # the seven system marbles still on the plane (back to front)
    labels = []
    rim_r = BOX_RANK - OPEN_HX / DX
    for k, (name, r, z_off, inside) in enumerate(reversed(packs)):
        if z_off < -8.0:
            continue
        p = R3(r, 0.0)
        mcol = _bright(DEEP[name])
        got = draw_marble(d, cam, (p[0], p[1], p[2] + z_off), mcol, 28.0,
                          beat_pulse(t) * (1 - dim), bed_z=p[2])
        if got and r < rim_r - 1.0:
            # stagger alternate labels upward so the queue reads clean
            labels.append((got[0], got[1] - got[2] - px(10 + (k % 2) * 30), name, mcol))
    for sx_, sy_, name, mcol in labels:
        if dim < 0.9:
            text(d, (sx_, sy_), name, "mono", 19, mcol, anchor="ms")
    # the retained label: IN the plate plane, legible through the
    # fade (r2 item 2 - texture warped onto the inset plate quad;
    # border re-stroked on top so the rim stays crisp)
    _p, dep, _s = cam.one((lx, 0.0, plane_z(lx) + 125.0))
    if dep > 40:
        plate_q, text_q = plate_quads(cam, lx)
        paste_on_quad(img, plate_texture(n_in, dim), text_q)
        d = ImageDraw.Draw(img, "RGBA")
        d.line(plate_q + [plate_q[0]], fill=tuple(rimcol) + (255,),
               width=max(2, px(4)), joint="curve")
    if dim < 0.9:
        text(d, (px(48), px(42)), "every system drops in, kept", "mono", 24, S.CYAN)
        text(d, (px(48), px(80)), f"marbles in: {n_in} / 7", "mono", 21, S.DIM)

# ---------- HUD ----------
def draw_replay_legend(d):
    """v7: compact DEEP role legend persisting through the replay -
    the same words/colours the introduction teaches (DEEP keys), so
    the replay keeps meaning them. Bottom-right, above the strip."""
    rows = [("lead / main", DEEP["lead / main"]), ("parcels (authors)", DEEP["parcels"]),
            ("verifiers", DEEP["verifiers"]), ("studies (surveyors)", DEEP["studies"]),
            ("escalations (fixers)", DEEP["escalations"])]
    pw_, rh = px(400), px(33)
    x1, y1 = W - px(40), H - px(124)
    x0, y0 = x1 - pw_, y1 - (rh * (len(rows) + 1) + px(20))
    d.rounded_rectangle([x0, y0, x1, y1], px(12), fill=(8, 11, 22, 215),
                        outline=(70, 80, 110), width=2)
    text(d, (x0 + px(18), y0 + px(8)), "AGENTS BY ROLE", "mono", 19, (200, 170, 90))
    for j, (name, col) in enumerate(rows):
        cy = y0 + px(46) + rh * j
        d.rounded_rectangle([x0 + px(18), cy - px(8), x0 + px(54), cy + px(8)], px(7),
                            fill=tuple(col) + (255,))
        text(d, (x0 + px(68), cy - px(13)), name, "body", 22, S.INK)
    cy = y0 + px(46) + rh * len(rows)
    oc = DEEP["plants"]
    d.rectangle([x0 + px(24), cy - px(8), x0 + px(40), cy + px(8)], fill=tuple(oc) + (255,))
    d.rectangle([x0 + px(44), cy - px(8), x0 + px(60), cy + px(8)],
                outline=tuple(oc) + (255,), width=2)
    text(d, (x0 + px(72), cy - px(13)), "plants: filled caught, hollow missed", "body", 20, S.DIM)

def draw_hud(img, t, cur, gate):
    d = ImageDraw.Draw(img, "RGBA")
    merges_done = sum(1 for m in MERGES if m["target"] == "main" and m["rank"] <= cur)
    # v7 agent counter: lane episodes whose lane has lit (pure
    # function of the cursor); scope stated on screen - Wave 6
    # episodes are outside passes.jsonl and are NOT in the 93
    agents_lit = sum(1 for e in LANE_EPS if e["draw_start"] <= cur)
    agents_active = sum(1 for e in LANE_EPS if e["draw_start"] <= cur < e["draw_end"])
    ci = max(0, min(LAST_RANK, int(cur))); c = COMMITS[ci]
    if t < T_REPLAY:
        beat = "same track, real history ahead" if t >= T_BRIDGE else "teaching diagram"
        title = "1 - THE CHASE" if t < T_BRIDGE else "1 > 2 - REAL HISTORY AHEAD"
    elif t < T_BOX:
        beat = ("next: IAS15 window" if t < GATES[0]["t1"] else
                "next: KissFFT window" if t < GATES[1]["t1"] else
                "next: interval epilogue" if t < GATES[2]["t1"] else "close: HEAD a73e97d")
        title = "2 - AS IT HAPPENED"
    else:
        return  # opening draws its own titles
    ink = S.INK if dark_u_at(t) > 0.4 else TEXT_DARK
    sub = S.CYAN if dark_u_at(t) > 0.4 else DEEP["lead / main"]
    if t >= T_BRIDGE:  # during the chase the legend owns this corner (v2 idiom)
        text(d, (px(48), px(42)),
             f"{beat}   commit {ci + 1}/{HIST['commit_count_all']}   merges {merges_done}/{HIST['merges_into_main']}"
             f"   agents {agents_lit}/{N_AGENTS} (Waves 0-5)   active {agents_active}",
             "mono", 25, sub)
        # legend from bridge start (not T_REPLAY): appearing at the
        # 45.0 seam would re-introduce a one-frame pop there (r2
        # item 3). Hidden while a gate window is up - the r2 house
        # rule "one reading load at a time"; it returns with the track.
        if gate is None:
            draw_replay_legend(d)
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
        # v7: OLDEST steps left of the persistent role legend
        text(d, (W - px(468), H - px(150)), "OLDEST v", "mono", 23, S.FAINT, anchor="ra")

# ---------- dispatch ----------
def _bridge_blend(t, cam, cur):
    """r2 item 3: ONE continuous cross-fade of the two finished
    world frames from T_BRIDGE to T_REPLAY+BRIDGE_TAIL (a=0.57 at
    the old seam), so the chase track is carried across the bridge
    and fades out over ~4.5 s instead of vanishing in the seam
    frame as in r1. The blend is of finished opaque frames, not
    transparent layers: PIL's RGBA draw-blending double-attenuates
    glow halos drawn onto a transparent layer, which itself popped
    at the seam (measured 5.51 vs 0.63 median frame diff - see
    report_r2.md)."""
    a = ss((t - T_BRIDGE) / (BRIDGE_DUR + BRIDGE_TAIL))
    du = dark_u_at(t)
    img_c = base_bg(du).convert("RGBA")
    draw_chase_world(img_c, t, cam)
    img_r = base_bg(du).convert("RGBA")
    draw_replay_world(img_r, t, cam, cur if t >= T_REPLAY else 0.0)
    return Image.blend(img_c, img_r, a)

def frame_at(t):
    if t < 1.0:
        return Image.new("RGB", (W, H), WHITE)
    du = dark_u_at(t)
    img = base_bg(du).convert("RGBA")
    cam = master_cam(t)
    cur = cursor_rank(t)
    gate, glt = gate_at(t)
    if T_BRIDGE <= t < T_REPLAY + BRIDGE_TAIL:
        img = _bridge_blend(t, cam, cur)  # r2: no world switch at the seam
        draw_hud(img, t, cur, gate)
        return img.convert("RGB")
    if t < T_REPLAY:
        active, node_scr = draw_chase_world(img, t, cam)
        if active is not None and active in node_scr and t < T_BRIDGE:
            p = clamp((t - (node_arrival(active) - 0.1)) / 0.35)
            sx, sy = node_scr[active]
            draw_popup(img, active, clamp(sx, px(60), W - px(60)), clamp(sy, px(80), H - px(80)), p)
        if t < T_BRIDGE:
            draw_legend(img)
            d = ImageDraw.Draw(img, "RGBA")
            u = lift_u(t)
            ph = "flat plane" if u < 0.02 else ("lifting into 3D..." if u < 0.98 else "marbles split at branches")
            # v5: the chase scene's one short source tag
            text(d, (W - px(48), H - px(64)), SRC_CHASE, "mono_reg", 20, (120, 128, 150), anchor="ra")
    else:
        draw_replay_world(img, t, cam, cur, gate, glt)
        if t >= T_BOX:
            draw_opening(img, t, cam, cur)
        if gate is not None:
            draw_gate_window(img, t, cam, gate, glt)
    draw_hud(img, t, cur, gate)
    out = img.convert("RGB")
    if t > T_FADE:
        out = Image.blend(out, Image.new("RGB", (W, H), NEAR_BLACK), clamp((t - T_FADE) / 1.0))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "gitvisual7.mp4"))
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
