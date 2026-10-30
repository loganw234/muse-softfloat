## 2026-10-28 09:12:44 -07:00 - Design entry: correctly rounded exp2/exp2m1, binary16/32/64 (6 rows; log2/log2p1 registered planned), written BEFORE any kernel code

Measured: brief `ledger/briefs/w5-exp2.md` read first and
obeyed exactly; governing `docs/studies/SF-2.md` Secs. 1, 4,
6-9 read in the worktree; spike `scratch/sf2-explog/report.md`
read in full (Secs. 2.1-2.4 margins and ties, 4 reuse audit
and specials, 5 fences incl. the named `exp2m1` RN
subnormal-corner pre-screen fence, 6.1 sketch, 7 stop
conditions R1-R7). Worktree `worktrees/w5-exp2` is on branch
`wave5-exp2` at base a0acf2a (git worktree list, verified).
Shipped substrate read in full and judged sufficient with no
lead-owned edit: `src/msf_math.c` (702 lines, wf_t /
wf_mul / wf_addsub / wf_normalize / trig_pack_big /
trig_pack_wf / trig_pack_one_minus / trig_decide),
`tools/gen_trig_tables.py` (floor_entry, bracket-floor,
scalar Ek recurrence shape with 9-bit reserve),
`src/msf_decode.h`, `src/msf_roundpack.c` (pack contract:
magnitude (sig+f)*2^exp2 over 128-bit sig + sticky, five
modes, tininess after rounding, overflow delivers inf or
largest finite by mode/sign and always carries inexact),
`tools/gen_tables.py` + `tools/run.sh` registration seam.
Specials confirmed against S1 extracts
(`scratch/S1/extract/combined.txt` lines 2738-2739,
2810-2811): exp2m1-class f(+0)=+0 and f(-0)=-0 no exception;
exp2-class f(+-0)=+1 no exception; exp2-class f(+inf)=+inf,
f(-inf)=+0 no exception; exp2m1-class f(+inf)=+inf,
f(-inf)=-1 no exception. Board source lists already carry
`src/msf_math.c` (`board/run_board.sh`, `board/CMakeLists.txt`
x2, verified by grep) - no new TU, no escalation. Clean
room: nothing with `cft` in its name opened, searched, or
listed; CORE-MATH contact this parcel is ONLY mechanical
parsing of two `.wc` files already in the Step 0b pinned
tree (not re-fetched), first data token per line, every
value re-decided by my own MPFR decider; no foreign
implementation source opened (directory names/sizes only,
for the hashes below). Foreign-oracle fences: no foreign
binary is executed by this parcel at all; the spike Sec. 5
`exp2m1` RN subnormal-corner cell (foreign false alarm ~1
per 1e4) is therefore never consulted - MPFR bracket
decides every cell, as the brief's named fence requires.
No kernel code exists yet; this entry is the design gate.

Fetch record (worst-case inputs; scratch only, never
committed): source publication https://core-math.gitlabpages.inria.fr/worst.html
(fetched by the spike 2026-10-28, sha256
5941af171fbde6c119ef4d1865842697e9d82ca198e9fe25dad1eeaf2a09e379,
recorded in `ledger/study-sf2-explog.md`); input files are
the Step 0b pin `core-math-3b2163bb87c222c7db17a721425fbef31e98fd94`
copies at `scratch/oracles/.../src/binary64/exp2/exp2.wc`
(1,661,958 bytes, sha256
51f847cf7102c56fb6d474a304cc56f55ae84b405c8366d77fba3d22523d0f2b,
measured this parcel by Get-FileHash) and
`.../exp2m1/exp2m1.wc` (5,358,578 bytes, sha256
70516fe27283474d55d38ed120569027c81e9bdd3b6f914f6cc855744afbc057).
Spike census counts (its Sec. 1, re-used as the import
expectation, to be re-printed by my importer): exp2 77,182
data lines / 77,120 finite unique; exp2m1 240,834 data
lines / 240,824 finite unique; per file 2 nan + 2 inf + 2
signed-letter 5-char non-finite anchor tokens are excluded
by the mechanical parse and itemized in the evidence log,
never silently rounded (spike R6/R7 hygiene).

### 1. Registration (work item 1)

`tables/operations.tsv` gains four family rows
`exp2`/`exp2m1`/`log2`/`log2p1` (std names exp2, exp2m1,
log2, log2p1; clause 9.2; sig `math_un`; rounding `attr`;
flags `yes`; wave 5; authority `mpfr-exact`; comparison
`exact`; tier 2; claim `C-754`) - 12 instantiations.
`tables/implemented.tsv` gains ONLY the six exp2-pair
instantiations `msf{16,32,64}_{exp2,exp2m1}` at wave 5; the
log2 pair stays `planned` (NULL dispatch, reported
not-implemented by name). `tools/run.sh`:
`TIER2_TOTAL_EXPECTED` 45 -> 57 with the freeze comment
rewritten to name SF-2 Step 3a, and `VECS` gains
`tests/vectors/explog-{f16,f32,f64}.vec`. Runner inventory
after this parcel, stated exactly as printed (brief wording
decision): tier2 51 implemented, 6 planned, 57 registered
(the brief's "51/51 ... registered 51,
implemented 51-with-6-planned" phrasing is internally
inconsistent against the seam arithmetic 45+12=57
registered / 45+6=51 implemented; the runner-printed line
governs and the discrepancy is named here and in the
report, not silently resolved). Regen twice byte-stable
(gen_tables.py + gen_explog_tables.py).

