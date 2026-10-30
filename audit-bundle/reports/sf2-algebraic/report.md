GO rSqrt, GO hypot, GO-CONDITIONAL pown, GO-CONDITIONAL compound (rides pown), GO-CONDITIONAL rootn (last; deferrable whole) - conditions are priced leg-(c) margin proofs in Sec. 8, not new inventions

# SF-2 input study: the algebraic Clause 9.2 bundle, designed and priced

Role: study-sf2-algebraic (scratch only; no repository edits, no
commits). Brief: `ledger/briefs/sf2-algebraic.md`, obeyed exactly.
Base: `muse-softfloat` at `7ebbe70`, working tree verified clean
at close. Date: 2026-10-28. Host records: Git Bash + MSYS2
gcc 16.1.0 (x86_64-w64-mingw32), MPFR 4.2.2
(`MPFR_VERSION_STRING` read from its header), workspace `.venv`
Python 3.12.15 pinned as `MSF_PYTHON` in every run script; TMP
inside `scratch/sf2-algebraic/tmp`.

Clean-room record: nothing with `cft` in its name was opened,
searched, or listed. No third-party implementation source was used
as design input; every design below derives from the standard text
(S1 extracts, cited by extract page + clause, never quoted beyond
a few words) and exact integer arithmetic. MPFR was executed as an
oracle probe. CORE-MATH (Step 0b pin, commit `3b2163b...`) was
execution-only: directory listings, three public
`function_under_test.h` interface headers (rsqrt), and built
binaries run over my own harness; no implementation source,
constants, or `.wc` contents were read. Build log for the foreign
units was 0 bytes (clean compile, no diagnostics quoted anything).

Marker discipline: [M] measured this study, [R] read in a governing
file, [D] derived here by stated proof, [E] estimate. Anything
unread or unexecuted is named in Sec. 9.

## 1. Verdicts and parcel order

| Function | Verdict | Why (one line) |
|---|---|---|
| `rSqrt` (3 rows) | **GO** | Exact integer decision; prototype bit-matches MPFR on all 262,144 binary16 cases (Sec. 6); no overflow/underflow attainable [D] |
| `hypot` (3 rows) | **GO** | Exact in the existing 128-bit class [D], refining the Clause 9 survey's wider guess; 153,600 prototype decisions agree with an independent exact decider [M] |
| `pown` (3 rows) | **GO, conditional** | Exact tie/representability path proven [D+M]; the capped-interval stage margin at binary32/64 is a priced proof/search obligation (Sec. 8) |
| `compound` (3 rows) | **GO, conditional** | Exactly `pown` on an exact dyadic base `1+x` (<=1075 bits at binary64) - inherits the `pown` condition, adds only specials |
| `rootn` (3 rows) | **GO, conditional, last** | Exact integer-root route bounded in `|n|`; general-`n` interval route needs the same class of margin proof, least measured here; the whole family defers cleanly if the schedule cuts |

Format parity is structural throughout: every name is one
binary16/32/64 bundle (15 core rows total), developed f16 -> f32
-> f64 inside a parcel, merged and claimed only at bundle closure
[SF-1 Sec. 2.1]. Recommended order (Sec. 7): lead seam for two new
signature classes, then rSqrt, hypot, pown (+ shared capped-power
helper), compound, rootn. Nothing else should be interleaved: the
helper lands with `pown`, its first consumer.

## 2. Common contract

### 2.1 The pack-feed lemma (one decision shape for all five)

Every kernel reduces to: deliver `(sign, exp2, sig128, sticky)` to
the unmodified `msf_pack_generic` ([msf_roundpack.c](/C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat/src/msf_roundpack.c:85)),
whose contract is exact magnitude `(sig + f) * 2^exp2` with `f = 0`
iff `sticky == 0`, else `0 < f < 1` [R: file header + WIDTHS].
A kernel that produces `Q = floor(true * 2^S)` for a chosen scale
`S`, with `sticky = (true * 2^S != Q)`, and with Q's least
significant bit at least two bits below the destination ulp in
every attainable binade (including the subnormal clamp), makes
the pack's single rounding the correctly rounded answer in all
four attributes, with overflow/underflow(tininess-after)/
inexact flags correct by construction [D]. Ties survive
faithfully: an exact midpoint is dyadic at or above Q's scale,
so it arrives as guard=1, round=0, sticky=0 - the pack's tie
path, not a kernel special case. Each function below is an
exact integer method for computing such a Q and its stickiness;
interval variants (pown/compound/rootn at large `|n|`) compute
two such Q's bracketing the truth and pack both endpoints,
accepting only on bit+flag agreement (the shipped
`trig_decide` pattern, [msf_math.c](/C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat/src/msf_math.c:551)).

**No new pack entry points are needed** [D audit]: finite results,
interval endpoints (scratch flag accumulators), and the synthetic
certain-overflow/certain-tiny feeds of Sec. 3.4 all fit the
existing signature and domain contract (`sig != 0` whenever
sticky is set - feeds use `sig = 1`). Lead-owned new surface is
limited to: (a) generator signature classes `math_bin` /
`math_int` (Sec. 7.1),
(b) WIDTHS rows rested per parcel, (c) one new TU
`src/msf_alg.c` carrying each family's three formats (SF-1
Sec. 8 placement rule; Tier 1 files byte-stable).

### 2.2 Shared semantic rulings

- Rounding attributes: the four public attributes on every row.
  Ties-to-away is not a public attribute in this project window
  [SF-1 Sec. 7]; the internal mode exists in the pack and the
  kernels are mode-agnostic, so a later fifth-attribute wave is
  an evidence sweep, not redesign [D].
- Inexact: Clause 9.2 makes inexact a `should`/`should not`
  (extract p059 L34-35); per the Clause 9 survey's Sec. 4.6.1
  recommendation this study designs for the project's standing
  promise: inexact exactly when the delivered result differs
  from the exact value, free from faithful sticky [R+D].
