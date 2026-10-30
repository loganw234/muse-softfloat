FAIL

Verifier: verifier-sf2. Copy: `worktrees/verify-sf2` (SF-2.md as delivered).
Authorities read in full: the four input studies
(`scratch/sf2-{attribute,algebraic,explog,augmented}/report.md`), the copy's
`docs/studies/SF-0.md` (skimmed for claim tokens/refusals),
`docs/studies/SF-1.md` (Secs. 7/8/10/11/14 read), `docs/COVERAGE.tsv`
(recomputed), `src/msf_internal.h`, `src/msf_roundpack.c`,
`src/msf_string.c` (dec_round_inc, to_hex_generic), `src/msf_math.c`
(trig_decide presence), `tests/VECTORS.md` (ta token), `tools/run.sh`
(presence). Nothing with `cft` in its name opened/searched/listed.
Delivery branch, other worktrees, keys, `scratch/lead/`, other ledger
files: not consulted. No repo files modified.

## Recomputed arithmetic (all hold)

- Baseline: copy COVERAGE.tsv carries 822 rows with status=implemented
  (783 tier 1 + 39 tier 2, recomputed by column split; 1 header line is
  the only other non-comment line). SF-2 Sec.1 "822" correct.
- Step rows: Step 1 = 0 new rows (mode sweep over 255 attr rows;
  recomputed 255 attr rows, all implemented, in the copy) — correct.
  Step 2 = rSqrt+hypot x 3 formats = 6 — correct (algebraic Sec.7.2,
  15-row full bundle minus deferred pown/compound/rootn 9).
  Step 3 = 2 bundles x 2 names x 3 formats = 12 — correct (explog Sec.7).
  Step 4 = 3 ops x 3 formats = 9 — correct (augmented Sec.0/1.1).
- Closure 822 + (0+6+12+9=27) = 855 — correct.
- Prices: Step 1 study band 11-17 h (14-20 with MPFR route, attribute
  Sec.4); Step 2 = A1 16-24 + A2 12-20 = 28-44 + seam S 6-10
  (algebraic Sec.8) — SF-2 "28-44 h + seam" correct; Step 3 = 55-75 +
  40-55 = 95-130 (explog Sec.7 rows 1-2) — correct; Step 4 = 7-10 h
  (augmented Sec.0) — correct.

## Findings (disconfirm-only)

### F1. SF-2 Sec.5 interval catalogue number contradicts the study (wrong by 200,000; breaks its own percentage)

- SF-2 Sec.5: "the frozen catalogue drops from 616,754 to 594,666
  counted ops (exact stage -78.4%) with zero decision changes".
- Augmented study Sec.2 table and Sec.5 appendix: baseline 616,754,
  variant **394,666** (build/var-{r2,r1,r1adapt}-out.txt), delta
  -222,088 (-36.0%); stage 3: 283,314 -> 61,226 = -222,088 (-78.4%).
- 616,754 - 594,666 = 22,088, which is neither -222,088 nor -78.4% of
  anything cited. The study's 394,666 reproduces both figures exactly.
  SF-2's "594,666" is a wrong digit (5 for 3) that invalidates the
  sentence's own arithmetic. Baseline 616,754 and "zero decision
  changes" verified correct against the study.

### F2. SF-2 Sec.5 mislabels the P1 pin (R1 vs R2); Sec.5 and Sec.9 contradict each other

- SF-2 Sec.5: "Pin P1 (owner, 2026-10-28): the exact-tiny-residual
  underflow-flag cell takes the study's R1 reading (underflow not
  raised)".
- Augmented study Sec.1.3: **R1** = the flag-raising inversion (exact
  tiny residual raises underflow); **R2** (recommended) = no flag
  raised under default handling. "Underflow not raised" is R2, not R1.
- SF-2 Sec.9 correctly records "(R2 + second read)". So Sec.5 and Sec.9
  direct the parcel to opposite labels for a cell whose two readings
  have opposite observable flag semantics. The parenthetical
  description in Sec.5 matches the study recommendation; the label
  does not. Fix: Sec.5 should read R2.

### F3. SF-2 Sec.2 code-state claim contradicts the copy's src (internal mode 4 already exists)