### 2. Specials as shipped (Clause 9.2 via S1 extracts)

NaN handling is the SF-0 2.5 matrix unchanged via
`msf_nan_delivery(fmt, ops, fmts, 1, 0, ...)` -
`invalid_without_nan == 0` because infinities are NOT
invalid for these two functions (spike Sec. 4). A signaling
NaN signals invalid and delivers itself quieted; a quiet
NaN delivers itself, no flag. Explicit branches:

| input | exp2 | flags | exp2m1 | flags |
|---|---|---|---|---|
| +0 | +1 | none | +0 | none |
| -0 | +1 | none | -0 | none |
| +inf | +inf | none | +inf | none |
| -inf | +0 | none | -1 | none |
| qNaN | qNaN (operand) | none | qNaN (operand) | none |
| sNaN | qNaN (quieted) | invalid | qNaN (quieted) | invalid |

No divideByZero anywhere in this bundle. Overflow and
underflow are the shared pack's judgements on exact
endpoint values (Sec. 5), including on the cut and
exact-integer deliveries, which route through the pack -
never hand-flagged.

### 3. Exact / tie branches and inexact obligations (enumerated)

Claim (the bundle's tie-completeness proof, spike Sec. 2.3
specialised): for dyadic-rational x, 2^x is rational only
when x is an integer. Proof: write x = a/2^k in lowest
terms with k >= 1 and a odd (x not an integer). If
2^x = p/q rational in lowest terms then
(p/q)^(2^k) = 2^a, so p^(2^k) * q' ... in integers
p^(2^k) = 2^a * q^(2^k) with a possibly negative; moving
powers of two to one side, unique prime factorisation
forces p and q to be powers of two, say p/q = 2^s, whence
2^(s*2^k) = 2^a gives a = s*2^k, contradicting a odd with
k >= 1 unless... precisely: a divisible by 2^k with k>=1
contradicts lowest terms. Hence 2^x, and 2^x - 1, are
irrational (in fact algebraic irrational) for every
non-integer dyadic x. Every rounding boundary of a binary
format (representable value or midpoint of two adjacent
representables, including the overflow midpoint and the
u/2 subnormal midpoint) is a dyadic rational. Therefore:

- No exact result and no exact tie is attainable for
  non-integer x, at any format, in any mode.
- Every kernel-path (non-integer, non-special) result is
  inexact: the kernel ORs MSF_FLAG_INEXACT exactly as
  trig_decide does, and this is a proof, not a heuristic.
  Underflow remains the pack's after-rounding tininess
  judgement on the endpoint packs (they must agree in
  bits AND flags to decide).
- All exact/tie-capable inputs are exactly the integers,
  enumerated here per format (p = precision,
  emin/emax the format exponents, u = 2^(emin-p+1) the
  smallest subnormal, tie exponent E_tie = emin-p):

exp2, integer n (result 2^n):
  (a) emin <= n <= emax: exact normal power, no flags.
  (b) E_tie+1 <= n < emin (i.e. emin-p+1 .. emin-1):
      exact subnormal power u*2^(n-(emin-p+1)), no flags.
  (c) n = E_tie (f64 -1075, f32 -150, f16 -25): result
      exactly u/2 - the midpoint tie between 0 and u.
      Delivered by packing the exact value 2^E_tie through
      msf_pack_generic: ties-to-even picks 0 (even),
      ties-to-away / towardPositive pick u, others 0;
      inexact signals (a tie is not the delivered value),
      underflow per the pack's Clause 7.5 judgement. This
      is THE named tie branch ("x = -1075 packed exactly"
      at f64). Flags come from the pack alone.
  (d) n < E_tie: folded into the zero-threshold cut
      (Sec. 4), which itself packs a proxy exact value;
      rounding identical by the cut argument.
  (e) n = emax+1 .. cut: result >= 2^(emax+1): overflow
      delivery (inf or largest finite by mode) with
      overflow+inexact, via packing the exact 2^n when
      n = emax+1 in the kernel strip (Sec. 4: only
      x >= emax+1 takes the cut, so this is the cut case)
      or the cut proxy beyond.