- Tininess: after rounding, judged by the shared pack only
  (SF-0 2.5) [R]. Kernels never judge tininess themselves.
- NaN delivery: the SF-0 2.5 matrix in `msf_nan_delivery`
  ([msf_decode.h](/C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat/src/msf_decode.h:102)):
  first signaling operand quieted (+invalid), else first quiet
  operand, else the default quiet NaN. Homogeneous rows keep
  payload and sign bit-exact; the narrowing-truncation case
  cannot arise [D]. Two bundle cells defeat direct reuse and are
  hand-ordered before the helper call: `hypot` infinity-over-
  quiet-NaN, and the `n == 0` anchors of `pown`/`compound`
  (Sec. 5) [R: survey Sec. 4.6.1 same warning].
- Integer operand: `int64_t` (`integralFormat` = the widest
  shipped integer format), per Clause 9 survey Sec. 4.6.1 [R].
  This makes the language-defined non-integral/infinite-`n`
  region (extract p063 L28-30) unreachable by construction.
  The alternative (floating `n`) buys nothing and costs owner
  rulings; refused [D].
- Preferred exponents (Clause 9.2.2, extract p065): decimal
  quantum machinery; no effect on binary encodings [R: S1
  report Sec. 5]. Noted so a parcel does not re-derive it.

## 3. Per-function designs

Notation: destination precision `p` = 11/24/53; a finite operand
decodes as `(-1)^s * M * 2^E` with `M < 2^p` (the `msf_decode`
convention [R]). `o(v)` is the odd part of integer `v`.

### 3.1 rSqrt(x) = 1/sqrt(x) - exact, no new storage width

