**Role:** study-tier2-interval (read-only expansion-workload survey)

**Question:** Would interval arithmetic applied to geometry be a strong
scientific workload for *earning* specific Tier 2 additions to
muse-softfloat, rather than merely using directed rounding and FMA,
which already exist? Recommend for or against a concrete workload with
measured or carefully bounded evidence. Do not force a fit.

**Authorization and sources:** `ledger/README.md`, repo `AGENTS.md`,
`muse-softfloat/docs/studies/SF-0.md` especially §2.7 and §4, surveys
`scratch/S1/report.md` and `scratch/S2/report.md`, current
`docs/COVERAGE.tsv`, `include/muse_softfloat.h`, and `docs/RECORD.md`.
Base commit `54e4bff`. Clean room: never open, search, or list anything
with `cft` in its name. External papers/docs may be read for workload
concepts; do not copy a third-party interval/softfloat implementation
into design notes as code. Any prototype is your own scratch code.

**Scope:** read-only study. You may write small exact-arithmetic
prototypes/models in `scratch/tier2-interval/` to test operation needs.
Do not modify the repository, board, ledgers other than your own, or the
kit. First action: write `ledger/urgent/study-tier2-interval-test.md`,
then a survey-plan entry in `ledger/study-tier2-interval.md`. Time box
180 minutes from that entry; checkpoint at 120. Script files, not
inline heredocs; TMPDIR/TMP/TEMP into scratch.

**Investigate concretely:**
1. Compare at least three candidate workloads, for example: guaranteed
   ray/box or ray/sphere classification; interval implicit-surface ray
   marching/root isolation; robust geometric predicates via expansions;
   interval kinematics or CSG. Pick the strongest one (or reject all).
2. For each, inventory operations and separate: already in Tier 1;
   Tier 2 additions that are truly load-bearing; workload-level helpers
   that should not become library claims. Test augmented add/mul,
   min/max family, NaN payloads, dynamic rounding, reductions/dot
   products, and Clause 9 functions for actual necessity, with a
   remove-it-and-what-breaks analysis.
3. Distinguish scalar correctly rounded functions from directed
   interval enclosures. If trigonometry or other functions are needed,
   state the enclosure theorem/gate required; correct rounding in
   ties-to-even alone does not prove containment.
4. Define proof claims and oracles: containment by construction,
   exact rational/MPFR reference, host-vs-board bit identity, randomized
   adversarial cases, and examples where naive floating geometry gives a
   different classification from the guaranteed interval result.
5. Estimate RP2040 feasibility: interval operation counts, memory,
   scene size, subdivision blow-up, and expected runtime scale from
   existing measured softfloat evidence. Label estimates as believed.
6. Assess demo/video value: can a viewer see a missed/extra intersection
   or crack that the guaranteed method resolves? Propose the smallest
   visual experiment and its negative controls.

**Report:** `scratch/tier2-interval/report.md` with recommendation at
the top (ADOPT / ADOPT WITH FRAMING / REJECT), candidate comparison,
operation/addition table, proof and oracle design, RP2040 budget,
proposed SF-1 gates, and open owner/lead questions. Close in
`ledger/study-tier2-interval.md` with evidence counts and gaps named.