exp2m1, integer n (result 2^n - 1):
  (a) n = 0: +0 (x = +-0 handled in specials with sign).
  (b) 1 <= n <= p-1 (f64 n<=52, f32 n<=23, f16 n<=10):
      2^n - 1 has n one-bits, representable exactly,
      no flags.
  (c) n = p (53/24/11): 2^p - 1 needs p one-bits in the
      binade [2^(p-1), 2^p) whose spacing is 1:
      representable exactly, no flags. (f64: 2^53-1 exact.)
  (d) n = p+1 (54/25/12): 2^(p+1) - 1 is the exact
      midpoint between 2^(p+1)-2 and 2^(p+1) in the
      spacing-2 binade - tie branch (spike: exp2m1(54)).
      Packed exactly; ties-to-even picks 2^(p+1) (even
      significand), ties-to-away likewise away (= up),
      directed pick their side; inexact signals.
  (e) n > p+1: 2^n - 1 is strictly between representables
      but never a midpoint for n >= p+2? Neighbours are
      2^n - 2^(n-p) and 2^n, midpoint 2^n - 2^(n-p-1);
      2^n-1 equals it iff 2^(n-p-1) = 1 iff n = p+1,
      already (d). So (e) is inexact non-tie; packing the
      exact integer 2^n - 1 decides it in all modes.
      n >= emax+2 folds into the overflow cut (Sec. 4);
      emax+1 stays on the exact-pack path.
  (f) n < 0: result -(1 - 2^n), magnitude 1 - 2^n with
      -n one-bits below the point. Representable exactly
      iff -n <= p (bits 2^-1..2^n fit p significand bits
      in binade [1/2,1)... precisely magnitude in [1/2,1)
      has ulp 2^-p, so exact iff -n <= p): cases
      -p <= n <= -1 exact, no flags (but n = -1: -1/2);
      n = -(p+1) (f64 -54): magnitude 1 - 2^-(p+1) is the
      exact midpoint between 1 - 2^-p and 1 - tie branch
      (spike: exp2m1(-54)); packed exactly with sign;
      ties-to-even picks -1 (even significand 1.0),
      ties-to-away picks -1 (away from zero), towardZero /
      towardPositive pick -(1-2^-p), towardNegative -1;
      inexact signals. n < -(p+1): magnitude in
      (1 - 2^-(p+1), 1), inexact non-tie, folded into the
      saturation cut (Sec. 4) whose proxy packs identical
      bits/flags in every mode.

Integer detection is on decoded (sig, exp): x finite
nonzero is an integer iff exp >= 0 or the low -exp bits of
sig are zero. The exact branches pack materialised exact
integers/dyadics (Sec. 5 big buffers; |n| <= emax+1 after
the cuts, <= 1026 bits worst case, inside the 64-limb big).

Inexact obligations summary: specials - none. Integer
exact cases (a)-(c)/(a)-(c),(f)-exact above - no inexact,
and the pack sees an exactly representable value so it
cannot invent one. Integer tie/inexact cases - inexact
(plus underflow at (c) per pack judgement, plus overflow
in (e)-overflow) delivered BY THE PACK on the exact value,
never ORed by hand; a planted tie-branch flag-strip
mutant (Sec. 7) must be caught by committed vectors at
exactly these cells. Kernel path - inexact always (proof
above), underflow/overflow from agreed endpoint packs.
Cut paths - pack judgements on proxies proven to round
identically (Sec. 4). NaN/inf - table above. No other
flag sources exist.

### 4. Reductions and exact exponent cuts

All cut comparisons are exact integer comparisons of the
decoded x against small integer thresholds, via a helper
comparing sig*2^exp (sign separate) against |T| <= 4096 by
bit-length then aligned compare - no floating literals
anywhere (type scan enforces). Cuts run BEFORE the n+f
split, so afterwards |x| <= max(p+2, emax+2, |E_tie|+1)
<= 1076 and the integer part fits int32/uint64 by
construction. Thresholds per function (T evaluated on x
itself, all formats through fp->emin/emax/precision):

exp2:
  - x >= emax+1: result >= 2^(emax+1). Deliver
    pack_big(exact 2^(emax+1)): every value >= 2^(emax+1)
    rounds identically in all five modes (RN/RNA/RU: inf;
    RZ/RD: largest finite - positive sign) with
    overflow+inexact from the pack. The strip
    emax+1/2 <= x < emax+1 stays with the kernel
    (n = emax+1, f < 0), per spike Sec. 6.1: "(n = 1024:
    kernel decides against the overflow midpoint)".
  - x < E_tie (= emin - p): result in (0, u/2). Deliver
    pack_big(exact 2^(E_tie-1)): every value in (0, u/2)
    rounds identically (RU: u; else +0) with
    underflow+inexact from the pack. x = E_tie exactly is
    NOT cut: it is an integer (E_tie is an integer) and
    takes exact branch 3(c). Non-integer x in
    (E_tie, E_tie+1) take the kernel (n = E_tie+1 strip or
    n = E_tie with f > 0) which decides against the u/2
    midpoint by interval.

