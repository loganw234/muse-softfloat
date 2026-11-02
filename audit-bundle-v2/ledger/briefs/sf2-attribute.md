**Role:** study-sf2-attribute (SF-2 input study, scratch only)

**Question:** price `roundTiesToAway` as the fifth public
rounding attribute across the whole surface (0 new rows;
mode-sweep over 249 Tier 1 attribute-carrying rows + the
Tier 2 attr rows), and give a verdict on public
`roundToOdd` (currently an internal pack mode used inside
the trig kernel). The deliverable is the evidence bill:
kernel delta, runner/vector delta, oracle-mode availability
per family, and honest hours. No repo changes.

**Sources:** `muse-softfloat/docs/studies/SF-1.md` Sec.7
(ties-to-away + roundToOdd rows), `scratch/tier2-clause9/
report.md` (attribute section), the pack path
(`src/msf_roundpack.c` - modes as implemented today,
`src/msf_math.c` roundToOdd use), the runner
(`tests/msf_runner.c` mode enum), `tables/operations.tsv`
attr column, Berkeley/MPFR oracle mode support (execute
probes; recipes in `scratch/tier2-oracle-0b/report.md`),
`scratch/S1/` extracts for Clause 4.3 attribute wording.
Never open/search/list anything with `cft` in its name.

**Required content:**
1. Kernel delta: exact list of files/functions whose mode
   switch grows; proof sketch that ties-to-away is a pack-
   level concern only (or counterexamples: conversion,
   string, minmax, FMA jam paths), incl. tininess/overflow
   interactions and the runner's mode tokens.
2. Oracle audit by execution: which deciding authorities can
   emit ties-to-away expectations per family class
   (TestFloat modes? MPFR RNDA? exact-py path?); coverage
   gaps named per family; vector volume multiplier for
   smoke/standard and wall-budget impact measured from
   current budgets.
3. roundToOdd: what promoting it costs beyond the internal
   mode (header attribute semantics, ops that the standard
   does/doesn't define it for, oracle support); recommend
   promote / keep internal / bundle with ties-to-away.
4. Sequencing: can the attribute land before more math
   (so new families are born five-mode) - interaction with
   the in-flight SF-2 families; plant shapes a verifier
   would cut for it; hours + stop conditions.

**Outputs:** `scratch/sf2-attribute/report.md` (first line:
PRICED-GO/NO-GO + when) and `ledger/study-sf2-attribute.md`.
Structured complete/evidence/unresolved. Script files for
probes (Git Bash, MSF_PYTHON pinned, TMP in your scratch).
