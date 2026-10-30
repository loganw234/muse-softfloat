**Role:** study-video-gitvisual-polish (git segment polish, full model)

**Input:** v1 in `scratch/study-video-gitvisual/`
(gitvisual.mp4 78s, history.json, beats.md, report.md,
stills). Owner verdict: theme correct, needs to be
more visually engaging and active - energy comparable
to Meta/Apple ads. Produce `gitvisual2.mp4` beside v1
(never overwrite v1).

**Owner direction (all required):**
1. **2D -> 3D transition:** open in the established
   flat 2D white-plane world, then transition into a
   3D space (depth, parallax, lines lifting off the
   plane). Choose the lightest honest route and
   justify it (custom software 3D projection in
   numpy/PIL is fine; anything heavier must already
   exist in scratch/.venv - no network installs).
2. **Chase camera:** through the informational
   (popup) sections the camera actively CHASES the
   travelling neon line - following, banking,
   closing on nodes as popups fire; motion is eased
   and continuous (no velocity steps; measure your
   camera curves like the intro polish did).
3. **Pull-back + axis switch:** after the chase, the
   camera pulls back until the whole tree takes up
   the screen, and progression switches from
   left-to-right to **down-to-up** for the full-history
   replay (the tree grows upward as merges land).
   The axis switch itself should read as a deliberate
   camera move, not a cut.
4. **Energy:** quicker pulse on the 120 BPM grid,
   glow/bloom on neon, node-lighting pops, gate
   impacts. Advertisement energy, still clean and
   legible - popups must remain readable (hold times
   respected; speed lives in the camera and light,
   not in shrinking text dwell below readability).

**Carry over from v1 (do not regress):**
- Real history only (history.json; true merge order/
  parentage; simplifications S1-S8 named again, any
  new ones added). Popup sources cited.
- Both gates with Pico mockups; gate PASS now holds
  the LEDs solid briefly (v1 named this its polish
  debt).
- Gate 2 numbers REGENERATED from refreshed metrics
  (`docs/metrics/usage.jsonl` at a73e97d = 93 labeled
  rows summing 1,196,128,770 input, or state your
  definition on-frame) - v1's 1,514,499,184 is
  known-stale (double-counted 38.6M); do not reuse it.
- Handoff frames DO NOT MOVE: opens full-frame pure
  white (255,255,255), ends box-lid-shut near-black
  matching outro2's open. Duration may flex a few
  seconds; report the delta (assembly budget: the
  film targets 180s total, currently 89s spoken for).

**Fences:** scratch only (`scratch/study-video-gitvisual/`),
repo untouched, nothing committed, v1 preserved;
never open/search/list anything with `cft` in its
name; bounded renders, memory ceilings; eyeball your
own stills at every beat before claiming them.

**Outputs:** gitvisual2.mp4 (probe-verified
1920x1080/30fps), stills2/ at the beats (2D open,
3D transition, mid-chase popup, axis-switch moment,
full-tree up-growth, each gate, box end), updated
beats sheet, `scratch/study-video-gitvisual/
polish-report.md` (first line READY/NOT READY; camera
design + measured smoothness; 3D route + its limits;
simplifications; assembly needs), append
`ledger/study-video-gitvisual.md`. Structured
complete/evidence/unresolved. Script files, Git Bash,
MSF_PYTHON pinned.