exp2m1:
  - x >= emax+2: result >= 2^(emax+2) - 1, past the RN
    overflow midpoint (2^(emax+1) - 2^(emax-p+1) - 1 =
    midpoint-1 < 2^(emax+1)) - deliver
    pack_big(exact 2^(emax+2)), identical rounding/flags
    argument as exp2's cut. x in [emax+1, emax+2) goes
    kernel/exact (n can be emax+1 or emax+2 with f<0;
    composition pack handles the exponent).
  - x < -(p+1) (saturation cut, spike M1SAT): then
    2^x < 2^-(p+1) and the result lies in
    (-1, -(1 - 2^-(p+1))), strictly between -1 and the
    midpoint below 1. Deliver pack_generic of the exact
    proxy magnitude 1 - 2^-128 with sign 1 (sig =
    2^128-1 at exp2 = -128 in pack input form... in
    msf_pack_generic terms sig all-ones-128,
    exp2 = -128, sticky 0): every magnitude in
    (1 - 2^-(p+1), 1) rounds identically in all modes
    (RN/RNA/RD: -1; RU/RZ: -(1-2^-p)) and is inexact,
    never tiny. The proxy is itself such a magnitude, so
    bits/flags agree. x = -(p+1) is an integer: exact
    branch 3(f) tie. Non-integer x in (-(p+1), -p) stay
    kernel-side (in-class max RN extra measured 48.86 by
    the spike - stage 1 territory, composition decides).

Cut-threshold off-by-one is a named negative control
(Sec. 7): each threshold gets committed vectors at T-1ulp,
T, T+1ulp in all modes.

Split (exact, spike Sec. 6.1): after specials and cuts,
decode |x| = sig*2^e (sig < 2^53). Form I = floor(|x|) and
rem, half exactly as trig_core does (shift by k = -e;
k >= 64 means |x| < 1/2 with I = 0, rem = sig). Then
signed nearest-integer split x = n + f, f in [-1/2, 1/2]:
for x >= 0: r <= 1/2 -> n = I, f = +r; r > 1/2 ->
n = I+1, f = -(1-r). For x < 0: r <= 1/2 -> n = -I,
f = -r; r > 1/2 -> n = -(I+1), f = +(1-r). f is carried
as (f_sign, f_num uint64, f_exp = -k) exact dyadic,
<= 54 significant bits. f == 0 is the integer branch of
Sec. 3 (detected as rem == 0, or e >= 0). The factor 2^n
is NEVER a multiply: it enters as an exponent offset in
the pack input of the composed value (Sec. 5).

### 5. Kernel series and Ek proof shape

Reuse (spike Sec. 4 audit, confirmed by reading): wf_t
positive wide float, wf_mul, wf_addsub, wf_normalize,
trig_pack_big (top-128 + sticky exact-endpoint pack),
trig_pack_wf, the three stages W = 160/256/384 (limbs
5/8/12), interval decision by endpoint bit+flag agreement.
New in this TU section: wf_from_xentry over the explog
table (same floor-truncation behaviour), the exp Horner
evaluator, three composition packers, the split/cuts, and
per-format wrappers `msf{16,32,64}_{exp2,exp2m1}` over one
`explog_core(fmt, is_m1, bits, rm, flags)`.

Kernel argument u = f * ln2, |u| <= U := ln2/2 < 0.346574
(rigorous ceiling U = 34658/100000 proven in the generator
from its own bracketed ln2 hi endpoint). Two positive
series share ONE coefficient table c_k = 1/k! :

  v = exp(u), u >= 0: Horner in u over c_0..c_{K-1}.
  M(z) = sum_{k>=0} z^k / (k+1)! (Horner over c_1..c_K),
    z = |u|:  u > 0: m = u * M(u) = expm1(u) (positive);
              u < 0: delta = z * M(z) = 1 - exp(u) > 0
    (the delta form for u < 0, per the brief: all Horner
    terms positive, no cancellation, exactly the trig
    delta-branch role).

Evaluated kernel quantities (each a positive wf
approximation A with proven RELATIVE bound |A - q| <=
A * 2^-Ek[stage]):
  Q_V: q = v (u >= 0), for exp2.       A = Horner_exp(u).
  Q_D: q = delta (u < 0), for exp2 via 1-delta and for
       exp2m1 negative side.           A = z * M(z).
  Q_M: q = m (u > 0), for exp2m1.      A = u * M(u).
Q_D and Q_M are the same code path (z * M(z)) differing
only in downstream composition; u = 0 cannot reach the
kernel (f = 0 is exact-branched).

