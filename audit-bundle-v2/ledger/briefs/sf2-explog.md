**Role:** study-sf2-explog (SF-2 input spike, scratch only)

**Question:** price the exponential/logarithm Clause 9.2
families as three-format correctly-rounded bundles, spike-
style like the Step 2b trig spike: for `exp2`/`exp2m1`,
`log2`/`log2p1`, `exp`/`expm1`, `exp10`/`exp10m1`,
`log`/`logp1`, `log10`/`log10p1` (12 names, 36 rows),
measure the binary64 hardest-to-round margins by MPFR
re-decision of published worst-case inputs (leg (a)
authority, same reading SF-1 settled for trig), confirm the
Ziv three-stage kernel pattern reuses mechanically from
`src/msf_math.c`, and return PRICED-GO / NO-GO per family
with hours. No repo changes.

**Sources:** `muse-softfloat/docs/studies/SF-1.md` (Sec.8
evidence ladder, leg-(c) settlement), `scratch/
tier2-trig-spike/report.md` (the method to mirror),
`scratch/tier2-clause9/report.md` Sec.4.6 ranks 5-8,
`src/msf_math.c` + `tools/gen_trig_tables.py` (kernel/table
pattern to cost), CORE-MATH worst-case vector files as
published inputs (execute/fetch-record style only; tree in
`scratch/oracles`; never read its implementation source or
use its constants as design input; `cr_cospif` precedent:
verify any executed function per `scratch/tier2-oracle-0b/
report.md`), MPFR 4.2.2 as decider (Step 0b recipes).
Never open/search/list anything with `cft` in its name.

**Required content:**
1. Margins measured, not quoted: for each family at
   binary64 and binary32, re-decide the published worst-case
   inputs with MPFR at >=320 bits and report the smallest
   margin in extra bits (method = trig spike's); state input
   counts per family and any family whose published set is
   missing/incomplete (that is a NO-GO trigger for the leg
   (c) reading used here).
2. Kernel reuse audit: which parts of the trig Ziv pattern
   (wide mul, table generation, error-bound generator,
   decided/interior logic) carry over per family; what is
   genuinely new (constants: log2/ln10 chains, near-1 and
   near-0 branches, exact exponent cuts for
   over/underflow). Specials burden per Clause 9.2 from
   `scratch/S1/` extracts.
3. Recommended first family (presumably `exp2`/`log2` pair)
   with a worked error-budget sketch at binary64: stage
   widths that the measured margin demands.
4. Price: hours per family bundle (gen tables, kernel,
   vectors, planted verification), dependency order, risks,
   stop conditions; families to keep deferred named with
   reasons (e.g. incomplete worst-case publication).

**Outputs:** `scratch/sf2-explog/report.md` (first line
PRICED-GO/NO-GO per family; margin table with counts) and
`ledger/study-sf2-explog.md`. Structured
complete/evidence/unresolved. Script files (Git Bash,
MSF_PYTHON pinned, TMP in your scratch). Any fetch you make
is recorded in your ledger with URL + sha256 (scratch only).
