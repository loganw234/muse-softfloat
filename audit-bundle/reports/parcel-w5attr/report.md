READY

# parcel-w5attr report: roundTiesToAway, fifth public rounding attribute (SF-2 Step 1)

Branch `wave5-attr` in `worktrees/w5-attr`, base `889ec2e`.
Brief `ledger/briefs/w5-attr.md` obeyed; governing study
`scratch/sf2-attribute/report.md` + SF-2 Secs. 2,6-9. Design
entry was written to `ledger/parcel-w5attr.md` before any code
change. All gates below ran from script files in
`scratch/parcel-w5attr/` (Git Bash, `MSF_PYTHON` pinned to the
workspace `.venv`, `TMPDIR/TMP/TEMP` in `scratch/parcel-w5attr/tmp`):
`01_regen.sh`, `02_smoke_standard.sh`,
`03_unit_determinism_audit.sh`, `04_berkeley.sh`,
`05_exhaustive_controls.sh`, `05b_mutants.sh`,
`06_sqrt_relabel.sh` (+ `counts.py`, `counts_ops.py`,
`check_attr_rows.py`, `string_ta_unit.c`,
`make_trig_relabel_f16.py`, `make_controls.py`,
`make_sqrt_relabel.py`). Logs in `scratch/parcel-w5attr/out/`.
Raw MPFR `RNDNA` was not used anywhere; no generator needed
`mpfr_round_nearest_away` (Berkeley + exact-py decide all ta,
per study Sec. 2.2 consequence). Nothing with `cft` in its
name was opened, searched, or listed. No board work.

## What changed (owned files only)