Ek recurrence (generator-proven integers; shape mirrors
the trig generator's scalar_ek_exp): one truncating op or
stage-truncated floor constant errs <= eps := 2^(1-W)
relative. e_f = 0 (f exact dyadic, <= 54 bits < W,
wf_normalize exact). e_u <= 2*eps + eps^2 (ln2 constant
<= eps; one truncating multiply). Horner for exp:
P_k = sum_{j=k}^{K-1} u^(j-k)/j! satisfies
1/k! <= P_k <= (1/k!) * 1/(1 - U/(k+1)) (geometric
successor-ratio bound), so the product term's weight in
P_k is rho_k = U / ((k+1)(1 - U/(k+2))) < 1.
e_{K-1} = eps;
e_prod = e_u + e_{k+1} + e_u*e_{k+1} + eps;
e_k = eps (coefficient) + rho_k * e_prod + eps (sum
truncation). Final: e_v = e_0 + tail_K with
tail_K = [U^K/K! / (1 - U/(K+1))] / 1 (v >= 1).
Horner for M identically with factorials shifted by one
(rho^M_k = U / ((k+2)(1 - U/(k+3))), T_k bounds with
1/(k+1)!), then e_{zM} = e_z + e_M0 + e_z*e_M0 + eps +
tail^M_K / 1 (M >= 1), e_z = e_u. Term counts K per stage
chosen in the generator so both tails <= 2^-(W+24)
(exact-rational check, spike sizing: ~35/47/66).
Ek[stage] emitted = floor(-log2(max(e_v, e_zM))) - 9
(the standard 9-bit reserve), asserted by exact Fraction
arithmetic at generation time and printed; expected class
(per spike Sec. 6.1): ~2^-150 / 2^-246 / 2^-374. The
decide step forms endpoints lo = A - A*2^-Ek (truncate
sub) and hi = A + A*2^-Ek (away add) exactly as
trig_decide, then packs THE COMPOSED ENDPOINT VALUES
(below) and requires bit+flag agreement; monotone (in
either direction) composition makes agreement sufficient.
Demand vs reach (spike-measured margins only, SF-1 leg
(c) reading): plain binary64 maxima exp2 RN 60.54 / DIR
60.43, exp2m1 plain RN 59.10 / DIR 56.74 with in-class
attractor RN <= 59.92 decided by composition; stage 1 at
~2^-150 decides every observed plain case (needs
2^-(53+60.6) ~ 2^-114), stage 3 decides plain extra to
~318 bits - 5.3x exp2's measured maximum, under the same
published-completeness authority SF-2 Sec. 4 records.
Final-stage undecided: counted
(MSF_EXPLOG_TEST_COUNTERS, test builds only), defined
fallback packs the lo endpoint as unreachable code, and
ANY nonzero count in evidence is a brief STOP (report NOT
READY, never widen ad hoc - spike R4).

Composition packers (exact endpoint values; sign applied
inside; each is monotone in the kernel quantity as noted):
  P1 scaled wf: value q * 2^n - copy wf, e += n,
     trig_pack_wf. (exp2 Q_V; monotone increasing.)
  P2 one-minus scaled: value (1 - d) * 2^n, d in
     (0, 1-2^-1/2]subset(0,0.293) - trig_pack_one_minus
     generalised by adding n to the pack base exponent
     (288-bit fixed point + g sticky, copied with the
     offset parameter). (exp2 Q_D; decreasing in d.)
  P3 m1-positive bracket: exp2m1 with n >= 1:
     result = 2^n (1 + s_q) - 1 = (2^n - 1) + s * Q * 2^n
     where Q = m (s=+1) or delta (s=-1). Exact endpoint:
     V = (2^n - 1) + s * M_Q * 2^(e_Q - (W-1) + n),
     materialised in a 64-limb (2048-bit) big at base
     b = min(0, t), t = e_Q-(W-1)+n: bits [-b, n-b) set
     (the 2^n-1 ones) then add/sub M_Q << (t-b), packed
     via trig_pack_big(big, base b). Span proof: n >= 1
     implies x >= 1/2, so decoded e >= -53 at f64 (format
     analogues by p), nonzero |f| >= 2^-53 (f is a
     multiple of 2^e, e >= -(p) for |x| >= 1/2... stated
     per format in code comments with the p-formula),
     |u| >= 2^-54, Q >= 2^-55 (m >= u for u > 0; delta =
     1-e^u >= |u| e^u >= 2^-55), so e_Q >= -55 at f64
     (resp. >= -(p+2) generally) and t >= -(p+2) - 383.
     Width <= (emax+2) + (p+385) + 2 <= 1464 bits f64,
     less at f32/f16: inside 64 limbs with margin.
     n = 0 case: result = m or -delta directly (P1 with
     n = 0 and sign = (u<0)). (Increasing in m; composed
     value decreasing in delta - endpoints swapped
     accordingly by packing both, order irrelevant to the
     agreement test.)
  P4 m1-negative bracket: exp2m1 with x < 0, n <= -1:
     magnitude D = 1 - 2^n v = (1 - 2^n) - s' * Q * 2^n
     with s' = +1, Q = m when u > 0 and s' = -1, Q = delta
     when u < 0, i.e. D = (1 - 2^n) + s * Q * 2^n,
     s = -1 (u>0) / +1 (u<0). Materialised at base
     b = min(n, t): (1-2^n)*2^-b has ones in bits
     [n-b, -b); add/sub M_Q << (t-b); pack with sign 1.
     Saturation cut bounds n >= -(p+2), and n <= -1
     implies |x| >= 1/2 so e_Q >= -(p+2) as in P3:
     width <= (p+2) + (p+385) + 2 < 560 bits. x < 0 with
     n = 0 forces f < 0, result = -delta (P1, sign 1).
  Exact-integer packing reuses the same big: 2^n - 1 is
  the ones-pattern at base 0 (n in [1, emax+1]); 1 - 2^n
  the ones-pattern at base n (n in [-(p+1), -1]); 2^E_tie
  a single bit - all through trig_pack_big.
  Endpoint Q can be the zero wf (lo endpoint of a tiny Q
  after the Ek subtraction): materialisation treats M_Q=0
  as no-op; P1/P2 zero cases follow trig behaviour.

Stage/counter plumbing mirrors trig: MSF_EXPLOG_TEST_COUNTERS
(stage hits[3], final undecided), MSF_EXPLOG_FORCE_START,
and the negative-control macro MSF_EXPLOG_EK_NARROW
(subtracted from Ek exponents in the decide step, default
0, never defined in a quoted build) so the brief's
"Ek narrowed past its bound" control is a build-time plant
caught by differential replay, in addition to generator
re-derivation (regen diff refuses a hand-narrowed header).

### 6. Constants and generator

`tools/gen_explog_tables.py` (trig-generator pattern,
first principles only): ln2 by mpmath at dps 260 and 210,
bracket floor at +-2^-590 proven stable to the same
384-bit floor (printed agreement); EXP_C[k] = floor entries
of the exact rationals 1/k! for k = 0..K3 (K3 = stage-3
term count; M uses c_{k+1} so the table carries one past
the exp need); every entry verified lo <= true < hi by
Fraction (ln2 against the bracket). Emits
`src/msf_explog_tables.h`: stage limbs (5,8,12), NTERMS
per stage (max of exp/M needs), EK_EXP[3] as proven
integers, LN2 + EXP_C entries as 12 little-endian limbs.
No decimal literals in C; the only rationals in the
generator are 1/k! and the U ceiling derived from its own
ln2 bracket hi endpoint. Regeneration byte-identical
twice (checked), and run.sh drift discipline covers
gen_tables outputs; the explog header is re-derived and
cmp'd in parcel evidence (run.sh owns only gen_tables -
named, not silently extended).

