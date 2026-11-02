**Role:** verifier-w6filmretime (ParcelRound verifier, film retime)

**Stance:** disconfirm only. The parcel claims the film now fits
the 3-minute cap, poses its question once, and zooms without
pixelation. Re-derive every one of those claims from the copy
itself; anything you cannot re-derive is a finding.

**Copy:** `worktrees/verify6-filmretime` (detached HEAD
`a1e83d9`, parent `101b4aa`). Never consult the parcel
branch/worktree (`wave6-filmretime`, `worktrees/w6-filmretime`),
other worktrees, keys (`scratch/lead/keys/`), `scratch/lead/`,
`scratch/parcel-w6filmretime/`, `ledger/lead.md`, or GitHub.
Authorities: this brief, `ledger/parcel-w6filmretime.md`, the
copy's tree. **Fence by name: `docs/metrics/plants.jsonl` must
not be opened, read, grepped, or cited — no exception.**
Nothing with `cft` in its name. Never modify the copy; run
renders/assemblies/gates in a duplicate. No board.

**Required probes:**
1. Durations and the cap. Probe every segment MP4 in the copy
   with your own commands (duration, resolution, fps, audio).
   Compare each against `video/assemble.py` SEGMENTS and its
   docstring arithmetic. Recompute the native sum and the
   scaled total from the tempo factor **as written in the
   code**; state whether the assembly as coded lands under
   180 s with cuts on 124 BPM beats. Assemble in the duplicate
   if the arithmetic needs settling, and probe the product.
2. The duplicate question. From the copy's `idea.py`/`why.py`
   scene and BLOCKS structure plus stills grabbed from the
   copy's MP4s (why's first seconds, idea's closing scene):
   the question is posed exactly once, why opens on the spec,
   and no dead title-scene copy remains.
3. Dwell audits. The pacing RULE: dwell = smallest 0.5 s
   multiple >= max(1.5 s, 0.5 + words/2.5). Import the copy's
   modules and recompute dwells from the BLOCKS values they
   actually compute (idea, why, outro via `intro_outro.py`,
   gitvisual popup dwells) — not from literals you read. Every
   dwell >= RULE, none zero/negative, no scene overlaps,
   gone-times match the scene cut constants. From the diff vs
   parent: added time is dwell only (typing speeds, dive and
   pull-back windows, marble leg durations unchanged).
4. Supersampling. From the copy code's defaults (no env
   override): the internal canvas size in effect, and
   `measurements3.json` consistency with it (ss, internal
   resolution, period centroid/clamps derived at that SS).
   Produce a mid-dive frame at copy defaults in the duplicate
   (import-probe or re-render) and compare bubble-text
   sharpness (stills + a numeric edge metric) against the
   shipped `intro3.mp4` mid-dive frame and stills. Join
   colours: intro's last frame and outro's first frame solid
   values in source terms, matched to their neighbours.
5. Gitvisual sync. Import the copy's `gitvisual.py`: gate
   ranks equal the merge ranks derived from the copy's own
   history/process data; `cursor_rank` sits exactly on each
   gate's rank at its t0 and through its window; legs
   8/5/7 s, gate windows 9/9/8.5 s as the ledger claims;
   cursor monotonic over a dense time sample; TOTAL 108.0.
6. Gate and scope. `tools/run.sh standard` PASS unchanged in
   the duplicate. Diff vs parent limited to the parcel's
   owned files (`video/segments/{idea,why,render_why,
   intro_outro,gitvisual}.py`, `video/assemble.py`, the
   `briefs.jsonl` own row, regenerated segment artifacts).
   The briefs row's numbers match your probed reality. Claim
   discipline: timings as records only, no performance
   claims, film silent.

**Outputs:** `scratch/verifier-w6filmretime/report.md` +
`ledger/verifier-w6filmretime.md`, verdict READY or NOT READY
with numbered findings (tag each blocker = wrong answer or
regression vs the parcel brief, or note). Structured
complete/evidence/unresolved mandatory. Script files, Git
Bash, MSF_PYTHON pinned to workspace .venv. Stop and report
if a frame pipeline would exceed ~6 GB. ~300 min.
