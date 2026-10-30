**Role:** verifier-w4interval (ParcelRound verifier, SF-1 Step 1c host proof)

**Stance:** disconfirm only. You fix nothing. Findings one claim
per line, (a) regression / claim-surface deviation or (b) wrong
answer. A workload that ever decides wrong - or an oracle that
says so - is the core (b); check containment yourself, do not
trust the parcel's audit script or catalogue decisions.

**Copy:** `worktrees/verify4-interval` (detached HEAD, parent
`b704b4c`). Never consult the parcel branch/worktree, other
worktrees, keys, `scratch/lead/`, `scratch/parcel-w4interval/`,
or `ledger/lead.md`. Clean room: nothing with `cft` in its
name, ever. Never modify the copy or commit. No board, no PDF.

**Subject:** Step 1c host proof only (brief
`ledger/briefs/w4-interval.md`; design entry
`ledger/parcel-w4interval.md`; survey in scratch). No
on-silicon claim is in scope; the board sample is lead work.

**Required probes (counts each; skips named):**
1. Rebuild the host runner from the copy (`-Wall -Wextra
   -Werror`, contraction off) via script files; rerun the full
   catalogue; reproduce or refute the IW1 SHA-256 the host
   prints (state the value you measured).
2. Independent containment audit with your own exact-rational
   code over the stored bit patterns: violations, decided-wrong
   per stage, flips, guard rows UNCERTAIN, counts by family.
   Cross-check the TSV exact/naive columns - do not trust them.
3. Source-read the workload core line by line against the
   brief: directed modes on every endpoint op, stage-3 EFT
   correctness conditions and the flags guard, box outer/inner
   logic and axis-parallel branch, torus bracket proof shape
   and op-cap behaviour, minimum/maximum endpoint selection,
   **no Number form anywhere in the core** (scan), no hardware
   floating type named, no allocation.
4. Regeneration: catalogue TSV byte-identical from the
   generator; table-generator drift clean; `smoke` then
   `standard` in the copy PASS (script files, Git Bash,
   MSF_PYTHON pinned to workspace `.venv`).
5. Your own mutants on scratch copies: RD/RU swapped, RN for
   directed, Number form substituted, stage-3 guard weakened -
   each watched failing against your audit, positive
   counterpart passing.
6. Claim surface vs parent: exactly the brief-owned files;
   ceiling; catalogue provenance on every row; survey-count
   reproduction sanity (tangent staging, limb band, torus
   march-miss) recomputed, not quoted.

**Outputs:** `scratch/verifier-w4interval/report.md` (first
line `READY` or `NOT READY`; findings with smallest repro -
row id + stage for containment failures; counts; not-done
list) and `ledger/verifier-w4interval.md`. Structured
complete/evidence/unresolved. Times are records only.
