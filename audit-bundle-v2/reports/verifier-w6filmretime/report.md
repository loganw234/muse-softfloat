# verifier-w6filmretime — report

Copy: `worktrees/verify6-filmretime`, HEAD `a1e83d9`, parent `101b4aa`.
Duplicate for renders/gates: `tmp/v6dup` (copy untouched; `git status` clean).
Tooling: workspace `.venv` python, its `imageio_ffmpeg` binary. Fences kept:
no `docs/metrics/plants.jsonl`, no parcel branch/worktree, no `scratch/lead`,
no `scratch/parcel-w6filmretime`, no `ledger/lead.md`, no GitHub, nothing `cft`.

Verdict: **NOT READY** — 3 blockers (1, 2, 3), 2 notes (4, 5).

## Probe 1 — durations and the cap (BLOCKER 1)

Probed every segment MP4 header with our own ffmpeg calls
(`scratch/verifier-w6filmretime/probe1_durations.py`):

| segment | duration | res | fps | audio | size |
|---|---|---|---|---|---|
| intro3.mp4 | 7.00 s | 2560x1440 | 30 | none | 752800 |
| idea2-1440p.mp4 | 26.00 s | 2560x1440 | 30 | none | 899508 |
| why3-1440p.mp4 | 32.00 s | 2560x1440 | 30 | none | 1354807 |
| gitvisual7.mp4 | 108.00 s | 2560x1440 | 30 | none | 50568834 |
| outro3.mp4 | 12.00 s | 2560x1440 | 30 | none | 829917 |

Native sum of probed reality = **185.0 s** (matches ledger 7/26/32/108/12).
But `video/assemble.py` as written:

- `SEGMENTS` lists why as **29.0** (stale; `why.py` DUR = 32.0, MP4 = 32.00 s).
  SEGMENTS native sum = 182.0, not 185.0.
- `tempo = 120.0 / 120.0` (= 1.0, no scaling) while the docstring, the
  comment ("native 120 BPM grid -> 124 BPM music sync"), and the
  ledger/briefs row all claim 120/124 → ~179.0 s and cuts on 124 BPM beats.
  Parent `101b4aa` had `tempo = 120.0 / 124.0`; wave6 regressed it to 1.0.
- Assembled in the duplicate (`tmp/v6dup/video/out/assembly_v6.mp4`):
  probed product = **185.00 s (3:05) — over the 180 s cap**.
  Cuts land on the unscaled 120 BPM grid, not 124 BPM.
- Consequence: the script's own join checks sample the wrong times
  (6.7/31.8/59.9/164.4 s, i.e. 120/124-scaled bounds) instead of the true
  cuts (7/33/65/173 s) — they pixel-check mid-segment frames, not joins.
  (Observed outputs were still white/white/dark as happens; the check is
  vacuous at those positions.)
- The tempo-line edit also exceeds the parcel's "assemble.py SEGMENTS only"
  scope.

So "the film now fits the 3-minute cap" is not re-derivable from the copy:
as coded it is 185 s. Fix = restore 120/124 tempo and correct the why
SEGMENTS row to 32.0 (then 185 × 120/124 = 179.03 s).

## Probe 2 — the duplicate question (PASS with note)

- `WHY NOT USE WHAT / ALREADY SHIPS?` occurs only in `idea.py` (Q_H1/Q_H2,
  question scene 21.5–26 s). `why.py` has no title copy: no `scene_title`,
  `T_H`, `T_SUB`, or title BLOCKS rows (grep over both files).
- Stills from the copy's MP4s: `p2_why_t10.png` shows why at t=1.0 opening
  on the spec header (`TOGETHER: A JOB SPEC`); `p2_why_t02.png` mean is pure
  white (white lead); `p2_idea_t220.png` shows the question mid-pose;
  `p2_idea_t255.png` mean is pure white (fade-out).
- Note (pre-existing, not this parcel): `why.py` still defines the dead
  `scene_workloads` function and `HD_WORK`/`WORK` constants (deleted scene
  from an earlier trim); `frame()` never calls it. No dead *title*-scene
  copy remains.

## Probe 3 — dwell audit (BLOCKER 2, rest passes)

Imported the copy's modules and recomputed RULE
(dwell = smallest 0.5 s multiple ≥ max(1.5, 0.5 + words/2.5)) from the
computed BLOCKS values (`probe3_dwells.py`):

