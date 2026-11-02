**Role:** verifier-w6captions (ParcelRound verifier, captions + stills)

**Stance:** disconfirm only. Captions are claims about what is
on screen at an instant; check them against the film itself,
not against the generator's self-report.

**Copy:** `worktrees/verify6-captions` (detached HEAD `c537e0d`,
parent `cdc40ae`). Never consult the parcel branch/worktree
(`wave6-captions`, `worktrees/w6-captions`), other worktrees,
keys (`scratch/lead/keys/`), `scratch/lead/`,
`scratch/parcel-w6captions/`, `ledger/lead.md`, or GitHub.
Authorities: this brief, `ledger/parcel-w6captions.md`, the
copy's tree. **Fence by name: `docs/metrics/plants.jsonl` must
not be opened, read, grepped, or cited — no exception.**
Nothing with `cft` in its name. Never modify the copy; work in
a duplicate. No board.

**Required probes:**
1. Reproducibility: run the copy's `video/captions.py` in the
   duplicate; its regenerated `assembly_v6.srt`/`.vtt` must be
   byte-identical to the committed ones, twice in a row
   (hashes). The generator's scale and segment offsets must
   re-derive from `video/assemble.py` as written in the copy
   (read both; state the values each side carries).
2. Format strictness: parse both files with a parser you
   write (not the generator's own validator): SRT comma
   timestamps and numbering, VTT header + dot timestamps,
   monotonic non-overlapping cues, 0 < start < end <= the
   assembly's probed duration, srt cue set == vtt cue set
   (times and text).
3. Frame truth: at least 12 cues spread over all five
   segments — grab the committed `assembly_v6.mp4` frame at
   each cue's midpoint and view it; the cue text must be the
   readable new text on screen at that instant (quote
   cue-vs-frame per sample). Include the first cue and one
   outro cue in the sample.
4. Stills: every `stills_v6/INDEX.md` row recomputed from
   the segment audit data (scaled/native/local times), each
   filename's embedded time checked against its row, and at
   least 6 stills byte-compared against fresh grabs at their
   stated scaled times. All stills viewed for content match
   with their "Shows" text.
5. Gate and scope: `tools/run.sh standard` PASS unchanged
   in the duplicate; diff vs parent limited to the parcel's
   owned files (`video/captions.py`, `video/out/assembly_v6.srt`,
   `video/out/assembly_v6.vtt`, `video/out/stills_v6/**`, the
   briefs own row, at most the declared one-line
   `video/README.md` pointer).

**Outputs:** `scratch/verifier-w6captions/report.md` +
`ledger/verifier-w6captions.md`, verdict READY or NOT READY
with numbered findings (blocker = wrong answer/regression vs
the parcel brief, or note). Structured
complete/evidence/unresolved mandatory. Script files, Git
Bash, MSF_PYTHON pinned to workspace .venv. Stop and report
if a frame pipeline would exceed ~6 GB. ~240 min.
