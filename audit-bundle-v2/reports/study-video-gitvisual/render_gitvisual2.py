"""Git-visual segment v2 (polish): flat 2D white plane -> lifted 3D chase
camera -> pull-back + 90-degree axis switch -> down-to-up full-history
replay -> two study gates (six Pico mockups) -> box ending.

1920x1080 @ 30 fps, video/style.py fonts/palette, cuts on the 0.5 s /
120 BPM grid. Handoffs unchanged from v1: opens full-frame pure white
(255,255,255) held 1.0 s; ends box lid shut on near-black (3,4,9) source.
Data: history.json (real git history at a73e97d) + study datasets +
gate2_numbers.json (regen_gate2.py from refreshed usage.jsonl).

3D route (lightest honest): custom perspective projection in numpy,
vector drawing in PIL. World->camera basis from position/target/up with
bank (roll); ground plane + shadows give parallax. No 3D engine, no
network. Popups/legend/gate panels are screen-space billboards (S9).

Run: $MSF_PYTHON render_gitvisual2.py --still 12.0 --out stills2/test.png
     $MSF_PYTHON render_gitvisual2.py --out gitvisual2.mp4
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

W, H, FPS = S.W, S.H, S.FPS
TOTAL = 83.0
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
G1_RANK = next(m["rank"] for m in MERGES if m["short"] == HIST["gate_anchors"]["gate1_kissfft_merge"])
G2_RANK = next(m["rank"] for m in MERGES if m["short"] == HIST["gate_anchors"]["gate2_metrics_merge"])
LAST_RANK = HIST["commit_count_all"] - 1
_spec = json.loads((ROOT / "scratch/study-kissfft-visual/spectrum_n256.json").read_text())
_inp = json.loads((ROOT / "scratch/study-kissfft-visual/input_n256.json").read_text())
SPEC, WAVE_RE = _spec["mag"], _inp["re"]
G2N = json.loads((HERE / "gate2_numbers.json").read_text(encoding="utf-8"))

# ---------- easing / helpers ----------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def ss(x):
    """Smootherstep 6x^5-15x^4+10x^3: zero velocity AND acceleration at ends."""
    x = clamp(x)
    return x * x * x * (x * (x * 6 - 15) + 10)

def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def text(d, xy, s, kind, size, color, anchor=None):
    d.text(xy, s, font=S.font(kind, size), fill=color, anchor=anchor)

def beat_pulse(t):
    """Decay after each 0.5 s beat (120 BPM): 1 at the beat -> 0."""
    ph = (t % 0.5) / 0.5
    return math.exp(-4.0 * ph)

def glow_poly(d, pts, core, width=7, pulse=0.0):
    if len(pts) < 2:
        return
    grow = int(3 * pulse)
    halo = tuple(int(c + (255 - c) * 0.5) for c in core)
    d.line(pts, fill=halo + (55,), width=width + 16 + grow, joint="curve")
    d.line(pts, fill=halo + (110,), width=width + 7 + grow, joint="curve")
    d.line(pts, fill=tuple(core) + (255,), width=width, joint="curve")
    d.line(pts, fill=tuple(int(c + (255 - c) * 0.65) for c in core) + (255,),
           width=max(2, width // 3), joint="curve")

# ---------- minimal perspective camera (world: X trail, Y lateral, Z up) ----------
class Cam:
    def __init__(self, pos, target, roll=0.0, focal=1150.0, up_hint=(0.0, 0.0, 1.0)):
        self.pos = np.array(pos, float); self.tgt = np.array(target, float)
        self.focal = focal
        f = self.tgt - self.pos; f /= np.linalg.norm(f)
        up0 = np.array(up_hint, float)
        if abs(np.dot(f, up0)) > 0.98:  # near top-down: keep trail going right
            up0 = np.array([0.0, 1.0, 0.0])
        r = np.cross(f, up0); r /= np.linalg.norm(r)
        u = np.cross(r, f)
        if roll:  # bank: rotate right/up about forward
            c, s = math.cos(roll), math.sin(roll)
            r, u = r * c + u * s, u * c - r * s
        self.f, self.r, self.u = f, r, u

    def proj(self, pts):
        """pts Nx3 -> (screen Nx2, depth N, scale N). Behind-camera -> depth<0."""
        p = np.atleast_2d(np.asarray(pts, float)) - self.pos
        x, y, z = p @ self.r, p @ self.u, p @ self.f
        zc = np.where(np.abs(z) < 1e-6, 1e-6, z)
        sx = W / 2 + self.focal * x / zc
        sy = H / 2 - self.focal * y / zc
        return np.stack([sx, sy], 1), z, self.focal / zc

def proj_line(d, cam, pts3, core, width=7, pulse=0.0, ghost=False):
    if len(pts3) < 2:
        return
    sc, dep, scl = cam.proj(np.array(pts3, float))
    ok = [(float(sc[i, 0]), float(sc[i, 1])) for i in range(len(sc)) if dep[i] > 30]
    if len(ok) < 2:
        return
    wdt = max(2, int(width * clamp(float(np.median(scl[dep > 30])) if np.any(dep > 30) else 1.0, 0.25, 2.2)))
    if ghost:
        d.line(ok, fill=tuple(core) + (60,), width=wdt, joint="curve")
    else:
        glow_poly(d, ok, core, wdt, pulse)

# ---------- chase timeline (2D flat 1-3 s, lift 3-6.5 s, popups held 2.3 s) ----------
NODE_X = [820, 1520, 2220, 2920, 3620, 4320, 5020]
NODE_DY = [-320, 330, -320, 330, -320, 330, -320]
CHASE_END = 30.0
KEYS = [(1.0, 110.0), (3.0, 520.0), (6.5, 834.0), (8.8, 834.0)]
_t = 8.8
for _nx in NODE_X[1:]:
    _t += 1.0; KEYS.append((_t, float(_nx + 14)))
    _t += 2.3; KEYS.append((_t, float(_nx + 14)))
_t += 1.4; KEYS.append((_t, 5480.0))  # _t == 30.0
assert abs(KEYS[-1][0] - CHASE_END) < 1e-9, KEYS[-1]

def head_x(t):
    if t <= KEYS[0][0]:
        return KEYS[0][1]
    for (t0, x0), (t1, x1) in zip(KEYS, KEYS[1:]):
        if t <= t1:
            return x0 + (x1 - x0) * ss((t - t0) / max(1e-9, t1 - t0))
    return KEYS[-1][1]

def node_arrival(i):
    return (6.5, 9.8, 13.1, 16.4, 19.7, 23.0, 26.3)[i]

def lift_u(t):
    return ss((t - 3.0) / 3.5)

def trail_z(x, t):
    return lift_u(t) * 130.0

def chase_cam(t):
    """Camera pos/target/roll. All components ss()-eased -> no velocity steps."""
    hx = head_x(t); u = lift_u(t)
    hz = trail_z(hx, t)
    flat_off = np.array([-420.0, 0.0, 1900.0])     # top-down: reads as v1 2D
    chase_off = np.array([-980.0, -760.0, 500.0])  # behind-side-above
    off = flat_off * (1 - u) + chase_off * u
    close = 0.0  # close in on the active popup node, eased in/out
    for i in range(len(NODES)):
        a = node_arrival(i)
        close = max(close, ss((t - (a - 0.5)) / 0.7) * (1 - ss((t - (a + 1.9)) / 0.6)))
    off = off * (1.0 - 0.20 * close * u)
    pos = np.array([hx, 0.0, hz]) + off
    look = np.array([hx + 120.0 + 260.0 * u, 0.0, hz * 0.85])
    for i in range(len(NODES)):  # aim drifts to the lit node while its popup holds
        a = node_arrival(i)
        wgt = ss((t - (a - 0.4)) / 0.6) * (1 - ss((t - (a + 2.0)) / 0.5))
        if wgt > 0:
            node_p = np.array([NODE_X[i], NODE_DY[i], hz + 110.0 * u])
            look = look * (1 - 0.45 * wgt) + node_p * (0.45 * wgt)
    roll = u * 0.10 * math.sin(t * 0.55)
    up = np.array([0.0, 1.0 - u, u])  # flat: world Y up (trail -> right); 3D: world Z up
    return Cam(pos, look, roll=roll, focal=1150.0 + 350.0 * (1 - u), up_hint=up)

def branch_pts3(i, t):
    nx, dy, u = NODE_X[i], NODE_DY[i], lift_u(t)
    z0 = trail_z(nx, t)
    return [(nx - 340, 0.0, z0), (nx - 190, dy * 0.5, z0 + 60 * u),
            (nx - 60, dy * 0.9, z0 + 100 * u), (nx, dy, z0 + 110 * u)]

def clip_branch(pts, hx):
    """Reveal a branch as the head travels fork->node (param by head X)."""
    x_fork, x_node = pts[0][0], pts[-1][0]
    f = clamp((hx - x_fork) / max(1.0, x_node - x_fork))
    if f <= 0:
        return []
    out, total, acc = [pts[0]], 0.0, 0.0
    segs = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(segs)
    for (a, b), ln in zip(zip(pts, pts[1:]), segs):
        if acc + ln <= f * total:
            out.append(b); acc += ln
        else:
            r = (f * total - acc) / ln if ln else 0
            out.append(tuple(a[k] + (b[k] - a[k]) * r for k in range(3)))
            break
    return out

SHORT_SRC = ["src: RECORD Wave 1", "src: RECORD Wave 1 + escalations.jsonl",
             "src: ledger/verifier-w5twiddledoc.md", "src: RECORD Wave 1 + plants.jsonl",
             "src: RECORD Wave 1", "src: study-*-visual reports", "src: git log 2843792"]

def draw_popup(img, i, sx, sy, alpha_p):
    node = NODES[i]; col = DEEP[node["system"]]
    lines = node["lines"]
    pw = 780; ph = 74 + 38 * len(lines) + 34
    px = int(min(max(sx - 140, 490), W - pw - 40))
    py = int(sy - ph - 60) if NODE_DY[i] < 0 else int(sy + 60)
    py = max(140, min(py, H - ph - 70))
    py += int((1 - S.ease_out_back(alpha_p)) * -16)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([px + 9, py + 12, px + pw + 9, py + ph + 12], 18, fill=(100, 115, 155, 90))
    d.rounded_rectangle([px, py, px + pw, py + ph], 18, fill=(255, 255, 255, 250), outline=col, width=4)
    d.line([(sx, sy), (px + 70, py + ph if NODE_DY[i] < 0 else py)], fill=col, width=3)
    text(d, (px + 28, py + 18), node["title"], "black", 34, col)
    for j, ln in enumerate(lines):
        text(d, (px + 28, py + 66 + 38 * j), ln, "body", 27, TEXT_DARK)
    text(d, (px + 28, py + ph - 32), SHORT_SRC[i], "mono_reg", 20, (120, 128, 150))

def draw_legend(img):
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0 = 44, 40
    rows = list(DEEP.items())
    pw, ph = 430, 52 + 36 * len(rows)
    d.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], 14, fill=(255, 255, 255, 235),
                        outline=(190, 196, 214), width=2)
    text(d, (x0 + 22, y0 + 12), "LEGEND - SYSTEMS", "mono", 22, (110, 90, 10))
    for j, (name, col) in enumerate(rows):
        cy = y0 + 56 + 36 * j
        d.rounded_rectangle([x0 + 22, cy - 9, x0 + 62, cy + 9], 8, fill=col)
        text(d, (x0 + 78, cy - 14), name, "body", 25, TEXT_DARK)

def sc_chase(t):
    u = lift_u(t); hx = head_x(t); cam = chase_cam(t); pulse = beat_pulse(t)
    top = tuple(int(255 - 5 * u) for _ in range(3))
    bot = tuple(int(255 - 20 * u) for _ in range(3))
    grad = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    arr = (np.array(top, np.float32) * (1 - grad) + np.array(bot, np.float32) * grad).astype(np.uint8)
    img = Image.fromarray(np.repeat(arr, W, axis=1), "RGB").convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    # ground plane grid (only the window around the camera) -> parallax
    gx0 = int((hx - 2600) // 400 * 400)
    for gx in range(gx0, int(hx + 2800), 400):
        proj_line(d, cam, [(gx, -900, 0), (gx, 900, 0)], (185, 194, 218), 2, ghost=True)
    for gy in (-900, -450, 0, 450, 900):
        proj_line(d, cam, [(hx - 2600, gy, 0), (hx + 2800, gy, 0)], (195, 203, 225), 2, ghost=True)
    xs = np.linspace(90, 5510, 140)
    main3 = [(float(x), 0.0, trail_z(x, t)) for x in xs]
    shadow = [(float(x), 0.0, 0.0) for x in xs if x <= hx]
    proj_line(d, cam, shadow, (165, 174, 200), 6, ghost=True)  # lifted line's shadow
    lit = [p for p in main3 if p[0] <= hx] + [(hx, 0.0, trail_z(hx, t))]
    ghost = [p for p in main3 if p[0] > hx]
    proj_line(d, cam, ghost, DEEP["lead / main"], 4, ghost=True)
    active, node_scr = None, {}
    for i in range(len(NODES)):
        col = DEEP[NODES[i]["system"]]
        bp = branch_pts3(i, t)
        proj_line(d, cam, bp, col, 4, ghost=True)
        proj_line(d, cam, clip_branch(bp, hx), col, 6, pulse)
        if i == len(NODES) - 1:
            nx, dy = NODE_X[i], NODE_DY[i]
            rejoin = [(nx, dy, trail_z(nx, t) + 110 * u), (nx + 160, dy * 0.4, trail_z(nx, t) + 50 * u),
                      (nx + 290, 0.0, trail_z(nx, t))]
            if hx > nx:
                proj_line(d, cam, rejoin, DEEP["lead / main"], 6, pulse)
        np3 = bp[-1]
        sc, dep, scl = cam.proj(np.array([np3], float))
        if dep[0] <= 30:
            continue
        sx, sy = float(sc[0, 0]), float(sc[0, 1]); node_scr[i] = (sx, sy)
        r = clamp(17 * float(scl[0]), 3, 34)
        if t >= node_arrival(i) - 0.1:
            age = t - node_arrival(i)
            pop = S.ease_out_back(clamp(age / 0.45)) if age >= 0 else 1.0
            rr = r * (0.6 + 0.55 * pop) + 2.5 * pulse
            d.ellipse([sx - rr - 9, sy - rr - 9, sx + rr + 9, sy + rr + 9], outline=col + (130,), width=3)
            d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], fill=col + (255,))
            d.ellipse([sx - rr * 0.4, sy - rr * 0.4, sx + rr * 0.4, sy + rr * 0.4],
                      fill=tuple(int(c + (255 - c) * 0.7) for c in col) + (255,))
            if t < node_arrival(i) + 2.3:
                active = i
        else:
            d.ellipse([sx - r, sy - r, sx + r, sy + r], outline=GREY_NODE + (220,), width=4)
    proj_line(d, cam, lit, DEEP["lead / main"], 8, pulse)
    sc, dep, scl = cam.proj(np.array([(hx, 0.0, trail_z(hx, t))], float))
    if dep[0] > 30:
        sx, sy = float(sc[0, 0]), float(sc[0, 1]); r = clamp(16 * float(scl[0]), 5, 30) + 3 * pulse
        d.ellipse([sx - r - 8, sy - r - 8, sx + r + 8, sy + r + 8], outline=(29, 78, 216, 120), width=3)
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=DEEP["lead / main"] + (255,))
        d.ellipse([sx - r * 0.42, sy - r * 0.42, sx + r * 0.42, sy + r * 0.42], fill=(190, 220, 255, 255))
    if active is not None and active in node_scr:
        p = clamp((t - (node_arrival(active) - 0.1)) / 0.35)
        sx, sy = node_scr[active]
        draw_popup(img, active, clamp(sx, 60, W - 60), clamp(sy, 80, H - 80), p)
    draw_legend(img)
    ph = "flat 2D plane" if u < 0.02 else ("lifting into 3D..." if u < 0.98 else "chase camera in 3D")
    d2 = ImageDraw.Draw(img, "RGBA")
    d2.rounded_rectangle([36, H - 76, 1030, H - 24], 12, fill=(255, 255, 255, 215))
    text(d2, (52, H - 64), f"1 - THE CHASE: the trail lights each system  |  {ph}", "mono_reg", 24, (110, 118, 145))
    return img.convert("RGB")

# ---------- replay graph in (rank, lane-slot) space ----------
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
            if not any(s == slot and not (m["rank"] < a - 1 or m["merge_base_rank"] > b + 1) for s, a, b in taken):
                _LANES[m["short"]] = slot; taken.append((slot, m["merge_base_rank"], m["rank"])); break
    return _LANES

_BG = None
def dark_bg():
    global _BG
    if _BG is None:
        grad = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None, None]
        arr = (np.array(S.BG2, np.float32)[None, None, :] * (1 - grad)
               + np.array(S.BG, np.float32)[None, None, :] * grad).astype(np.uint8)
        _BG = Image.fromarray(np.repeat(arr, W, axis=1), "RGB")
    return _BG.copy()

def g2s(rank, slot, theta, len_px, lane_px, cx=960.0, cy=545.0, parallax=0.0):
    """Graph->screen. theta 0: rank runs left->right. theta 90deg: rank runs
    down->up, lanes spread left<->right. One continuous rotation = the switch."""
    a = (rank / LAST_RANK - 0.5) * len_px
    b = slot * lane_px + parallax * slot
    c, s = math.cos(theta), math.sin(theta)
    return (cx + a * c - b * s, cy - a * s + b * c) if theta > 0.01 else (cx + a, cy + b)

def clip_rank(pts, cur):
    """pts = [(rank, slot), ...] in rank order; keep rank <= cur (+interp)."""
    out = []
    for i, (r, s) in enumerate(pts):
        if r <= cur:
            out.append((r, s))
        else:
            if i:
                pr, ps = pts[i - 1]
                f = (cur - pr) / max(1e-9, r - pr)
                out.append((cur, ps + (s - ps) * f))
            break
    return out

def draw_graph(d, cur, theta, len_px, lane_px, t, labels=False, ghost_full=False, guides=True):
    lanes = assign_lanes()
    sway = 7.0 * math.sin(t * 0.6)
    def P(r, s):
        return g2s(r, s, theta, len_px, lane_px, parallax=sway * 0.35)
    seen = {}
    for c in COMMITS:
        seen.setdefault(c["date"][:10], c["rank"])
    for day, r in seen.items():
        if not guides:
            break
        p0, p1 = P(r, -4.4), P(r, 4.4)
        d.line([p0, p1], fill=(120, 130, 165, 70), width=2)
        if labels:
            ep = P(r, -4.55)
            text(d, (ep[0] + 8, ep[1] - 12), day[5:], "mono_reg", 22, (120, 130, 160, 255), anchor="la")
    for m in MERGES:
        if m["target"] != "main":
            continue
        slot = lanes[m["short"]]; col = lane_color(m["branch"])
        chain = sorted(float(r) for r in m["exclusive_ranks"])
        base_r, merge_r = float(m["merge_base_rank"]), float(m["rank"])
        mid = (base_r + merge_r) / 2
        ex0 = min(base_r + 2.0, chain[0], mid) if chain else min(base_r + 2.0, mid)
        ex1 = max(merge_r - 2.0, chain[-1], mid) if chain else max(merge_r - 2.0, mid)
        pts = [(base_r, 0.0), (ex0, float(slot))] + [(r, float(slot)) for r in chain] + [(ex1, float(slot)), (merge_r, 0.0)]
        if ghost_full:
            gp = [P(r, s) for r, s in pts]
            if len(gp) > 1:
                d.line(gp, fill=col + (55,), width=4, joint="curve")
        cp = clip_rank(pts, cur)
        sp = [P(r, s) for r, s in cp]
        if len(sp) > 1:
            glow_poly(d, sp, col, 4, beat_pulse(t) * 0.5)
        for r in m["exclusive_ranks"]:
            if r <= cur:
                x, y = P(r, slot)
                d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=col + (255,))
    sp0, sp1 = P(0, 0), P(min(cur, LAST_RANK), 0)
    glow_poly(d, [sp0, sp1], (147, 197, 253), 5, beat_pulse(t) * 0.4)
    if ghost_full:
        d.line([P(0, 0), P(LAST_RANK, 0)], fill=(240, 244, 255, 45), width=3)
    for c in COMMITS:
        if c["on_main_first_parent"] and not c["is_merge"] and c["rank"] <= cur:
            x, y = P(c["rank"], 0)
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=S.DIM + (255,))
    by_branch = {m["branch"]: m for m in MERGES if m["target"] == "main"}
    for m in MERGES:
        if m["target"] == "main" or m["rank"] > cur:
            continue
        host = by_branch.get(m["target_branch"])
        if not host:
            continue
        p2 = next(c["rank"] for c in COMMITS if c["hash"] == m["second_parent"])
        d.line([P(p2, 0), P(m["rank"], lanes[host["short"]])], fill=S.RED + (230,), width=3)
        x, y = P(m["rank"], lanes[host["short"]])
        d.ellipse([x - 6, y - 6, x + 6, y + 6], outline=S.RED + (255,), width=3)
    for m in MERGES:
        if m["target"] == "main" and m["rank"] <= cur:
            x, y = P(m["rank"], 0)
            fresh = clamp(1.0 - (cur - m["rank"]) / 6.0)
            if fresh > 0:
                rr = 10 + (1 - fresh) * 34
                d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=S.GREEN + (int(170 * fresh),), width=3)
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=S.GREEN + (255,))
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(6, 40, 26, 255))
    for gi, gr in enumerate((G1_RANK, G2_RANK), 1):
        if not guides:
            break
        p0, p1 = P(gr, -4.6), P(gr, 4.6)
        d.line([p0, p1], fill=(251, 191, 36, 235), width=4)
        if labels:
            lx = min(p0[0], p1[0]); ly = min(p0[1], p1[1])
            text(d, (lx - 10, ly - 13), f"GATE {gi}", "mono", 22, (251, 191, 36, 255), anchor="ra")
    if labels:
        band = {}
        for m in MERGES:
            if m["target"] == "main" and m["rank"] <= cur:
                slot = lanes[m["short"]]
                x, y = P(m["rank"], slot)
                for gr in (G1_RANK, G2_RANK):  # keep labels off the gate lines
                    gy_ = P(gr, 0)[1]
                    if abs(y - gy_) < 20:
                        y = gy_ - 26
                key = (slot, int(y // 44))
                while key in band:
                    y -= 26; key = (slot, int(y // 44))
                band[key] = True
                anch = "ra" if x < 960 else "la"  # label outward, away from spine
                xo = -14 if anch == "ra" else 14
                text(d, (x + xo, y - 12), m["branch"], "mono_reg", 20, lane_color(m["branch"]) + (255,), anchor=anch)

def sc_morph(t):
    """30-34 s: pull back + rotate L->R progression to down->up (no cut)."""
    lt = t - 30.0
    dim = ss((lt - 0.3) / 1.6)
    base = Image.blend(Image.new("RGB", (W, H), (238, 242, 252)), dark_bg(), dim)
    img = base.convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    rot = ss((lt - 0.7) / 2.7)
    theta = rot * math.pi / 2
    dip = 1.0 - 0.30 * math.sin(math.pi * rot)  # keep the diagonal inside frame
    len_px = (1660 + (800 - 1660) * rot) * dip
    lane_px = (62 + (112 - 62) * rot) * (1.0 - 0.15 * math.sin(math.pi * rot))
    draw_graph(d, float(LAST_RANK), theta, len_px, lane_px, t, labels=False, ghost_full=False, guides=False)
    a = ss((lt - 1.2) / 1.4)
    if a > 0:
        ink = tuple(int(S.INK[i] * a + (20, 24, 40)[i] * (1 - a)) for i in range(3))
        text(d, (48, 42), "NOW PULL BACK - AND TURN", "black", 54, ink)
        text(d, (48, 112), "the whole tree fills the screen; time now grows UP", "bold", 34, ink)
        text(d, (48, 1000), f"{HIST['commit_count_all']} commits - {HIST['merge_count']} merges - {HIST['date_first'][:10]} to {HIST['date_last'][:10]}  |  oldest at the bottom, newest at the top", "mono", 25, ink)
    return img.convert("RGB")

def sc_replay(t, rank_from, rank_to, t0, t1, beat):
    p = ss(clamp((t - t0) / (t1 - t0)))
    cur = rank_from + (rank_to - rank_from) * p
    img = dark_bg().convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    draw_graph(d, cur, math.pi / 2, 800.0, 112.0, t, labels=True, ghost_full=True)
    cx_, cy_ = g2s(cur, 0, math.pi / 2, 800.0, 112.0)
    d.line([(420, cy_), (1500, cy_)], fill=S.AMBER + (200,), width=3)
    r = 11 + 4 * beat_pulse(t)
    d.ellipse([cx_ - r, cy_ - r, cx_ + r, cy_ + r], fill=S.AMBER + (255,))
    d.ellipse([cx_ - r * 0.4, cy_ - r * 0.4, cx_ + r * 0.4, cy_ + r * 0.4], fill=(255, 240, 200, 255))
    merges_done = sum(1 for m in MERGES if m["target"] == "main" and m["rank"] <= cur)
    ci = max(0, min(LAST_RANK, int(cur))); c = COMMITS[ci]
    text(d, (48, 42), "2 - THE REPO, AS IT HAPPENED", "black", 44, S.INK)
    text(d, (48, 96), f"{beat}   commit {ci + 1}/{HIST['commit_count_all']}   merges {merges_done}/{HIST['merges_into_main']} into main", "mono", 26, S.CYAN)
    text(d, (48, 1000), f"{c['date'][:16].replace('T', ' ')}  {c['short']}  {c['subject'][:84]}", "mono_reg", 24, S.DIM)
    text(d, (W - 48, 1032), "y = committer-date order, growing UP  |  git log --all -> history.json  |  green = merge to main  |  red = lead-fix re-gate", "mono_reg", 19, S.FAINT, anchor="ra")
    text(d, (W - 48, 60), "NEWEST ^", "mono", 24, S.AMBER, anchor="ra")
    text(d, (W - 48, 940), "OLDEST v", "mono", 24, S.FAINT, anchor="ra")
    return img.convert("RGB")

# ---------- gates ----------
def draw_picos(d, t, state):
    """state 'working' blinks per board; 'pass' holds ALL six LEDs solid on."""
    x0, y0 = 1200, 215
    text(d, (x0, y0 - 58), "SIX BOARDS - mockup, not footage", "mono", 23, S.AMBER)
    for k in range(6):
        bx, by = x0 + (k % 2) * 330, y0 + (k // 2) * 205
        genuine = (k == 0)
        d.rounded_rectangle([bx, by, bx + 300, by + 165], 16, fill=(14, 64, 40), outline=(60, 160, 105), width=3)
        d.rectangle([bx + 118, by - 2, bx + 182, by + 22], fill=(150, 158, 175))
        d.rectangle([bx + 105, by + 55, bx + 195, by + 130], fill=(22, 26, 38), outline=(90, 100, 125))
        text(d, (bx + 150, by + 84), "RP2040", "mono", 20, S.DIM, anchor="mm")
        on = True if state == "pass" else (math.sin(t * 6.2 + k * 1.7) > (-0.6 if genuine else 0.05))
        led = (70, 255, 150) if on else (28, 80, 52)
        if genuine:
            d.rectangle([bx + 36, by + 34, bx + 54, by + 52], fill=led)
            lbl = "Pico (genuine) - GP25 LED"
        else:
            d.ellipse([bx + 30, by + 28, bx + 62, by + 60], fill=led, outline=(200, 255, 225) if on else (70, 90, 80), width=2)
            lbl = "RP2040-Zero - WS2812"
        if on:
            gr = 26 + (8 * beat_pulse(t) if state == "pass" else 0)
            d.ellipse([bx + 46 - gr, by + 44 - gr, bx + 46 + gr, by + 44 + gr], outline=(70, 255, 150, 90), width=3)
        text(d, (bx + 4, by + 172), lbl, "mono_reg", 20, S.DIM)

def gate_frame(t, lt, fn, title, sub):
    img = dark_bg().convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (48, 42), title, "black", 46, S.INK)
    text(d, (48, 100), sub, "mono", 25, S.CYAN)
    d.rounded_rectangle([70, 160, 1150, 845], 18, fill=(10, 14, 28, 235), outline=S.FAINT, width=3)
    fn(img, lt)
    d = ImageDraw.Draw(img, "RGBA")
    done = lt >= 6.5
    draw_picos(d, t, "pass" if done else "working")
    gy, gx = 945, 1495
    impact = math.exp(-9 * (lt - 6.5)) if done else 0.0
    ox = int(6 * impact * math.sin(lt * 90))
    d.line([(60, gy), (1860, gy)], fill=(70, 84, 120), width=6)
    run = clamp(lt / 6.5)
    glow_poly(d, [(60, gy), (60 + 1430 * run, gy)], S.CYAN, 7, beat_pulse(t))
    if not done:
        d.rectangle([gx, 852, gx + 34, 1038], fill=S.RED)
        text(d, (gx + 17, 828), "GATE", "mono", 22, S.RED, anchor="ma")
    else:
        lift = ss(clamp((lt - 6.5) / 0.7)) * 170
        d.rectangle([gx + ox, 852 - lift, gx + 34 + ox, 1038 - lift], fill=S.GREEN)
        text(d, (gx + 48, 978), "PASS - LEDs solid", "mono", 24, S.GREEN, anchor="la")
        if impact > 0.02:
            rr = 30 + (1 - impact) * 150
            d.ellipse([gx + 17 - rr, gy - rr, gx + 17 + rr, gy + rr], outline=S.GREEN + (int(200 * impact),), width=4)
        glow_poly(d, [(gx, gy), (gx + 360 * ss(clamp((lt - 6.8) / 0.9)), gy)], S.CYAN, 7, beat_pulse(t))
    return img.convert("RGB")

def gate1_viz(img, lt):
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0, x1 = 110, 195, 1110
    text(d, (x0, y0), "waveform -> twiddles -> spectrum   (illustration; spectrum via numpy - NOT KissFFT output)", "mono_reg", 21, S.AMBER)
    if lt > 0:
        n = int(len(WAVE_RE) * clamp(lt / 1.8))
        pts = [(x0 + i * (x1 - x0) / len(WAVE_RE), 320 - v * 70) for i, v in enumerate(WAVE_RE[:max(2, n)])]
        d.line(pts, fill=S.CYAN + (255,), width=3)
    text(d, (x0, 405), "shared LCG input, N=256 complex fwd (cfg 0)", "mono_reg", 21, S.DIM)
    cx, cy, r = 330, 620, 150
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=S.FAINT, width=2)
    for k in range(max(0, int(256 * clamp((lt - 1.8) / 1.8)))):
        a = -2 * math.pi * k / 256
        px_, py_ = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([px_ - 4, py_ - 4, px_ + 4, py_ + 4], fill=S.VIOLET)
    text(d, (cx, cy + r + 18), "exact-fraction twiddles e^-2pik/N", "mono_reg", 21, S.DIM, anchor="ma")
    bx0, by1, bw = 560, 790, (x1 - 560) / 128
    mx = max(SPEC[:128]) or 1
    for k in range(max(0, int(128 * clamp((lt - 3.6) / 2.7)))):
        hgt = (SPEC[k] / mx) * 300
        d.rectangle([bx0 + k * bw, by1 - hgt, bx0 + (k + 1) * bw - 1, by1], fill=S.GREEN)
    text(d, (bx0, by1 + 14), "magnitude spectrum builds bin by bin", "mono_reg", 21, S.DIM)
    if lt >= 6.3:
        d.rounded_rectangle([x0 + 60, 440, x1 - 60, 530], 14, fill=(6, 40, 26, 240), outline=S.GREEN, width=3)
        text(d, ((x0 + x1) / 2, 470), "12 / 12 CONFIGURATIONS - HASHES RECORDED", "black", 34, S.GREEN, anchor="ma")
        text(d, ((x0 + x1) / 2, 508), "src: scratch/study-kissfft-visual/report.md", "mono_reg", 20, S.DIM, anchor="ma")

def gate2_viz(img, lt):
    d = ImageDraw.Draw(img, "RGBA")
    x0, x1 = 110, 1110
    billed, inp, outp = G2N["project_billed_in_plus_out"], G2N["input_tokens"], G2N["output_tokens"]
    text(d, (x0, 195), "REGENERATED at a73e97d - definition below; v1 number retired (stale)", "mono_reg", 21, S.AMBER)
    p = S.ease_out_cubic(clamp(lt / 2.4))
    text(d, (x0, 238), f"{int(billed * p):,}", "mono", 66, S.INK)
    text(d, (x0, 316), "project billed = input + output, 93 labeled rows (usage.jsonl)", "body", 24, S.DIM)
    text(d, (x0, 350), f"input {inp:,} (cached {G2N['cached_tokens_inside_input']:,} inside input) + output {outp:,}", "mono_reg", 21, S.FAINT)
    by = 400
    d.rectangle([x0, by, x0 + (x1 - x0) * p, by + 60], fill=S.CYAN)
    d.rectangle([x0, by, x0 + 2, by + 60], fill=S.AMBER)
    text(d, (x0, by + 74), "owner-typed ~1,928 tokens (chars/4, frozen study est.) - amber tick is to scale", "body", 23, S.AMBER)
    if lt > 2.5:
        zp = S.ease_out_back(clamp((lt - 2.5) / 1.1))
        zx, zy, zw, zh = 330, 530, int(540 * max(0.05, zp)), int(180 * max(0.05, zp))
        d.rectangle([x0 - 4, by - 8, x0 + 14, by + 68], outline=S.AMBER, width=3)
        d.line([(x0 + 14, by + 68), (zx, zy)], fill=S.AMBER, width=2)
        d.rounded_rectangle([zx, zy, zx + zw, zy + zh], 12, fill=(20, 18, 10, 245), outline=S.AMBER, width=3)
        if zp > 0.6:
            text(d, (zx + 24, zy + 16), "x500,000 ZOOM", "mono", 24, S.AMBER)
            text(d, (zx + 24, zy + 54), "YOU: ~1,928 tokens [1,350-2,507]", "black", 30, S.INK)
            text(d, (zx + 24, zy + 96), "40 owner prompts - 7,713 chars (study, frozen)", "body", 24, S.DIM)
            d.rectangle([zx + 24, zy + 134, zx + 24 + int(210 * zp), zy + 156], fill=S.AMBER)
    if lt > 4.8:
        text(d, (x0, 748), f"~1 : {G2N['ratio_billed_per_owner_token']:,}  -  human share {G2N['human_share_pct']:.5f}%  -  {G2N['messages']:,} logged msgs", "black", 31, S.GREEN)
    text(d, (x0, 800), "src: regen_gate2.py <- muse-softfloat/docs/metrics/usage.jsonl @ a73e97d; owner: study-tokens-visual", "mono_reg", 19, S.FAINT)

# ---------- box ending ----------
def sc_box(t):
    lt = t - 75.0
    img = dark_bg().convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    bx0, by0, bx1, by1, gy = 1160, 430, 1640, 800, 615
    dx, dy = 90, -62  # isometric depth offset
    head = 60 + (bx0 + 210 - 60) * ss(clamp(lt / 3.0))
    dim = clamp((lt - 4.6) / 1.4)
    core = tuple(int(S.CYAN[i] * (1 - dim) + 40 * dim) for i in range(3))
    glow_poly(d, [(60, gy), (head, gy)], core, 7, beat_pulse(t) * (1 - dim))
    d.ellipse([head - 11, gy - 11, head + 11, gy + 11], fill=core + (255,))
    boxcol = tuple(int(S.INK[i] * (1 - dim * 0.75)) for i in range(3))
    d.polygon([(bx1, by0), (bx1 + dx, by0 + dy), (bx1 + dx, by1 + dy), (bx1, by1)], fill=(18, 24, 46), outline=boxcol, width=5)
    d.rectangle([bx0, by0, bx1, by1], fill=(22, 28, 52), outline=boxcol, width=6)
    shut = ss(clamp((lt - 3.2) / 1.4))  # lid swings on a hinge arc (far edge: cos/sin)
    ang = (1 - shut) * 1.85
    lx, ly = math.cos(ang) * 496, -math.sin(ang) * 300
    d.polygon([(bx0, by0), (bx0 + lx, by0 + ly), (bx0 + lx + dx, by0 + ly + dy), (bx0 + dx, by0 + dy)],
              fill=(30, 38, 70), outline=boxcol, width=6)
    d.line([(bx0, by0), (bx1, by0)], fill=boxcol, width=6)
    if dim < 0.9:
        text(d, ((bx0 + bx1) / 2, gy + 60), "muse-softfloat", "mono", 30, S.DIM, anchor="ma")
        text(d, (48, 42), "3 - BOXED", "black", 46, S.INK)
        text(d, (48, 100), "the trail goes in - the lid shuts - the neon goes dark", "mono", 25, S.CYAN)
    out = img.convert("RGB")
    if lt > 6.0:
        out = Image.blend(out, Image.new("RGB", (W, H), NEAR_BLACK), clamp((lt - 6.0) / 1.0))
    return out

# ---------- dispatch ----------
def frame_at(t):
    if t < 1.0:
        return Image.new("RGB", (W, H), WHITE)
    if t < 30.0:
        return sc_chase(t)
    if t < 34.0:
        return sc_morph(t)
    if t < 46.0:
        return sc_replay(t, 0.0, G1_RANK - 0.5, 34.0, 46.0, "replay A: Wave 0 -> KissFFT gate")
    if t < 54.0:
        return gate_frame(t, t - 46.0, gate1_viz, "GATE 1 - KISSFFT STUDY", "the line waits: a study visualisation runs on the boards")
    if t < 62.0:
        return sc_replay(t, float(G1_RANK), G2_RANK - 0.5, 54.0, 62.0, "replay B: SF-2 waves -> metrics gate")
    if t < 70.0:
        return gate_frame(t, t - 62.0, gate2_viz, "GATE 2 - TOKENS, RECOUNTED", "the line waits: who typed what, counted honestly")
    if t < 75.0:
        return sc_replay(t, float(G2_RANK), float(LAST_RANK), 70.0, 75.0, "replay C: Wave 5 close -> HEAD")
    return sc_box(t)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "gitvisual2.mp4"))
    ap.add_argument("--still", type=float)
    ap.add_argument("--crf", type=int, default=18)
    a = ap.parse_args()
    assign_lanes()
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
    print(f"rendering {n} frames ({TOTAL:.0f}s @ {FPS}fps) -> {out}", flush=True)
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