Decision [D, prototyped bit-exact]: normalize subnormals by exact
left shifts to `x = M' * 2^E'`, `2^(p-1) <= M' < 2^p`; if `E'` is
odd, double `M'` (now `< 2^(p+1)`) and decrement `E'`. With
`S = p + 9 + (p-1)/2` (25/44/88), let `Q = isqrt(floor(2^(2S)/M'))`.
Then Q is exactly `floor(2^S / sqrt(M'))` (integer lemma:
`isqrt(floor(A)) = floor(sqrt(A))` for `A >= 0`), lies in
`(2^(p+8), 2^(p+10)]` (binary64: 62 bits), `sticky` iff
`Q^2 * M' != 2^(2S)`, and one pack of `(0, -S - E'/2, Q, sticky)`
decides all four modes. C realization follows the shipped craft:
long division of the single-bit dividend `2^(2S)` by `M'`
(`div_core` loop shape, remainder `< 2^(p+1)`) or, simpler,
`sqrt_core`-style bit search on Q with the comparison
`Q^2 * M' <= 2^(2S)` done as a **split-u128 compare**: at the
binary64 bound `Q < 2^62`, write `Q^2 = a*2^64 + b` in one
existing `msf_u128_mul_u64_u64`; both `M'*a < 2^114` and
`M'*b < 2^118` fit `msf_u128`, and the pair compares against the
power of two limbwise. Logical decision width `3p + 19 <= 178`
bits (the survey's "~3p" [R] made exact); no new storage width.
Both realizations are proven-equivalent to the Python prototype
that exhausted binary16 against MPFR [M, Sec. 6]; the parcel
picks one and says so in its WIDTHS row (new row: `r_sqrt`,
width "128-bit + split compare (178-bit logical)").

Degenerate ranges [D]: the result range is strictly interior at
every format - binary16 `[2^-8.01, 2^12]`, binary32
`[2^-64.01, 2^74.5]`, binary64 `[2^-512.01, 2^537]` - so
overflow and underflow are **unattainable**, matching Table 9.1's
silence (extract p060 L33). The only flags ever raised are
invalid (negative / signaling), divideByZero (signed zeros),
inexact. Exactness: result exact iff `M'` is a perfect square
(sticky criterion); 20 exact of 31,743 positive-finite binary16
inputs [M]. Ties are unattainable [D]: a midpoint result would be
an odd dyadic `y > 1` significant bits `p+1`, forcing `M'` to be
the reciprocal square of an odd `> 1` - impossible for an integer.
Cost class: one `sqrt_core`-scale loop (~62 iterations of
64x64->128 multiply + compare at binary64) [D by shape].

### 3.2 hypot(x,y) = sqrt(x^2 + y^2) - exact inside u128

Decision [D, prototype-validated]: order `|a| >= |b|`. Anchor a
128-bit window at the top of `a^2` (`<= 2p <= 106` bits): form
`TOT = a^2 + trunc(b^2 aligned)` with a separate sticky for every
bit of `b^2` falling below the window - truncation, **not** a jam
into the sqrt input (a jammed sum can cross a square boundary and
fabricate exactness; the floor-sum lemma
`isqrt(floor(N)) = floor(sqrt(N))` plus `sticky = tail OR
(remainder != 0)` is the sound form, and is what the prototype
implements). Finish with the `sqrt_core` scaling (~120-bit
radicand, 61-bit root) and one pack. Width audit: squares
`<= 106` bits, sum `<= 107` bits, alignment shift unbounded but
jam-class exact - **no new width** (new WIDTHS row `hypot`,
"128-bit anchored sum + sticky", refining the survey's "wide
accumulator of 4.5 kin" guess [R]). Only the top ~107 bits of the
sum can move a `p+2`-bit root decision, because the decision is
floor+sticky at root scale, not relative approximation [D].

Overflow is attainable only through the true value (max
`sqrt(2)*Fmax`) and is the pack's call; underflow only when both
operands are tiny and the true sum's root lands subnormal
inexact - also the pack's call [D]. Exactness iff sqrt remainder
zero and no tail (e.g. 3-4-5); **ties are attainable** - two
binary16 midpoint cases are measured in Sec. 6 with kernel
verification in all modes [M], which is why the floor (not jam)
form is mandatory. Signs: function is even in both operands
(extract p061 L37); result sign is always `+`, including `+0`
and `+inf` deliveries [R+D].

### 3.3 pown(x,n) = x^n - capped interval powering + exact tie path

Structure (finite nonzero x, `n != 0`; specials in Sec. 5):
sign = `sign(x)` iff n odd. Work on `|x| = M * 2^E`, with
`o = o(M)`, `M = o * 2^v`.

1. **Trivial/exact paths.** `|x| = 1` (`M` a power of two with
   `E + log2 M = 0`): result `1` or `-1` by parity. `o = 1`
   (x a power of two): exact exponent arithmetic into one pack;
   over/underflow decided by the pack, ties exact. `n = ±1`:
   identity / one exact division (`div_core` pattern).
2. **Certain over/underflow by exponent bounds.** From
   `bitlen(M)`, `log2|x| ∈ [E+L-1, E+L)` (L = bit length).
   If the whole interval `n * log2|x|` lies above `emax+1`,
   feed the pack the synthetic `(sign, emax+2, 1, sticky=1)` -
   overflow + inexact with mode-correct delivery follow [D].
   If it lies below half the smallest subnormal ulp
   (`2^(emin-p)` in exponent terms `emin-p-1` for the value),
   feed `(sign, emin-p-8, 1, sticky=1)`: every value in
   `(0, 2^(emin-p-1))` packs identically (round-to-nearest
   zero, directed to zero or the smallest subnormal by mode
   and sign), and inexact+underflow are certain since no
   nonzero representable lives there [D]. This decides all
   sufficiently large `|n|` except `|x|` near 1, where step 3
   remains bounded because an in-range result bounds
   `|n * log2|x|| <= ~2149` (binary64 span) [D].
3. **Capped interval powering** for the rest: binary
   exponentiation keeping, per factor, top-W bits plus sticky
   and a proven relative error bound (`trig_decide` shape),
   stages W = 192 then 384. At most 63 squarings + 63
   multiplications for any int64 `n` - the loop count is
   `O(log|n|)`, never `O(|n|)`; huge `|n|` with an in-range
   result (measured possible: near-1 bases, Sec. 6) costs the
   same as small `|n|` [D]. For `n < 0`, interval-power the
   denominator `|x|^|n|` and finish with one exact integer
   division of a power of two by each endpoint (`div_core`
   pattern), feeding endpoint packs.
4. **Exact tie / representability path.** For `n > 0` the value
   is dyadic; it is a midpoint or representable only if its
   odd part `o^n` fits `p+1` bits [D: a midpoint is
   `odd * 2^k` with the odd part `< 2^(p+1)`, and
   `o(M^n) = o(M)^n`]. Deciding this is exact and cheap:
   if `|n| * (bitlen(o)-1) >= p+2` the odd part certainly
   exceeds (value inexact, non-tie); otherwise `o^|n|` has
   `<= 2p+3 <= 109` bits and is computed exactly - and in
   that case the whole capped computation is exact (the
   value has `<= p+2` significant bits), so ties and exact
   results are decided by the pack from true bits, never by
   an interval. For `n < 0` ties/exactness require `o = 1`
   (else the value is non-dyadic), already in path 1 [D].
   The characterization held on 154,724 measured binary16
   cases with 330 ties found, 0 violations [M, Sec. 6].

Widths (new class, WIDTHS row per parcel): capped limbs W =
192/384 (6/12 x 32-bit), transient exact products `2W <= 768`
before capping (24 limbs), odd-part check `<= 128` bits.
Nothing exceeds the shipped decimal accumulator's 2560-bit
precedent class [R]. The open obligation is leg (c): a proof
(or quoted worst-case bound) that stage W=384 decides every
binary32/64 input outside the exact path - measured binary16
margins are <= 15 extra bits over all `x` for small `n` and
<= 3 in near-1 large-`n` samples [M], but samples are not the
proof. Priced in Sec. 8; this is the GO-condition.

### 3.4 compound(x,n) = (1+x)^n - pown on an exact wide base

Form `B = 1 + x` exactly as a dyadic integer: with `x = ±M * 2^E`
(`E < 0` case), `B = (2^(-E) ± M) * 2^E`; the integer has at most
`max(p, -E+1) <= 1075` bits at binary64 (smallest subnormal `x`
gives `2^1074 + 1`), `<= 150` at binary32, `<= 25` at binary16
[D]. For `E >= 0`, `B` is an integer `<= 2^(p)+2^E` handled by
the same `(Mb, Eb)` normal form. Then `compound = pown(B, n)`
through Sec. 3.3 verbatim, including the odd-part tie path on
`o(Mb)` (ties measured at binary16: 22 in sample [M]). The wide
base enters capped powering by one exact reduce step (top W
bits + sticky + exactness flag); no product wider than Sec. 3.3's
`2W` arises, and the 1075-bit base is storage, not a new
arithmetic width class (WIDTHS row: `compound` base "exact
<=1075-bit integer, reduced to capped class before powering").
`B ∈ [0, ∞)`, so results are never negative [D]. `B = 0`
(`x = -1`) and `B = 1` (`x = ±0`) are specials/anchor paths,
never reaching powering (Sec. 5). Overflow/underflow in
Table 9.1 (extract p060 L34) arise through the same degenerate
bounds as pown with `bitlen(Mb)` interval arithmetic [D].

### 3.5 rootn(x,n) = x^(1/n) - three routes by |n| regime

Finite nonzero x, `n != 0`; sign carried iff `x < 0` and `n` odd
(else `x < 0` is invalid, extract p060 L37).

1. **`n = 1`**: identity (exact, no flags beyond NaN matrix).
   **`n = -1`**: one exact reciprocal division - the only
   `n` that can overflow/underflow [D: for `|n| >= 2`,
   `|y|` lies in `[2^-537, 2^512]` at binary64, matching
   Table 9.1 listing over/underflow only at `n = -1`,
   extract p060 L38]. **`|x| = 1`**: `±1` exact by parity.
2. **Exact scaled-integer root** (decides small-to-mid `|n|` with
   zero margin assumptions): `Q = floor(|y| * 2^S)` by binary
   search / Newton on integer compares `Q^|n|` vs the scaled
   target (reciprocated compares for `n < 0`), powers capped
   just above the target's bit length with early abort. Total
   exact width `B ≈ |n|(p+9) + p`; cap the route at
   `B <= 4096` bits (128 limbs, 512 B stack) i.e. `|n| <= ~65`
   binary64, `~170` binary32, `~200` binary16. Exactness iff
   the final power compares equal: equivalently `o(M)` a
   perfect `|n|`-th power with exponent divisibility [D];
   92 exact results in the measured sample, 0 false-exact [M].
3. **Interval search + collapse** (large `|n|`): binary-search
   the destination candidate directly, deciding each probe by
   comparing `candidate^|n|` against `x` with capped interval
   powering (Sec. 3.3 helper, W = 192/384). Once `|n|` is large
   enough that `y` is within a few ulp of 1, only comparisons
   against thresholds `(1 ± k*2^-p)^n` remain, decidable in
   closed form by exact binomial bounds (Bernoulli lower,
   k-term partial sums with ratio-bounded tails) in
   `O(p + log|n|)`-bit rationals: at binary16 all 528 measured
   near-1 threshold decisions closed (490 on the one-term
   bound, 38 within 40 terms, 0 undecided; 264 verified
   against exact big powers) [M]. Perfect-power equality is
   excluded in advance by route 2's odd-part test on `M`
   (`<= 53` bits - always cheap) [D].

Widths: route 2 cap 4096 bits is the bundle's widest class (new
WIDTHS row `rootn`, stated cap + abort rule); route 3 reuses the
capped class. Leg (c) obligation: prove route 3's stage-384
interval (outside binomial-decidable and exact cases) never
straddles - the mid-`|n|` seam between routes 2 and 3 is where
the proof must bite. This is the thinnest measured leg in the
bundle (binary16 small-`|n|` prototype used a 200-bit exact
search [M], which *is* route 2 at that format, so binary16 is
fully decided by exhaustion at gate time regardless) and the
reason rootn goes last / defers whole.

## 4. Width audit against docs/WIDTHS.md

Existing classes [R]: add/sub/mul/fma/div/sqrt/remainder/
conversions all rest on the 128-bit significand + sticky pack
interface; decimal rests on 2560 bits. The shipped trig TU adds
a de-facto 160/256/384-bit staged class inside `msf_math.c`
(not a WIDTHS row; rested in its design entry) [R].

| New WIDTHS row | Width | Why exact / bounded |
|---|---|---|
| `r_sqrt` | 128-bit storage; 178-bit logical compare (split) | Sec. 3.1 bounds `Q < 2^62`, `M' < 2^54`; both partial products `< 2^118` |
| `hypot` | 128-bit anchored sum + sticky | squares `<= 106` bits; floor-sum + sticky lemma (Sec. 3.2) |
| `pown` / `compound` capped powering | W = 192/384 limbs; transient `2W <= 768`; compound base `<= 1075`-bit storage | interval endpoints + exact odd-part path (Sec. 3.3-3.4); stage termination = Sec. 8 obligation |
| `rootn` exact route | capped `B <= 4096` bits with early-abort compares | target bit length `|n|(p+9)+p`; above cap, route 3 (Sec. 3.5) |

No existing row widens; the pack interface is untouched. The
4096-bit rootn cap exceeds the 2560-bit decimal accumulator in
bits but is compare-only limb storage (512 B), rested explicitly
so the "nothing widened silently" rule holds [R: WIDTHS header].

## 5. Specials tables (Clause 9.2.1)

Traceability: extract page = S1 PDF-page file (`p060` = printed
p.59 Table 9.1; `p063`/`p064` = printed pp.62/63 Sec. 9.2.1;
`p059` = printed p.58 Sec. 9.2 head rules). Common rules first;
per-function tables list only deviations/additions. "qNaN
(matrix)" = payload/sign per Sec. 2.2 (`msf_nan_delivery`);
"default qNaN" = positive canonical (`0x7e00` / `0x7fc00000` /
`0x7ff8000000000000` [R: msf_formats.h]). Flags use Clause 7
names; `inexact` never accompanies an exact, infinite-pole, or
NaN delivery (Sec. 2.2). Cells marked [D] are derived (affine
limit / sign composition), [2R] need the parcel second reader.

Common (all five): signaling NaN float operand -> quieted
delivery + invalid (p059 L25-29); quiet NaN float operand ->
qNaN (matrix), no flag, except the stated cells below (p059
L26-27); finite outside-domain -> default qNaN + invalid (p059
L30-31); simple pole at finite operand -> correctly signed
infinity + divideByZero, no inexact (p059 L32-33). The integer
operand `n` is never a NaN (int64).

### 5.1 rSqrt (domain `[0,+inf]`, p060 L33; p063 L27)

| Input | Result | Flags | Ref |
|---|---|---|---|
| `+0` | `+inf` | divideByZero | p063 L27 |
| `-0` | `-inf` | divideByZero | p063 L27 paired-sign [2R: MPFR disagrees, Sec. 6] |
| `+inf` | `+0` | none | p063 L27 |
| `-inf`, finite `< 0` | default qNaN | invalid | p060 L33 |
| qNaN / sNaN | matrix | invalid iff sNaN | Sec. 2.2 |
| finite `> 0` | Sec. 3.1 | inexact iff sticky | - |

### 5.2 hypot (domain all pairs, p060 L32; p063 L26)

Evaluation order is part of the semantics: (1) any signaling
NaN -> matrix + invalid (p059 L28-29 "for all operations");
(2) any `±inf` operand -> `+inf`, no flag - **including with a
quiet NaN other operand** (p063 L26, both orders stated);
(3) any quiet NaN -> matrix; (4) finite path. `hypot(±0,±0)`
= `+0` (p063 L26). inf+finite -> `+inf` is [D] from the domain
including infinities with exact function value `+inf`; MPFR
execution agrees (Sec. 6). `hypot(±inf, sNaN)`: step (1) wins
-> qNaN + invalid [D from p059 L25 which is unconditional for
signaling; the p063 exception names only qNaN] [2R].

### 5.3 compound (domain `[-1,+inf] x Z`, p060 L34; p063 L31-39)

| Case | Result | Flags | Ref |
|---|---|---|---|
| `(x, 0)`, `x >= -1` or x qNaN | `1` | none | p063 L32 |
| `(x, 0)`, `x < -1` (incl `-inf`) | default qNaN | invalid | p063 L38 + L32 scope [2R precedence; MPFR agrees] |
| `(sNaN, 0)` | quieted | invalid | p059 L28-29 over L32 |
| `(-1, n<0)` | `+inf` | divideByZero | p063 L33 |
| `(-1, n>0)` | `+0` | none | p063 L34 |
| `(±0, n)` any n | `1` | none | p063 L35 |
| `(+inf, n>0)` / `(+inf, n<0)` | `+inf` / `+0` | none | p063 L36-37 |
| `(x<-1, n)` any n | default qNaN | invalid | p063 L38 |
| `(qNaN, n!=0)` | matrix | none | p063 L39 |
| finite `x > -1` | Sec. 3.4 (always `>= 0`) | ovf/unf/inexact via pack | p060 L34 |

### 5.4 rootn (domain all x, `n` in Z; p060 L35-39; p063 L40-52)

| Case | Result | Flags | Ref |
|---|---|---|---|
| `(x, 0)` any x | qNaN (matrix payload if x NaN, else default) | invalid | p060 L36 [2R payload choice] |
| `(±0, odd n<0)` | `±inf` (sign of zero) | divideByZero | p063 L41 |
| `(±0, even n<0)` | `+inf` | divideByZero | p063 L42 |
| `(±0, even n>0)` | `+0` | none | p063 L43 - note `rootn(-0,2)=+0` differs from `sqrt(-0)=-0` (p063 L51-52) |
| `(±0, odd n>0)` | `±0` | none | p063 L44 |
| `(+inf, n>0)` / `(+inf, n<0)` | `+inf` / `+0` | none | p063 L45, L48 |
| `(-inf, odd n>0)` / `(-inf, odd n<0)` | `-inf` / `-0` | none | p063 L46, L49 |
| `(-inf, even n)` any sign of n | default qNaN | invalid | p063 L47, L50 |
| finite `x<0`, even n | default qNaN | invalid | p060 L37 |
| finite `x<0`, odd n | negative root (Sec. 3.5) | as computed | domain |
| overflow/underflow | only `n = -1` | via pack | p060 L38 + Sec. 3.5 [D] |

### 5.5 pown (domain all x, `n` in Z; p060 L40; p064 L3-14)

| Case | Result | Flags | Ref |
|---|---|---|---|
| `(x, 0)`, x not sNaN (incl qNaN, `±inf`, `±0`) | `1` | none | p064 L4 |
| `(sNaN, 0)` | quieted | invalid | p064 L4 scope + p059 |
| `(±0, odd n<0)` | `±inf` | divideByZero | p064 L5 |
| `(±0, even n<0)` | `+inf` | divideByZero | p064 L6 |
| `(±0, even n>0)` | `+0` | none | p064 L7 |
| `(±0, odd n>0)` | `±0` | none | p064 L8 |
| `(+inf, n>0)` / `(+inf, n<0)` | `+inf` / `+0` | none | p064 L9, L12 |
| `(-inf, odd n>0)` / even | `-inf` / `+inf` | none | p064 L10-11 |
| `(-inf, odd n<0)` / even | `-0` / `+0` | none | p064 L13-14 |
| finite | Sec. 3.3; sign iff x neg & n odd | ovf/unf/inexact via pack | p060 L40 |

Second-reader list for parcel entry gates (SF-1 Sec. 11 item 2
makes this mandatory anyway): rSqrt `-0` sign; hypot
`(±inf, sNaN)` order; compound `(x<-1, 0)` precedence; rootn
`(x, 0)` payload; hypot inf+finite [D] cell. Everything else
above is stated verbatim in the extracts.

## 6. Oracle recipes and executed probes

MPFR emulation recipes (proven Step 0b, binary64 completed by
the trig spike) [R]: per format precision/emin/emax =
binary16 `11 / -23 / 16`, binary32 `24 / -148 / 128`, binary64
`53 / -1073 / 1024`; operation path = `mpfr_op` then
`mpfr_subnormalize`, skipped on zero/inf/NaN intermediates;
narrowing path adds `mpfr_check_range` between set and
subnormalize. Generator flags are always derived from exact
state, never transcribed (Step 0b measured MPFR flag divergence;
this study re-confirmed: MPFR raises no invalid-class flag on
any domain error below [M]).

MPFR entry points (header declarations read [M], 4.2.2):
`mpfr_rec_sqrt`, `mpfr_hypot`, `mpfr_pow_si` + `mpfr_pow_z`
(mpz exponent), `mpfr_compound_si`, `mpfr_rootn_si/ui`.
Measured host fact: `sizeof(long) == 4` (->
`LONG_MAX = 2147483647`), so the `_si` oracles cover
`|n| <= 2^31 - 1` only. Coverage plan per function:

| Function | MPFR decider | Beyond-`long` / fences |
|---|---|---|
| rSqrt | `mpfr_rec_sqrt`, all formats | one fenced cell: `rSqrt(-0)` sign (below) |
| hypot | `mpfr_hypot`, all formats | specials agree incl. inf-over-NaN [M]; flags never from MPFR |
| pown | `mpfr_pow_z` covers full int64 | executed at `±2^40` exponents [M] |
| compound | `mpfr_compound_si` to `|n| <= 2^31-1` | larger `|n|`: exact-Python generator leg (Sec. 3.4 algorithms), cross-decided vs MPFR over the overlap |
| rootn | `mpfr_rootn_si` to `|n| <= 2^31-1` | larger `|n|`: same exact leg (collapse regime: threshold compares); `n = 0` returns NaN with no flag [M] - invalid from the table |

Executed results (scripts and logs in `scratch/sf2-algebraic/`):

1. **rSqrt binary16 exhaustive vs MPFR** [M] (`rsqrt_mpfr.c`,
   `proto_alg.py:rsqrt_proto`, `check_rsqrt.py`,
   `out/check_rsqrt.log`): `TOTAL=262144 NUMERIC_COMPARED=126984
   NAN_CLASS_COMPARED=135160 FENCED_NEGZERO=4 MISMATCH=0`.
   All 65,536 encodings x 4 modes; numeric bit-exact, NaN by
   class (payloads are the project matrix's, not MPFR's). The
   4 fenced cases are input `-0` x modes: prototype `-inf`,
   MPFR `+inf`; the clause's paired-sign statement (Sec. 5.1)
   outranks MPFR on specials meaning (SF-0 authority order),
   so MPFR must not generate that cell. Independent Fraction
   midpoint-square decider agrees on 12,000 sampled cases,
   0 disagreements. This is the brief-required exhaustive leg,
   and it validates the exact C design (same Q, same sticky),
   not merely the mathematics.
2. **rSqrt CORE-MATH corroboration** [M] (`cm_rsqrt_harness.c`
   over public `cr_rsqrtf16/cr_rsqrtf/cr_rsqrt`; units compiled
   unopened, regular positives only): binary16 122,880 +
   binary32 240,000 + binary64 160,000 comparisons vs the
   prototype across 4 modes, **0 disagreements**. Corroboration
   role only - it also incidentally validates the prototype's
   binary32/64 scaling. This licenses pricing a one-time
   recorded binary32-exhaustive differential at parcel time
   (`cr_rsqrtf` as fast decider, MPFR adjudicating samples and
   any disagreement) [E: minutes-to-hours class by Step 0b
   foreign-f32 throughput records; not run here].
3. **MPFR specials probe, 54 cells at binary64** [M]
   (`mpfr_specials.c`, `mpfr_rootn0.c`): class/sign/value agree
   with Sec. 5 on every cell except `rSqrt(-0)` (fenced above),
   including: hypot inf-over-NaN in both orders, `(-0,+0)->+0`;
   `pown(qNaN,0)=1`, full signed zero/inf parity trees;
   `compound(-1.5,0)->NaN` (supports the Sec. 5.3 precedence),
   `(-1,±)`, `(±0,n)=1`, `(+inf,±)`; rootn signed-zero parity
   incl. `(-0,2)->+0`, `(-inf,even)->NaN`, `(-8,3)=-2` exact with
   inexact clear on all five exact anchors. MPFR divideByZero
   flag tracks the poles; its invalid-class flag never rises -
   fenced as unusable, already known [R Step 0b]. MPFR is
   therefore licensed as value decider on finite regular
   inputs and as class corroborator on specials, never as
   flags/payloads authority - exactly the Step 0b fences.
4. **Prototype cross-checks** [M] (`proto2.py`-`proto5.py`):
   hypot kernel vs independent Fraction sqrt-decider:
   153,600 decisions (pool pairs + 30k random + 8k subnormal
   pairs, x 4 modes, bits+flags), 0 disagreements, 440 exact
   results seen. Hypot midpoint ties found (2 in 136,384):
   e.g. `hypot(395*2^-22, -1659*2^-24) = 2291*2^-24` exactly at
   a midpoint; kernel matches the exact decider in all 4 modes
   on both ties (to-even splits correctly per candidate parity).
   pown ties are common at binary16: 328 + 2 across scans
   (e.g. `(47/4096)^2 = 2209*2^-24`, midpoint, to-even chooses
   down, inexact set) and 22 for compound; tie characterization
   (Sec. 3.3 step 4) verified on 154,724 cases, 0 violations.
   Margins (extra bits beyond the round bit): pown max 15
   (all-x, small `n`), 13 (sampled larger `n`), compound max
   14, near-1 large-`n` pown max 3 in samples - lower bounds
   on worst cases, stated as such. rootn exact-search decider:
   65,000 decisions sampled, 0 false-exact; large-`n` binomial
   collapse: 528/528 decided, 264 exact-verified, 0 wrong.
5. **CORE-MATH availability, listing only** [M]: units for
   `rsqrt`, `hypot`, `pow` at all three formats; `compound` at
   binary16/32 only; no `pown`/`rootn` units (`pow` is a
   different function and must not be used as a `pown` oracle
   outside integral-exponent agreement checks - expensive and
   unnecessary given `mpfr_pow_z`). hypot units unexecuted
   here (priced, Sec. 9). The Step 0b `cr_cospif` fence is
   untouched and irrelevant to this bundle.

## 7. Inventory shape

### 7.1 Signature classes (lead seam)

Current generator facts [R: tools/gen_tables.py]: `math_un`
already expands homogeneous unary `attr`+`flags` families and is
in `REPLAYABLE`. Two additions, each a few lines mirroring
existing branches plus tests:

- `math_bin`: homogeneous binary `f(f,f)->f`, same expansion
  shape as `minmax`/`remainder` (lines 131-137) but under its
  own token (reusing `minmax` for hypot would typecheck -
  rounding comes from the row - but would lie in dispatch
  metadata; refused). Join `REPLAYABLE` + `SIGS`.
- `math_int`: `f(f, i64)->f` with `argkinds = [F, I64]`.
  `MSF_AK_I64` already exists in the runner's kind-width table
  [R: tests/runner.c], and vector args are already hex bit
  patterns truncated to kind width [R: VECTORS.md], so `n`
  rides the existing wire shape as 64-bit two's complement -
  **no new vector shape, no CDC harness change anticipated**
  [D; board replay is line-based over the same runner kinds -
  board lead confirms at parcel time]. Watched-failing seam
  controls, SF-1 Sec. 4 style: unknown sig token refuses;
  a `math_int` line with float-width `n` truncation refuses;
  Tier 1 invariant still prints 783.

API names follow generation: `msf16_r_sqrt`, `msf16_hypot`,
`msf16_pown` (`pown`/`rootn`/`compound` take `int64_t n` second),
at f16/f32/f64 - token `r_sqrt` per the survey's hump precedent
[R Sec. 4.6.1]. Kernels live in new `src/msf_alg.c`, one core
per family parameterized by format like `trig_core` [R+D].

### 7.2 Proposed operations.tsv rows (verbatim shape)

Columns: `op std_name clause sig rounding flags wave authority
vectors comparison tier claim` [R header]. Wave `5` proposed
(SF-2 wave; lead/owner pin - if wave 4 continues, only this
column changes). All rows tier 2, claim `C-754`, comparison
`exact`, authority `mpfr-exact` (specials cells table-decided
inside the generator and cross-checked, trig precedent):

```
r_sqrt    rSqrt     9.2  math_un   attr yes 5  mpfr-exact  directed-alg;ties;seeded-random  exact  2  C-754
hypot     hypot     9.2  math_bin  attr yes 5  mpfr-exact  directed-alg;ties;seeded-random  exact  2  C-754
compound  compound  9.2  math_int  attr yes 5  mpfr-exact  directed-alg;ties;n-classes;seeded-random  exact  2  C-754
rootn     rootn     9.2  math_int  attr yes 5  mpfr-exact  directed-alg;n-classes;seeded-random  exact  2  C-754
pown      pown      9.2  math_int  attr yes 5  mpfr-exact  directed-alg;ties;n-classes;seeded-random  exact  2  C-754
```

Manifest arithmetic [M current state]: COVERAGE carries 822
implemented rows (Tier 1 = 783 `required`, Tier 2 = 39
`C-754`), `implemented.tsv` matching. At full bundle closure:
**837 implemented (783 + 54)**, Tier 2 split 39 + 15. Per-tier
headline counting stays mandatory (SF-1 Sec. 8).

### 7.3 Committed-vector volumes (project idiom)

Idiom anchors [M]: today's committed surface is 42 files /
146,488 lines all replayed in `smoke`; trig committed 11,166 /
14,242 / 18,090 lines (f16/f32/f64, two functions). One new
generator `tests/gen_vectors_alg.py` + C decider
`tests/alg_decider.c` (MPFR, trig pattern), one provenance tag
family `mpfr-alg:{specials,directed,ties,n-classes,seeded,
f16-exhaustive}` (tag table has used 18 of 128 slots [M
VECTORS.md count]). Exact-Python legs tag `exact-py-alg:...`
only where they decide (beyond-`long` `n`, Sec. 6) and are
cross-decided in the generator against MPFR over the overlap -
disagreement aborts generation.

Proposed committed lines per function per format [E, structured
like trig]: rSqrt ~1,200 (specials tree, square/non-square
lattice, binade edges `±3 ulp`, seeded); hypot ~2,500
(boundary pool squared, exponent-span lattice both orderings,
subnormal-corner pairs, measured ties, seeded); each float-int
~3,000 (`x`-pool (zeros/infs/±1/neighbors-of-specials/binade
edges/seeded) x `n`-classes `{0, ±1, ±2, ±3, ±5, ±10, ±53-ish
parity/boundary, ±2^31±1, ±2^62, INT64_MIN}`, tie pool for
pown/compound, perfect-power pool for rootn). Bundle committed
total `~3 * (1200+2500+3*3000) ≈ 38k` lines (+26% smoke,
inside SF-1's ~2x budget [R]). Generated, not committed:
binary16 rSqrt exhaustive 262,144 (parcel gate; cheap - this
study's probe is the shape), binary16 hypot
second-operand sweep vs boundary pool (minmax-sweep pattern),
float-int binary16 `x`-exhaustive x small-`n` set, seeded
binary32/64 volume per SF-1 Sec. 4 budgeting; binary32 rSqrt
exhaustive as a one-time recorded run (Sec. 6 item 2).

Negative controls per parcel (watched failing): 1-ulp-moved
hardest case; specials mutants (`hypot(qNaN,inf)->NaN`,
`pown(qNaN,0)->NaN`, `rootn(-0,2)->-0` [sqrt semantics],
`compound(-1,-1)` finite); inexact stripped from a known tie;
directed-mode swap on a subnormal-output pown case; truncated
stage width (W=192 forced, or capped mul at 128) must fail the
directed margin family; odd-part path disabled must fail the
tie family (pown/compound); `n` truncated to 32 bits in the
runner must refuse (seam control).

## 8. Parcel split, price, stop conditions

Hours are worked hours [E] for implementation + generator +
design entry + gates through `standard` green and sampled board
replay, **excluding** lead merge and planted-copy verification
(add ~30-50% programme-side). Anchor: the trig spike priced a
harder 6-row K3 bundle at 3-5 days [R]; the algebraic kernels
are K2-class (exact decisions, no constants tables, no argument
reduction), with specials trees as the weight on float-int.

| Parcel | Contents | Rows | Depends on | Hours [E] |
|---|---|---|---|---|
| S (lead) | `math_bin`/`math_int` sig classes, dispatch, seam controls, this study's rows registered planned | 0 | - | 6-10 |
| A1 | rSqrt + `msf_alg.c` birth + alg generator/decider v1 + f16 exhaustive gate | 3 | S | 16-24 |
| A2 | hypot (evaluation-order specials) | 3 | S, A1 generator | 12-20 |
| A3 | capped-power helper + pown (+ leg-(c) spike below) | 3 | S | 30-45 |
| A4 | compound on A3 helper | 3 | A3 | 10-16 |
| A5 | rootn (3 routes) | 3 | A3 helper | 25-40 |
| spike | leg-(c) closure for pown/compound/rootn stage margins (below) | 0 | before A3 merges | 8-16 |

Bundle total: ~99-155 h + spike, in five independently
stoppable three-format parcels after a 6-10 h seam. Partial
delivery values: after A2 the bundle has its two unconditional
families (6 rows); A4 without A5 is complete (12 rows) - rootn
is the named deferral candidate, whole-family, if the window
cuts. No parcel may merge a single format (parity) - sequence
inside parcels f16 -> f32 -> f64 for de-risking only.

**Leg-(c) spike price (the GO-conditions)**: close stage-384
termination outside exact paths for pown (odd-part gap
arguments - values are integer powers, so distance to a
midpoint is a Diophantine quantity; the spike must either prove
a usable lower gap for in-range results at binary32/64, or quote
a published hardest-to-round bound for integer powers with its
source, or return with a widened escalation + measured
worst-case search), compound (same on wide odd bases), rootn
(mid-`|n|` seam). Also in the spike: timed MPFR-C decider rates
for the chosen vector volumes (unmeasured here) and, if the
recorded binary32 rSqrt exhaustive is wanted, its harness (~2 h
of the spike; Step 0b rates suggest hours-scale wall [R]).

Stop conditions: A1/A2 - any exhaustive/sampled disagreement
unadjudicated, or a second-read cell flips (Sec. 5 list)
without owner ruling: stop, do not relabel. A3-A5 - spike
returns without a closing margin argument: that family defers
(no C-ULP relabel exists in this window [R SF-1 Sec. 8]);
binary16-green alone never ships (parity). Board: sampled
replay hash-identical per parcel; RP2040 cost by shape [D]:
rSqrt/hypot are `sqrt_core`-class loops; pown `<= 126` capped
6-limb muls at stage 1; rootn exact route worst-case bounded by
the 4096-bit cap with early abort - flash/stack measured at
parcel time (trig parcel precedent: few KB text, < 1 KB stack
class), not estimated numerically here.

## 9. Unresolved, priced - and what was not read or executed

1. Leg-(c) margin proofs (pown/compound/rootn) - the spike
   above. Failure mode if skipped: stage-384 straddle fallback
   would be an unproven defined-behaviour branch - do not ship.
2. Five [2R] specials cells (Sec. 5) need the parcel second
   reader; `rSqrt(-0)` additionally contradicts MPFR, so its
   vector must be generator-table-decided, never MPFR-sourced.
3. CORE-MATH `cr_hypot*` execution unprobed (listings only);
   ~1 h with the Sec. 6 harness shape when A2 wants the
   corroboration leg. `cr_pow*` deliberately not used.
4. MPFR decider throughput for the Sec. 7.3 volumes unmeasured;
   ~15 min timing run at A1 planning (0b precedent item).
   Beyond-`long` exact-Python generator leg is prototyped in
   spirit (`proto2/proto3` use exact big integers - 220k-bit
   exact powers ran in seconds [M]) but not productionized.
5. Board replay of `math_int` lines: shape-compatible by
   reading [R], not executed (no board work in a study); parcel
   sampled-replay gate carries it.
6. RP2040 flash/stack/time: unmeasured (nothing here compiled
   for target); parcel gates measure, trig-style.
7. Skipped reads, named: SF-0 (relied on via SF-1/survey
   restatements), the kissfft/interval/architecture surveys
   (out of this bundle's scope), `msf16.c`/`msf32.c` kernel
   bodies (per-format sqrt/div read in `msf64.c`; the .inc and
   shared decode/pack generalized design makes the f64 read
   representative - parcel confirms at implementation),
   `msf_string.c`, board/ tree. IEEE PDF never opened; S1
   extracts p059-p065 read in full.
8. Nothing with `cft` in its name was listed, searched, or
   opened. No prior-workflow scratch summaries were consulted;
   the only sibling artefacts consumed are the governing files
   the brief names (SF-1 in full, Clause 9 survey Sec. 4.6 with
   the Sec. 5 authority table head, Step 0b report in full,
   WIDTHS, roundpack/wide/decode/internal headers, msf64
   div/sqrt, msf_math.c, gen_tables expansion, operations/
   implemented/COVERAGE inventories, VECTORS.md, run.sh gates).

Artefacts (all `scratch/sf2-algebraic/`): this report;
`proto_alg.py`, `proto2.py`-`proto5.py` (decision prototypes +
censuses); `rsqrt_mpfr.c`, `check_rsqrt.py`; `mpfr_specials.c`,
`mpfr_rootn0.c`; `cm_rsqrt_harness.c`, `cm_cases.py`;
`env_probe.sh`, `run_*.sh`; logs in `out/`
(`check_rsqrt.log`, `proto2.log`, `proto3.log`, `proto4.log`,
`proto5.log`, `mpfr_specials.log`, `cm_rsqrt.log`,
`env_probe.log`, `rsqrt_mpfr.log`, `cm_cases.txt`,
`cm_out_*.txt`). Ledger: `ledger/study-sf2-algebraic.md`.
Repository `muse-softfloat`: untouched (`git status` clean at
`7ebbe70`).





