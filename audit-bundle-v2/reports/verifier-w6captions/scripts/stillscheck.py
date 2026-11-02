"""Independent stills_v6 recompute (verifier-owned; does not use build_stills)."""
import re
import subprocess
import sys
from pathlib import Path

BASE = Path("C:/Users/logan/source/repos/Muse-Softfloat")
COPY = BASE / "worktrees/verify6-captions"
SEG = COPY / "video/segments"
OUT = COPY / "video/out"
STILLS = OUT / "stills_v6"
sys.path.insert(0, str(SEG))
sys.path.insert(0, str(COPY / "video"))
import idea, why, intro_outro, gitvisual  # noqa: audit sources only

K = 120.0 / 124.0  # assemble.py tempo (setpts PTS*120/124)
OFF = {"intro": 0.0, "idea": 7.0, "why": 33.0, "gitvisual": 65.0, "outro": 173.0}
# offsets re-derived from assemble durations
DURS = {"intro3.mp4": 7.0, "idea2-1440p.mp4": 26.0, "why3-1440p.mp4": 32.0,
        "gitvisual7.mp4": 108.0, "outro3.mp4": 12.0}
ORDER = ["intro3.mp4", "idea2-1440p.mp4", "why3-1440p.mp4", "gitvisual7.mp4", "outro3.mp4"]
t = 0.0
for m in ORDER:
    seg = {"intro3.mp4": "intro", "idea2-1440p.mp4": "idea", "why3-1440p.mp4": "why",
           "gitvisual7.mp4": "gitvisual", "outro3.mp4": "outro"}[m]
    assert abs(OFF[seg] - t) < 1e-9, (seg, OFF[seg], t)
    t += DURS[m]
assert abs(t - 185.0) < 1e-9
print("offsets re-derived OK:", OFF, "native total 185.0 -> scaled", round(185.0 * K, 2))


def scene_beat(blocks, scene):
    rows = [(float(a), float(b)) for (s, a, b, _ls) in blocks if s == scene]
    assert rows, scene
    return (rows[-1][0] + rows[-1][1]) / 2.0


print("idea scenes:", sorted({s for s, _, _, _ in idea.BLOCKS}))
print("why scenes:", sorted({s for s, _, _, _ in why.BLOCKS}))

stills = []  # (slug, native, segment, local, shows)


def add(slug, seg, local, shows):
    stills.append((slug, OFF[seg] + local, seg, local, shows))


a, b = float(intro_outro.BLOCKS_INTRO[0][1]), float(intro_outro.BLOCKS_INTRO[0][2])
add("intro-msg", "intro", (a + b) / 2.0, "intro phone msg")
for sc in ["idea", "correct", "prove", "method", "question"]:
    add(f"idea-{sc}", "idea", scene_beat(idea.BLOCKS, sc), "idea")
for sc in ["spec", "opt1", "opt2", "opt3", "settle"]:
    add(f"why-{sc}", "why", scene_beat(why.BLOCKS, sc), "why")
g = gitvisual
add("git-chase-start", "gitvisual", 2.0, "chase start")
for i, (title, _ln) in enumerate(g.POPUP5):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    add(f"git-popup-{slug}", "gitvisual",
        float(g.ARRIVALS[i]) + float(g.POPUP_DWELL[i]) / 2.0, title)
add("git-bridge", "gitvisual", (float(g.T_BRIDGE) + float(g.T_REPLAY)) / 2.0, "bridge")
add("git-replay-early", "gitvisual", (float(g.T_REPLAY) + float(g.GATES[0]["t0"])) / 2.0, "replay early")
for gate in g.GATES:
    add(f"git-gate-{gate['id']}", "gitvisual", float(gate["t0"]) + 6.0, gate["title"])
add("git-replay-late", "gitvisual", (float(g.GATES[1]["t1"]) + float(g.GATES[2]["t0"])) / 2.0, "replay late")
add("git-opening-fall", "gitvisual", float(g.T_BOX) + 3.5, "opening fall")
add("git-opening-plate", "gitvisual", float(g.T_BOX) + 8.0, "opening plate")
bo = intro_outro.BLOCKS_OUTRO
add("outro-replies", "outro", (float(bo[1][1]) + float(bo[2][1])) / 2.0, "replies")
add("outro-human-ai", "outro", (float(bo[4][1]) + float(bo[5][1])) / 2.0, "human-ai")
add("outro-stats", "outro", (float(bo[7][1]) + float(bo[7][2])) / 2.0, "stats")
stills.sort(key=lambda s: s[1])
assert len(stills) == 30, len(stills)

rows = [ln for ln in (STILLS / "INDEX.md").read_text(encoding="utf-8").splitlines()
        if ln.startswith("| ") and not ln.startswith("| #")]
assert len(rows) == 30, len(rows)
errs = []
for i, (slug, native, seg, local, _sh) in enumerate(stills, start=1):
    exp_file = f"{i:02d}_t{native * K:06.2f}_{slug}.png"
    m = [c.strip() for c in rows[i - 1].split("|")]
    # m: ['', #, Still, Scaled, Native, Segment, Shows, '']
    got_file = m[2].strip("`")
    got_scaled, got_native, got_seg = float(m[3]), float(m[4]), m[5]
    if got_file != exp_file:
        errs.append(f"row {i}: filename {got_file} != recomputed {exp_file}")
    if abs(got_scaled - native * K) > 0.005 + 1e-9:
        errs.append(f"row {i}: scaled col {got_scaled} != recomputed {native * K:.4f} (native {native:.2f})")
    if abs(got_native - native) > 0.005 + 1e-9:
        errs.append(f"row {i}: native col {got_native} != recomputed {native:.4f}")
    if got_seg != f"{seg} ({local:.2f})":
        errs.append(f"row {i}: segment col {got_seg!r} != recomputed {seg} ({local:.2f})")
    mt = re.match(r"\d+_t(\d+\.\d+)_", got_file)
    if mt and abs(float(mt.group(1)) - got_scaled) > 0.005 + 1e-9:
        errs.append(f"row {i}: filename t={mt.group(1)} != row scaled {got_scaled}")
    print(f"{i:02d} {exp_file} scaled={native*K:.2f} native={native:.2f} {seg}({local:.2f}) "
          f"{'OK' if got_file == exp_file and not [e for e in errs if e.startswith(f'row {i}:')] else 'DIFF -> ' + got_file}")
if errs:
    print(f"RECOMPUTE FAIL ({len(errs)}):")
    for e in errs:
        print("  " + e)
else:
    print("RECOMPUTE PASS: 30/30 rows match (filename, scaled, native, segment-local)")
