**Role:** study-video-gitvisual-v3 (git segment rework, full model)

**Input:** v2 in `scratch/study-video-gitvisual/`
(gitvisual2.mp4, polish-report.md, beats2.md,
render_gitvisual2.py, history.json). Owner verdict:
theme correct, but rework the staging as below.
Produce `gitvisual3.mp4`; v1/v2 preserved.

**Owner direction (all required):**
1. **No full-tree reveal.** The pull-back-to-whole-
   tree shot goes. Replace with a closer, angled
   camera that stays IN the flow: lines flowing
   UPWARDS past/around the camera through the full-
   history replay, the tree implied by the stream
   rather than framed whole. Down-to-up progression
   from v2 stays.
2. **Marble-track motion model:** think of it as a
   track of marbles that split into multiple when
   needed (branch = marbles forking onto parallel
   tracks, merge = tracks rejoining and marbles
   continuing as one stream). Continuous forward
   motion in ONE space from start to box ending.
3. **Corrections/sendbacks visible in the flow:**
   when history shows a correction or sendback (real
   sourced events: e.g. a verifier NOT READY round, a
   fixed defect commit, a study FAIL), the marbles on
   that track visibly bounce/loop back, get stamped,
   and rejoin - small labels, sourced in your report.
4. **Gates become windows, not scene shifts:** when
   the stream reaches a gate moment, a window pops up
   FROM the segment space (rises/scales from the
   track plane, camera keeps its world), plays its
   visualization inside the window beside the blinking
   Pico mockups, then closes down into a green check
   and the flow progresses again - no abrupt exit
   from the tree to a separate scene. Apply to all
   three gates: KissFFT (existing), tokens (existing),
   and NEW: IAS15 (figure-8 orbit + hash rows idiom
   from video/ scenes + six-board fact), anchored at
   its true history beat.
5. **Resolution:** render at 2560x1440 master (owner:
   1080p pixelates, especially zooms). All camera
   moves render the scene parametrically at output
   scale - no crop-upscale beyond 1.5x anywhere.
   Deliver the 1440p mp4 (a 1080p downscale twin is
   welcome but secondary).

**Carry over (do not regress):** real history
(history.json; true order/parentage; simplifications
renamed incl. any new), sourced popups in the chase,
legend, refreshed Gate-2 numbers with definition
on-frame, PASS solid hold, box ending, handoff frames
(open pure white 255,255,255; end near-black matching
outro2 - VALUES unchanged, now at 1440p). Chase intro
and 2D->3D lift from v2 may evolve but the early
popup teaching beats stay.

**Fences:** scratch only, repo untouched, nothing
committed, v1/v2 preserved; never open/search/list
anything with `cft` in its name; bounded renders with
memory ceilings (1440p frames are 3.7 Mpx - stream,
never buffer the film); eyeball your stills.

**Outputs:** gitvisual3.mp4 (probe-verified 1440p),
stills3/ (angled upward flow, marble split, a
sendback loop, each gate-window open + green-check
close, box end), beats3.md, `scratch/study-video-
gitvisual/polish3-report.md` (READY/NOT READY; marble
model as built; measured camera; duration delta vs
83s and the 180s budget; assembly needs), append
`ledger/study-video-gitvisual.md`. Structured
complete/evidence/unresolved. Script files, Git Bash,
MSF_PYTHON pinned.
