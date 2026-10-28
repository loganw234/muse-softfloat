# SF-2: Tier 2 expansion, second prefix

Status: DRAFT for planted verification, 2026-10-28.
Authorisation basis: owner's SF-2 decisions of 2026-10-28
(Sec. 9 below). Inputs (scratch studies, cited by report
hash in the lead ledger): `sf2-attribute`,
`sf2-algebraic`, `sf2-explog`, `sf2-augmented`. SF-0 and
SF-1 remain governing where this document does not extend
them; IEEE 754-2019 clauses are cited, standards text is
not reproduced.

## 1. What this authorises

Four steps, in order. Each family ships at binary16,
binary32 and binary64 or not at all (owner parity rule,
2026-10-27). Core-row claim token stays `C-754` (Tier 2);
no new claim token is introduced.

| Step | Content | New core rows |
|---|---|---|
| 1 | `roundTiesToAway` as fifth public rounding attribute | 0 (mode sweep over 255 attr rows) |
| 2 | `rSqrt`, `hypot` (Clause 9.2, algebraic) | 6 |
| 3 | `exp2`/`exp2m1`, `log2`/`log2p1` (Clause 9.2) | 12 |
| 4 | Augmented add/sub/mul (Clause 9.5) | 9 |

Inventory at closure: 822 + 27 = **849** instantiations.
Everything else from SF-1 Sec. 7 stays deferred by name:
`pown`/`compound`/`rootn` (behind their priced leg-(c)
spike), the remaining exp/log bundles (`exp`/`expm1`,
`exp10`/`exp10m1`, `log`/`logp1`, `log10`/`log10p1`),
`tanPi` and the inverse-Pi set, radian trig, hyperbolics,
`pow`/`powr` (refused), Clause 9.4 reductions (NO-GO,
nowhere in the library), dynamic rounding wrappers
(design confirmed, unearned), public `roundToOdd` (does
not exist in the tree; NO-GO as a promotion - it would be
built from scratch by a kernel that needs it).

## 2. Step 1 - fifth attribute (first, deliberately)

Study verdict PRICED-GO, ~11-17 h (14-20 with the MPFR
route). The pack is already correct under ties-to-away
(internal mode 4; proven by the study on 6.28M Berkeley
`roundTiesToAway` cases). The kernel bill is
`src/msf_string.c`, where mode 4 silently behaves as
toward-zero in `dec_round_inc` and `to_hex` (2 cases),
plus every mode-switch site the study enumerates. The
rest is evidence: runner mode token, per-family vectors
(Berkeley where it emits the mode, MPFR-RNDA/exact
elsewhere), and the attribute column of the inventory.
Stop rule (study): the public enum value must never ship
ahead of its vectors - today mode 4 is reachable through
the internal header and wrong in the string path, so this
step closes that trap before any new family is born
four-mode.

## 3. Step 2 - rSqrt and hypot

Study verdicts GO (unconditional): exact integer
decisions, no new pack entry points; `hypot` needs no new
width, `rSqrt` a 178-bit logical split compare over the
existing u128. Prototype evidence already measured:
binary16 `rSqrt` exhaustive vs MPFR (262,144 cases, 0
mismatches), `hypot` 153,600 decisions vs an independent
exact decider (0 disagreements, midpoint ties found and
decided). Parcels S (seam) + A1 (`rSqrt`, 16-24 h) + A2
(`hypot`, 12-20 h) from the study's split, five-mode from
birth. Two recorded fences: MPFR's `rSqrt(-0)` sign
disagrees with the clause cell (table-decided generation
required); `hypot`'s infinity-over-sNaN precedence cell
gets a parcel second read.

## 4. Step 3 - exp2/log2 pairs

Study verdicts PRICED-GO: `exp2`/`exp2m1` 55-75 h,
`log2`/`log2p1` 40-55 h. Margins were measured by MPFR
320-bit re-decision of the published worst-case inputs
(leg (a) authority, the SF-1 Sec. 8 settlement): plain
binary64 maxima 55.8-69.8 extra bits across the exp/log
programme, with the stage-3 kernel reach at 4.6x the
`exp2` demand. The Ziv three-stage pattern of
`src/msf_math.c` carries mechanically; genuinely new
parts are the generalised pack composition, wide division
(for `log2`), constant chains, exact exponent cuts and
tie tables - all per the spike's audit. Binary32 legs
are exhaustive MPFR differentials (priced), binary16
exhaustive by construction. Oracle fences from the
spike (F1: `cr_expm1/log1p` directed wrong on this host;
H1: 8 non-binary64 tokens in `exp10m1.wc`) do not touch
these two bundles; they bind the later ones.

## 5. Step 4 - augmented arithmetic

Owner-approved 2026-10-28: the interval workload's exact
stage is the named consumer. Measured remove-it test:
the frozen catalogue drops from 616,754 to 394,666
counted ops (exact stage -78.4%) with zero decision
changes. Design per the study: exact 128-bit window plus
verbatim far-operand pair, one internal
round-to-nearest-ties-to-zero pack mode, `aug_pair`
signature with a two-result runner line, ~7-10 h.
**Pin P1 (owner, 2026-10-28):** the exact-tiny-residual
underflow-flag cell takes the study's R2 reading
(underflow raised), confirmed by an independent second
read inside the parcel brief before kernel code. If the
second read cannot settle P1 to one reading, the parcel
stops and returns as an owner decision (study stop
condition).

## 6. Evidence and gates (unchanged discipline)

Per-parcel: brief, planted-copy Spark verification,
`smoke` then `standard` on the merge tree, board sampled
replay where the family has a board caller (Step 4: the
interval firmware path; Steps 1-3: sampled vector replay).
Vector authorities per the studies; any family whose
leg cannot close is refused, not downgraded (SF-0 rule).
Negative controls named in each brief, incl. one plant
that would pass if mode 4 still leaked toward-zero
semantics (Step 1) and one that swaps head/tail rounding
directions (Step 4).

## 7. Sequencing interactions

Step 1 strictly precedes Steps 2-4 (born five-mode).
Steps 2 and 3 share the table seam; the seam parcel
lands first and each bundle registers its own rows.
Step 4's runner change is its own seam. No step may
start while its predecessor's verification is open, and
the board lock discipline is unchanged.

## 8. Prices and stop rule

Step 1 ~14-20 h, Step 2 ~28-44 h + seam, Step 3
~95-130 h, Step 4 ~7-10 h (agent + verifier hours,
study-calibrated). Hard stop: any step not merge-ready
with its verifier closed by **2026-11-02** defers whole
(family parity), so the 2026-11-04 close keeps the video
and board sweeps uncontested.

## 9. Owner decisions (2026-10-28, recorded)

- Scope: the recommended prefix above (over "everything
  priced GO" and "algebraics only").
- Augmented: included, P1 pinned at the parcel brief
  (R2 + second read), interval workload named as the
  consumer.
- `pow`/`powr`, reductions, wrappers, `roundToOdd`:
  remain as Sec. 1 states.

## 10. Open items carried, by name

- Leg-(c) spike for `pown`/`compound`/`rootn` (8-16 h,
  priced, unauthorised).
- Float KissFFT configuration; three unenumerated clone
  boards (owner cables); video music (owner).
- F1 oracle-defect origin (Linux documented check is the
  priced decider; fences stand meanwhile).
