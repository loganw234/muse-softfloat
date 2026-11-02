# study-video-gitvisual: READY (rough draft)

Brief: `ledger/briefs/study-video-gitvisual.md`. Work in
`scratch/study-video-gitvisual/` (repo untouched, nothing committed;
`git -C muse-softfloat status` clean after the run).

Delivered:
- `gitvisual.mp4` - the segment, 78.0 s, 1920x1080, 30 fps, H.264,
  silent, 2,340/2,340 frames decoded clean (video/probe.py, rc 0).
- Handoffs measured on the MP4: t=0.5 all px (255,255,255) = intro's
  white frame; t=77.5 all px (2,3,8) = outro's near-black, box lid
  shut, neon dark.
- `history.json` - real topology from `git log --all` at a73e97d
  (141 commits, 27 merges, 25 into main; counts cross-checked).
- `extract_history.py`, `render_gitvisual.py` - re-runnable
  (MSF_PYTHON = workspace .venv).
- `stills/` - 15 probe grabs at the beats, inspected.
- `beats.md` - timing/beat sheet; `report.md` - legend, popup
  sources, every simplification (S1-S8), polish list, effort.

Structure: 1.0 s white -> slow chase with 7 sourced popups (incl.
the twiddledoc truncated-hash sendback) -> pull-back -> true
branch/merge replay interrupted twice by study gates beside six
blinking Pico mockups (Gate 1 KissFFT idiom at its real merge
32bbd93; Gate 2 tokens idiom anchored editorially at metrics merge
a1a888f - named as such) -> box, lid shut, neon dark.

Verdict standard: rough draft for lead assembly + owner iteration,
per the brief. Owner calls open: Gate 2 anchor, white->dark dim at
the pull-back, popup copy.

---

# study-video-gitvisual-polish: READY (v2)

Brief: `ledger/briefs/study-video-gitvisual-polish.md`. v1 preserved
untouched; v2 beside it in `scratch/study-video-gitvisual/`
(repo untouched, nothing committed, `git -C muse-softfloat status`
clean after the run).

Delivered:
- `gitvisual2.mp4` - 83.0 s (+5.0 vs v1), 1920x1080, 30 fps, H.264,
  silent, 2,490/2,490 frames decoded clean (video/probe.py, rc 0).
  Handoffs measured: t=0.5 all px (255,255,255); t=82.5 dominant
  (2,3,8) = outro2 first frame (28 px within 2 levels, encoder noise).
- Owner moves: flat 2D white open -> continuous lift into a custom
  numpy/PIL perspective 3D chase (camera chases/banks/closes on
  nodes, smootherstep throughout, measured zero-velocity joins in
  camera_measurements.json) -> 4 s pull-back with a continuous
  90-degree turn so the full real tree fills the frame and time
  grows DOWN-TO-UP for the replay -> 120 BPM beat-pulsed glow,
  node/merge pops, gate PASS impacts; popup holds kept at 2.3 s.
