**Role:** parcel-w5exp2 (SF-2 Step 3a: `exp2`/`exp2m1`)

**Deliverable:** correctly rounded `exp2` + `exp2m1`
at binary16/32/64 (6 rows, `C-754`, five attributes),
merge-ready on branch `wave5-exp2` (worktree
`worktrees/w5-exp2`, base = the hypot merge commit; Tier
2 goes to 51 registered / 51 implemented). Time box
900 min; checkpoint notes at 600 min.

**Governing:** `docs/studies/SF-2.md` Secs. 1, 4, 6-9 and
`scratch/sf2-explog/report.md` (read in full - its Sec. 6.1
sketch, Sec. 2 margins, Sec. 4 reuse audit, Sec. 5 fences
bind). Leg (c) is the SF-1 settlement: cite only the
spike-measured margins against published hardest cases,
never a quoted upstream gap. Stop conditions from the
spike Sec. 7 bind; in particular any final-undecided at
stage 3 in your evidence is a STOP (report, do not widen
ad hoc), and the `exp2m1` RN subnormal-corner pre-screen
cell is a named fence (~1 foreign false alarm per 1e4;
MPFR decides, never the foreign oracle).

**Work:**
1. Registration: `exp2`/`exp2m1`/`log2`/`log2p1` rows in
   `operations.tsv` (wave 5, `math_un`, `C-754`); exp2 pair
   implemented here, log2 pair registered **planned**;
   `tools/run.sh` totals 51/51 after this parcel... state
   them as registered 51, implemented 51-with-6-planned
   exactly as the runner prints. Regen twice byte-stable.
2. Kernel in `src/msf_math.c` (trig TU pattern) per the
   sketch: exact n+f split, 2^n as pack exponent input
   (never a multiply), u = f*ln2 Taylor with the delta
   form for u<0, three Ziv stages at 160/256/384 with
   generator-derived Ek; `exp2m1` by the composition
   forms (no new series) incl. the saturation cut and the
   x = -1075 exact tie packed exactly. Constants from
   your own generator (`tools/gen_explog_tables.py`,
   trig-generator pattern: bracket floors, factorial
   entries, Ek integers proven in the generator output,
   never decimal literals in C). Specials per Clause 9.2
   via `scratch/S1/` extracts; exact/tie branches and
   their inexact obligations enumerated in the design
   entry BEFORE kernel code.
3. Evidence legs per format: binary16 exhaustive;
   binary32 **exhaustive** finite differential against
   your MPFR decider (sharded; counts printed; `ulimit -v`
   ceilings; the spike's measured rates price it);
   binary64 100% of the published worst-case inputs for
   both functions + seeded volume, all five modes, MPFR
   decider (adaptive precision where the spike's collapse
   audit demands it). Committed vectors in the trig idiom.
   Negatives watched: 1-ulp hardest, Ek narrowed past its
   bound (must be caught by re-derivation or replay),
   constant-table digit flip, cut-threshold off-by-one,
   tie-branch flag strip. `smoke` + `standard` PASS;
   target-compile clean (sizes recorded).
Clean room: nothing with `cft` in its name; worst-case
inputs are a fetch-record act (record URL+sha256 in your
ledger; scratch only); no third-party constants/tables/
polynomials as design input.

**Owned files:** `tables/{operations,implemented}.tsv`,
`tools/{gen_tables.py,run.sh,gen_explog_tables.py}`,
generated header/COVERAGE, `src/msf_math.c`,
`src/msf_explog_tables.h` (generated), `tests/
{gen_vectors_explog.py,explog_decider.c,explog_exhaustive.c}`,
`tests/vectors/explog-*.vec`, `tests/VECTORS.md`,
`docs/WIDTHS.md` (your rows), `docs/metrics/{briefs,
fetches}.jsonl` proposed rows noted in report (fetches
row itself is lead-landed at merge). Board lists already
carry msf_math.c - verify, escalate if a new TU appears.

**Report:** `scratch/parcel-w5exp2/report.md` (first line
READY/NOT READY; per-leg counts incl. exhaustive totals
and worst-case coverage; Ek integers as proven; specials
as shipped; not-done incl. log2 pair planned) +
`ledger/parcel-w5exp2.md`. Detailed commits ending
`Co-Authored-By: Muse Code (muse-wonder-full-1.0)
<noreply@meta.ai>`. Never push/merge; no board flashing.
Structured complete/evidence/unresolved.