- why: 33/33 rows pass. intro BLOCKS_INTRO: 1/1. outro BLOCKS_OUTRO: 8/8.
- **idea question rows FAIL as computed**: remap sets `_BGONE["question"]
  = T_Q = 21.5`, i.e. the scene *start*, giving dwells **0.0** (6 words,
  RULE 3.0) and **−0.5** (2 words, RULE 1.5) — zero and negative,
  contradicting the parcel's "zero violations". The renders themselves are
  fine (question scene runs 21.5 → FADE_T 25.0, true dwells 3.5/3.0, both ≥
  RULE); the audit source of truth is degenerate for these two rows
  (gone should be the fade/end, as it is for why's settle scene).
- No multi-gone scenes; scene spans sequential, no overlaps
  (idea [0.5–5–11–17–21.5–26], why [0.5–7–13.5–20.5–25.5–31/32]).
- Added time is dwell only: typing windows (intro type 1.0–1.5, outro
  reply2 3.0–4.0), dive 4.5–6.5, pull-back `(t−0.5)/2.0`, marble legs 8/5/7 s
  all byte-identical to parent per diff; popup dwell = RULE + 0.5 × 7
  (`POPUP_DWELL [4.0, 5.0, 4.5, 4.5, 5.5, 5.0, 5.0]`, recomputed RULE
  matches); TOTAL derivation 46.0 → 48.5 → SHIFT 17.5 → T_BOX 96.5 →
  T_FADE 106.0 → TOTAL 108.0 verified by import.

## Probe 4 — supersampling (NOTE 4, artifacts verified SS=2)

- Code defaults with no env override: `SS = int(os.environ.get("MSF_SS",
  "1"))` → **SS=1, internal canvas 2560x1440** (verified by import).
- `measurements3.json` records ss=2, internal [5120, 2880] — **not
  consistent with a default-code reproduction**; re-running
  `intro_outro.py` at defaults would regenerate SS=1 artifacts and
  overwrite measurements3.json with ss:1 values. (Also `scale_K` 1.3333 is
  the base K, not the in-effect SS=2 K 2.6667 — recorded after the canvas
  context exited.)
- The shipped pixels ARE SS=2: mid-dive frame re-rendered at SS=1 vs SS=2
  in the duplicate path and compared to shipped `intro3.mp4` t=5.4
  (`probe24_stills_ss.py`): SS=2 MSE 3.4 (match), SS=1 MSE 407.0, edge
  energy shipped 1.21 vs SS=2 0.5 vs SS=1 0.23 on the same crop.
- proof error_abs 0.2 ✓, clamps 0.0 / 0.25 ✓ as ledger claims.
- Joins in source terms: intro last frame mean (255,255,255) ✓; outro frame
  0 mean (2,3,8), corner (2,3,8) ≈ near-black (3,4,9) within yuv420p
  rounding ✓.
- Bottom line: "SS=2 chosen" is true of the artifacts (needs `MSF_SS=2` in
  the environment); the choice is not encoded in the code defaults, so the
  tree does not reproduce its own measurements/MP4s as written.

## Probe 5 — gitvisual sync (BLOCKER 3, rest passes)

Imported the copy's `gitvisual.py` against its own `history.json`
(`probe5_gitvisual.py`):

- IAS_RANK 44 = merge d9718cf rank 44 ✓; G1 69 = gate1 anchor 32bbd93 ✓;
  LAST_RANK 140 = commit_count_all − 1 ✓.
- **kissfft gate rank = 70.0 = G1_RANK + 1.0, not the merge rank 69.**
  Parent had `float(G1_RANK)`; wave6 added `+ 1.0`. This contradicts the
  parcel brief ("gate ranks [44,69,140]") and the probe requirement (gate
  ranks equal the merge ranks). Gate line and head marble sit one rank off
  the merge node for the whole 70.5–79.5 s window.
- **cursor_rank is not monotonic**: drops 70.0 → 69.0 at t=79.5 (0.05 s
  sample; the single decrease over TOTAL). There is also a +1.0 jump at
  gate open (69.0 → 70.0 at t=70.5; increasing, but discontinuous).
- Otherwise verified: windows 9.0/9.0/8.5 s ✓, legs (8.0, 5.0, 7.0 s) ✓,
  TOTAL 108.0 ✓, cursor exactly on each gate's own rank at its t0 and
  through its window ✓.

## Probe 6 — gate and scope (PASS except scope note folded into Blocker 1)

- `tools/run.sh standard` in the duplicate (`tmp/v6dup`): **PASS in 50 s**
  (f16-exhaustive 917504 + pack-sweep 200000 vectors exact; aug pool
  5505024 mismatches 0).
- Diff `101b4aa..a1e83d9` file scope: `video/assemble.py`,
  `video/segments/{idea,why,intro_outro,gitvisual}.py`,
  `docs/metrics/briefs.jsonl` (+1 own row), regenerated MP4s/stills/
  measurements — `render_why.py` owned but unchanged as claimed. No other
  files. Exception: the `assemble.py` tempo-line edit falls outside
  "SEGMENTS only" (see Blocker 1).
- Briefs-row numbers vs probed reality: native 185.0 ✓ (7/26/32/108/12
  probed), scaled 179.0 ✗ as coded (product is 185.0), SS=2 ✓ of artifacts
  (not of defaults), proof 0.2 px ✓, join solids ✓, PASS ✓.
- Claim discipline ✓: row states timings as records, no performance
  claims; all five MP4s have video-only streams (silent) ✓.

## Findings (numbered)

1. (blocker) Assembly as coded does not meet the cap: `tempo` 1.0
   (regression from 120/124), stale why SEGMENTS 29.0, product 185.0 s;
   join checks sample wrong times; tempo edit out of scope.
2. (blocker) `idea.py` BLOCKS question rows degenerate (dwells 0.0, −0.5)
   vs "zero violations"; renders unaffected (true dwells 3.5/3.0).
3. (blocker) kissfft gate rank 70 ≠ merge rank 69 (added `+ 1.0`);
   cursor_rank non-monotonic (70→69 at t=79.5).
4. (note) SS=2 true of artifacts, not of code defaults
   (`MSF_SS` default "1"); measurements3.json unreproducible at defaults;
   `scale_K` records base K.
5. (note) Dead `scene_workloads`/workload constants remain in `why.py`
   (pre-existing; title copy fully gone).