- SF-2 Sec.2: "The pack has no ties-to-away mode yet; one is added
  (internal mode 4; ...)".
- Copy's src: `msf_internal.h:19` already defines
  `MSF_IROUND_TIES_TO_AWAY = 4`; `msf_roundpack.c:58-59` already
  carries the ties-to-away arm (plus line 118 overflow arm). The study
  (attribute Sec.1.1, heading "Already done (the seam exists)") prices
  only the public enum value, the two string-path cases, seam,
  generators, and vectors — no pack-mode addition.
- What is true and verified: mode 4 exists internally and is pack-
  correct; it is missing from the public enum and wrong (silent
  toward-zero) in the two string-path switches. SF-2's phrasing sends
  a parcel to re-add what exists. Fix: "the public enum value is
  added (internal mode 4 already exists and is pack-correct)".

### F4. SF-2 Sec.2 vector line drops the study's MPFR-RNA fence (wrong-oracle risk)

- SF-2 Sec.2: "per-family vectors (Berkeley where it emits the mode,
  MPFR-RNDA/exact elsewhere)".
- Attribute study Sec.2.2: raw `MPFR_RNDNA` as a general mode is
  "DO NOT USE" (measured incoherent: away-always in `mpfr_set`
  narrowing, ties-to-even in `mpfr_subnormalize`); the sanctioned
  `mpfr_round_nearest_away` macro works only with narrowed emin/emax
  set first (aborts at default emin) and needs a boundary battery
  cross-decided by exact-py before trust; trig/sqrt need no MPFR ta
  at all (te relabel + Niven theorem note, with a second-read stop
  condition if Niven fails).
- SF-2's bare "MPFR-RNDA" names the exact route the study forbids
  without stating any of its three fences, and never mentions the
  trig/sqrt relabel or the Niven second-read stop condition (study
  stop condition 2). A parcel brief written from SF-2 Sec.2 alone
  would invent the wrong oracle pin. Fix: name the relabel route for
  trig/sqrt, the exact-py decider for the rest, and the RNDNA
  prohibition with its emin/battery fences.

### F5 (minor). SF-2 Sec.4 misattributes the 4.6x headroom denominator

- SF-2 Sec.4: "the stage-3 kernel reach at 4.6x the `exp2` demand".
- Explog Sec.6.1: stage-3 reach ~318 bits is "4.6x the measured
  maximum", i.e. vs the programme-wide plain max (log10 69.77;
  318/69.77 = 4.56). Against exp2's own plain max (60.54) the ratio
  is ~5.3x. Either the number or the denominator is wrong; the
  leg-(c) margin argument itself is unaffected.
- Also Sec.4's "plain binary64 maxima 55.8-69.8" is the RN-max range
  (55.78-69.77) rounded; fine, recorded here to show it was checked.

## Verified-correct (probe record, no action)

- Measured numbers: 6.28M Berkeley ta cases (study 6,275,532 PASS,
  attribute Sec.1.1); rSqrt binary16 exhaustive 262,144 x 4 modes,
  0 mismatches, 4 fenced -0 cases (algebraic Sec.6.1); hypot 153,600
  decisions, 0 disagreements, 2 midpoint ties (algebraic Sec.6.4);
  rSqrt 178-bit logical split compare (algebraic Sec.3.1, 3p+19);
  hypot no-new-width anchored-sum design (algebraic Sec.3.2).
- Fences carried: rSqrt(-0) table-decided generation (algebraic
  Sec.5.1/6.1, prototype -inf vs MPFR +inf); hypot inf-over-sNaN
  second read (algebraic Sec.5.2 [2R]); F1 scoped to exp/expm1 and
  log/logp1 bundles and H1 to exp10m1 (explog Sec.5.2, Sec.1/H1) —
  neither touches exp2/exp2m1 + log2/log2p1, except one measured
  exp2m1 RN subnormal-corner pre-screen cell (explog Sec.5.1, ~1 per
  1e4 false alarms) which SF-2's blanket "do not touch" overstates
  slightly (see U7).
- roundToOdd: zero hits for "odd" in copy `src/` (searched); SF-2
  "does not exist in the tree; NO-GO as a promotion" matches the
  study (attribute Sec.0 correction 1, Sec.3).
