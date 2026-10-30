**Role:** parcel-w5log2 (SF-2 Step 3b: `log2`/`log2p1`)

**Deliverable:** correctly rounded `log2` + `log2p1` at
binary16/32/64 (6 rows, `C-754`, five attributes),
merge-ready on branch `wave5-log2` (worktree
`worktrees/w5-log2`, cut by the lead from main `54ac1bb`
(exp2 merged + recorded); Tier 2 stays 57 registered,
goes 51 -> 57 implemented, 0 planned). Time box
900 min; checkpoints at 600 min.

**Governing:** `docs/studies/SF-2.md` Secs. 1, 4, 6-9;
`scratch/sf2-explog/report.md` Secs. 6.2, 2, 4-5, 7 (read
in full). Same leg-(c) settlement and stop conditions as
Step 3a; any stage-3 final-undecided in evidence is a
STOP. Reuse the exp2 parcel's generator/decider/exhaustive
harness shapes - extend, do not fork them.

**Work:**
1. Kernel per Sec. 6.2: decode 2^k*mm, recentre by the
   exact mm^2>=2 compare, s=(mm-1)/(mm+1) via the new
   wide division (its error a named Ek line), atanh
   series, integer composition pack k+(t±Ek) exact at
   pack scale (this decides the attractor tail; log2(2^k)
   = k exact by construction incl. subnormal x).
   `log2p1`: exact wide 1+x formation into the same path
   (sticky into the s-division Ek line - the line the
   sketch warns not to forget), tiny-|x| relative path,
   pole at -1 exact. Specials per Clause 9.2 extracts;
   exact/tie branches + inexact obligations enumerated
   in the design entry first.
2. Evidence legs exactly as Step 3a: binary16 exhaustive;
   binary32 exhaustive finite differential (sharded,
   counts printed, memory ceilings); binary64 100% of
   published worst-case inputs + seeded, five modes,
   MPFR decider with adaptive precision. Negatives:
   1-ulp hardest, Ek narrowed, division-sticky dropped
   (must fail somewhere named), recentring compare
   flipped, pole flag strip. Committed vectors in the
   trig idiom; `smoke` + `standard` PASS; target-compile
   clean.
Clean room and fetch discipline as Step 3a.

**Owned files:** `tables/implemented.tsv`, generated
header/COVERAGE, `src/msf_math.c`,
`src/msf_explog_tables.h` (regenerated),
`tools/gen_explog_tables.py`,
`tests/{gen_vectors_explog.py,explog_decider.c,
explog_exhaustive.c}`, `tests/vectors/explog-*.vec`,
`tests/VECTORS.md`, `docs/WIDTHS.md`,
`docs/metrics/briefs.jsonl` (your row). Everything else:
escalate.

**Report:** `scratch/parcel-w5log2/report.md` +
`ledger/parcel-w5log2.md`, shapes as Step 3a. Never
push/merge; no board flashing. Structured
complete/evidence/unresolved. Script files only (Git
Bash, MSF_PYTHON pinned, TMP in scratch).
