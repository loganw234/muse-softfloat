"""Independently recompute every stills_v6 INDEX row from segment audit data.

Does NOT import captions.build_stills: re-derives each beat time from
the raw audit tables with locally written formulas, then compares
against INDEX.md (filenames + scaled/native/local columns).
"""
import re
import sys
from pathlib import Path

WS = Path(__file__).resolve().parent.parent.parent
WT = WS / "worktrees" / "w6-captions"
sys.path.insert(0, str(WT / "video" / "segments"))
sys.path.insert(0, str(WT / "video"))
import assemble  # noqa: E402
import gitvisual as G  # noqa: E402
import idea  # noqa: E402
import intro_outro as IO  # noqa: E402
import why  # noqa: E402

SCALE = 120.0 / 124.0
OFF = {}
t = 0.0
for name in assemble.ORDER:
    OFF[name] = t
    t += {m: d for _s, m, d in assemble.SEGMENTS}[name]
OI, OD, OW, OG, OO = (OFF["intro3.mp4"], OFF["idea2-1440p.mp4"],
                      OFF["why3-1440p.mp4"], OFF["gitvisual7.mp4"],
                      OFF["outro3.mp4"])


def beat(blocks, scene):
    rows = [(float(a), float(b)) for (s, a, b, _l) in blocks if s == scene]
    assert rows, scene
    return (rows[-1][0] + rows[-1][1]) / 2.0


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


expect = []  # (slug, scaled, native, segment, local)
a, b = IO.BLOCKS_INTRO[0][1], IO.BLOCKS_INTRO[0][2]
expect.append(("intro-msg", (OI + (a + b) / 2) * SCALE, OI + (a + b) / 2,
               "intro", (a + b) / 2))
for scene in ["idea", "correct", "prove", "method", "question"]:
    loc = beat(idea.BLOCKS, scene)
    expect.append((f"idea-{scene}", (OD + loc) * SCALE, OD + loc, "idea", loc))
for scene in ["spec", "opt1", "opt2", "opt3", "settle"]:
    loc = beat(why.BLOCKS, scene)
    expect.append((f"why-{scene}", (OW + loc) * SCALE, OW + loc, "why", loc))
expect.append(("git-chase-start", (OG + 2.0) * SCALE, OG + 2.0, "gitvisual", 2.0))
for i, (title, _l) in enumerate(G.POPUP5):
    loc = float(G.ARRIVALS[i]) + float(G.POPUP_DWELL[i]) / 2.0
    expect.append((f"git-popup-{slug(title)}", (OG + loc) * SCALE, OG + loc,
                   "gitvisual", loc))
expect.append(("git-bridge", (OG + (float(G.T_BRIDGE) + float(G.T_REPLAY)) / 2) * SCALE,
               OG + (float(G.T_BRIDGE) + float(G.T_REPLAY)) / 2, "gitvisual",
               (float(G.T_BRIDGE) + float(G.T_REPLAY)) / 2))
expect.append(("git-replay-early",
               (OG + (float(G.T_REPLAY) + float(G.GATES[0]["t0"])) / 2) * SCALE,
               OG + (float(G.T_REPLAY) + float(G.GATES[0]["t0"])) / 2, "gitvisual",
               (float(G.T_REPLAY) + float(G.GATES[0]["t0"])) / 2))
for gate in G.GATES:
    loc = float(gate["t0"]) + 6.0
    expect.append((f"git-gate-{gate['id']}", (OG + loc) * SCALE, OG + loc,
                   "gitvisual", loc))
expect.append(("git-replay-late",
               (OG + (float(G.GATES[1]["t1"]) + float(G.GATES[2]["t0"])) / 2) * SCALE,
               OG + (float(G.GATES[1]["t1"]) + float(G.GATES[2]["t0"])) / 2,
               "gitvisual",
               (float(G.GATES[1]["t1"]) + float(G.GATES[2]["t0"])) / 2))
expect.append(("git-opening-fall", (OG + float(G.T_BOX) + 3.5) * SCALE,
               OG + float(G.T_BOX) + 3.5, "gitvisual", float(G.T_BOX) + 3.5))
expect.append(("git-opening-plate", (OG + float(G.T_BOX) + 8.0) * SCALE,
               OG + float(G.T_BOX) + 8.0, "gitvisual", float(G.T_BOX) + 8.0))
bo = IO.BLOCKS_OUTRO
loc = (float(bo[1][1]) + float(bo[2][1])) / 2.0
expect.append(("outro-replies", (OO + loc) * SCALE, OO + loc, "outro", loc))
loc = (float(bo[4][1]) + float(bo[5][1])) / 2.0
expect.append(("outro-human-ai", (OO + loc) * SCALE, OO + loc, "outro", loc))
loc = (float(bo[7][1]) + float(bo[7][2])) / 2.0
expect.append(("outro-stats", (OO + loc) * SCALE, OO + loc, "outro", loc))
expect.sort(key=lambda e: e[2])

rows = (WT / "video" / "out" / "stills_v6" / "INDEX.md").read_text(
    encoding="utf-8").splitlines()
pat = re.compile(r"^\| (\d+) \| `(\d+_t([\d.]+)_(.+)\.png)` \| ([\d.]+) "
                 r"\| ([\d.]+) \| (\S+) \(([\d.]+)\) \|")
got = [m.groups() for r in rows if (m := pat.match(r))]
assert len(got) == 30, f"INDEX rows: {len(got)}"
assert len(expect) == 30, f"expected rows: {len(expect)}"
fails = 0
for i, (sl, sc, na, sg, lo) in enumerate(expect, start=1):
    n, fn, fsc, fsl, isc, ina, isg, ilo = got[i - 1]
    ok = (int(n) == i and f"{i:02d}_t{sc:06.2f}_{sl}.png" == fn
          and abs(float(isc) - sc) < 0.005 and abs(float(ina) - na) < 0.005
          and isg == sg and abs(float(ilo) - lo) < 0.005)
    if not ok:
        fails += 1
        print(f"MISMATCH {i}: expect {i:02d}_t{sc:06.2f}_{sl} "
              f"native={na:.2f} {sg}({lo:.2f}) got {fn} {isc}/{ina} {isg}({ilo})")
print(f"index check: {30 - fails}/30 rows recomputed exactly"
      + (" -- ALL MATCH" if not fails else " -- FAILURES"))
sys.exit(1 if fails else 0)
