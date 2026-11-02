---
type: project
description: SF-2 input study - fifth rounding attribute priced GO, public roundToOdd NO-GO
---

# study-sf2-attribute (2026-10-28)

Full report: `scratch/sf2-attribute/report.md` (probe scripts +
`out/` logs beside it). No repo writes; muse-softfloat tree clean.

## Verdicts

- **roundTiesToAway as 5th public attribute: PRICED-GO, ~11-17 h,
  first SF-2 implementation parcel** (before algebraic/exp-log so
  they are born five-mode; SF-1 Sec.7's "after first math
  function" condition is satisfied by landed sinPi/cosPi).
  0 new rows; mode sweep over 255 attr rows (249 Tier 1 counted
  fresh + 6 Tier 2 trig).
- **Public roundToOdd: NO-GO. Internal: build only inside a
  parcel that proves it needs it (~2-3 h then). Never bundle.**

## Load-bearing corrections to the brief

- roundToOdd is **not** an existing internal pack mode and the
  trig kernel does not use it: zero `odd` hits in src/include;
  msf_math.c decides via interval endpoints packed under the
  caller's rm (trig_decide). It would be built from scratch.
- Runner source is tests/runner.c (binary msf_runner.exe), and it
  (plus board harness, dispatch, berkeley_ingest) already speaks
  the `ta` token.

## Measured headline facts

- Berkeley level-1 `-rnear_maxMag` replayed on the **current
  kernel**: 6,275,532/6,275,532 PASS incl. flags (f16/f32/f64
  add/mul/div-class, sqrt, mulAdd, format+int conversions). The
  pack (round_inc guard arm + overflow arm + unbounded tininess
  judge) is already ties-to-away-correct; FMA jam included.
- **The one real kernel delta is msf_string.c**: `dec_round_inc`
  and the to_hex precision switch have no TA case, so rm=4 today
  silently means toward-zero there (probed: to_decimal(2.5,prec1)
  gives 2e+00 not 3e+00). Two one-case fixes. from_decimal
  beyond-H needs only the dec case (5.12.2 two-step is the
  project's stated semantics; direct-vs-two-step trap analysed
  in report). Zero-sign rule and integer helpers already correct.
- MPFR: raw MPFR_RNDNA is incoherent by execution (away-always
  in mpfr_set, ties-to-even in mpfr_subnormalize; header says
  DON'T USE it). MPFR_RNDA is away-always, not ta. The sanctioned
  mpfr_round_nearest_away macro works but only inside the
  oracle-0b narrowed emin/emax context (aborts at default emin)
  and is unproven as a recipe — and unnecessary: Berkeley
  decides its 39 rows, exact-py refs the 216 mpfr-exact rows
  (refs ta-ready except xf/str, 5 one-branch fixes total).
- Berkeley gaps by name: f64_scaleB and Clause 9.2 functions are
  absent from the oracle (invalid argument) — same as other
  modes. CORE-MATH cannot be asked for ta here (host fenv has
  exactly 4 FE modes).
- sinPi/cosPi + sqrt have **no exact ties** (Niven / midpoint-LSB
  arguments, flagged for second read) => ta==te bit+flag; gate =
  relabeled te replay + theorem note. Same split makes SF-2
  exp/log + rSqrt/rootn born-five-mode nearly free, while
  pown/compound/reductions owe real ta sets.
- Volumes: smoke 146,442 lines; ta at mean-mode volume +23,938
  (smoke x1.164, standard x1.020; standard extras mode-free or
  already 5-mode); verify wall +<0.1 s (~360k lines/s measured).
  Tie density in Berkeley level-1: f64_add 592/46,464 differ
  te-vs-ta, sqrt 0 — directed tie-rich pools are the gate.
- roundToOdd Berkeley semantics measured for the shelf:
  overflow delivers largest finite (not inf) with ovf+inexact;
  exact-py decider agreed on 43,050 decided add/sqrt lines.

## Stop conditions recorded in report

No enum-first shipping if any out-of-pack rounding site beyond
the two named is found; Niven second-read failure reprices trig
(+MPFR-RNA battery ~3 h); no carving out from_decimal; Berkeley
level-2 fma volume may need a lead ruling (level-1 + directed).

## Unprobed / unresolved

- Berkeley level-2 ta (only level-1 executed per function;
  level-2 priced, not run, mulAdd volume especially).
- Berkeley ta for the remaining homogeneous functions beyond the
  8 replayed (sub/div/etc. accepted-flag probed via argument
  acceptance, not full replay).
- MPFR-RNA macro as a proven narrowing recipe (spot cases pass;
  boundary battery not run — priced ~3 h, skippable).
- CORE-MATH ta (unaskable via host fenv; not executed).
- Tininess-under-round-to-odd flag behaviour (no underflow
  combos in decided sample).
- Niven/transcendence tie-absence claims are [R]/[A] pending
  parcel second-read, not executed evidence.
