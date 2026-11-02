**Role:** parcel-w5aug (SF-2 Step 4: Clause 9.5 augmented arithmetic)

**Deliverable:** `augmentedAddition/Subtraction/
Multiplication` at binary16/32/64 (9 rows, `C-754`,
caller rounding attribute forbidden - the clause fixes
roundTiesTowardZero), merge-ready on branch `wave5-aug`
(worktree `worktrees/w5-aug`, cut by the lead from main
`bce49e0` (Steps 1-3 merged + recorded); Tier 2 goes to
66 registered / 66 implemented, 849 instantiations).
Time box 480 min; **seam stop: if the pair seam (sig +
runner + board reply) exceeds 3 h on its own, stop and
report NOT READY before kernel work** (study Sec. 0).

**Governing:** `docs/studies/SF-2.md` Secs. 1, 5, 6-9 and
`scratch/sf2-augmented/report.md` Secs. 0-2, 5 (read in
full). **Entry gate before kernel code:** pins P1/P4/P5
written into your design entry and the Sec. 1.3 flag
table independently second-read there against the S1
extracts. P1 stands as SF-2 Sec. 5 pins it - **R2: an
exact tiny residual signals underflow but raises no flag
under default handling** (owner-approved 2026-10-28; if
your second read cannot ratify R2 from the extracts,
STOP with NOT READY naming the cell - the owner is away,
do not guess). P4: rounding-column token `fixed`. P5:
your internal RTTZ pack-mode value, coordinated so it
can never collide with a public attribute value.

**Work:**
1. Seam slice (own commit, first): `aug_pair` sig,
   three table rows per study Sec. 1.6 (`augmented_add/
   sub/mul`, clause 9.5, tier 2, C-754, authority
   `project-exact`, flags yes, rounding `fixed`), pair
   structs + struct-return header shape (state the
   msf64 hidden-pointer ABI note in the header comment),
   two-result runner line + trampoline, board harness
   two-result reply (`board/harness_main.c`,
   `board/host_replay.py` - owned for this parcel),
   counts in run.sh, regen twice byte-stable, smoke
   green with rows planned.
2. Kernel per Sec. 1.5: exact 128-bit window + verbatim
   far-operand branch (no wide accumulator); flags
   computed from the Sec. 1.3 table from exact-residual
   tests - never inherited from a head pack (the pack
   tininess leak is a named mutant); inexact tracks
   pair exactness (header comment says so); WIDTHS rows
   with the representability proof restated rigorously
   incl. the binade-crossing step.
3. Evidence: project-exact integer reference in house
   generator style (Sec. 5 prototype is a shape, rewrite
   it; reviewed against the clause table independently);
   directed families per Sec. 1.6 (RTTZ discriminators,
   overflow-threshold tie + one step above, verbatim
   pairs, zero signs, tiny-exact-residual cells under
   P1, mul below-step cells, NaN/inf matrix twice);
   binary16 all-first-operand x pool standing + one-time
   exhaustive-pairs C run recorded (2^32 per name,
   memory ceilings, counts printed); negatives: ties-to-
   even head mutant, zero-tail sign flip, swapped pair,
   jam-window mutant, P1-opposite flag mutant,
   pack-tininess-leak mutant - each watched refusing.
   `smoke` + `standard` PASS; target-compile clean.
Clean room: nothing with `cft` in its name; semantics
from the clause extracts only.

**Owned files:** `tables/{operations,implemented}.tsv`,
`tools/{gen_tables.py,run.sh}`, generated
header/dispatch/COVERAGE, `src/msf_aug.c` (new) +
`src/msf_roundpack.c` (internal RTTZ mode only),
`tests/{gen_vectors_aug.py,runner.c (pair lines),
aug_exhaustive.c}`, `tests/vectors/aug-*.vec`,
`tests/VECTORS.md`, `board/{harness_main.c,
host_replay.py,run_board.sh,CMakeLists.txt}` (pair
reply + src wiring), `docs/WIDTHS.md`,
`docs/metrics/briefs.jsonl` (your row). Interval
workload integration is NOT this parcel (lead may brief
it after merge; keep the op-count claim story honest in
your report either way).

**Report:** `scratch/parcel-w5aug/report.md` (first line
READY/NOT READY; entry-gate dispositions P1/P4/P5; flag
table as shipped; per-family counts incl. exhaustive
totals; not-done) + `ledger/parcel-w5aug.md`. Detailed
commits ending the Co-Authored-By trailer. Never
push/merge; no board flashing (replay is lead work).
Structured complete/evidence/unresolved. Script files
only (Git Bash, MSF_PYTHON pinned, TMP in scratch).