### 7. Evidence plan (legs, negatives, gates)

Decider (`tests/explog_decider.c`, included by
`tests/explog_exhaustive.c`): independent MPFR bracket
decider in the trig_exhaustive idiom - exact input
reconstruction from bits, mpfr_exp2 / mpfr_exp2m1 at
adaptive precision (start 192 f64 / 160 f32,f16; escalate
384/768/1536/3072), bracket = two nextabove/nextbelow
steps, both ends narrowed in FIVE modes by a
first-principles integer-grid narrow (ties-to-even and
ties-to-away both decided from scaled-integer parity/
half comparisons on the exact bracket ends - no raw
MPFR RNDNA anywhere, per SF-2 Sec. 2 prohibition), flags
from first principles (inexact = nonzero discarded tail
at the delivered grid; overflow = unbounded prec-p
rounding exceeds largest finite, delivering by mode with
inexact; underflow = inexact and unbounded prec-p
rounding below 2^emin, tininess after rounding).
Specials and ALL integer inputs (the Sec. 3 exact/tie
table) decided in the decider from the table/exact
dyadic construction, independently of the kernel; MPFR
exception flags never read. Stride audits cross-check the
grid narrow against mpfr_get_flt/get_d bits (f32/f64,
modes te/tz/tp/tn) and against raw signed re-decision.
Far-cut structural shortcuts in the decider exist ONLY
with >= 60 bits of margin beyond every kernel threshold
(proxy exact values), are counted, and cannot mask a
kernel cut off-by-one. The exp2m1 saturation strip and
subnormal corner are always full-bracket decided (the
named fence: no foreign oracle anywhere).

