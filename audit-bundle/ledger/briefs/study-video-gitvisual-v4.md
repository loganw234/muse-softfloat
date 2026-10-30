**Role:** study-video-gitvisual-v4 (marble sync + packaging, full model)

**Input:** v3 in `scratch/study-video-gitvisual/`
(gitvisual3.mp4 88s/1440p, polish3-report.md,
beats3.md, render_gitvisual3.py). Owner feedback after
watching assembly v3. Produce `gitvisual4.mp4`;
v1-v3 preserved.

**Owner fixes (both required):**
1. **Marble desync.** The marble track gets a bit
   desynced at times - marbles drift out of phase
   with the track events they are meant to ride
   (node lightings, splits, merges, sendback loops,
   gate arrivals). Fix at the model level, not by
   fudging offsets: every marble's position must be a
   pure function of the same rank/cursor clock that
   drives node lighting and lane drawing, so a marble
   is AT a node on the exact frame it lights, splits
   spawn at the true merge-base frame, merges absorb
   on the merge frame. Prove it numerically: sample
   the event frames and report marble-centroid vs
   node-center distance (target <= a few px at
   1440p) for every chase node, every sendback loop
   entry/exit, and a sample of replay merges; list
   worst offenders before/after if measurable.
   Also keep marbles on the 120 BPM grid pulse
   without letting the pulse move them off-event.
2. **Packaging ending.** Currently the trail enters
   the box and the lid shuts. Change to: EVERY
   colored marble (each system color from the legend
   - parcels, verifiers, plants, gates, studies,
   escalations, lead) visibly travels into the box
   before the lid shuts, conveying the retained
   documentation the process keeps. Small labels or
   stamped icons for what is retained are welcome if
   legible (RECORD, ledgers, vectors, metrics - only
   real artefacts, named in your report). The lid
   shut + dark end frame values do not move.

**Carry over (do not regress):** everything v3
carried (real history + simplifications renamed,
gate windows incl. IAS15, refreshed tokens numbers,
PASS solid hold, handoff values at 1440p). Duration:
stay within ~88s +/- a few (film is heading for
~141s with the new why/idea pair; state your exact
duration and any trims you traded for the packaging
beat).

**Fences:** scratch only (`scratch/study-video-
gitvisual/`), repo untouched, nothing committed;
never open/search/list anything with `cft` in its
name; 2560x1440 parametric rendering, memory
ceilings, stream frames; another agent is rendering
concurrently in sibling scratch dirs - moderate load,
stay in your directory.

**Outputs:** gitvisual4.mp4 (probe-verified) +
optional 1080p twin, stills4/ (sync proof frames at
events, packaging sequence frames, box end), sync
measurement data (json), beats4.md,
`scratch/study-video-gitvisual/polish4-report.md`
(READY/NOT READY; sync model + measured residuals;
packaging design; duration), append
`ledger/study-video-gitvisual.md`. Structured
complete/evidence/unresolved. Script files, Git Bash,
MSF_PYTHON pinned.