- Kernel (exactly the study's two sites, nothing else in `src/`):
  `src/msf_string.c` `dec_round_inc` gains
  `case MSF_IROUND_TIES_TO_AWAY: return gt_half || eq_half;`;
  `to_hex_generic` precision switch gains
  `case MSF_IROUND_TIES_TO_AWAY: inc = dropped >= half;`.
- Seam: `tools/gen_tables.py` prelude gains
  `MSF_ROUND_TIES_TO_AWAY = 4` with the named-forms-only
  sentence rewritten; `include/muse_softfloat.h` regenerated
  (that enum block is the only header diff).
  `docs/COVERAGE.tsv`, `src/msf_formats.h`,
  `tests/msf_dispatch.h` regenerate byte-identical (no diff,
  0 new rows, inventory still 783 + 39). `tests/VECTORS.md`
  token note + relabel provenance row. `tools/run.sh` gains
  control `wrong-rounding-mode-te-ta` (te<->ta swap on
  `arith-f32.vec`, watched refused). `docs/metrics/briefs.jsonl`
  gains my row.
- Generators to five modes: `gen_vectors_f16.py`,
  `gen_vectors_f32.py` (`RMS4` + ta, refs already armed);
  `gen_vectors_f64.py` (`RMS` + ta, pool modulo `%4` ->
  `%len(RMS)`); `gen_vectors_xf.py` (+ ta, `_round_q` and
  `to_inf` ta arms, `%4` -> `%len(RMS4)` in the trap cycles,
  `exhaustive_f16` sqrt modes gain ta, directed byte budget
  1,000,000 -> 1,400,000 for the five-mode growth);
  `gen_vectors_str.py` (+ ta with **four** reference arms
  fixed - see study corrections); `gen_vectors_trig.py`
  (relabel route, below). `gen_vectors.py` was already
  five-mode; `berkeley_ingest.py` already mapped ta;
  `gen_vectors_tier2.py` has no rounding attribute.
- Tie-rich directed design (new, per brief item 3): each
  arith/fma/conv generator gained a searched directed tie
  section - dyadic operands built so exact results land on
  destination midpoints (even significands, half-ulps,
  subnormal multiples, FMA jam at wide binades, int->float
  midpoint integers, format-conversion cut ties) - keeping
  only cases where the exact reference's te and ta outcomes
  actually differ, emitted decided in all five modes with a
  generation-time assert on the homogeneous combos. The str
  generator gained to_decimal digit-tie, to_hex half-tie,
  from_hex per-format binary-tie and from_decimal beyond-H
  digit-tie sections (the study's plant shapes 1-2), and
  scaleB gained subnormal-delivery tie constructions plus
  `ta` in two directed mode loops that still enumerated only
  `("tz","tp","tn")`.

## Headline counts (committed vectors, `counts.py`/`counts_ops.py`)

Base -> now: counted lines 146,442 -> 171,423; `ta` lines
3,720 (internal pack only) -> 21,858, i.e. directed-mode
volume (tz = 21,883). Mode census now: te 36,363, tz 21,883,
tp 21,881, tn 22,469, ta 21,858, rm-less 46,969.
ta-vs-te **tie witnesses** (same op+operands, different
result/flags): 2,143 committed lines.
Cross-check (`check_attr_rows.py`): `docs/COVERAGE.tsv` has
255 `rounding=attr` rows; distinct public ops carrying a
committed ta line = 255; **0 attr rows without a ta line, 0
extra** (+3 internal.pack ops).

## Per-family ta evidence (committed counts + gates)

ta/wit = committed ta lines / of those, lines whose expected
result or flags differ from the same-operand te line.
Decider = authority for the committed ta expectations.

| family | rows | ta | wit | decider | extra gate evidence |
|---|---|---|---|---|---|
| add/sub/mul/div (homog+cross) | 108 | 2,236 | 298 | exact-py (Berkeley homog) | Berkeley L1: 12 fns x 46,464 |
| fma | 81 | 706 | 201 | exact-py | Berkeley L1: 3 x 6,133,248 mulAdd |
| sqrt | 9 | 405 | 33 | exact-py (decided; see theorems) | Berkeley L1 408/600/768; f16 exhaustive 327,680 (5-mode); xf exhaustive sqrt |
| convertFormat | 9 | 402 | 54 | exact-py | Berkeley L1: 6 ordered pairs |
| convertFromInt | 24 | 411 | 62 | exact-py | Berkeley L1: 12 int->float (372/756 each) |
| scaleB | 3 | 306 | 33 | exact-py | f16 exhaustive (in ex-rint stream; ta present) |
| roundToIntegralExact | 3 | 115 | 15 | exact-py | f16 exhaustive 65,536/inputs sweep in 5 modes |
| from_decimal | 3 | 840 | 181 | exact-py str | bulk 20,000 (4,057 ta); beyond-H ties included |
| to_decimal | 3 | 1,140 | 924 | exact-py str | bulk 20,000 (4,039 ta); unit probe |
| from_hex | 3 | 357 | 76 | exact-py str | bulk 20,000 (4,072 ta) |
| to_hex | 3 | 330 | 114 | exact-py str | bulk 20,000 (3,902 ta); unit probe |
| sinPi/cosPi | 6 | 10,873 | 0 | **relabeled te** (theorem) | f16 exhaustive relabel 131,072 PASS |
| internal.pack{16,32,64} | - | 3,718 | 152 | exact-py (pre-existing) | pack sweep 200,000 in `standard` |

Named already-public ties-to-away forms were cross-checked
in the Berkeley replay (`f*_to_{i,ui}{32,64}`,
`f*_roundToInt` with `--rm ta`: 15 fns, all PASS).

Ops with ta lines but **zero** tie witnesses: 43, every one
provably tie-free - (a) sinPi/cosPi (6, Niven below);
(b) homogeneous and widening sqrt (6, bit-count below);
(c) exact/widening conversions and small-integer sources
(20: source significand/int width <= dest precision, no
rounding occurs); (d) wide-dest arithmetic on narrow
sources whose exact result fits the dest (add/sub/mul, 6);
(e) narrow-source div into a wider dest (6: a dyadic
quotient's odd numerator is bounded by the source
significand - <= 24 bits vs the >= dest-p+1 bits a normal
midpoint needs - and the quotient range either never
reaches dest subnormals or reaches them only at exponents
that make the midpoint coefficient even). Where ties are
constructible but were missing, I added decided vectors
instead of arguing: cross-format FMA jam ties, scaleB
subnormal ties, narrowing sqrt ties (below).

## Relabeled vs decided split

| class | lines | where |
|---|---|---|
| decided ta, committed | 10,985 | exact-py generator refs (7,267 public + 3,718 internal.pack) |
| relabeled ta, committed | 10,873 | trig only: `mpfr640-trig:<fam>-ta-relabel` (te expectation, tag + header state the relabel) |
| decided ta, gate-only | 19,322,038 | Berkeley L1 18,978,288 + f16-exhaustive ta 196,608 + xf-exhaustive ta 131,072 + str bulk ta 16,070 |
| relabeled ta, gate-only | 131,344 | trig f16 exhaustive 131,072 + sqrt theorem-scope replay 272 |

Relabeled lines are never presented as independently
decided: the trig provenance tag itself says `-ta-relabel`,
each trig file header says the same, `tests/VECTORS.md`
carries the row, and committed sqrt ta lines are decided by
the exact references (sqrt appears only in the decided
column; the sqrt relabel files are scratch gates).

## Theorem notes (second read, mine; study stop condition 2)

**sinPi/cosPi - no exact ties; ta == te in bits and flags.**
A ta/te difference requires the exact result to be a
rounding midpoint: the midpoint of two adjacent destination
values, or of two adjacent values on the
unbounded-exponent precision-p grid the tininess judge uses.
Every such midpoint is a dyadic rational (an odd multiple of
half the local quantum). Niven's theorem: if `t` is rational
and `sin(pi*t)` is rational, then `sin(pi*t)` is in
{0, +-1/2, +-1}. A finite binary input `x` is a dyadic
rational, so for sinPi apply with `t = x`; for cosPi use
`cos(pi*x) = sin(pi*(1/2 - x))` and `1/2 - x` is rational.
Hence the exact result is either irrational - not a
midpoint, the tie branch is unreachable, and te/ta agree on
value and flags (inexact in both; the pack's tininess judge
rounds on the same class of dyadic grids, so underflow
agrees too; overflow impossible, |result| <= 1) - or it is
in {0, +-1/2, +-1}. Each of those is a *grid point* in every
binary format (one significand bit), and a grid point is
never a midpoint (midpoints lie strictly between grid
points, including at binade boundaries and on the subnormal
grid, where the neighbours of 0 are +-minsubnormal and the
midpoint is +-minsubnormal/2, not 0). Such results are
delivered exactly, including the settled 9.2.1 specials
(integer/half-integer inputs, whose zero signs are
table-fixed in all modes). NaN/infinity inputs are
mode-independent table cases. Sharper still: +-1/2 in fact
never occurs for dyadic `x` (it needs `x = +-1/6`-class or
`+-1/3`-class arguments), but the proof does not need that.
Conclusion: the second read **holds**; no MPFR-RNA decider
battery is needed. Gate shape as directed: te sets
relabeled `ta` and replayed against the kernel (committed
sets, incl. hardest-known excerpts, + the exhaustive
binary16 stream of all 65,536 encodings x both functions,
131,072 cases PASS through the real runner under rm=ta).

**sqrt - homogeneous and widening: no ties. Narrowing
cross-format: ties EXIST (study statement needs this
scope).** Classical part: a normal-range midpoint has an
odd (p_dest+1)-bit significand `m` (also at binade
boundaries). If `sqrt(x) = m * 2^t` exactly, then in lowest
terms `x = m^2 * 2^(2t)` with `m^2` odd on >= 2*p_dest+1
bits, while a source operand's odd significand has at most
p_src bits. Homogeneous (p_src = p_dest) and the widening
pairs here (p_src < 2*p_dest+1 always suffices for the
narrow sources into f64/f32) cannot tie. Subnormal-grid
midpoints `m = odd_L * 2^(emin-p_dest)`: bit count needs
2L-1 <= p_src, so `m < 2^(emin-(p_dest-1)/2)`-class bounds
force `x = m^2` below the source's smallest positive value
for homogeneous/widening pairs - impossible. **But** for a
wider source the count no longer excludes ties:
`x = (1 + 2^-11)^2` is exact in binary32 (23-bit odd
significand) and `msf16_sqrt_f32(x)` is exactly the binary16
midpoint between 1 and 1+2^-10 - te and ta differ. The
study's Sec. 2.2 sentence "sqrt's 9 rows are ta==te by
proof" is therefore over-broad for the three narrowing rows
(msf16_sqrt_f32, msf16_sqrt_f64, msf32_sqrt_f64). This does
**not** engage stop condition 2 (that is the Niven read) and
nothing in the committed sets relies on the over-broad
claim: all sqrt ta lines are decided by the exact
references. I added directed narrowing-sqrt tie vectors
(x = m^2 constructions incl. dest-subnormal midpoints;
33 witnesses now committed) and split the scratch relabel
gate: homogeneous+widening relabel replay 272/272 PASS,
while the full-file relabel replay (416 lines) fails on
**exactly** the 33 narrowing tie lines - the two counts
cross-corroborate.

## Study corrections recorded (evidence over summary)

1. `gen_vectors_str.py` has **four** ta-less reference arms,
   not three: `_round_ratio_to_int`, `pack_ratio` to_inf,
   `dec_round_inc`, and `to_hex_ref` (line ~514, missed in
   the study's list). All four fixed. Generator-side only.
2. sqrt no-ties needs homogeneous/widening scope (above).
3. Study stop condition (1) did **not** trigger: I audited
   every mode switch in `src/` (grep of `MSF_IROUND`,
   `switch (rm)`, `rm ==` into `out/audit_iround.log`):
   pack `round_inc` + overflow (ta armed), per-format
   integer helpers (ta armed), exact-zero sign tests (only
   compare toward-negative - right for ta), `msf_math.c`
   (passes rm through, decides by monotone endpoint pack),
   and the two `msf_string.c` switches (now ta-armed). No
   third out-of-pack rounding site exists; 27M+ executed ta
   cases found none.

## Gates run (all on the final tree unless named)

- `tools/run.sh smoke` PASS (171,423 committed cases, all
  negative controls refused incl. the new
  `wrong-rounding-mode-te-ta`); `tools/run.sh standard`
  PASS (+ f16-exhaustive 917,504 + pack64 sweep 200,000;
  unit PASS). `out/02_final2.log`, `out/{smoke,standard}.log`.
- String unit probe `string_ta_unit.c`: 13/13 OK - both
  study probe cases now give the ta answers
  (to_decimal 2.5@prec1 -> `3e+00`, to_hex 1+2^-9@prec2 ->
  `0x1.01p+0`), both signs, below-half non-increment
  discriminators, one beyond-H digit tie, pack-path
  controls. `out/string_ta_unit.log`.
- Berkeley `-rnear_maxMag` level-1: **51 functions,
  18,978,288 cases, flags exact, all PASS** through the
  runner (18 arith, 6 format conversions, 12 int->float,
  12 float->int named, 3 roundToInt named).
  `out/berkeley_summary.log`, `out/berk/*.verify.log`.
- Binary16 five-mode exhaustive streams:
  `gen_vectors_f16.py exhaustive` 6,947,324 PASS
  (ex-sqrt = 327,680 = 65,536x5 exactly as the study
  priced; ta lines: rint/scale stream 131,072 + sqrt
  65,536); `gen_vectors_xf.py exhaustive-f16` 655,360 PASS
  (131,072 ta); trig f16 relabel 131,072 PASS;
  str bulk x4 80,000 PASS. `out/exh/*.log`.
- Negative controls, watched failing in scratch:
  (a) `dec_round_inc` mutant (ta arm deleted, scratch
  build): FAIL with 1,044 wrong ta digit-tie lines on the
  decimal files, PASS on to-hex/arith (isolation checked);
  (a2) `to_hex` mutant: 166 fails on to-hex-str, PASS on
  decimal files; (b) te/ta swap on arith-f32: FAIL
  (106 lines), also refused in `smoke`;
  (c) one flipped relabeled trig expectation: FAIL
  (exactly 1 line). `out/ctrl/*.log`, `out/05*_run.log`.
- Determinism: two full regenerations of header/coverage
  and every touched vector file are byte-identical to each
  other and to the committed files. `out/03_final2.log`.
- Attr-row cross-check: 255/255 attr rows carry committed
  ta lines. `out/check_attr_rows.log`.

## Not done / for the lead at merge

- **Claim wording restatement (lead-owned files, not
  touched):** README, `docs/RECORD.md` (~line 65), and
  BOARD docs still say "four rounding attributes" - restate
  to the study's landed claim (five attributes; 783+39
  headline unchanged; per-row tokens extend at gate close).
- Board sampled replay incl. ta lines (brief: lead replays
  after merge; harness already parses `ta`). Not run.
- Berkeley level-2: not run (brief specifies level-1;
  study stop condition 3 not engaged).
- `traps-xf.vec` carries only 5 ta lines: the trap search
  assigns modes by cycle (`%len(RMS4)` now reaches ta) and
  the kept ta lines are decided, but volume there is thin
  by the trap-search quota, not a directed ta design.
  The cross-format trap zone is additionally covered by the
  decided tie sections in arith-xf/fma-sqrt-xf (91/115
  witnesses) and Berkeley homogeneous replay.
- Verifier parcel (planted copies) is separate work, as in
  every wave so far.
- Time: this parcel ran well inside its 600-min box; no
  480-min what-is-left note was needed.
