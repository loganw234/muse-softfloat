**Role:** parcel-w6captions (seal: captions + stills for the final cut)

**Base:** `cdc40aec9b11eeab61ab3c6cc9940b5dbbac4a67`, branch
`wave6-captions`, worktree `worktrees/w6-captions`. Work only there.

**Deliverables (all generated, reproducible):**
1. `video/captions.py` — a generator that derives caption cues
   from the segment modules' own audit data (import them; do not
   hand-transcribe): idea/why BLOCKS, intro/outro BLOCKS tables,
   gitvisual POPUP5 + gate-window titles, each at native segment
   offsets [intro 0, idea 7, why 33, gitvisual 65, outro 173],
   scaled x120/124 into assembly time (179.03 s). The header
   states the inclusion rule in one paragraph: readable
   headline/body text a viewer is meant to read in sequence;
   named exclusions (HUD counters, graph branch labels, hashes,
   legend, source tags). If a segment's audit table cannot
   express a readable beat (e.g. outro typed replies/panels),
   add the smallest explicit cue table inside captions.py with
   its source named per cue — never guess text that is not on
   screen; verify against stills (below).
2. `video/out/assembly_v6.srt` and `video/out/assembly_v6.vtt`
   from that generator (byte-stable across re-runs: state and
   prove by sha256 of two runs). For the owner's YouTube upload
   and for any other host.
3. `video/out/stills_v6/` — a stills set for the current cut
   (the existing `stills/` belongs to final.mp4): one still per
   scene beat across all five segments, grabbed from the
   committed `assembly_v6.mp4` in scaled time, filenames
   `NN_t<seconds>_<slug>.png`, plus an `INDEX.md` mapping each
   still to its scaled+native time and what it shows.

**Validation (acceptance):** (a) SRT and VTT parse under a
strict parser you write or reuse from the venv: monotonic
starts, no overlaps, every cue 0 < start < end <= 179.03,
cue count stated; (b) sampled truth check: at least 12 cues
spread over all five segments — grab the assembly frame at
each sampled cue's midpoint, view it, and confirm the cue
text is the readable text on screen (quote frame-vs-cue in
the report; mismatches are fixed, not noted); (c) every
stills_v6 still viewed, INDEX times recomputed not copied;
(d) `tools/run.sh standard` PASS unchanged in the worktree;
(e) diff vs base limited to owned files.

**Owned files:** `video/captions.py`, `video/out/assembly_v6.srt`,
`video/out/assembly_v6.vtt`, `video/out/stills_v6/**`,
`docs/metrics/briefs.jsonl` (own row, wave "wave6",
binary-append), plus at most a one-line pointer in
`video/README.md` layout table if needed (say so in report).
No segment code, no renders, no assembly changes, no audio.

**Outputs:** tip commit(s) on `wave6-captions`, detailed body +
`Co-Authored-By: Muse Code (muse-wonder-full-1.0)
<noreply@meta.ai>`; `scratch/parcel-w6captions/report.md` +
`ledger/parcel-w6captions.md`. Structured
complete/evidence/unresolved mandatory. Script files, Git Bash,
MSF_PYTHON = workspace .venv. Nothing with `cft` in its name;
do not open `docs/metrics/plants.jsonl`. ~300 min.