- Carry-overs: same real history.json/topology + sourced popups;
  both gates with six Pico mockups, PASS now holds all six LEDs
  solid 1.5 s; Gate 2 regenerated (regen_gate2.py): billed
  1,196,128,770 = input 1,190,490,305 + output 5,638,465, 93 labeled
  rows @ a73e97d, definition on frame (v1's 1,514,499,184 retired;
  note the brief's parenthetical mislabels the sum as input-only).
- `render_gitvisual2.py`, `measure_camera.py`, `verify_handoff2.py`,
  `stills2/` (18 eyeballed MP4 grabs), `beats2.md`,
  `polish-report.md` (READY; camera design + measurements, 3D
  route/limits, simplifications S1-S12, assembly trims if the
  +5 s must come back).

---

# study-video-gitvisual-v3: READY (full marble-track model, 1440p)

Brief: `ledger/briefs/study-video-gitvisual-v3.md`. v1/v2 preserved
untouched; v3 beside them in `scratch/study-video-gitvisual/`
(repo untouched, nothing committed, `git -C muse-softfloat status`
clean after the run).

Delivered:
- `gitvisual3.mp4` - 88.0 s (+5.0 vs v2: +8 IAS15 window, -4
  pull-back/turn deleted, +1 bridge/box), **2560x1440**, 30 fps,
  H.264, silent, 2,640/2,640 frames decoded clean (video/probe.py,
  rc 0), 28,205,015 bytes; `gitvisual3-1080.mp4` downscale twin
  (make_twin3.py, probe-clean). Film now ~115 s of the 180 s
  budget incl. the 16 s why-segment - no overrun; trims listed in
  polish3-report.md. Handoffs (verify_handoff3.py): t=0.5 all
  3,686,400 px (255,255,255); t=87.5 dominant (2,3,8) = outro2
  (1,024 px within 2 levels).
- Owner moves: NO full-tree reveal - closer angled camera rides
  the cursor in ONE continuous space (chase trail -> real track
  -> box), bed climbs so marbles travel UP-screen, only ranks
  [cursor-18, cursor+48] drawn; marble-track model (head +
  trailing spine marbles, lane marbles split at true merge-bases
  and rejoin at true merges); five sourced correction loop-backs
  with stamps (4cdb912, tininess re-gate 9bb8723/80cbc97, 83622cf,
  048aa29, twiddledoc a41f026); gates as WINDOWS rising from the
  track plane and closing into green checks - IAS15 NEW at its
  true beat (d9718cf rank 44: figure-8 illustration + real
  IAS15FH1 hash rows 0/944/2000 + 2,001/2,001 stamp), KissFFT
  (32bbd93), tokens (a1a888f, regenerated numbers, definition on
  frame), six Pico mockups in every window, PASS solid 1.5 s;
  1440p fully parametric (max crop-upscale 1.0, streamed).
- `render_gitvisual3.py`, `measure_camera3.py` +
  `camera_measurements3.json` (joins 0.0-0.35 vs peaks
  1,509/17.4; caught+fixed a half-rank gate-exit jump),
  `verify_handoff3.py`, `render_checks3.py`, `make_twin3.py`,
  `stills3/` (25 eyeballed MP4 grabs), `beats3.md`,
  `polish3-report.md` (READY; marble model as built, measured
  camera, simplifications S1-S18 with S11 retired, assembly flag:
  segment is 1440p vs video/ 1080p).

## v4 - marble sync + packaging (2026-10-29, study-video-gitvisual-v4)

- `gitvisual4.mp4`: 88.0 s (+0.0 vs v3), 2560x1440, 30 fps,
  2,640/2,640 frames probe-clean, 28,236,272 bytes; twin
  `gitvisual4-1080.mp4` probe-clean. `polish4-report.md` READY.
  Handoffs identical to v1-v3 (`verify_handoff4.py`): t=0.5 all
  px (255,255,255); t=87.5 dominant (2,3,8), 1,024 px within 2.
- Marble sync: every marble is a pure function of the clock that
  lights its event (`head_x` chase / `cursor_rank` replay).
  Removed v3 sources: 26-unit ride-height (~16.5 px hover),
  time-based gate bob, half-rank gate hold gap (cursor now waits
  ON each gate rank), 6-vs-4-rank sendback stamp window (stamp
  now lands at the computed loop-apex rank), chase wall-time
  lighting (now gated on `head_x`). Found+fixed a v1-v3 bug:
  Wave-1 lanes 2843792/06fdec8 had backwards lane polylines
  (exclusive time-ranks precede merge-base rank) - marbles
  teleported a full lane (~101 px) one frame after splitting.
  `measure_sync4.py` -> `sync_measurements4.json`: at-event
  marble-centroid vs node-center 0.0 px on all rows (7 chase
  lightings, 25 splits, 25 absorbs, 17 sampled exclusive nodes,
  15 sendback entry/apex/exit, 3 gate arrivals; v3 max 35.0 px);
  nearest-30fps-frame residual <=25.7 px = pure frame
  quantization; BPM-pulse centroid drift 0.0 px (v3 1.76).
- Packaging: all seven legend system marbles file into the box
  (parcels..escalations, lead/main last), each labelled, arcing
  over the rim before the lid shuts (lid waits for 7/7); box
  front stamps retained artefacts RECORD / LEDGERS / VECTORS /
  METRICS as they land (S19). Bought inside the 79-88 s box
  window - no duration change, nothing else trimmed.
- `render_gitvisual4.py`, `measure_sync4.py`,
  `verify_handoff4.py`, `render_checks4.py`, `make_twin4.py`,
  `stills4/` (29 eyeballed MP4 grabs), `beats4.md`,
  `polish4-report.md`. v1-v3 preserved; scratch only; nothing
  committed.

## v5 - text/pacing revision (2026-10-29, study-video-textpacing Agent B)

- `gitvisual5.mp4`: 102.0 s (+14.0 vs v4's 88.0), 2560x1440,
  30 fps, 3,060/3,060 frames probe-clean, 30,201,691 bytes.
  `polish5-report.md` READY (copy table + dwell audit +
  full sourcing). Film ~159.5 s vs the 160 s ceiling
  (assembly v4 145.5 s, other segments 57.5 s). Handoffs
  (`verify_handoff5.py`): t=0.5 all px (255,255,255);
  t=101.5 dominant (2,3,8), 492 px within 2 levels.
- THE RULE applied (dwell = smallest 0.5 s-grid multiple >=
  max(1.5, 0.5 + words/2.5), computed from the copy in
  `render_gitvisual5.py`): popups are title + <=2 short
  plain lines with rule dwells 3.5-5.0 s (was flat 2.3 s;
  marbles wait on their nodes); window captions trimmed,
  staggered (<=2 new lines/beat), late stamps moved earlier
  so every popup/window block meets the rule exactly
  (`audit_text5.py`, 63 blocks). On-screen words 633 -> 335
  (-47%). Per-claim src stamps collapsed to one short tag
  per scene (chase / replay / each window title bar); full
  sourcing in `polish5-report.md`. Named deviations: four
  cursor-paced sendback labels (ranks 7/12/99/114, 6 words,
  measured 1.02-1.78 s vs 3.0 s min - dwell set by the
  unchanged leg speeds; 3-6x v4's dwell at 1/4 the words)
  and the worst branch-name label (1.11 vs 1.5 s); HUD
  commit ticker is a data readout, unchanged.
- Sync re-measured (`measure_sync5.py` ->
  `sync_measurements5.json`): at-event marble-vs-node
  0.0 px on every row (7 lightings, 25 splits, 25 absorbs,
  17 exclusive, 15 sendback, 3 gates), pulse drift 0.0 px;
  event identity vs v4 asserted (NODE_X, gate ranks
  44/69/134 + 8.0 s windows, leg spans/durations, sendback
  ranks) - popup dwell growth moved wall times only.
- `render_gitvisual5.py`, `audit_text5.py` +
  `audit_text5.json`, `measure_sync5.py`,
  `verify_handoff5.py`, `render_checks5.py`, `stills5/`
  (31 eyeballed MP4 grabs + checks), `beats5.md`,
  `polish5-report.md`. No 1080p twin this round. v1-v4
  preserved; scratch only; nothing committed.