Legs: (i) binary16 exhaustive: all 65,536 encodings x 2
functions x 5 modes vs decider, bits+flags, stage/final
counters printed. (ii) binary32 EXHAUSTIVE finite
differential: all 2^32 encodings (nonfinite decided by
the specials table; finite count 4,278,190,080 printed)
x 5 modes, sharded by encoding range across processes
under per-process ulimit -v ceilings (Git Bash ulimit;
values recorded), shard counts summed and printed, zero
mismatch / zero decider-undecided / zero kernel
final-undecided required. (iii) binary64: 100% of the
published worst-case finite unique inputs for BOTH
functions (wc mode; coverage counts = spike census
77,120 + 240,824, re-printed by the importer, shortfall
is failure) x 5 modes + seeded volume (seeded finite
patterns, >= 2 seeds/function) vs decider. (iv) committed
vectors in the trig idiom
(`tests/gen_vectors_explog.py` -> explog-{f16,f32,f64}.vec,
provenance mpfr-explog:<family>): specials (cross-checked
against an independent Python settled-table restatement,
generation refuses on disagreement), integer/tie anchors
(every Sec. 3 cell incl. -1075, +-54-class ties, p, p+1
per format, with ulp neighbours), cut thresholds
(T-1ulp/T/T+1ulp per cut), saturation strip ladders,
tiny/subnormal inputs and results, overflow strip,
hardest excerpts (spike Sec. 2.1 maxima patterns:
exp2 0x3f5e4596526bf94d-class inputs only, values
re-decided; plus top patterns harvested from my own wc
replay escalation log), seeded sweep. ta lines are
INDEPENDENTLY decided by the five-mode decider (ties
exist here - no relabel; VECTORS.md will say so).
(v) smoke + standard PASS via tools/run.sh. (vi) target
compile: arm-none-eabi-gcc -std=c11 -Wall -Wextra -Werror
-mcpu=cortex-m0plus -mthumb -ffreestanding at BOTH -Os
(run.sh symbol_scan) and -O3 (standalone parcel check -
the previous parcel's -O3 maybe-uninitialized miss is the
named reason), sizes of msf_math.o recorded both ways;
host -O2/-O3 -Werror also clean.

Negative controls (each watched refusing/failing, logs
kept): NC1 Ek narrowed (build -DMSF_EXPLOG_EK_NARROW=100:
differential replay on wc-hardest excerpt + committed
vectors MUST produce mismatches; also generator
re-derivation refuses a hand-edited EK_EXP via cmp).
NC2 constant-table digit flip (one limb of LN2 flipped in
a scratch copy of the header: vector verify must FAIL).
NC3 cut-threshold off-by-one (scratch patch shifting the
exp2 zero cut and the saturation cut by 1: committed
cut-boundary vectors must FAIL). NC4 tie-branch flag
strip (scratch patch clearing inexact on the integer
exact-pack path: tie-cell vectors at E_tie and +-(p+1)
must FAIL on flags). NC5 1-ulp hardest corruption
(standard runner control shape on an explog hardest line:
flipped expected bit refused). NC0 pre-existing: the
run.sh control battery must stay all-refused with the new
inventory line (its tier-inventory mutants re-watched).

Stop conditions (brief + spike Sec. 7, binding): any
stage-3 final-undecided > 0 in any evidence leg; any
kernel-vs-decider disagreement not adjudicated to a
decider defect by a second route; any decider
final-undecided at 3072 bits; wc coverage short of 100%
of finite unique inputs; regen not byte-stable; -O3
target warnings. Any stop => report NOT READY with the
counter, never widen a stage or threshold ad hoc.

Believed: the design above is a faithful specialisation
of the spike Sec. 6.1 sketch to kernel code - exact split,
2^n as pack-exponent input, delta form for u < 0,
composition-only exp2m1 (no new series), 160/256/384 Ziv
stages with generator-proven Ek; the biproducts to watch
are the P3/P4 materialisation span bounds (proven above
from the decoded-exponent floor for |x| >= 1/2, and
additionally guarded in debug evidence by the exhaustive
legs) and the decider's first-principles five-mode narrow
(cross-audited by stride against MPFR's own conversions,
so a decider grid bug cannot masquerade as a kernel pass
at volume). Remaining prices are engineering judgement,
not measurements: kernel+generator ~1 day, decider/
exhaustive harness ~half day, f32 exhaustive wall-clock
measured on day 1 (spike R7: kernel throughput unknown;
MPFR side priced 4-7 h/function single-core by the spike,
host has 12 logical cores for sharding).
For: lead

## LEAD NOTE 2026-10-28 12:25:32 -0700 (owner request, system contention)

The f32 exhaustive sweep's process tree (run_f32_exhaustive.sh
launcher + 11 explog_exhaustive.exe shards + shells, 37
processes) was lowered to BelowNormal priority by the lead at
the owner's request; verified BelowNormal on a live shard;
children of the lowered shells inherit it. No shard was
stopped; nothing needs redoing. If you restart any sweep leg,
keep concurrency modest (<=2-4 shards) and note the throttling
in your report. Direct messaging to the workflow child was
rejected by the tool, hence this ledger note + OS-level action.
For: parcel-w5exp2

## 2026-10-28 17:28:32 -07:00 - Results entry: exp2/exp2m1 READY on wave5-exp2 (report scratch/parcel-w5exp2/report.md, 10,146 bytes, sha256 7159a22078b361138767494a9e30989916395bf9b0ae963619c7b3116edaa294, first line READY)

