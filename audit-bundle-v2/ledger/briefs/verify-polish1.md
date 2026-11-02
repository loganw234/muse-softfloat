**Role:** verifier-polish1 (ParcelRound verifier, stale-info cleanup)

**Stance:** disconfirm only. Findings: a changed claim the tree
contradicts, a regenerated artefact that does not reproduce, a
link or command that does not resolve.

**Copy:** `worktrees/verify-polish1` (detached HEAD, parent
`400b271`). Never consult the parcel branch/worktree
(`polish-stale1`, `worktrees/polish-stale1`), the main checkout,
other worktrees, keys, `scratch/lead/`, or `ledger/lead.md`.
Authorities: this brief, `ledger/parcel-polish1.md`, the copy's
tree itself (README, RECORD, BOARD, COVERAGE, header, video
scripts, the copy's git history at and before the parent).
**Fence by name: `docs/metrics/plants.jsonl` must not be opened,
read, grepped, or cited by you, in the copy or anywhere** (the
copy's `site/build_data.py` aggregates it internally when run as
a reproduction probe; cite only that regenerated output).
Nothing with `cft` in its name. Never modify the copy: do all
runs in a duplicate under your own scratch.

**Required probes:**
1. Claim surface vs parent (`git diff 400b271..HEAD` in the copy):
   every changed present-tense claim re-derived -
   README video master/duration/resolution vs
   `video/assemble.py` segment table + `video/out/` contents;
   BOARD TWIDDLES link resolves on disk; BOARD clone serials and
   LED pins vs the RECORD six-board entry and `board/msf_led.h`;
   msf_math.c attribute count vs the header enum and COVERAGE
   `ta` rows; every `audit-bundle/ledger/parcel-*.md` path cited
   in src/tools exists in the copy; board/CMakeLists flavour
   comment vs what the file registers.
2. Generated header: rerun `tools/gen_tables.py` in your
   duplicate; all four outputs byte-identical to the copy's;
   the decimal comment in the header matches the generator.
3. Site data: rerun `site/build_data.py` in your duplicate;
   `data.json`/`ops.json`/`vectors-sample.json` byte-identical
   to the copy's. Internal sums: plants by-wave rows sum to the
   headline caught/total; instantiations and vector totals vs
   COVERAGE and the gate inventory.
4. Gate: `bash tools/run.sh smoke` in your duplicate PASSes.
5. Video commands: every run command in video/README,
   STORYBOARD, assemble.py, probe.py, and the segment `Run:`
   lines resolves from its stated working directory (paths and
   script self-names exist); segment durations sum to the
   claimed assembly total.
6. RECORD appendix: the briefs arithmetic checks against the
   copy's `docs/metrics/briefs.jsonl` row count and its git
   history (`498a916`); the appendix must be appendix-only
   (no earlier RECORD line altered vs parent).

**Outputs:** `scratch/verifier-polish1/report.md` (READY/NOT READY;
findings F1..Fn each claimed-vs-re-derived with file:line;
not-done list) + `ledger/verifier-polish1.md`. Structured
complete/evidence/unresolved - mandatory, evidence entries carry
the finding ids. Script files (Git Bash, MSF_PYTHON pinned to the
workspace .venv), no long renders, keep memory modest. ~180 min.
