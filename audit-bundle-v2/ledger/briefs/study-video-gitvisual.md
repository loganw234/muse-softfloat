**Role:** study-video-gitvisual (rough-draft main segment, full model)

**Task (owner):** Rough-draft the demo video's central
"git visuals" segment - the largest piece of the video.
Concept: the camera enters a flat white plane (from the
intro's period zoom). A neon line begins travelling,
branching in various colors to represent each of the
project's systems/metrics. The first handful of
examples play as a slower chase: descriptive small
popups appear as trails reach small disabled (grey)
nodes, which light up in the trail's color once reached
- e.g. a popup titled "Verifier" showing an example
sendback - introducing each system revolving around the
worktrees. Once the format and colors are established,
pull back and replay the FULL set of worktrees'
progress as it actually happened in this repo,
remerging into the main neon line exactly as the real
merges did. End: the neon trail travels into a simple
box, the lid shuts, the neon goes dark (cut to outro).
Embedded beats: twice, the main line hits a solid
"gate"; beside it a visualization plays next to a
mockup of Picos blinking; when it finishes the gate
goes green and the neon continues through. The two
visualizations are the existing studies:
KissFFT (scratch/study-kissfft-visual/) and tokens
(scratch/study-tokens-visual/) - reuse their idiom/
assets as gate content.

**Ground truth (extract, never invent):**
- Real history from `git -C muse-softfloat log --all`:
  branches (wave*/parcel branches), merges, order,
  dates. The pull-back replay must be the repo's
  actual branch/merge topology (simplification for
  legibility is allowed only if the report names every
  simplification; merge ORDER and parentage of shown
  branches must be true).
- Systems/colors from the method as recorded:
  parcels, verifiers, plants (caught/missed),
  gates (smoke/standard/board), studies, lead merges,
  escalations/sendbacks. Real examples for popups from
  ledger/RECORD (e.g. a real sendback: twiddledoc
  truncated hash; a caught plant; a board run) -
  each popup cites its source in your report.
- Pico mockup: simple board rectangles with blinking
  LEDs (green, WS2812; one GP25 board) - the six-board
  story; blink while "working" per actual runs.

**Handoff contract:** 1920x1080 30 fps, video/ idiom
(style.py/scenes.py/timeline.py/STORYBOARD read first).
Starts on the intro's full-frame flat white plane
(exact spec in the intro study if it has landed;
otherwise define it and state it). Ends: box lid shut,
neon dark, near-black final frames. Programmatic only.
Rough draft: this is for lead assembly + owner
iteration - structure, timing, data plumbing, readable
popups; final polish later.

**Fences:** scratch only (`scratch/study-video-gitvisual/`),
repo untouched, nothing committed; never open/search/
list anything with `cft` in its name; git reads are
fine (log/show); no board use; memory ceilings; the
full history is ~150 commits - data extraction is
small, keep renders bounded.

**Deliverables:** extracted history dataset (JSON:
branches/merges/timestamps + node events with sources),
render script(s), the segment as one mp4 (probe-
verified) + stills at the beats (chase popup, pull-back
full graph, each gate, box ending), a timing/beat sheet
mapping seconds->events, `scratch/study-video-gitvisual/
report.md` (first line READY/NOT READY as rough draft;
color/system legend; every simplification named; popup
sources; what assembly/polish still needs; effort
estimate to final), `ledger/study-video-gitvisual.md`.
Structured complete/evidence/unresolved. Script files,
Git Bash, MSF_PYTHON pinned.
