**Role:** parcel-w6filmretime (owner film notes: dedupe, zoom quality, 3-minute cap)

**Base:** `101b4aa98fc9f53005778fb424197d7ec7d26c82`, branch
`wave6-filmretime`, worktree `worktrees/w6-filmretime`. Work only there.

**Three owner items:**

1. **Duplicate question removed.** `idea.py` ends by posing
   "WHY NOT USE WHAT ALREADY SHIPS?" and `why.py` opens by
   posing it again (title scene, E_TITLE 3.5 s). Delete the
   why title scene entirely (scene, BLOCKS rows, unused
   copy) so the why segment opens on the spec; retime via
   its existing SHIFT-style time map. The idea segment's
   question stays as the single posing. Why native duration
   drops by the title's 3.5 s before item 3 re-extends it.

2. **Phone zoom pixelation.** `intro_outro.py`'s camera()
   crops a small box from the 2560x1440 frame and bilinear-
   upscales it - mid-dive text pixelates. Supersample INSIDE
   this segment only: render the phone scenes on an internal
   canvas at SSx (start SS=2, i.e. 5120x2880; try 3 if memory
   allows) and have the camera downscale from that canvas to
   the 2560x1440 output frame. Output file stays 2560x1440;
   no other segment changes resolution. Probe stills at a
   readable-text mid-dive depth for SS in {1 (current), 2, 3}
   and pick the smallest SS where bubble text is no longer
   visibly pixelated; state render wall time + peak memory
   per SS tried (records, not rates). The measured period
   centroid/clamps must be re-derived at the chosen SS (the
   file's own measurement path), and open/close colours stay
   exact (intro ends source white; outro opens source
   near-black - downscaling must not tint full-frame solids;
   verify pixel values, they are join-checked).

3. **Retime to the cap via text dwell.** Submission cap is
   3 minutes; current assembly is 163.5 s at 124 BPM. Target
   **179.0 s at 124 BPM** by setting segment text dwell, not
   by changing the tempo scale: native (120-grid) total must
   be exactly **185.0 s** (185 x 120/124 = 179.03). Starting
   allocation (adjust within ranges, total exact, all values
   on the 0.5 s grid): intro 7.0 (unchanged duration),
   idea 25.0-27.0, why 31.0-33.0 (after item 1's cut),
   gitvisual 106.0-110.0, outro 10.5-12.0. Added time must
   land as *dwell* - longer holds after lines complete
   (scene-end extension, gate-window holds, popup dwells,
   outro panel holds) - not slower typing, slower marbles,
   or slower camera moves, except where a renderer's only
   honest knob is a uniform internal stretch (say which and
   why). The pacing RULE is a minimum; longer holds satisfy
   it - recompute each segment's BLOCKS audit tables to the
   new times. Gitvisual invariants hold: gate ranks and
   cursor sync pure, episode activity from the same clock,
   gates/holds may lengthen but ranks do not move.

**Owned files:** video/segments/{idea.py, why.py,
render_why.py, intro_outro.py, gitvisual.py} (dwell/timing/
supersample only - no copy changes beyond item 1, no visual
redesign), video/assemble.py (SEGMENTS durations only),
docs/metrics/briefs.jsonl (own row, wave "wave6",
binary-append). Rendered segment MP4s regenerate in place.
Do NOT produce the assembly - the lead assembles at merge.

**Acceptance:** (a) each segment MP4 probed: durations sum
185.0 native (state each); (b) duplicate question gone
(quoted before/after scene lists); (c) SS probe stills +
chosen SS with the dive text legible, centroid error
re-measured, join colours exact; (d) gitvisual sync
re-measured at the new timing (adapt measure script from
scratch/study-video-gitvisual-v6/measure_sync7.py);
(e) `tools/run.sh standard` PASS unchanged (sanity that
nothing outside video moved).

**Outputs:** tip commit(s) on `wave6-filmretime`, detailed
body + `Co-Authored-By: Muse Code (muse-wonder-full-1.0)
<noreply@meta.ai>`; `scratch/parcel-w6filmretime/report.md`
+ `ledger/parcel-w6filmretime.md`. Structured
complete/evidence/unresolved mandatory. Script files, Git
Bash, MSF_PYTHON = workspace .venv. Memory: state the SS
peak; stop and report if a frame pipeline would exceed
~6 GB. Nothing with `cft` in its name. ~480 min.
