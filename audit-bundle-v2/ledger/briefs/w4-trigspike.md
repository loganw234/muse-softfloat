# Brief: Wave 4 Step 2b - sinPi/cosPi pricing spike (Fork B)

Role: study-tier2-trigspike (scratch design note; no repo
writes, no library code). Base:
`b704b4c9b805b584a2e221c3fa889017d480ac88`. Time box: 300
minutes. Outputs: `scratch/tier2-trig-spike/report.md` +
`ledger/study-tier2-trigspike.md`.

## Question to answer

SF-1 Section 6.2: can correctly rounded `sinPi`/`cosPi` be
built and **gated** as one binary16/32/64 bundle (claim C-754,
all four rounding attributes) inside the remaining hackathon
schedule - and at what price per format? Answer with a priced
parcel plan or a priced refusal. Fork B is adopted (SF-1
Section 14); Fork A is fallback only if you prove B cannot
close, in which case price A equally and say so plainly.

## Fences (hard)

Nothing with `cft` in its name; no IEEE PDF (SF-1/S1 clause
citations only). No third-party implementation source,
constants, polynomial coefficients, or proof material as design
input - for CORE-MATH you may use official documentation,
directory metadata, the pinned executables from Step 0b, and
worst-case `.wc` files **mechanically** (parse input encodings
and counts only; expected values are always re-decided by
MPFR/exact code you write). Step 0b fences stand: `cr_cospif`
toward-zero/downward corroborates nothing; MPFR is the decider;
foreign binaries are differential partners, never authorities.
Literature/documentation statements about worst-case gaps may
be quoted with sources; do not fetch implementation papers'
coefficient tables or code listings as design input.

## Required work

1. **Worst-case facts per format.** For each of sinPi/cosPi at
   binary16/32/64: quoted hardest-to-round gap (bits) and its
   source (official documentation or published worst-case
   data), or an explicit "no quoted gap found" with your own
   measured lower bound. Mechanical `.wc` census: files,
   counts, hardest inputs re-decided by MPFR at >=200 bits
   with the resulting correct roundings and margins printed.
2. **MPFR binary64 boundary recipe.** Extend the Step 0b probe
   pattern to binary64 (believed emin/emax -1073/1024) with the
   same known-answer discipline before any binary64 boundary
   narrowing is trusted anywhere below.
3. **Empirical margin measurement.** Fresh Python (mpmath/
   Fractions): binary16 exhaustive over all finite inputs -
   correctly rounded results in all modes and the minimum
   distance-to-boundary per function; binary32/64 over the
   `.wc` hardest inputs plus directed families near integers,
   halves, quarters, and seeded randoms. Report, per format,
   the intermediate precision at which a correctly rounded
   decision becomes always-decidable on your evidence.
4. **Original algorithm design.** Exact period/symmetry
   reduction to a bounded kernel range; kernel shape (wide
   fixed-point polynomial evaluated from constants we generate
   ourselves with MPFR at build time - never copied tables);
   directed-mode strategy (roundToOdd-style internal pack or
   nearest+neighbor with sign argument - argue it); Ziv
   escalation or fixed-precision proof obligation per format,
   stated as the SF-1 leg-(c) argument a parcel would carry;
   specials table from SF-1/S1 pins; NaN delivery via the
   existing matrix.
5. **Priced parcel plan.** Per format: kernel lines estimate,
   constant-table bytes, RP2040 flash/stack estimate from the
   design, gate sets (committed directed counts, exhaustive /
   worst-case / seeded volumes and their wall-time at measured
   host rates), negative controls, and the f16 -> f32 -> f64
   intra-parcel sequence with bundle-closure criteria. One
   number the owner can act on: total estimated parcel cost
   against the days left to 2026-11-04, with the stop rule if
   leg (c) cannot close.

## Output

Report verdict first: `PRICED - GO` with the plan, or
`PRICED - NO-GO` with the missing argument named. Every
load-bearing number carries its route (quoted source / your
script + log path). Ledger in house format. Times under load
are records, not performance claims.
