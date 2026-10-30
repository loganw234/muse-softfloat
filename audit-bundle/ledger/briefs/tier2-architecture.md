**Role:** study-tier2-architecture (read-only architecture/integration survey)

**Question:** How should Tier 2 be integrated into this codebase and
RP2040 evidence chain without weakening the Tier 1 claim, and what
selection criteria should decide the expansion workload?

**Authorization and sources:** `ledger/README.md`, repo `AGENTS.md`,
`docs/studies/SF-0.md` (especially §§2.7, 3, 4, 5, 7-9), current
`tables/`, `tools/gen_tables.py`, public header, runner/dispatch,
compat and board layers, existing ledgers/reports for Waves 1-3/IAS15,
and `docs/RECORD.md`. Base commit `54e4bff`. Clean room: never open,
search, or list anything with `cft` in its name.

**Scope:** read-only. First action:
`ledger/urgent/study-tier2-architecture-test.md`, then a survey-plan
entry in `ledger/study-tier2-architecture.md`. Time box 180 minutes;
checkpoint 120. Scratch `scratch/tier2-architecture/`; script files;
TMPDIR/TMP/TEMP there. You may run existing counts/probes and inspect
build outputs, but do not modify repo code or flash the board.

**Map the integration choices:**
1. API/state design for dynamic rounding wrappers, payload get/set,
   min/max, reductions, augmented two-result operations, and future
   mathematical functions. Preserve the pure bit-container core;
   identify what belongs in core, compat, workload, or nowhere.
2. Table generation: how operations.tsv/instantiations should grow,
   claim levels and authorities, generated dispatch/header effects,
   new vector shapes (multi-result, stateful wrappers, mathematical
   functions), provenance caps, and smoke/standard/board budget growth.
3. RP2040 evidence: ABI/libm interposition surface, code/RAM/table
   costs, board-harness protocol extensions, per-core dynamic state,
   and what can be bit-compared host-vs-board. Reuse measured IAS15
   lessons rather than inventing rates.
4. Workload-earning rubric for the lead's decision: define falsifiable
   criteria (addition is load-bearing, cannot be pinned away, oracle is
   independent, claim is exact or honestly bounded, board budget fits,
   licence boundary clean, visual/demo value, implementation parcel is
   bounded). Apply the rubric generically, not by pre-judging KissFFT
   vs interval geometry; note what evidence each survey must return.
5. Sequence/parallelism: propose SF-1 study structure, first gated
   parcels, verification/plant strategy, metrics rows, and stop rules if
   a candidate's additions are cosmetic or its oracle is weak.
6. Risks to Tier 1: generated-surface churn, claim dilution, runner or
   board protocol breakage, performance/table blow-up, licence leakage,
   and schedule risk before 2026-11-04. Name mitigations and refusals.

**Report:** `scratch/tier2-architecture/report.md` with an integration
map, rubric, proposed parcel sequence, and owner/lead decision list.
Close in `ledger/study-tier2-architecture.md` with evidence and gaps.
