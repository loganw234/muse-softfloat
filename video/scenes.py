"""Scene primitives. Every scene is a dict: {kind, t0, t1, ...params}.

render_scene(scene, t, ctx) draws one 1920x1080 RGB frame at absolute time t.
Kinds: kinetic, counter, barchart, linechart, ticker, orbit, stat, hash.
All motion uses eased entrances; cuts are hard (the renderer just switches
scene) with a 2-frame accent flash so the cut reads as intentional.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

import data as D
import style as S

# ---------------------------------------------------------------- background
_BG = None


def base_frame(t: float, accent=S.CYAN) -> Image.Image:
    global _BG
    if _BG is None:
        grad = np.linspace(0.0, 1.0, S.H, dtype=np.float32)[:, None, None]
        top = np.array(S.BG2, dtype=np.float32)[None, None, :]
        bot = np.array(S.BG, dtype=np.float32)[None, None, :]
        arr = (top * (1 - grad) + bot * grad).astype(np.uint8)
        arr = np.repeat(arr, S.W, axis=1)
        _BG = Image.fromarray(arr, "RGB")
    img = _BG.copy()
    d = ImageDraw.Draw(img, "RGBA")
    # panning dot grid
    ox = int((t * 24) % 64)
    for x in range(-64 + ox, S.W, 64):
        for y in range(32, S.H, 64):
            d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 255, 255, 18))
    # diagonal accent slash, top-right, drifting
    sx = int(S.W * 0.72 + 30 * math.sin(t * 0.7))
    d.polygon([(sx, 0), (sx + 260, 0), (sx + 60, S.H), (sx - 200, S.H)],
              fill=accent + (10,))
    return img


def _progress(scene: dict, t: float) -> float:
    return min(1.0, max(0.0, (t - scene["t0"]) / max(1e-9, scene["t1"] - scene["t0"])))


def _local(scene: dict, t: float) -> float:
    return max(0.0, t - scene["t0"])


def word_image(text: str, kind: str, size: int, color, tracking: int = 0) -> Image.Image:
    f = S.font(kind, size)
    tmp = Image.new("RGBA", (10, 10))
    td = ImageDraw.Draw(tmp)
    if tracking:
        w = sum(int(td.textlength(c, font=f)) + tracking for c in text)
    else:
        w = int(td.textlength(text, font=f))
    box = td.textbbox((0, 0), text, font=f)
    h = box[3] - box[1]
    im = Image.new("RGBA", (max(1, w + 8), max(1, h + 16)), (0, 0, 0, 0))
    dd = ImageDraw.Draw(im)
    if tracking:
        x = 0
        for c in text:
            dd.text((x, -box[1] + 4), c, font=f, fill=color + (255,))
            x += int(td.textlength(c, font=f)) + tracking
    else:
        dd.text((4, -box[1] + 4), text, font=f, fill=color + (255,))
    return im


def paste_scaled(img: Image.Image, word: Image.Image, cx: float, cy: float,
                 scale: float, alpha: float, anchor_x: str = "center") -> None:
    if alpha <= 0 or scale <= 0:
        return
    w = max(1, int(word.width * scale))
    h = max(1, int(word.height * scale))
    resized = word.resize((w, h), Image.LANCZOS) if scale != 1.0 else word
    if alpha < 1.0:
        a = resized.getchannel("A").point(lambda v: int(v * alpha))
        resized = resized.copy()
        resized.putalpha(a)
    x = int(cx - w / 2) if anchor_x == "center" else int(cx)
    img.alpha_composite(resized, (x, int(cy - h / 2)))


def kicker(img: Image.Image, text: str, accent, t_in: float) -> None:
    """Small tracked label, top-left, slides in."""
    if not text:
        return
    p = S.ease_out_cubic(min(1.0, t_in / 0.35))
    wi = word_image(text.upper(), "mono", S.T_SMALL, accent, tracking=6)
    paste_scaled(img, wi, 90 + (1 - p) * -40, 84, 1.0, p, anchor_x="left")
    d = ImageDraw.Draw(img)
    d.rectangle([90, 112, 90 + int(120 * p), 118], fill=accent)


def footer(img: Image.Image, scene: dict, t: float, total: float) -> None:
    d = ImageDraw.Draw(img)
    p = min(1.0, t / total) if total else 0
    d.rectangle([0, S.H - 10, S.W, S.H], fill=S.BG2)
    d.rectangle([0, S.H - 10, int(S.W * p), S.H], fill=S.AMBER)
    src = scene.get("source", "")
    if src:
        wi = word_image(src, "mono_reg", 24, S.DIM)
        img.alpha_composite(wi, (S.W - 90 - wi.width, S.H - 66))


def cut_flash(img: Image.Image, scene: dict, t: float, accent) -> None:
    lt = _local(scene, t)
    if lt < 0.09:
        d = ImageDraw.Draw(img, "RGBA")
        a = int(120 * (1 - lt / 0.09))
        d.rectangle([0, 0, S.W, 14], fill=accent + (a,))
        d.rectangle([0, S.H - 24, S.W, S.H - 10], fill=accent + (a,))


def apply_zoom(img: Image.Image, zoom: float) -> Image.Image:
    if zoom <= 1.001:
        return img
    w, h = int(S.W * zoom), int(S.H * zoom)
    big = img.resize((w, h), Image.LANCZOS)
    x, y = (w - S.W) // 2, (h - S.H) // 2
    return big.crop((x, y, x + S.W, y + S.H))


# ------------------------------------------------------------------- scenes
def sc_kinetic(scene: dict, t: float, ctx: dict) -> Image.Image:
    accent = tuple(scene.get("accent", S.CYAN))
    img = base_frame(t, accent).convert("RGBA")
    lt = _local(scene, t)
    kicker(img, scene.get("kicker", ""), accent, lt)
    lines = scene["lines"]            # list of {text, at, size?, color?}
    total_h = sum(ln.get("size", S.T_HERO) * 1.18 for ln in lines)
    y = S.H / 2 - total_h / 2
    for ln in lines:
        size = ln.get("size", S.T_HERO)
        at = ln.get("at", 0.0)
        words = ln["text"].split(" ")
        imgs = []
        for wd in words:
            col = tuple(ln.get("color", S.INK))
            if wd.startswith("*"):    # *word* renders in accent
                col, wd = accent, wd.strip("*")
            imgs.append((wd, word_image(wd, "black", size, col)))
        gap = int(size * 0.32)
        line_w = sum(w.width for _, w in imgs) + gap * (len(imgs) - 1)
        x = S.W / 2 - line_w / 2
        for i, (_wd, wi) in enumerate(imgs):
            wt = lt - at - i * scene.get("word_gap", 0.14)
            if wt > 0:
                p = min(1.0, wt / 0.32)
                scale = 0.6 + 0.4 * S.ease_out_back(p)
                paste_scaled(img, wi, x + wi.width / 2, y + size * 0.59 + (1 - S.ease_out_cubic(p)) * 34,
                             scale, S.ease_out_cubic(p))
            x += wi.width + gap
        y += size * 1.18
    sub = scene.get("sub")
    if sub and lt > scene.get("sub_at", 0.8):
        p = S.ease_out_cubic(min(1.0, (lt - scene.get("sub_at", 0.8)) / 0.4))
        wi = word_image(sub, "bold", S.T_BODY, S.DIM)
        paste_scaled(img, wi, S.W / 2, y + 46, 1.0, p)
    if scene.get("zoom"):
        img = apply_zoom(flatten(img), 1.0 + 0.045 * S.ease_in_out(_progress(scene, t))).convert("RGBA")
    return img


def sc_counter(scene: dict, t: float, ctx: dict) -> Image.Image:
    accent = tuple(scene.get("accent", S.AMBER))
    img = base_frame(t, accent).convert("RGBA")
    lt = _local(scene, t)
    kicker(img, scene.get("kicker", ""), accent, lt)
    target = int(scene["target"])
    dur = scene.get("count_dur", 1.6)
    p = S.ease_out_cubic(min(1.0, lt / dur))
    val = int(target * p)
    txt = f"{val:,}"
    wi = word_image(txt, "mono", scene.get("size", S.T_MEGA), S.INK)
    paste_scaled(img, wi, S.W / 2, S.H * 0.44, 1.0, 1.0)
    d = ImageDraw.Draw(img)
    d.rectangle([S.W / 2 - wi.width / 2, S.H * 0.44 + 130,
                 S.W / 2 - wi.width / 2 + wi.width * p, S.H * 0.44 + 142], fill=accent)
    label = word_image(scene.get("label", ""), "black", S.T_H2, accent)
    paste_scaled(img, label, S.W / 2, S.H * 0.44 + 220, 1.0, S.ease_out_cubic(min(1.0, lt / 0.5)))
    if scene.get("sub"):
        sub = word_image(scene["sub"], "body", S.T_BODY, S.DIM)
        paste_scaled(img, sub, S.W / 2, S.H * 0.44 + 300, 1.0,
                     S.ease_out_cubic(min(1.0, max(0.0, lt - 0.4) / 0.5)))
    return img


def sc_barchart(scene: dict, t: float, ctx: dict) -> Image.Image:
    accent = tuple(scene.get("accent", S.CYAN))
    img = base_frame(t, accent).convert("RGBA")
    lt = _local(scene, t)
    kicker(img, scene.get("kicker", ""), accent, lt)
    title = word_image(scene.get("title", ""), "black", S.T_H1, S.INK)
    paste_scaled(img, title, 90, 190, 1.0, S.ease_out_cubic(min(1.0, lt / 0.4)), anchor_x="left")
    rows = ctx["data"][scene.get("series", "tool_uses_by_agent")]
    vmax = max(v for _, v in rows) or 1
    x0, x1, y0, rowh = 520, 1560, 300, 82
    d = ImageDraw.Draw(img)
    for i, (name, v) in enumerate(rows):
        p = S.ease_out_cubic(min(1.0, max(0.0, lt - 0.25 - i * 0.11) / 0.9))
        y = y0 + i * rowh
        col = S.ACCENTS[i % len(S.ACCENTS)]
        nm = word_image(name, "mono", 32, S.DIM)
        img.alpha_composite(nm, (x0 - 24 - nm.width, int(y + 8)))
        d.rounded_rectangle([x0, y, x0 + int((x1 - x0) * (v / vmax) * p), y + 46],
                            radius=12, fill=col)
        val = word_image(f"{int(v * p):,}", "mono", 36, S.INK)
        img.alpha_composite(val, (x0 + int((x1 - x0) * (v / vmax) * p) + 22, int(y + 4)))
    if scene.get("sub"):
        sub = word_image(scene["sub"], "body", S.T_SMALL + 4, S.DIM)
        paste_scaled(img, sub, 90, min(y0 + len(rows) * rowh + 52, 972), 1.0,
                     S.ease_out_cubic(min(1.0, max(0.0, lt - 1.2) / 0.5)), anchor_x="left")
    return img


def sc_linechart(scene: dict, t: float, ctx: dict) -> Image.Image:
    accent = tuple(scene.get("accent", S.GREEN))
    img = base_frame(t, accent).convert("RGBA")
    lt = _local(scene, t)
    kicker(img, scene.get("kicker", ""), accent, lt)
    title = word_image(scene.get("title", ""), "black", S.T_H1, S.INK)
    paste_scaled(img, title, 90, 190, 1.0, S.ease_out_cubic(min(1.0, lt / 0.4)), anchor_x="left")
    pts = ctx["data"]["cumulative"]           # [(time, running_total)]
    vals = [v for _, v in pts]
    vmax = max(vals) or 1
    x0, x1, y0, y1 = 160, 1760, 330, 860
    d = ImageDraw.Draw(img, "RGBA")
    for gy in range(5):
        yy = y0 + (y1 - y0) * gy / 4
        d.line([x0, yy, x1, yy], fill=(255, 255, 255, 28), width=2)
    n = len(vals)
    p = S.ease_in_out(min(1.0, max(0.0, lt - 0.3) / 1.6))
    upto = max(2, int(n * p))
    xy = [(x0 + (x1 - x0) * i / (n - 1), y1 - (y1 - y0) * (v / vmax))
          for i, v in enumerate(vals[:upto])]
    d.polygon(xy + [(xy[-1][0], y1), (x0, y1)], fill=accent + (36,))
    d.line(xy, fill=accent, width=7, joint="curve")
    ex, ey = xy[-1]
    d.ellipse([ex - 13, ey - 13, ex + 13, ey + 13], fill=S.INK)
    cur = vals[upto - 1]
    lab = word_image(f"{cur:,} tool uses", "mono", 44, accent)
    img.alpha_composite(lab, (int(min(ex + 24, S.W - lab.width - 40)), int(ey - 60)))
    if scene.get("sub"):
        sub = word_image(scene["sub"], "body", S.T_SMALL + 4, S.DIM)
        paste_scaled(img, sub, S.W / 2, 950, 1.0, S.ease_out_cubic(min(1.0, max(0.0, lt - 1.0) / 0.5)))
    return img


def sc_ticker(scene: dict, t: float, ctx: dict) -> Image.Image:
    accent = tuple(scene.get("accent", S.VIOLET))
    img = base_frame(t, accent).convert("RGBA")
    lt = _local(scene, t)
    kicker(img, scene.get("kicker", ""), accent, lt)
    title = word_image(scene.get("title", ""), "black", S.T_HERO - 20, S.INK)
    p = min(1.0, lt / 0.35)
    paste_scaled(img, title, S.W / 2, 300, 0.7 + 0.3 * S.ease_out_back(p), S.ease_out_cubic(p))
    subjects = ctx["data"]["git_subjects"]
    rows_spec = [(560, 1), (720, -1), (880, 1)]
    d = ImageDraw.Draw(img)
    for r, (y, direction) in enumerate(rows_spec):
        items = subjects[r::3] or subjects
        f = S.font("mono_reg", S.T_TICKER)
        segs = []
        total = 0
        for s in items:
            txt = s + "    ///    "
            wdt = int(d.textlength(txt, font=f))
            segs.append((txt, wdt))
            total += wdt
        if total == 0:
            continue
        speed = 340 * direction
        off = int((lt * speed) % total)
        x = -off if direction > 0 else off - total
        col = S.ACCENTS[r % len(S.ACCENTS)] if r != 1 else S.DIM
        while x < S.W:
            for txt, wdt in segs:
                if x + wdt > 0:
                    d.text((x, y), txt, font=f, fill=col)
                x += wdt
        d.rectangle([0, y - 14, S.W, y - 10], fill=S.BG2)
    return img


# ------------------------------------------------------------- orbit (n-body)
def simulate_fig8(n_frames: int, t_final: float) -> np.ndarray:
    """The REAL figure-8 ICs (data.fig8_ics) integrated in float64.

    Yoshida-4 symplectic, dt=0.002: measured period-closure error ~1e-4 over
    the full span (scratch probe). This is an ILLUSTRATION of the IAS15 run
    proven bit-identical by hashes - positions cannot be decoded from the
    hash records, and the scene says so on frame. Returns [frame, body, 2].
    """
    ics = D.fig8_ics()
    pos = np.array([[p[0], p[1]] for p in ics], dtype=np.float64)
    vel = np.array([[p[2], p[3]] for p in ics], dtype=np.float64)

    def accel(p):
        a = np.zeros_like(p)
        for i in range(3):
            for j in range(3):
                if i != j:
                    d = p[j] - p[i]
                    a[i] += d / (float(np.dot(d, d)) ** 1.5)
        return a

    def leapfrog(p, v, h):
        v = v + 0.5 * h * accel(p)
        p = p + h * v
        v = v + 0.5 * h * accel(p)
        return p, v

    w1 = 1.0 / (2.0 - 2.0 ** (1.0 / 3.0))
    w0 = -2.0 ** (1.0 / 3.0) * w1
    dt = 0.002
    steps_per_frame = max(1, int(round((t_final / max(1, n_frames - 1)) / dt)))
    out = np.empty((n_frames, 3, 2))
    out[0] = pos
    for fr in range(1, n_frames):
        for _ in range(steps_per_frame):
            pos, vel = leapfrog(pos, vel, w1 * dt)
            pos, vel = leapfrog(pos, vel, w0 * dt)
            pos, vel = leapfrog(pos, vel, w1 * dt)
        out[fr] = pos
    return out


def simulate_orbits(n_frames: int, fps: int = S.FPS) -> np.ndarray:
    """2D Newtonian n-body, leapfrog. Returns positions [frame, body, 2].

    A heavy centre plus six light planets on near-circular orbits; mutual
    perturbations precess the ellipses, which is what makes the trails pretty.
    PLACEHOLDER visual only - final video swaps in real IAS15 output.
    """
    rng = np.random.default_rng(7)
    G, M = 1.0, 120.0
    radii = np.array([0.55, 0.85, 1.2, 1.6, 2.05, 2.5])
    masses = np.concatenate([[M], rng.uniform(0.4, 1.6, len(radii))])
    pos = np.zeros((len(masses), 2))
    vel = np.zeros_like(pos)
    for i, r in enumerate(radii, start=1):
        a = rng.uniform(0, 2 * math.pi)
        pos[i] = r * np.array([math.cos(a), math.sin(a)])
        v = math.sqrt(G * M / r) * rng.uniform(0.86, 1.0)   # slight eccentricity
        vel[i] = v * np.array([-math.sin(a), math.cos(a)])
    vel[0] = -(masses[1:, None] * vel[1:]).sum(axis=0) / M  # zero total momentum

    def accel(p):
        diff = p[None, :, :] - p[:, None, :]
        d2 = (diff ** 2).sum(-1) + 0.02 ** 2
        inv = d2 ** -1.5
        np.fill_diagonal(inv, 0.0)
        return G * (diff * (inv * masses[None, :])[:, :, None]).sum(axis=1)

    dt, sub = 0.0008, 12          # sim-seconds per rendered frame = dt*sub (~12 deg/frame innermost)
    out = np.empty((n_frames, len(masses), 2))
    acc = accel(pos)
    for fr in range(n_frames):
        for _ in range(sub):
            vel += 0.5 * dt * acc
            pos += dt * vel
            acc = accel(pos)
            vel += 0.5 * dt * acc
        out[fr] = pos
    return out


def sc_orbit(scene: dict, t: float, ctx: dict) -> Image.Image:
    accent = tuple(scene.get("accent", S.CYAN))
    img = base_frame(t, accent).convert("RGBA")
    lt = _local(scene, t)
    dur = scene["t1"] - scene["t0"]
    fig8 = bool(scene.get("fig8"))
    key = "orbit_fig8" if fig8 else "orbit"
    if key not in ctx:
        n_fr = int(dur * S.FPS) + 2
        ctx[key] = (simulate_fig8(n_fr, D.FIG8_T_FINAL) if fig8
                    else simulate_orbits(n_fr))
    traj = ctx[key]
    frame = min(len(traj) - 1, int(lt * S.FPS))
    cx, cy = S.W * scene.get("cx_frac", 0.62), S.H * 0.54
    scale = float(scene.get("scale", 168.0))
    zoom = 1.0 + 0.10 * S.ease_in_out(_progress(scene, t))
    scale *= zoom
    trail = int(scene.get("trail", 150))
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    d = ImageDraw.Draw(img)
    first_body = 0 if fig8 else 1
    for b in range(first_body, traj.shape[1]):
        col = S.ACCENTS[b % len(S.ACCENTS)] if fig8 else S.ACCENTS[(b - 1) % len(S.ACCENTS)]
        lo = max(0, frame - trail)
        pts = traj[lo:frame + 1, b]
        ysign = -1.0 if fig8 else 1.0   # fig8 drawn in mathematical orientation
        xy = [(cx + float(x) * scale, cy + ysign * float(y) * scale) for x, y in pts]
        for i in range(len(xy) - 1):
            a = int(200 * (i / max(1, len(xy) - 1)) ** 1.6)
            if a > 8:
                gd.line([xy[i], xy[i + 1]], fill=col + (a // 3,), width=9)
                d.line([xy[i], xy[i + 1]], fill=col + (a,), width=3)
        if xy:
            x, y = xy[-1]
            gd.ellipse([x - 20, y - 20, x + 20, y + 20], fill=col + (60,))
            d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=S.INK)
    img.alpha_composite(glow)
    if not fig8:
        sx, sy = cx + float(traj[frame, 0, 0]) * scale, cy + float(traj[frame, 0, 1]) * scale
        d.ellipse([sx - 26, sy - 26, sx + 26, sy + 26], fill=S.AMBER + (70,))
        d.ellipse([sx - 13, sy - 13, sx + 13, sy + 13], fill=S.AMBER)
    kicker(img, scene.get("kicker", ""), accent, lt)
    ly = 330
    for j, (txt, size, col) in enumerate(scene.get("lines_rgb", [])):
        at = 0.5 + j * 0.45
        if lt > at:
            p = S.ease_out_cubic(min(1.0, (lt - at) / 0.4))
            wi = word_image(txt, "black", size, tuple(col))
            paste_scaled(img, wi, 90 + (1 - p) * -30, ly + size * 0.5, 1.0, p, anchor_x="left")
        ly += size + 28
    sub_at = float(scene.get("sub_at", 2.0))
    if scene.get("sub") and lt > sub_at:
        sub = word_image(scene["sub"], "body", S.T_SMALL + 2, S.DIM)
        paste_scaled(img, sub, 90, 760, 1.0, S.ease_out_cubic(min(1.0, (lt - sub_at) / 0.5)), anchor_x="left")
    tag_txt = scene.get("tag", "SIMULATED PLACEHOLDER - real IAS15 footage lands here")
    tag = word_image(tag_txt, "mono_reg", 24, S.AMBER)
    img.alpha_composite(tag, (90, S.H - 70))
    return img


def sc_stat(scene: dict, t: float, ctx: dict) -> Image.Image:
    accent = tuple(scene.get("accent", S.PINK))
    img = base_frame(t, accent).convert("RGBA")
    lt = _local(scene, t)
    kicker(img, scene.get("kicker", ""), accent, lt)
    stats = scene["stats"]            # [{value, label, sub?}]
    n = len(stats)
    cw = (S.W - 180) / n
    d = ImageDraw.Draw(img)
    for i, st in enumerate(stats):
        at = 0.2 + i * 0.45
        if lt <= at:
            continue
        p = min(1.0, (lt - at) / 0.4)
        cx = 90 + cw * (i + 0.5)
        col = S.ACCENTS[i % len(S.ACCENTS)]
        d.rounded_rectangle([cx - cw / 2 + 18, 300, cx + cw / 2 - 18, 720],
                            radius=26, outline=col, width=4)
        val = word_image(str(st["value"]), "black", 110 if n > 2 else 150, S.INK)
        paste_scaled(img, val, cx, 440, 0.6 + 0.4 * S.ease_out_back(p), S.ease_out_cubic(p))
        lab = word_image(str(st["label"]), "bold", 36, col)
        paste_scaled(img, lab, cx, 560, 1.0, S.ease_out_cubic(p))
        if st.get("sub"):
            sub = word_image(str(st["sub"]), "body", 28, S.DIM)
            paste_scaled(img, sub, cx, 620, 1.0, S.ease_out_cubic(p))
    # plant dots grouped by verifier, plants.jsonl file order: caught green,
    # missed red. Groups: W1 f32, W1 f64, W2 f16, W2 xf, W3 str (5 each).
    if scene.get("plant_dots") and lt > 0.8:
        f = S.font("mono", 30)
        d.text((90, 768), "PLANTED DEFECTS, BY WAVE:", font=f, fill=S.DIM)
        groups = ctx["data"]["plant_groups"]
        idx = 0
        x = 90
        for label, grades in groups:
            gx = x
            for grade in grades:
                if lt >= 0.9 + idx * 0.07:
                    col = S.GREEN if grade == "caught" else S.RED
                    d.ellipse([x, 824, x + 36, 860], fill=col)
                x += 48
                idx += 1
            lab = word_image(label, "mono", 24, S.DIM)
            img.alpha_composite(lab, (gx, 872))
            x += 44
        note = word_image(scene.get(
            "plant_note",
            "the one miss taught us byte-identity - RECORD.md tells it straight"),
            "body", 30, S.DIM)
        paste_scaled(img, note, 90, 940, 1.0,
                     S.ease_out_cubic(min(1.0, max(0.0, lt - 2.7) / 0.5)), anchor_x="left")
    return img


def sc_hash(scene: dict, t: float, ctx: dict) -> Image.Image:
    accent = tuple(scene.get("accent", S.GREEN))
    img = base_frame(t, accent).convert("RGBA")
    lt = _local(scene, t)
    kicker(img, scene.get("kicker", ""), accent, lt)
    title = word_image(scene.get("title", "SAME HASH. BOTH MACHINES."), "black", S.T_H1, S.INK)
    paste_scaled(img, title, S.W / 2, 300, 1.0, S.ease_out_cubic(min(1.0, lt / 0.4)))
    full = scene.get("hash", D.HEADLINE["board_hash_w1"])
    tdur = float(scene.get("type_dur", 1.1))
    shown = int(len(full) * S.ease_out_cubic(min(1.0, max(0.0, lt - 0.3) / tdur)))
    lines = [full[:32], full[32:]]
    d = ImageDraw.Draw(img)
    for li, line in enumerate(lines):
        s_here = max(0, min(32, shown - li * 32))
        txt = line[:s_here] + ("_" if s_here < 32 and lt > 0.3 else "")
        full_wi = word_image("SHA-256  " + lines[0], "mono", 40, accent)
        wi = word_image("SHA-256  " + txt if li == 0 else "         " + txt, "mono", 40, accent)
        img.alpha_composite(wi, (int(S.W / 2 - full_wi.width / 2), 470 + li * 84))
    if shown >= len(full):
        sat = 0.3 + tdur + 0.2
        p = S.ease_out_cubic(min(1.0, (lt - sat) / 0.3)) if lt > sat else 0.0
        d.rounded_rectangle([S.W / 2 - 460, 730, S.W / 2 + 460, 850], radius=20, outline=S.GREEN, width=5)
        ok = word_image(scene.get("stamp", "HOST == RP2040  -  BYTE-IDENTICAL"), "black", 48, S.GREEN)
        paste_scaled(img, ok, S.W / 2, 790, 0.7 + 0.3 * S.ease_out_back(max(p, 0.0)), max(p, 0.0))
        if scene.get("sub") and p > 0:
            sub = word_image(scene["sub"], "body", S.T_SMALL + 2, S.DIM)
            paste_scaled(img, sub, S.W / 2, 920, 1.0, p)
    return img


def sc_hashlock(scene: dict, t: float, ctx: dict) -> Image.Image:
    """IAS15 hash-lock: H_state digests at named steps type out row by row,
    each stamped desktop == RP2040, then the 2,001/2,001 verdict lands."""
    accent = tuple(scene.get("accent", S.GREEN))
    img = base_frame(t, accent).convert("RGBA")
    lt = _local(scene, t)
    kicker(img, scene.get("kicker", ""), accent, lt)
    title = word_image(scene.get("title", "STEP BY STEP. BIT BY BIT."), "black", S.T_H1 - 8, S.INK)
    paste_scaled(img, title, S.W / 2, 205, 1.0, S.ease_out_cubic(min(1.0, lt / 0.4)))
    dig = ctx["data"]["ias15"]
    native = dig["native"]
    steps = scene.get("steps", dig["steps_shown"])
    d = ImageDraw.Draw(img)
    hdr = word_image("IAS15FH1 H_state - unmodified desktop build vs RP2040 (muse-softfloat)",
                     "body", 30, S.DIM)
    paste_scaled(img, hdr, S.W / 2, 295, 1.0, S.ease_out_cubic(min(1.0, max(0.0, lt - 0.2) / 0.4)))
    done_at = 0.0
    all_shown = True
    for i, step in enumerate(steps):
        y = 395 + i * 138
        at = 0.7 + i * 1.55
        h = native[step][0]
        lab = word_image(f"STEP {step:,}", "mono", 38, S.AMBER)
        img.alpha_composite(lab, (110, y))
        shown = int(len(h) * S.ease_out_cubic(min(1.0, max(0.0, lt - at) / 1.15)))
        txt = h[:shown] + ("_" if 0 < shown < len(h) else "")
        wi = word_image(txt, "mono", 31, accent)
        img.alpha_composite(wi, (400, y + 4))
        if shown >= len(h) and lt > at:
            m = word_image("desktop == RP2040", "bold", 26, S.GREEN)
            img.alpha_composite(m, (400, y + 58))
            done_at = max(done_at, at + 1.15)
        else:
            all_shown = False
    sat = done_at + 0.35
    if all_shown and lt > sat and done_at > 0:
        p = S.ease_out_cubic(min(1.0, (lt - sat) / 0.3))
        d.rounded_rectangle([S.W / 2 - 660, 835, S.W / 2 + 660, 950], radius=20, outline=S.GREEN, width=5)
        ok = word_image(scene.get("stamp", "2,001 / 2,001 RECORDS - BIT-IDENTICAL ON SILICON"),
                        "black", 44, S.GREEN)
        paste_scaled(img, ok, S.W / 2, 892, 0.7 + 0.3 * S.ease_out_back(p), p)
    if scene.get("sub"):
        sub = word_image(scene["sub"], "body", S.T_SMALL, S.DIM)
        paste_scaled(img, sub, 110, 988, 1.0,
                     S.ease_out_cubic(min(1.0, max(0.0, lt - 1.0) / 0.5)), anchor_x="left")
    return img


REGISTRY = {
    "kinetic": sc_kinetic,
    "counter": sc_counter,
    "barchart": sc_barchart,
    "linechart": sc_linechart,
    "ticker": sc_ticker,
    "orbit": sc_orbit,
    "stat": sc_stat,
    "hash": sc_hash,
    "hashlock": sc_hashlock,
}


def flatten(img: Image.Image) -> Image.Image:
    """Composite an RGBA scene over the stage colour.

    PIL replaces (not blends) alpha when drawing on an RGBA image, so a bare
    convert('RGB') would resurrect full-strength colours under low alpha.
    Flattening over BG is what makes trail fades / chart fills real.
    """
    if img.mode == "RGB":
        return img
    bg = Image.new("RGBA", img.size, S.BG + (255,))
    return Image.alpha_composite(bg, img).convert("RGB")


def render_scene(scene: dict, t: float, ctx: dict, total: float) -> Image.Image:
    fn = REGISTRY[scene["kind"]]
    img = fn(scene, t, ctx)
    accent = tuple(scene.get("accent", S.CYAN))
    cut_flash(img, scene, t, accent)
    footer(img, scene, t, total)
    return flatten(img)


def build_ctx() -> dict:
    caught_total = D.plant_score()
    return {"data": {
        "tool_uses_by_agent": D.tool_uses_by_agent(8),
        "output_tokens_by_agent": D.output_tokens_by_agent(8),
        "cumulative": D.cumulative_tool_uses(),
        "plants": caught_total,
        "plant_grades": [str(r.get("grade")) for r in D.load_plants()],
        "plant_groups": D.plant_groups(),
        "ias15": D.ias15_digests(),
        "git_subjects": D.git_subjects(40),
    }}
