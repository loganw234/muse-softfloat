**Role:** study-tier2-clause9 (read-only standards/oracles survey)

**Question:** What should SF-1 propose for Tier 2's ordered surface,
claim levels, and evidence gates so each addition can be earned
honestly within the remaining hackathon window and beyond?

**Authorization and sources:** `ledger/README.md`, repo `AGENTS.md`,
`muse-softfloat/docs/studies/SF-0.md` §2.7 and §4 in full, S1/S2
survey reports and clause extracts under `scratch/S1/` / `scratch/S2/`,
current API/coverage/tables, current runner/vector conventions, and
`docs/RECORD.md`. Base commit `54e4bff`. Cite IEEE 754-2019 by clause
only; do not open the PDF or copy standard text. Clean room: never
open, search, or list anything with `cft` in its name. Do not inspect
third-party math-function implementation source for design; public
documentation, papers, accuracy claims, licenses, and oracle interfaces
may be surveyed.

**Scope:** read-only. First action:
`ledger/urgent/study-tier2-clause9-test.md`, then a survey-plan entry in
`ledger/study-tier2-clause9.md`. Time box 180 minutes; checkpoint 120.
Scratch `scratch/tier2-clause9/`; script files; TMPDIR/TMP/TEMP there.

**Deliver an SF-1-ready map:**
1. Enumerate SF-0 §2.7 in order: Clause 9.6 min/max, 9.7 payload get/set,
   dynamic rounding get/set + dynamic ties-to-away + any roundToOdd
   helper, augmented add/sub/mul, reductions, then Clause 9 mathematical
   functions one at a time. Never-in-scope items stay out.
2. For each item: operation names, formats/directions and instantiation
   count under this API, result/flag/state semantics, exactness claim
   available, implementation dependency on existing kernels, likely
   parcel boundaries, and a rough difficulty class with reasons.
3. Oracle/evidence plan per item: Berkeley/TestFloat if any, MPFR/exact
   generators, CORE-MATH-class foreign oracles (execution/metadata only,
   never copied source), exhaustive possibilities by format, hardest-case
   evidence needed for a correct-rounding claim, and negative controls.
   Separate 754-conforming, ULP-budgeted approximation, and
   API-compatible-only claims; recommend which claim (if any) each item
   can honestly carry first.
4. For mathematical functions, rank plausible first candidates without
   assuming the workload choice. Consider argument reduction, special
   values, directed rounding, binary16 exhaustiveness, binary32/binary64
   Table-Maker difficulty, and whether a function should be refused.
5. Identify table/API/runner implications at study level: multi-result
   augmented ops, dynamic state wrappers, payload encodings, vector
   syntax, provenance/authority labels, and coverage accounting.
6. Propose SF-1 decision questions for the owner with recommendations,
   entry gates per item, and a smallest useful first parcel sequence.

**Report:** `scratch/tier2-clause9/report.md`, structured so the lead
can draft SF-1 without redoing the survey. Close in
`ledger/study-tier2-clause9.md`, naming unread/unverified items.
