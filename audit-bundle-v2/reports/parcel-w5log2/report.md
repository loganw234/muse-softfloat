READY

# parcel-w5log2 report: log2/log2p1 (SF-2 Step 3b)

Branch wave5-log2, worktree worktrees/w5-log2, base 54ac1bb.
Design entry (written before kernel code, exact/tie
branches + inexact obligations + Ek lines enumerated):
ledger/parcel-w5log2.md.

## Inventory as printed by the runner tooling

tools/gen_tables.py prints: tier1 783 implemented of 783;
tier2 57 implemented of 57; instantiations 840
(implemented 840). Smoke inventory line exactly: "tier2
57 implemented, 0 planned, 57 registered; bad rows 0" -
Tier 2 stays 57 registered, goes 51 -> 57 implemented,
0 planned, as the brief states.

## Registration

tables/implemented.tsv: +msf{16,32,64}_log2,
+msf{16,32,64}_log2p1 at wave 5 (operations rows and
run.sh totals/VECS were already Step-3-shaped from 3a;
run.sh untouched, not owned). Regen: gen_tables.py twice
byte-stable (4 generated files), gen_explog_tables.py
twice byte-identical with the header diff additions-only
(exp entries/Ek unchanged), vector generator twice
byte-identical with Step-3a exp lines byte-prefix
preserved in all three .vec files.

## Kernel (src/msf_math.c log section)

Per spike Sec. 6.2: w (x itself, or exact wide 1+x,
span <= 1075 bits in a 40-limb big) = 2^k*mm; recentre
by the exact integer compare Wint^2 vs 2^(2top+1);
s = (mm-1)/(mm+1) by the new floor-exact bit-by-bit
wf_div from separately normalized NUM/DEN bigs - their
wf truncations are the charged s-division sticky Ek
line (2eps per conversion under the shipped bit-length
big_top_bit convention, probe-verified; identically
zero for log2); atanh series t = (2/ln2)*s*A(s^2);
endpoints k+(t+-Ek) materialised exactly at pack scale
(integer composition decides the attractor tail;
log2(2^k) = k exact by construction incl. subnormal
x); log2p1 tiny path floor(log2|x|) <= -9 by relative
x*(1/ln2)*B(x); pole at -1 exact. Ziv stages 160/256/384
shared with the exp/trig sections. Generator-proven:
EK_LOG {146,242,370} (terms {35,54,79}), EK_TINY
{147,243,371} (terms {23,35,51}); constants bracket-
floored 1/ln2, 2/ln2 (ln2 bracket diff ~2^-702.3),
exact 1/(2j+1) / 1/(j+1) floors; no decimal literals.

Specials as shipped (Clause 9.2, S1 extracts Table 9.1
lines 2657-2670 + 9.2.1 lines 2738, 2812-2814): NaN
matrix wholesale; log2: (+-0)->-inf+divideByZero,
(1)->+0, (+inf)->+inf, x<0 (incl. -inf)->default
qNaN+invalid; log2p1: (+-0)->+-0, (-1)->-inf+
divideByZero, (+inf)->+inf, x<-1->default qNaN+invalid.
Exact branches = powers of two only (log2 of a dyadic
is an integer or irrational - tie set EMPTY by proof,
design Sec. 3); every kernel result inexact by proof;
underflow is the pack's judgement on exact endpoints.

## Evidence (per-leg counts)

Decider: tests/explog_decider.c EXTENDED (fn 2/3;
independent settled table for specials/domain/poles/
powers - log2 powers by sig test, log2p1 powers by
exact common-exponent integer test; MPFR adaptive
bracket on mpfr_log2/mpfr_log2p1, five-mode grid
narrow, no raw RNDNA, stride audits vs mpfr_get_flt/
get_d). No foreign oracle executed anywhere. All legs
bits+flags, five modes; any stage-3 final-undecided
would be a STOP - none occurred anywhere.

- binary16 exhaustive (all 4 explog functions; exp pair
  re-swept as harness regression): 1,310,720 checks,
  mismatches 0, undecided 0, final_undecided 0, stage
  hits 783,325/0/0. PASS.
- binary64 worst-case 100% (fetch record in ledger:
  worst.html sha256 5941af17..., pin 3b2163bb...;
  log2.wc 729,771 B sha256 13f1db9d..., log2p1.wc
  28,782,572 B sha256 09c18f5e..., scratch only):
  log2: lines 33,279, tokens 33,248, finite 33,242
  occurrences = 33,238 unique encodings (spike census
  33,237 unique values + the -0 encoding, both zero
  encodings itemized in the dump), nonfinite skipped 4,
  unparsed 2, inexact tokens 0; checks 166,210 PASS.
  log2p1: lines 1,263,840, tokens 1,263,804, finite
  1,263,798 = 1,263,797 unique (census 1,263,796 + -0);
  checks 6,318,990 PASS. Stage 1 decided every wc
  input; decider escalations 0 + 1,628.
- seeded: f64 seed 20261028: 3,998,040 PASS; seed
  777001: 3,998,220 PASS (200k draws x 4 fn each);
  f32 seed 987654: 1,991,810 PASS.
- forced stages (test-only builds): wc pair + f16 +
  seeded rerun at FORCE_START=1 and =2: identical PASS
  counts, hits entirely at the forced stage, final 0.
