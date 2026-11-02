**Role:** parcel-w5alg2 (SF-2 Step 2b: `hypot`)

**Deliverable:** correctly rounded `hypot` at
binary16/32/64 (3 rows, `C-754`, five attributes),
merge-ready on branch `wave5-alg2` (worktree
`worktrees/w5-alg2`, base = the alg1 merge commit;
Tier 2 goes to 45 registered / 45 implemented).
Time box 600 min; checkpoint at 480 min.

**Governing:** `docs/studies/SF-2.md` Secs. 1, 3, 6-9;
`scratch/sf2-algebraic/report.md` Sec. 3.2 (kernel),
5.2 (specials + evaluation order), 6 (recipes incl. the
measured midpoint ties), 7.3 volumes, 8 stops - read in
full. Stop conditions: any unadjudicated disagreement;
either [2R] cell below flips on second read without an
owner ruling - stop, do not relabel (owner is away;
a flip means NOT READY with the cell named, never a
guess in code).

**Work:**
1. Kernel in `src/msf_alg.c` per Sec. 3.2: order
   |a|>=|b|, 128-bit anchored window at the top of a^2,
   floor-sum + separate sticky (never a jam into the
   sqrt input - ties are attainable and the floor form
   is mandatory), sqrt_core scaling, one pack. No new
   width; WIDTHS hypot row updated. Result sign always
   +, incl. +0/+inf deliveries.
2. Specials in the study's evaluation order: sNaN
   first (invalid), then any ±inf -> +inf (including
   with a quiet NaN - both operand orders), then qNaN
   matrix, then finite. Second reads recorded in your
   design entry for the two cells: (±inf, sNaN) order
   and inf+finite [D]. MPFR corroborates values, never
   flags (study Sec. 6).
3. Evidence: extend `tests/gen_vectors_alg.py` +
   decider (trig/alg1 pattern); ~2,500 committed
   lines/format (boundary pool squared, exponent-span
   lattice both orderings, subnormal-corner pairs, the
   measured ties, seeded); binary16 second-operand
   sweep vs the boundary pool + a counted sampled full
   sweep; f32/f64 directed+seeded volume with counts;
   optional `cr_hypot*` execution corroboration (~1 h,
   study Sec. 6 harness shape; execution only).
   Negatives watched: hypot(qNaN,inf)->NaN mutant,
   jam-instead-of-floor mutant must fail the tie family,
   1-ulp hardest, stripped inexact on a tie, mode swap
   on a subnormal-output case. Regeneration byte-stable
   x2; `smoke` + `standard` PASS; target-compile clean
   (sizes recorded, no performance claims).
Clean room: nothing with `cft` in its name; kernels are
your own integer arithmetic from the study design.

**Owned files:** `src/msf_alg.c`, `tables/implemented.tsv`,
generated `include/muse_softfloat.h` + `docs/COVERAGE.tsv`,
`tests/gen_vectors_alg.py`, `tests/alg_decider.c`,
`tests/vectors/alg-*.vec`, `docs/WIDTHS.md` (hypot row),
`tools/run.sh` (counts only), `docs/metrics/briefs.jsonl`
(your row). Everything else: escalate (board wiring for
msf_alg.c lands with the alg1 merge - check it exists and
escalate if not).

**Report:** `scratch/parcel-w5alg2/report.md` (first line
READY/NOT READY; per-format counts; specials as shipped
with both [2R] dispositions; tie evidence; not-done) +
`ledger/parcel-w5alg2.md` (design before code, results
after). Detailed commits ending `Co-Authored-By: Muse
Code (muse-wonder-full-1.0) <noreply@meta.ai>`. Never
push/merge; no board flashing. Script files only (Git
Bash, MSF_PYTHON pinned, TMP in scratch, explicit memory
ceilings). Structured complete/evidence/unresolved.