Measured: full report as hashed above; this entry records the verdict and the load-bearing numbers. Commits on wave5-exp2 (base a0acf2a, never pushed/merged): 87d00d2 (kernel+registration+generator+decider), 048aa29 (delta-series/near-1 fixes), 2618b34 (vectors+docs rows). Registration: tier2 57 registered / 51 implemented / 6 planned exactly as the runner prints it (log2 pair planned by name); regen byte-stable twice for gen_tables.py, gen_explog_tables.py, and the vector generator. Ek integers as proven: MSF_EXPLOG_EK_EXP {147, 243, 371}, stage terms {35, 49, 66}, ln2 bracket diff ~2^-702.3. Evidence legs (all bits+flags, five modes, MPFR adaptive bracket decider; no foreign oracle executed anywhere): binary16 exhaustive 655,360 checks PASS; binary32 EXHAUSTIVE 42,949,672,960 mode-checks over all 2^32 patterns per function (finite 4,278,190,080), 256 shards all rc=0, mismatches 0, undecided 0, final_undecided 0, stage hits 22,386,767,760/0/0, audits 25,986/0 fail, ulimit -v 4194304 KB, wall 7h49m (shared host; sweep tree lowered to BelowNormal mid-run per the LEAD NOTE above - correctly absorbed, nothing redone); binary64 worst-case 100% both functions (exp2 385,880 checks over 77,176 occurrences/77,121 unique encodings = spike census 77,120 + the -0 encoding set-diff-verified; exp2m1 1,204,140 over 240,828/240,825, spike 240,824 + -0), inexact tokens 0, stage 1 decided every wc input; seeded binary64 2 x ~2.0M and binary32 995,965 PASS; forced-stage (1 and 2) reruns of wc+f16+seeded identical PASS. Committed vectors 45,610 lines, ta independently decided (ties exist; exp2(-1075) and exp2m1(+-54-class) cells present with flags 0x18/0x10 as designed); smoke PASS, standard PASS, target ARM -Os AND -O3 -Werror clean (msf_math.o 13,908 B / 60,724 B text), host -O2/-O3 clean. Negative controls all refused (Ek tamper by re-derivation byte-compare and by stage-counter replay 374095/242117/0 vs */0/0; ln2 digit flip 7,349 runner FAILs; top-limb table plant 7,322; cut off-by-one refused on exactly the 3 tie ta lines; flag strip 4,565; 1-ulp hardest refused) - with the measured caveat recorded in the report that subtle 2-/3-limb drops do not bite this vector set (error below the hardest committed boundary distance), so the watched plants are the deterministic forms. STOP record: the stage-3 final-undecided STOP fired once during development (9 hits, wc exp2 first run, tiny inputs) and was closed by design (1+m ones-bracket composition for exp2 n=0), never by widening; two further defects were decider/tooling-side only, and one kernel defect (delta evaluated with the positive expm1 ratio instead of the alternating D series) was caught by the binary16 exhaustive on first run - all itemized in the report with logs under scratch/parcel-w5exp2/.
Correction to the design entry Sec. 5, recorded here as the results-side amendment: where the design entry wrote the u<0 quantity as A = z*M(z), read delta = z*D(z) with D the alternating series and its own Ek recurrence (generator proves all three Horners; Ek integers unchanged); and add the exp2 n=0, f>0 1+m bracket shape to its shape table (spike Sec. 4 item 2b, found load-bearing by leg (a)).
Fetch record (this parcel's act): no new network fetch; worst-case inputs consumed from the Step 0b pin (URL https://gitlab.inria.fr/core-math/core-math/-/archive/3b2163bb87c222c7db17a721425fbef31e98fd94/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94.tar.gz, already in docs/metrics/fetches.jsonl) with file hashes exp2.wc 51f847cf7102c56fb6d474a304cc56f55ae84b405c8366d77fba3d22523d0f2b, exp2m1.wc 70516fe27283474d55d38ed120569027c81e9bdd3b6f914f6cc855744afbc057; mechanical first-token parse only, every value MPFR-re-decided, scratch only. Proposed metrics rows are spelled out in the report (briefs row for parcel-w5exp2; no fetches row needed beyond the existing pin, file hashes supplied if the lead wants one).
Believed: merge-ready. Binary32 leg (c) is complete by exhaustion; binary64 leg (c) rests on the same published-completeness authority as the trig parcel, consciously: stage 3 decides plain extra to ~318 bits against a spike-measured maximum of 60.54 (exp2) on sets that the fetched completeness claim covers in full range, and every attractor class is removed by construction rather than by width - the one residual risk is the authority itself, named, not hidden. The log2 pair is the clean next parcel (wide division is its only new mechanism; the bracket composition here already carries item 2(c) of the spike's audit).
For: lead
