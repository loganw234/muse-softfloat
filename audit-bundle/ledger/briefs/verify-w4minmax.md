**Role:** verifier-w4minmax (ParcelRound verifier, SF-1 Step 1)

**Stance:** disconfirm only. You fix nothing. Findings one claim
per line, (a) regression / claim-surface deviation or (b) wrong
answer; only (a)/(b) send back. "Found nothing" needs the
evidence below actually produced. The standard is higher
authority than the parcel's generator: a generator whose
expectations are wrong is a finding even when every replay
passes.

**Copy:** `worktrees/verify4-minmax` (detached HEAD, parent
`8578114`). Never consult the parcel branch/worktree, other
worktrees, key files, `scratch/lead/`, `scratch/parcel-w4minmax/`,
or `ledger/lead.md`. Clean room: nothing with `cft` in its name,
ever. Never modify the copy or commit. No board, no PDF.

**Subject:** all 33 SF-1 Step 1 rows (Clause 9.6 eight names +
9.7 three names at binary16/32/64). Governing: brief
`ledger/briefs/w4-minmax.md` (frozen semantics), design entry
`ledger/parcel-w4minmax.md`, SF-1 Sections 5/8/14 in the copy,
Clause 9 survey 4.1/4.2 paraphrase. Berkeley silent; MPFR may
corroborate Number-form finite values only.

**Required probes (counts each; skips named):**
1. Budgets in the copy via script files (Git Bash,
   `MSF_PYTHON` pinned to workspace `.venv`, TMP into your
   scratch): `smoke`, then `standard`; verdicts, totals,
   inventory, controls by name.
2. Committed Tier 2 vectors: replay all six
   `tests/vectors/{minmax,payload}-f{16,32,64}.vec` explicitly
   with the built runner and expect-counts derived from the
   files; all 33 names present; provenance printed. (run.sh
   VECS wiring is lead merge work - its absence is not a
   finding; unwired-but-unreplayed vectors would be.)
3. Regeneration byte-identity: table generator to temp (4
   files) and `tests/gen_vectors_tier2.py directed` to temp
   (6 vector files), `cmp` each. Any difference is a finding.
4. Generated evidence rerun (your choice of full or stated
   sample with counts): binary16 payload exhaustive, binary16
   boundary-first min/max sweep, seeded binary32/64 sweep -
   through the runner, exact compare.
5. Independent semantics audit: your own small exact reference
   or hand-derived tables (not the parcel generator) over the
   class cells - plain vs Number NaN handling, ignored-sNaN
   invalid, matrix payload/sign delivery, -0/+0 order,
   magnitude tie-breaks, first-operand wins; payload
   admissible sets incl. max/max+1, -0 ruling, signaling
   setter bit, getPayload -1/sign behaviour, round-trips.
   Source-read the C core and generator reference against the
   brief pins line by line.
6. Claim surface vs parent: only brief-owned files; all 33
   implemented rows wave 4, none partial; formats and
   lead-owned files untouched; ceiling and hand-written line
   count sanity.
7. Your own negative controls (scratch copies): at least the
   brief's control shapes, watched failing with a passing
   positive counterpart each.

**Outputs:** `scratch/verifier-w4minmax/report.md` (first line
`READY` or `NOT READY`; findings with smallest repro; counts;
not-done list) and `ledger/verifier-w4minmax.md` in house
shape. Structured complete/evidence/unresolved. Machine under
load; times are records only.