- String-path trap: `dec_round_inc` (msf_string.c:411-427) and
  `to_hex_generic` (1151-1164) have no TA case -> silent toward-zero
  — matches study (attribute Sec.1.2) and SF-2 Sec.2 "(2 cases)".
- Decision fidelity: deferral list (pown/compound/rootn behind leg-c
  spike; remaining exp/log bundles; tanPi + inverse-Pi; radian trig;
  hyperbolics; pow/powr; reductions NO-GO nowhere; wrappers design-
  confirmed unearned) matches SF-1 Sec.7 dispositions and the
  studies' verdicts, with the Sec.1 "stays deferred by name" guard.
  Augmented inclusion with the interval exact stage as named consumer
  satisfies the study's entry condition letter (augmented Sec.0:
  "authorise only bundled with a named exact-stage workload").
- Claim token C-754, no new token: matches SF-1 Sec.8 closed set and
  augmented Sec.1.6 (`fixed` token is a rounding-column value, not a
  claim token). Parity rule (all families x3 formats) observed.
- Seam/parcel split S + A1 (16-24 h) + A2 (12-20 h), five-mode-first
  sequencing, aug_pair two-result runner line, P1 second-read stop
  rule, leg-(c) spike 8-16 h open item, F1 Linux-check open item,
  three unenumerated clone boards (SF-1 Sec.2/9): all traced.

## Under-specification list (notes, not blockers — parcel would have to guess)

- U1. Exp near-1 directed pocket (extra 105.58, explog Sec.2.1/6):
  study says "price both, choose in the parcel" (m1-composition path
  vs stage-2 reliance). SF-2 Sec.4 does not pin the choice.
- U2. Step 4 pins P4 (rounding-column token `fixed` vs
  named/none) and P5 (new internal RTTZ mode value coordination)
  from augmented Sec.1.5/1.6 are not mentioned in SF-2; the parcel
  brief must settle both.
- U3. Step 2 table tokens (`math_bin`/`math_int`, API names
  `r_sqrt`/..., wave number; study proposes wave 5 as lead/owner pin,
  algebraic Sec.7.1/7.2) are not pinned in SF-2.
- U4. Step 1 trig/sqrt ta==te relabel + Niven-theorem second-read
  dependency (attribute Sec.2.2, stop condition 2) is absent from
  SF-2 Sec.2 (see F4).
- U5. Step 3 per-function exact/tie-branch enumeration + inexact-flag
  proof obligation (explog Sec.2.3) is not stated in SF-2 Sec.4.
- U6. SF-2 Sec.8 prices Step 1 at ~14-20 h without naming the
  with-MPFR-route assumption (base band 11-17 h, attribute Sec.4).
- U7. "pow/powr (deferred, priced GO)" (SF-2 Sec.1): no pow/powr
  price or GO verdict exists in the four input studies (algebraic
  deliberately excludes pow, Sec.6.5; explog is exp/log only).
  Deferral itself matches SF-1 Sec.7 ("refused in any first
  sequence"); the "priced GO" gloss is unsourced from my
  authorities — possibly from the Clause 9 survey, which I may not
  consult.
- U8. Hard-stop dates (2026-11-02 verifier-close, 2026-11-04 close,
  Sec.8) and the "video and board sweeps" dependency are owner pins
  with no study source; unverifiable here by design.

## Not-done list (verification limits)

- N1. Margin maxima and probe outcomes (MPFR re-decisions, Berkeley
  replays, prototype cross-checks) were checked by transcription
  against the study tables, not by re-execution; no MPFR/Berkeley
  runs were made in this verification.
- N2. Board ABI note (`msf64_pair_t` hidden-pointer return, SF-2
  Sec.5 via augmented Sec.1.6) not verified against the toolchain.
- N3. Study-internal derivations (Niven/Lindemann-Weierstrass/
  Gelfond-Schneider invocations, odd-part tie characterisation,
  span-lemma sketch) taken as stated; proofs belong to parcel
  second reads.
- N4. SF-0 consulted only for claim/refusal context; full SF-0
  re-verification out of scope.
