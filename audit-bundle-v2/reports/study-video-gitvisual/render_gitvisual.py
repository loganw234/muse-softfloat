"""Rough-draft git-visual segment: white-plane chase -> real-history replay
-> two study gates with Pico mockups -> box ending.

1920x1080 @ 30 fps, video/style.py fonts/palette, cuts on the 0.5 s beat grid.
Starts EXACTLY on the intro handoff frame (full-frame 255,255,255, held 1.0 s);
ends box lid shut, neon dark, near-black (3,4,9) frames for the outro cut.
Data: history.json (extract_history.py) + the two study datasets. Programmatic.

Run (Git Bash / PowerShell, MSF_PYTHON = workspace .venv python):
  $MSF_PYTHON render_gitvisual.py --still 12.0 --out stills/test.png
  $MSF_PYTHON render_gitvisual.py --out gitvisual.mp4
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "video"))
import style as S  # noqa: E402

W, H, FPS = S.W, S.H, S.FPS
TOTAL = 78.0
NEAR_BLACK = (3, 4, 9)
WHITE = (255, 255, 255)

# System colours: deep variants read on the white plane; brights on the dark stage.
DEEP = {
    "lead / main": (29, 78, 216), "parcels": (8, 145, 178), "verifiers": (190, 24, 93),
    "plants": (217, 119, 6), "gates": (5, 150, 105), "studies": (124, 58, 237),
    "escalations": (220, 38, 38),
}
TEXT_DARK = (24, 28, 44)
GREY_NODE = (168, 174, 190)

HIST = json.loads((HERE / "history.json").read_text(encoding="utf-8"))
COMMITS = HIST["commits"]
MERGES = HIST["merges"]
NODES = HIST["node_events"]
G1_RANK = next(m["rank"] for m in MERGES if m["short"] == HIST["gate_anchors"]["gate1_kissfft_merge"])
G2_RANK = next(m["rank"] for m in MERGES if m["short"] == HIST["gate_anchors"]["gate2_metrics_merge"])
LAST_RANK = HIST["commit_count_all"] - 1

_spec = json.loads((ROOT / "scratch/study-kissfft-visual/spectrum_n256.json").read_text())
_inp = json.loads((ROOT / "scratch/study-kissfft-visual/input_n256.json").read_text())
SPEC = _spec["mag"]; WAVE_RE = _inp["re"]
TOK = json.loads((ROOT / "scratch/study-tokens-visual/data/tokens.json").read_text())
TOK_HEAD = TOK["headline"]

# ---------------------------------------------------------------- helpers

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def text(d, xy, s, kind, size, color, anchor=None):
    d.text(xy, s, font=S.font(kind, size), fill=color, anchor=anchor)

def glow_line(d, pts, core, width=7, halo_a=70):
    halo = tuple(int(c + (255 - c) * 0.45) for c in core) + (halo_a,)
    d.line(pts, fill=halo, width=width + 10, joint="curve")
    d.line(pts, fill=core, width=width, joint="curve")

# ---------------------------------------------------------------- chase

STRIP_W, TRAIL_Y = 5600, 560
NODE_X = [820, 1520, 2220, 2920, 3620, 4320, 5020]
NODE_DY = [-200, 205, -200, 205, -200, 205, -200]
KEYS: list[tuple[float, float]] = []  # (t, head_x) with pauses at nodes
_t = 1.0; KEYS.append((_t, 110.0))
for nx in NODE_X:
    _t += 1.15; KEYS.append((_t, float(nx + 14)))
    _t += 2.25; KEYS.append((_t, float(nx + 14)))
_t += 1.1; KEYS.append((_t, 5480.0))
CHASE_END = 27.0

def head_x(t: float) -> float:
    if t <= KEYS[0][0]:
        return KEYS[0][1]
    for (t0, x0), (t1, x1) in zip(KEYS, KEYS[1:]):
        if t <= t1:
            return x0 + (x1 - x0) * smooth((t - t0) / max(1e-9, t1 - t0))
    return KEYS[-1][1]

def node_arrival(i: int) -> float:
    return KEYS[1 + 2 * i][0]

def branch_pts(i: int):
    nx, dy = NODE_X[i], NODE_DY[i]
    x0 = nx - 300
    return [(x0, TRAIL_Y), (x0 + 140, TRAIL_Y + dy * 0.55), (nx - 40, TRAIL_Y + dy * 0.92), (nx, TRAIL_Y + dy)]

_STRIP = None
def chase_strip() -> Image.Image:
    global _STRIP
    if _STRIP is not None:
        return _STRIP
    img = Image.new("RGB", (STRIP_W, H), WHITE)
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(40, STRIP_W, 64):
        for y in range(40, H, 64):
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(210, 216, 230, 255))
    glow_line(d, [(90, TRAIL_Y), (5510, TRAIL_Y)], DEEP["lead / main"], 8)
    for i, node in enumerate(NODES):
        col = DEEP[node["system"]]
        glow_line(d, branch_pts(i), col, 6)
        nx, ny = NODE_X[i], TRAIL_Y + NODE_DY[i]
        d.ellipse([nx - 17, ny - 17, nx + 17, ny + 17], outline=GREY_NODE, width=5)
        if i == len(NODES) - 1:  # lead-merge branch rejoins the main line
            glow_line(d, [(nx, ny), (nx + 150, ny + 80), (nx + 270, TRAIL_Y)], DEEP["lead / main"], 6)
    _STRIP = img
    return img

SHORT_SRC = ["src: RECORD Wave 1", "src: RECORD Wave 1 + escalations.jsonl",
             "src: ledger/verifier-w5twiddledoc.md", "src: RECORD Wave 1 + plants.jsonl",
             "src: RECORD Wave 1", "src: study-*-visual reports", "src: git log 2843792"]

def draw_popup(img, i, sx, sy, alpha_p):
    node = NODES[i]; col = DEEP[node["system"]]
    lines = node["lines"]
    pw = 760; ph = 74 + 38 * len(lines) + 34
    px = int(min(max(sx - 120, 40), W - pw - 40))
    py = int(sy - ph - 56) if NODE_DY[i] < 0 else int(sy + 56)
    py = max(150, min(py, H - ph - 60))
    pop = int((1 - S.ease_out_back(alpha_p)) * -14)
    py += pop
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([px + 8, py + 10, px + pw + 8, py + ph + 10], 18, fill=(120, 130, 160, 70))
    d.rounded_rectangle([px, py, px + pw, py + ph], 18, fill=(255, 255, 255, 246), outline=col, width=4)
    d.line([(sx, sy), (px + 60, py + ph if NODE_DY[i] < 0 else py)], fill=col, width=3)
    text(d, (px + 28, py + 18), node["title"], "black", 34, col)
    for j, ln in enumerate(lines):
        text(d, (px + 28, py + 66 + 38 * j), ln, "body", 27, TEXT_DARK)
    text(d, (px + 28, py + ph - 32), SHORT_SRC[i], "mono_reg", 20, (120, 128, 150))

def draw_legend(img, dark=False):
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0 = 44, 40
    rows = list(DEEP.items())
    pw, ph = 430, 52 + 36 * len(rows)
    fill = (13, 17, 32, 215) if dark else (255, 255, 255, 232)
    d.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], 14, fill=fill,
                        outline=(90, 100, 130) if dark else (190, 196, 214), width=2)
    text(d, (x0 + 22, y0 + 12), "LEGEND - SYSTEMS", "mono", 22, S.AMBER if dark else (110, 90, 10))
    for j, (name, col) in enumerate(rows):
        cy = y0 + 56 + 36 * j
        c = col if not dark else tuple(min(255, int(v * 1.35 + 40)) for v in col)
        d.rounded_rectangle([x0 + 22, cy - 9, x0 + 62, cy + 9], 8, fill=c)
        text(d, (x0 + 78, cy - 14), name, "body", 25, S.INK if dark else TEXT_DARK)

def sc_chase(t: float) -> Image.Image:
    hx = head_x(t)
    cam = int(clamp(hx - 640, 0, STRIP_W - W))
    img = chase_strip().crop((cam, 0, cam + W, H)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    sx_head = int(hx - cam)
    d.rectangle([sx_head + 6, 0, W, H], fill=WHITE)  # hide the unrevealed future
    for x in range((-(cam % 64)) + 40, W, 64):  # restore dot grid on the white-out
        for y in range(40, H, 64):
            if x > sx_head:
                d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(210, 216, 230, 255))
    # lit nodes + active popup
    active = None
    for i in range(len(NODES)):
        if t >= node_arrival(i) - 0.15:
            nx, ny = NODE_X[i] - cam, TRAIL_Y + NODE_DY[i]
            col = DEEP[NODES[i]["system"]]
            pulse = 4 + 3 * math.sin(t * 5 + i)
            d.ellipse([nx - 22 - pulse, ny - 22 - pulse, nx + 22 + pulse, ny + 22 + pulse],
                      outline=col + (120,), width=3)
            d.ellipse([nx - 16, ny - 16, nx + 16, ny + 16], fill=col)
            if t < node_arrival(i) + 2.25:
                active = i
    # head glow
    d.ellipse([sx_head - 15, TRAIL_Y - 15, sx_head + 15, TRAIL_Y + 15], fill=DEEP["lead / main"])
    d.ellipse([sx_head - 7, TRAIL_Y - 7, sx_head + 7, TRAIL_Y + 7], fill=(160, 205, 255))
    if active is not None:
        p = clamp((t - (node_arrival(active) - 0.15)) / 0.35)
        draw_popup(img, active, NODE_X[active] - cam, TRAIL_Y + NODE_DY[active], p)
    draw_legend(img, dark=False)
    text(d, (48, H - 64), "1 - THE CHASE: each system lights as the trail reaches it", "mono_reg", 24, (110, 118, 145))
    return img.convert("RGB")

# ---------------------------------------------------------------- replay

SPINE_Y = 545
RX0, RX1 = 130, 1790

def rx(rank: float) -> float:
    return RX0 + (rank / LAST_RANK) * (RX1 - RX0)

def lane_color(branch: str):
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
    return (96, 165, 250)  # lead-* branches

_LANES: dict[str, int] = {}
def assign_lanes() -> dict[str, int]:
    if _LANES:
        return _LANES
    taken: list[tuple[int, int, int]] = []  # slot, x0rank, x1rank
    cycle = [-1, 1, -2, 2, -3, 3, -1, 2, -2, 1]
    order = [-1, 1, -2, 2, -3, 3, -4, 4]
    for k, m in enumerate([m for m in MERGES if m["target"] == "main"]):
        first = cycle[k % len(cycle)]
        for slot in [first] + [s for s in order if s != first]:
            if not any(s == slot and not (m["rank"] < a - 1 or m["merge_base_rank"] > b + 1) for s, a, b in taken):
                _LANES[m["short"]] = slot
                taken.append((slot, m["merge_base_rank"], m["rank"]))
                break
    return _LANES

_BG = None
def dark_bg() -> Image.Image:
    global _BG
    if _BG is None:
        grad = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None, None]
        arr = (np.array(S.BG2, dtype=np.float32)[None, None, :] * (1 - grad)
               + np.array(S.BG, dtype=np.float32)[None, None, :] * grad).astype(np.uint8)
        _BG = Image.fromarray(np.repeat(arr, W, axis=1), "RGB")
    return _BG.copy()

_GRAPH = None
def graph_layer() -> Image.Image:
    global _GRAPH
    if _GRAPH is not None:
        return _GRAPH
    lanes = assign_lanes()
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    # day separators from real dates
    seen = {}
    for c in COMMITS:
        seen.setdefault(c["date"][:10], c["rank"])
    for day, r in seen.items():
        x = rx(r)
        d.line([(x, 150), (x, 950)], fill=(255, 255, 255, 26), width=2)
        text(d, (x + 8, 958), day[5:], "mono_reg", 22, (120, 130, 160, 255))
    # branch lanes
    for m in MERGES:
        if m["target"] != "main":
            continue
        slot = lanes[m["short"]]; ly = SPINE_Y + slot * 62
        col = lane_color(m["branch"])
        bx_, mx_ = rx(m["merge_base_rank"]), rx(m["rank"])
        chain_x = [rx(r) for r in m["exclusive_ranks"]]
        ex0 = min(bx_ + 30, chain_x[0]) if chain_x else bx_ + 30
        ex1 = max(mx_ - 30, chain_x[-1]) if chain_x else mx_ - 30
        pts = [(bx_, SPINE_Y), (ex0, ly)] + [(x, ly) for x in chain_x] + [(ex1, ly), (mx_, SPINE_Y)]
        d.line(pts, fill=col + (90,), width=9, joint="curve")
        d.line(pts, fill=col + (255,), width=4, joint="curve")
        for r in m["exclusive_ranks"]:
            x = rx(r)
            d.ellipse([x - 5, ly - 5, x + 5, ly + 5], fill=col + (255,))
    # spine + main commits
    d.line([(rx(0), SPINE_Y), (rx(LAST_RANK), SPINE_Y)], fill=(147, 197, 253, 110), width=11)
    d.line([(rx(0), SPINE_Y), (rx(LAST_RANK), SPINE_Y)], fill=S.INK + (255,), width=5)
    for c in COMMITS:
        if c["on_main_first_parent"] and not c["is_merge"]:
            x = rx(c["rank"])
            d.ellipse([x - 4, SPINE_Y - 4, x + 4, SPINE_Y + 4], fill=S.DIM + (255,))
    # the two lead-fix re-gate merges: red second-parent connectors spine -> w1 lane
    by_branch = {m["branch"]: m for m in MERGES if m["target"] == "main"}
    for m in MERGES:
        if m["target"] == "main":
            continue
        host = by_branch.get(m["target_branch"])
        if not host:
            continue
        ly = SPINE_Y + lanes[host["short"]] * 62
        p2rank = next(c["rank"] for c in COMMITS if c["hash"] == m["second_parent"])
        d.line([(rx(p2rank), SPINE_Y), (rx(m["rank"]), ly)], fill=S.RED + (230,), width=3)
        x = rx(m["rank"])
        d.ellipse([x - 6, ly - 6, x + 6, ly + 6], outline=S.RED + (255,), width=3)
    # merge dots (gate-green) on the spine
    for m in MERGES:
        if m["target"] == "main":
            x = rx(m["rank"])
            d.ellipse([x - 9, SPINE_Y - 9, x + 9, SPINE_Y + 9], fill=S.GREEN + (255,))
            d.ellipse([x - 4, SPINE_Y - 4, x + 4, SPINE_Y + 4], fill=(6, 40, 26, 255))
    # gate bars
    for gi, gr in enumerate((G1_RANK, G2_RANK), 1):
        x = rx(gr)
        d.rectangle([x - 2, 215, x + 2, 875], fill=(251, 191, 36, 235))
        text(d, (x - 12, 182), f'GATE {gi}', 'mono', 22, (251, 191, 36, 255), anchor='ra')
    _GRAPH = img
    return img

def sc_replay(t: float, rank_from: float, rank_to: float, t0: float, t1: float, beat: str) -> Image.Image:
    p = smooth(clamp((t - t0) / (t1 - t0)))
    cur = rank_from + (rank_to - rank_from) * p
    img = dark_bg().convert("RGBA")
    cx = int(rx(cur))
    img.alpha_composite(graph_layer().crop((0, 0, max(1, cx), H)), (0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.line([(cx, 150), (cx, 950)], fill=S.AMBER + (200,), width=3)
    d.ellipse([cx - 10, SPINE_Y - 10, cx + 10, SPINE_Y + 10], fill=S.AMBER)
    lanes = assign_lanes()
    merges_done = 0
    label_right = {}
    for m in MERGES:
        if m["target"] == "main" and m["rank"] <= cur:
            merges_done += 1
            ly = SPINE_Y + lanes[m["short"]] * 62
            lx = rx(m["merge_base_rank"]) + 12
            row = int(ly) // 40
            if lx < label_right.get(row, 0) + 8:
                lx = label_right[row] + 8
            label_right[row] = lx + len(m["branch"]) * 13
            text(d, (lx, ly - 30 if lanes[m["short"]] < 0 else ly + 12),
                 m["branch"], "mono_reg", 21, lane_color(m["branch"]))
    ci = max(0, min(LAST_RANK, int(cur)))
    c = COMMITS[ci]
    text(d, (48, 42), "2 - THE REPO, AS IT HAPPENED", "black", 44, S.INK)
    text(d, (48, 96), f"{beat}   commit {ci + 1}/{HIST['commit_count_all']}   merges {merges_done}/{HIST['merges_into_main']} into main",
         "mono", 26, S.CYAN)
    text(d, (48, 1000), f"{c['date'][:16].replace('T', ' ')}  {c['short']}  {c['subject'][:86]}", "mono_reg", 24, S.DIM)
    text(d, (W - 48, 1032), "x = committer-date order  |  git log --all -> history.json  |  green dot = merge to main  |  red = lead-fix re-gate",
         "mono_reg", 20, S.FAINT, anchor="ra")
    return img.convert("RGB")

# ---------------------------------------------------------------- gates

def draw_picos(d, t: float, working: bool):
    x0, y0 = 1200, 215
    text(d, (x0, y0 - 58), "SIX BOARDS - mockup, not footage", "mono", 23, S.AMBER)
    for k in range(6):
        bx = x0 + (k % 2) * 330; by = y0 + (k // 2) * 205
        genuine = (k == 0)
        d.rounded_rectangle([bx, by, bx + 300, by + 165], 16, fill=(14, 64, 40), outline=(60, 160, 105), width=3)
        d.rectangle([bx + 118, by - 2, bx + 182, by + 22], fill=(150, 158, 175))  # USB
        d.rectangle([bx + 105, by + 55, bx + 195, by + 130], fill=(22, 26, 38), outline=(90, 100, 125))
        text(d, (bx + 150, by + 84), "RP2040", "mono", 20, S.DIM, anchor="mm")
        on = working and (math.sin(t * 6.2 + k * 1.7) > (-0.6 if genuine else 0.05))
        led = (70, 255, 150) if on else (28, 80, 52)
        if genuine:  # distinct: onboard GP25 LED, square, steadier blink
            d.rectangle([bx + 36, by + 34, bx + 54, by + 52], fill=led)
            lbl = "Pico (genuine) - GP25 LED"
        else:        # WS2812 packages on the Zero clones
            d.ellipse([bx + 30, by + 28, bx + 62, by + 60], fill=led, outline=(200, 255, 225) if on else (70, 90, 80), width=2)
            lbl = "RP2040-Zero - WS2812"
        if on:
            d.ellipse([bx + 24, by + 22, bx + 68, by + 66], outline=(70, 255, 150, 90), width=3)
        text(d, (bx + 4, by + 172), lbl, "mono_reg", 20, S.DIM)

def gate_frame(t: float, lt: float, fn, title: str, sub: str) -> Image.Image:
    img = dark_bg().convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (48, 42), title, "black", 46, S.INK)
    text(d, (48, 100), sub, "mono", 25, S.CYAN)
    d.rounded_rectangle([70, 160, 1150, 845], 18, fill=(10, 14, 28, 235), outline=S.FAINT, width=3)
    fn(img, lt)
    d = ImageDraw.Draw(img, "RGBA")
    done = lt >= 6.6
    draw_picos(d, t, working=not done)
    if done:  # all LEDs solid for the pass beat
        draw_picos(d, 0.35, working=True)
    # main line + solid gate at bottom
    gy = 945
    d.line([(60, gy), (1860, gy)], fill=(70, 84, 120), width=6)
    run = clamp(lt / 6.6)
    d.line([(60, gy), (60 + 1430 * run, gy)], fill=S.CYAN, width=7)
    gx = 1495
    if not done:
        d.rectangle([gx, 852, gx + 34, 1038], fill=S.RED)
        text(d, (gx + 17, 828), "GATE", "mono", 22, S.RED, anchor="ma")
    else:
        lift = smooth(clamp((lt - 6.6) / 0.8)) * 170
        d.rectangle([gx, 852 - lift, gx + 34, 1038 - lift], fill=S.GREEN)
        text(d, (gx + 17, 828 - lift), "PASS", "mono", 22, S.GREEN, anchor="ma")
        d.line([(gx, gy), (gx + 360 * smooth(clamp((lt - 6.9) / 0.9)), gy)], fill=S.CYAN, width=7)
    return img.convert("RGB")

def gate1_viz(img, lt: float):
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0, x1 = 110, 195, 1110
    text(d, (x0, y0), "waveform -> twiddles -> spectrum   (illustration; spectrum via numpy - NOT KissFFT output)", "mono_reg", 21, S.AMBER)
    # waveform
    if lt > 0:
        n = int(len(WAVE_RE) * clamp(lt / 1.8))
        pts = [(x0 + i * (x1 - x0) / len(WAVE_RE), 320 - v * 70) for i, v in enumerate(WAVE_RE[:max(2, n)])]
        d.line(pts, fill=S.CYAN, width=3)
    text(d, (x0, 405), "shared LCG input, N=256 complex fwd (cfg 0)", "mono_reg", 21, S.DIM)
    # twiddle unit circle
    cx, cy, r = 330, 620, 150
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=S.FAINT, width=2)
    npts = int(256 * clamp((lt - 1.8) / 1.8))
    for k in range(max(0, npts)):
        a = -2 * math.pi * k / 256
        px_, py_ = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([px_ - 4, py_ - 4, px_ + 4, py_ + 4], fill=S.VIOLET)
    text(d, (cx, cy + r + 18), "exact-fraction twiddles e^-2pik/N", "mono_reg", 21, S.DIM, anchor="ma")
    # spectrum bars grow bin by bin
    bx0, by1, bw = 560, 790, (x1 - 560) / 128
    mx = max(SPEC[:128]) or 1
    nb = int(128 * clamp((lt - 3.6) / 2.8))
    for k in range(max(0, nb)):
        hgt = (SPEC[k] / mx) * 300
        d.rectangle([bx0 + k * bw, by1 - hgt, bx0 + (k + 1) * bw - 1, by1], fill=S.GREEN)
    text(d, (bx0, by1 + 14), "magnitude spectrum builds bin by bin", "mono_reg", 21, S.DIM)
    if lt >= 6.4:
        d.rounded_rectangle([x0 + 60, 440, x1 - 60, 530], 14, fill=(6, 40, 26, 240), outline=S.GREEN, width=3)
        text(d, ((x0 + x1) / 2, 470), "12 / 12 CONFIGURATIONS - HASHES RECORDED", "black", 34, S.GREEN, anchor="ma")
        text(d, ((x0 + x1) / 2, 508), "src: scratch/study-kissfft-visual/report.md", "mono_reg", 20, S.DIM, anchor="ma")

def gate2_viz(img, lt: float):
    d = ImageDraw.Draw(img, "RGBA")
    x0, x1 = 110, 1110
    text(d, (x0, 195), "owner tokens vs project billed tokens (frozen 2026-10-28)", "mono_reg", 21, S.AMBER)
    p = S.ease_out_cubic(clamp(lt / 2.4))
    val = int(TOK_HEAD["project_billed"] * p)
    text(d, (x0, 250), f"{val:,}", "mono", 72, S.INK)
    text(d, (x0, 332), "project billed tokens (input+output; cached is inside input)", "body", 25, S.DIM)
    by = 420
    d.rectangle([x0, by, x0 + (x1 - x0) * p, by + 64], fill=S.CYAN)
    d.rectangle([x0, by, x0 + 2, by + 64], fill=S.AMBER)  # the human sliver: 1-2 px, to scale
    text(d, (x0, by + 80), "owner-typed: ~1,928 tokens (chars/4, +/-30%) - the amber tick at the left edge is to scale", "body", 24, S.AMBER)
    if lt > 2.5:
        zp = S.ease_out_back(clamp((lt - 2.5) / 1.1))
        zx, zy, zw, zh = 330, 545, int(520 * max(0.05, zp)), int(190 * max(0.05, zp))
        d.rectangle([x0 - 4, by - 8, x0 + 14, by + 72], outline=S.AMBER, width=3)
        d.line([(x0 + 14, by + 72), (zx, zy)], fill=S.AMBER, width=2)
        d.rounded_rectangle([zx, zy, zx + zw, zy + zh], 12, fill=(20, 18, 10, 245), outline=S.AMBER, width=3)
        if zp > 0.6:
            text(d, (zx + 24, zy + 18), "x500,000 ZOOM", "mono", 24, S.AMBER)
            text(d, (zx + 24, zy + 58), "YOU: ~1,928 tokens [1,350-2,507]", "black", 30, S.INK)
            text(d, (zx + 24, zy + 102), "40 owner prompts - 7,713 chars", "body", 25, S.DIM)
            d.rectangle([zx + 24, zy + 142, zx + 24 + int(200 * zp), zy + 164], fill=S.AMBER)
    if lt > 4.8:
        text(d, (x0, 760), "~1 : 785,000   -   human share 0.00013%   -   8,951 model responses", "black", 33, S.GREEN)
    text(d, (x0, 812), "src: scratch/study-tokens-visual/report.md + data/tokens.json", "mono_reg", 20, S.FAINT)

# ---------------------------------------------------------------- pullback + box

def sc_pullback(t: float) -> Image.Image:
    lt = t - 27.0
    p = smooth(clamp(lt / 2.0))
    base = Image.new("RGB", (W, H), tuple(int(WHITE[i] + (S.BG[i] - WHITE[i]) * p) for i in range(3)))
    strip = chase_strip()
    tw = int(STRIP_W + (1760 - STRIP_W) * p); th = int(H * tw / STRIP_W)
    small = strip.resize((max(2, tw), max(2, th)), Image.LANCZOS)
    base.paste(small, ((W - tw) // 2, int(430 - th / 2 + (1 - p) * 110)))
    d = ImageDraw.Draw(base, "RGBA")
    if p > 0.55:
        a = clamp((p - 0.55) / 0.35)
        ink = tuple(int(S.INK[i] * a + S.BG[i] * (1 - a)) for i in range(3))
        text(d, (W / 2, 700), "NOW PULL BACK", "black", 84, ink, anchor="ma")
        text(d, (W / 2, 798), "the real history, replayed merge by merge", "bold", 40, ink, anchor="ma")
        text(d, (W / 2, 866), f"{HIST['commit_count_all']} commits - {HIST['merge_count']} merges - {HIST['date_first'][:10]} to {HIST['date_last'][:10]}",
             "mono", 28, ink, anchor="ma")
    return base

def sc_box(t: float) -> Image.Image:
    lt = t - 70.0
    img = dark_bg().convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    bx0, by0, bx1, by1 = 1180, 400, 1620, 780
    gy = 590
    # neon trail travels in, then dims once the lid is shut
    head = 60 + (bx0 + 190 - 60) * S.ease_in_out(clamp(lt / 3.0))
    dim = clamp((lt - 4.6) / 1.4)
    core = tuple(int(S.CYAN[i] * (1 - dim) + 40 * dim) for i in range(3))
    d.line([(60, gy), (head, gy)], fill=core + (90,), width=15)
    d.line([(60, gy), (head, gy)], fill=core, width=7)
    d.ellipse([head - 11, gy - 11, head + 11, gy + 11], fill=core)
    # box body + hinged lid (lid far edge swings down 3.2s -> 4.6s)
    boxcol = tuple(int(S.INK[i] * (1 - dim * 0.75)) for i in range(3))
    d.rectangle([bx0, by0, bx1, by1], fill=(22, 28, 52))
    d.rectangle([bx0, by0, bx1, by1], outline=boxcol, width=6)
    shut = S.ease_in_out(clamp((lt - 3.2) / 1.4))
    lid_y = by0 - 190 * (1 - shut) - 6 * shut
    d.polygon([(bx0 - 26, by0), (bx0 + 70, lid_y), (bx1 + 96, lid_y), (bx1 + 26, by0)],
              fill=(30, 38, 70), outline=boxcol, width=6)
    d.line([(bx0 - 26, by0), (bx1 + 26, by0)], fill=boxcol, width=6)
    if dim < 0.9:
        text(d, ((bx0 + bx1) / 2, gy + 60), "muse-softfloat", "mono", 30, S.DIM, anchor="ma")
        text(d, (48, 42), "3 - BOXED", "black", 46, S.INK)
        text(d, (48, 100), "the trail goes in - the lid shuts - the neon goes dark", "mono", 25, S.CYAN)
    out = img.convert("RGB")
    if lt > 6.0:  # fade to the outro's exact near-black and hold it
        f = clamp((lt - 6.0) / 1.0)
        black = Image.new("RGB", (W, H), NEAR_BLACK)
        out = Image.blend(out, black, f)
    return out

# ---------------------------------------------------------------- dispatch

def frame_at(t: float) -> Image.Image:
    if t < 1.0:
        return Image.new("RGB", (W, H), WHITE)
    if t < 27.0:
        return sc_chase(t)
    if t < 29.0:
        return sc_pullback(t)
    if t < 41.0:
        return sc_replay(t, 0.0, G1_RANK - 0.5, 29.0, 41.0, "replay A: Wave 0 -> KissFFT gate")
    if t < 49.0:
        return gate_frame(t, t - 41.0, gate1_viz, "GATE 1 - KISSFFT STUDY",
                          "the line waits: a study visualisation runs on the boards")
    if t < 57.0:
        return sc_replay(t, float(G1_RANK), G2_RANK - 0.5, 49.0, 57.0, "replay B: SF-2 waves -> metrics gate")
    if t < 65.0:
        return gate_frame(t, t - 57.0, gate2_viz, "GATE 2 - TOKENS STUDY",
                          "the line waits: who typed what, counted honestly")
    if t < 70.0:
        return sc_replay(t, float(G2_RANK), float(LAST_RANK), 65.0, 70.0, "replay C: Wave 5 close -> HEAD")
    return sc_box(t)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "gitvisual.mp4"))
    ap.add_argument("--still", type=float)
    ap.add_argument("--crf", type=int, default=18)
    a = ap.parse_args()
    chase_strip(); graph_layer()
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
    t_start = time.time()
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for i in range(n):
            proc.stdin.write(frame_at(i / FPS).tobytes())
            if i % 300 == 0:
                print(f"  frame {i}/{n} [{time.time() - t_start:.0f}s]", flush=True)
    finally:
        proc.stdin.close()
    rc = proc.wait()
    print(f"DONE rc={rc} {out} {out.stat().st_size / 1e6:.1f} MB wall {time.time() - t_start:.0f}s")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

