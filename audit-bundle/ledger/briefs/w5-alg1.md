**Role:** parcel-w5alg1 (SF-2 Step 2a: seam + `rSqrt`)

**Deliverable:** on branch `wave5-alg1` (worktree
`worktrees/w5-alg1`, base `7c3819c`): (i) the algebraic
seam - `math_bin` signature class, dispatch, seam
controls, and Tier 2 registration of the `r_sqrt` and
`hypot` rows (rSqrt lands implemented here; hypot
registered **planned**) taking Tier 2 to 45 registered /
42 implemented; (ii) correctly rounded `rSqrt` at
binary16/32/64 (3 rows, `C-754`, five attributes from
birth), merge-ready. Time box 720 min; checkpoint note
at 600 min.

**Governing:** `docs/studies/SF-2.md` Secs. 1, 3, 6-9 and
`scratch/sf2-algebraic/report.md` (read in full; its Sec. 3
kernel design, Sec. 5 specials, Sec. 6 oracle recipes,
Sec. 7 inventory, Sec. 8 split/stops bind). Study stop
conditions: any unadjudicated disagreement, or a [2R]
specials cell flipping without owner ruling - stop, do
not relabel.

**Work:**
1. Seam commit first (its own commit): `math_bin` sig in
   `tools/gen_tables.py` (+ runner/dispatch), the two
   `operations.tsv` rows verbatim from study Sec. 7.2
   (wave 5), `tools/run.sh` Tier 2 expected totals 45/42,
   seam negative controls watched (unknown sig token
   refuses; Tier 1 still prints 783). Stamp every file
   the header generator touches; regen twice, byte-
   identical. Escalate, never improvise, if a kernel
   inadequacy appears in `msf_roundpack.c`/`msf_wide.c`.
2. Kernel in new `src/msf_alg.c` per study Sec. 3:
   exact integer decision (split compare over u128),
   `--wrap`-clean, no float/double anywhere in `src/`
   (type scan stays clean). Specials per study Sec. 5
   table incl. the fenced `rSqrt(-0)` cell (clause signs;
   generator-table-decided, never MPFR-sourced).
3. Evidence: `tests/gen_vectors_alg.py` + MPFR decider
   (`tests/alg_decider.c`, Step 0b emin/emax recipes)
   per study Sec. 6-7.3 (~1,200 committed lines/format);
   binary16 **exhaustive** differential, all encodings x
   5 modes, count printed (262,144-class gate from the
   study probe); binary32/64 directed+ties+seeded volume;
   negatives watched: 1-ulp-moved hardest case, specials
   mutants, stripped inexact on a known tie, directed-
   mode swap, truncated stage width. Regeneration byte-
   stable x2; `smoke` + `standard` PASS; target-compile
   clean (RP2040 text/stack measured, recorded - no
   performance claims).
Clean room: nothing with `cft` in its name; CORE-MATH/
Berkeley executed oracles only; constants/kernels are
your own integer arithmetic from the study design.

**Owned files:** `tables/operations.tsv`,
`tables/implemented.tsv`, `tools/gen_tables.py`,
`tools/run.sh` (counts/controls), generated
`include/muse_softfloat.h` + `docs/COVERAGE.tsv`,
`src/msf_alg.c` (new), `tests/gen_vectors_alg.py`,
`tests/alg_decider.c`, `tests/vectors/alg-*.vec`,
`tests/VECTORS.md` (tag row), `docs/WIDTHS.md` (your
width row), `docs/metrics/briefs.jsonl` (your row).
`tools/run.sh` host/board build lists: add `msf_alg.c`
where the other src files ride. Everything else:
escalate.

**Report:** `scratch/parcel-w5alg1/report.md` (first line
READY/NOT READY; seam evidence; per-format counts incl.
the exhaustive total; specials table as shipped with the
[2R] cells named; not-done list incl. hypot still
planned) + `ledger/parcel-w5alg1.md` (design before
code, results after). Detailed commit bodies ending
`Co-Authored-By: Muse Code (muse-wonder-full-1.0)
<noreply@meta.ai>`. Never push/merge; no board flashing.
Structured complete/evidence/unresolved. Script files
only for runs (Git Bash, MSF_PYTHON pinned, TMP in
scratch; explicit memory ceilings on any long sweep).