- binary32 EXHAUSTIVE differential, log pair: PASS.
  256 shards x 2^24 encodings over [0,2^32), ranges
  contiguous (re-verified), both functions, five modes,
  bits+flags; every shard rc=0. Aggregate re-summed
  exactly from shard logs (agg_f32.py; the driver's own
  awk mis-indexes stage fields by one - the re-sum
  governs): checked 42,949,672,960 mode-checks =
  4,294,967,296 patterns per function (finite
  4,278,190,080; 16,777,216 nonfinite per function
  table-decided inside the same sweep), mismatches 0,
  decider-undecided 0, kernel final_undecided 0 in all
  shards, stage hits 26,717,714,840/0/0 (stage 1
  decides every binary32 kernel input), decider
  escalations 0, table specials 3,246,391,624, stride
  audits 53,316 audit_fail 0. Driver
  run_f32_exhaustive.sh: 4 workers, ulimit -v 4194304
  KB, process tree lowered to BelowNormal (shared
  host); wall 2026-10-28 20:13:29 -> 2026-10-29
  07:29:58 -0700 (11 h 16 m courtesy-throttled;
  uncontended heavy-slice price was 35.1 s per 2^20
  patterns). Kernel under test is commit 56780d8.
- committed vectors: explog-f16.vec 29,090,
  explog-f32.vec 29,175, explog-f64.vec 32,050
  expectation lines (90,315 total; log families
  specials/powers/sqrt2/near1/tiny/lattice/pole/
  sticky/domain/hardest/seeded; ta independently
  decided; specials+powers cross-checked vs the
  generator's Fraction settled table; regen stable).
  Runner verify 90,315 passed / 0 failed.
- smoke PASS (26 s; built-in controls all refused);
  standard PASS (51 s; +917,504 f16-exhaustive and
  200,000 pack-sweep vectors).
- target: arm-none-eabi-gcc cortex-m0plus -Werror
  clean at BOTH -Os and -O3, host -O2/-O3 clean;
  msf_math.o text ARM -Os 23,700 B / -O3 94,980 B
  (Step 3a: 13,908 / 60,724 - growth is the log kernel
  + tables); symbol scans clean both ways.
- negative controls (run_negatives.sh, negatives.log)
  ALL REFUSED: NC-EKa Ek-tamper replay stage hits
  165740/128132/0 vs baseline */0/0; NC-EKb
  hand-narrowed EK_LOG refused by re-derivation;
  NC-TABLE 2/ln2 digit flip 2,555 runner FAILs;
  NC-DIVSTICKY (Wint top-53 mask) 1,268 FAILs and the
  named cell bites exactly as designed: f64
  log2p1(2^1022) plant delivers fake-exact
  408ff80000000000/00 vs want /10 (tp also 1 ulp low);
  NC-RECENTRE flipped compare 2,430 FAILs (first at
  the powers family: flipped recentring breaks the
  exact branches outright); NC-POLEFLAG strip 45
  flag FAILs at log2(+-0)/log2p1(-1) specials;
  NC-1ULP hardest (log2 0x7fe61555f75885b4 neighbour
  line) refused. Good build passes all vectors.

## Defects found by evidence/probes (fixed, by leg)

1. Shipped-convention probe (pre-evidence, dbg2):
   big_top_bit/clz32 as shipped return bit LENGTH
   (clz32(1)=30, top(0x80000000)=32). The whole wf
   world is value-consistent under it; the log
   helpers take index semantics through a
   log_top_index wrapper. First kernel cut was wrong
   exactly here (recentre/ exact-branch garbage);
   L_sticky re-proven at 2eps per NUM/DEN conversion
   in the generator (EK_LOG integers unchanged).
   Design-entry Sec. 5 wording "<= eps each" stands
   corrected by this entry + generator comment.
2. Decider-side cost only: the first log2p1 power
   test ran a 4224-bit MPFR 1+x per input; replaced
   by the exact common-exponent integer test (design
   Sec. 7's 4224-bit wording superseded; f16 counts
   identical after the swap). wf_div trial divisor
   rebuilt per bit -> built once + shifted down
   (same floor quotient; f16 counts identical).
3. Tooling record: an early background bench delivery
   quoted a 957.9 s shard figure that live process
   evidence contradicted (the bench process was
   still running with 385 CPU-s). The stale bench
   (own process, exact command line verified) was
   stopped; pricing was re-measured (35.1 s per
   2^20 heavy patterns) and the 957.9 s number is
   used nowhere. The driver's awk stage aggregate
   is field-shifted by one (prints 0/N/0); all
   quoted aggregates above are the exact re-sum.
   No kernel defect was found after the convention
   fix: f16 passed on its first full run.

## Metrics rows

briefs.jsonl row for parcel-w5log2 LANDED in commit
826f836 (owned file). No fetches row: wc inputs are
the Step 0b pin already recorded; file hashes above
if the lead wants a parcel row. (The Step-3a briefs
row proposed by parcel-w5exp2 is still not in
briefs.jsonl - noted, not mine to land.)

## Not done

- Board sampled replay: not run (no board flashing
  per brief; board lists already carry msf_math.c,
  verified in Step 3a; logs add no new TU).
- Nothing else in the brief's work list outstanding.

## Commits (branch wave5-log2, not pushed/merged)

56780d8 kernel + generator + registration + decider/
harness extension; 826f836 committed vectors + doc
rows (VECTORS.md, WIDTHS.md, briefs.jsonl). All end
Co-Authored-By: Muse Code (muse-wonder-full-1.0).

Believed: merge-ready. Binary32 leg (c) is complete
by exhaustion; binary64 leg (c) rests on the same
published-completeness authority as Steps 3a/trig:
stage 3 decides plain extra to ~317 bits against
spike-measured maxima of 56.4 (log2) / 60.5 (log2p1)
on full-range published sets, with every attractor
class removed by construction (integer composition,
tiny relative path, separately normalized division
inputs), never by width. Residual risk is that
authority itself, named. The later log/log10 bundles
inherit wf_div + composition (a) in full generality,
as the spike priced.
