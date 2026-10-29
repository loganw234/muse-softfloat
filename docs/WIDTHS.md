# Internal widths, with proof notes

P0 record for the duty SF-0 Section 3.2 fixes: every operation computes
on exact integers wide enough that the only rounding event is the final
pack. This file fixes the width per operation class and says why it is
exact. A wave brief that needs a wider class restates this file in its
own commit; nothing here is widened silently.

Conventions: `p` is the destination precision. "Jam shift" means a right
shift that ORs every shifted-out bit into the new bit 0. A jam-shifted
value preserves everything a rounding decision can ask of discarded
bits: after the shift, bit 0 records nonzero-ness of the discarded
tail, so the tail's relation to zero and to the half-way point (decided
by the bits kept above bit 0 together with bit 0 as the round bit's
sticky) is unchanged. Jam shifts are the mechanism that makes a fixed
width exact for unbounded exponent differences.

| class | width | why it is exact |
|---|---|---|
| add/sub (binary64 worst) | 128-bit significand + sticky | Both operands enter as p-bit significands. Aligning the smaller by a jam shift of any size loses only jam-recorded tail bits. The sum of two aligned 128-bit values is exact in 128 bits plus carry into a guard position. Only the final pack rounds. |
| mul | 128-bit product | A product of two p-bit significands has at most 2p bits; binary64 needs 106, inside 128 with the pack's guard/round room above the kept precision. Cross-format sources decode exactly into their own p, so 2p_max bounds every instantiation. |
| fma | 128-bit product + jam-aligned addend + sticky | The exact product is 106 bits as above. The addend is aligned to the product's scale by a jam shift (left shifts are bounded because the product scale dominates or the addend does, and the dominant side sets the accumulator scale with the other side jam-shifted). One rounding, at the pack. |
| div | 128-bit quotient + exact remainder | Long division produces p+2 quotient bits and the exact remainder; the remainder's nonzero-ness (and its half comparison against the divisor) is the sticky/tie evidence. No quotient bit beyond those can change a rounding decision once remainder evidence is carried. |
| sqrt | 128-bit root + exact remainder | Integer sqrt of the (evened) significand at p+2 bits with the exact remainder; remainder zero iff the result is exact, remainder against root decides tie-adjacent cases. |
| remainder | 128-bit scaled operands | Exponent difference is reduced by repeated exact subtraction at bounded scale; the result, when defined, is exact and strictly narrower than the operands, so 128 bits never round it. |
| format conversions | source significand widened exactly | Widening is exact. Narrowing feeds the destination pack with the full source significand plus sticky from the source's own subnormals; no intermediate format is rounded through (no double rounding, SF-0 Section 2.3). |
| integer conversions | 128-bit | Destination integers are at most 64 bits; source significands at most 53. Shifts in either direction are exact or jam-recorded. |
| decimal (Wave 3 engine) | 2560-bit accumulator (80 x 32-bit limbs) | Binary-to-decimal expands m x 2^e exactly; the widest case is binary64 subnormals, m < 2^53 with a 5^1074 factor: 53 + ceil(1074 log2 5) = 2547 bits. Decimal-to-binary forms the exact rational from at most H = 20 digits (< 2^67) scaled by powers of ten inside the same bound before one rounding. 2560 covers both with margin; the Wave 3 brief re-derives the digit-side bound before shipping. |
| r_sqrt (Wave 5, SF-2 Step 2a) | 128-bit storage; 178-bit logical decision as a split compare over u128 | The kernel (`src/msf_alg.c`) bit-searches Q = floor(2^S / sqrt(M')) with S = p + 9 + (p-1)/2 over the normalized operand significand M' < 2^(p+1), testing candidates by the exact compare Q^2 * M' vs 2^(2S). At the binary64 bound Q <= 2^62 and M' < 2^54, so with Q^2 split at 2^64 both partial products M'*hi and M'*lo stay below 2^118 and fit the existing 128-bit multiply; the 3p + 19 <= 178-bit product is assembled limbwise for the compare only and never stored wider. Q has at least seven bits below the destination significand in every attainable (strictly interior, never subnormal) binade, so one pack rounds correctly; stickiness is the compare's own equality test, exact iff M' is a perfect square. |
| exp2/exp2m1 (Wave 5, SF-2 Step 3a) | 160/256/384-bit wide significands (wf_t over 32-bit limbs) with relative error bounds 2^-147/2^-243/2^-371, plus exact endpoint composition in a 2048-bit (64-limb) pack-scale integer | The kernel (`src/msf_math.c`, explog section) splits x = n + f exactly (nearest integer n, dyadic f with \|f\| <= 1/2) and evaluates exp(f*ln2) or its expm1/delta forms by Taylor Horner at three Ziv stage widths, each a single truncating approximation A with generator-proven relative bound Ek (`tools/gen_explog_tables.py`: exact-rational recurrence over the ln2 floor constant, one multiply, Horner weights, and tails <= 2^-(W+24), 9-bit reserve). The 2^n factor is a pack exponent offset, never a multiply. Endpoints A +- A*2^-Ek are composed into exact result values at pack scale - (1-delta)*2^n by a 288-bit fixed-point subtraction, 1+m / 2^n(1+-m)-1 / 1-2^n*v by materialising the exact dyadic in a 64-limb integer (span proven under 1500 bits at binary64 from the decoded-exponent floor for \|x\| >= 1/2, and under 1460 bits for the near-1 bracket) - and packed through the shared 128-bit-plus-sticky pack; bit-and-flag agreement of the endpoints decides (rounding is monotone). Integer inputs bypass the kernel with exact 2^n / 2^n-1 / 1-2^n values (the only attainable exacts and ties: 2^x is irrational for non-integer dyadic x), and the exponent cuts pack proxy exact values proven to round identically. Stage 3 decides plain cases to ~318 extra bits beyond p against spike-measured published maxima of 60.5 extra bits (ledger/parcel-w5exp2.md). |
| log2/log2p1 (Wave 5, SF-2 Step 3b) | 160/256/384-bit wide significands (same wf_t) with relative error bounds 2^-146/2^-242/2^-370 (tiny path 2^-147/2^-243/2^-371), exact 1280-bit (40-limb) argument materialisation, floor-exact wide division, and exact endpoint composition in the same 2048-bit pack-scale integer | The kernel (`src/msf_math.c`, log section; ledger/parcel-w5log2.md) materialises w (x itself, or the exact wide 1+x for log2p1, span at most 1075 bits) as an exact big integer, splits 2^k*mm, recentres mm into [2^-1/2, 2^1/2) by the exact integer compare Wint^2 vs 2^(2top+1), and forms s=(mm-1)/(mm+1) by a floor-exact bit-by-bit wide division from separately normalized numerator/denominator bigs (the log2p1 wide-span truncation in those conversions is a named Ek line at 2 ulp-class per conversion; division error under 1 ulp - one truncating op). The atanh series t=(2/ln2)*s*A(s^2) runs at the same three Ziv widths with generator-proven Ek (`tools/gen_explog_tables.py`: bracket-floored 1/ln2 and 2/ln2, exact 1/(2j+1) entries, Horner weights at \|s\| <= 4143/24143, tails <= 2^-(W+24), 9-bit reserve); endpoints k+(t+-Ek) are materialised exactly at pack scale (span under 1473 bits at binary64: \|k\| < 2^11 over a correction down to 2^-1461), which is what decides the power-of-two attractor tail. log2p1 for \|x\| < 2^-8 takes a relative x*(1/ln2)*B(x) path (1/(j+1) entries) instead of forming 1+x. Exact results are exactly the powers of two (log2 of a dyadic is an integer or irrational, so the tie set is empty and every kernel result is inexact by proof), delivered as the exact integer k including for subnormal x. Stage 3 decides plain cases to ~317 extra bits beyond p against spike-measured published maxima of 60.5 extra bits (log2p1). |
| hypot (Wave 5, SF-2 Step 2b) | 128-bit anchored sum + sticky | With magnitudes ordered, both squares are single 128-bit products (<= 106 bits at binary64). The larger square is shifted so its top bit sits at bit 120 and the smaller square is aligned into the same window by truncation with a separate tail sticky (never a jam into the sqrt input - exact midpoint ties are attainable, so the floor-sum form is mandatory); the window sum stays below 2^122 inside the existing u128. The sqrt_core scaling finishes: a parity shift makes the window exponent even, giving a 119..122-bit radicand whose 60/61-bit integer root plus (tail OR parity-dropped OR remainder) sticky is the exact floor-at-scale the pack rounds once. The root has at least seven bits below the destination significand in normal binades and more below the subnormal ulp under the clamp, so overflow/underflow/inexact are the pack's judgements on true bits. |

| augmented add/sub (Wave 5, SF-2 Step 4) | exact 128-bit window (operand bit span <= 127) or verbatim far-operand pair (span > 127); one bits-only RTTZ pack for the head, exact integer residual for the tail | See the three-part proof below this table: window exactness and the span bound, the verbatim gap lemma, and representability of the residual (including the binade-crossing step). Flags never come from the head pack. |
| augmented mul (Wave 5, SF-2 Step 4) | exact 128-bit product (<= 2p <= 106 bits), tail split at the head grid | The product is the mul row's exact integer. Splitting it by p-bit integer rounding leaves a residual with at most p significant bits in every normal-head case (proof below); it is representable unless it has a set bit below the subnormal step, which is exactly the Clause 9.5 inexact-tail cell. The kernel tests representability exactly (significant bits, lowest set bit, top bit) rather than assuming the bound. |

Augmented proof notes (kernel `src/msf_aug.c`). Write a decoded
finite operand as a signed integer significand times a power of
two, significand below `2^p` at its own ulp exponent `e_i` (the
`msf_decode.h` form), and let `u0 = 2^(emin-p+1)` be the
subnormal step. Every finite operand is a multiple of `u0`.

(1) Window and verbatim split (add/sub). For nonzero operands
let `top_i = e_i + bitlen(sig_i) - 1` and define the span as
`max(top) - min(e) + 1`. If the span is at most 127, both
significands are aligned by plain left shifts (never a jam) at
`E = min(e)` inside the u128: each aligned magnitude is below
`2^127`, so the signed sum is exact in 128 bits. If the span
exceeds 127, the top gap between the operands is at least
`span - bitlen(sig_lo) >= 128 - p` (75/104 at binary64/32; at
binary16 the largest attainable span is 40, so this branch is
unreachable). The needed bound is only `p + 2` (55/26): the
grid step below the larger operand `hi` is `ulp(hi)` except
when `hi` is an exact power of two above the smallest normal,
where the step below is `ulp(hi)/2` (the binade-crossing
step); at the smallest normal the step below is `u0 =
ulp(hi)`, and a subnormal `hi` cannot occur at this span. So
half the smaller adjacent step is at least
`2^(top_hi-p-1)`, while `|lo| < 2^(top_lo+1) <=
2^(top_hi-p-1)` by the gap. The exact sum therefore lies
strictly between `hi` and either neighbouring midpoint,
`RTTZ(sum) = hi`, and the residual is the smaller operand
verbatim (effective sign applied). No wide accumulator is
ever needed.

(2) The add/sub residual is always representable. Scale so
the exact sum is an integer `S` at scale `E`. If the head is
zero or subnormal, then `|exact| < 2^emin` (a larger exact
value has a normal nearest neighbour); the exact sum is a
multiple of `u0` below `2^emin`, hence itself a subnormal or
zero, the head is exact, and the residual is zero. Otherwise
rounding to the format grid is rounding the integer `S` to
`p` significant bits: with `k = bitlen(S) - p > 0` (if
`k <= 0`, `S` is exact and the residual is zero), write
`S = q*2^k + w`, `0 <= w < 2^k`; the head is `q*2^k` or
`(q+1)*2^k` and the residual is `w` or `w - 2^k` at scale
`E`. This integer form is also the binade-crossing case:
just below a power of two the grid step is the one `k`
computed from the smaller bit length gives, and
`(q+1)*2^k` may be the power of two itself, with the
residual still of the form `w - 2^k`. It remains to show
`w`, or the centred `w - 2^k` when `w > 2^(k-1)`, has at most
`p` significant bits. At scale `E` one aligned operand has
shift 0 and the other shift `d >= 0`; each has set bits only
in a `p`-wide window. If `d >= k`, the shifted operand is a
multiple of `2^k` and contributes nothing to `w`; `w` is the
low part of the unshifted operand (a subset of its window),
and the centred alternative `2^k - w` can only be the nearer
choice when `w > 2^(k-1)`, which forces `k <= p` (since
`w < 2^p`), so its set bits lie inside `[lowbit(w), k-1]`, a
span of at most `p`. If `d < k` and no cancellation shrank
`S`, then `bitlen(S) <= d + p + 1` (the `+1` only from a
carry, which needs overlapping windows, i.e. `d < p`), so
either `k <= d` (previous case) or `k <= p`, when any integer
with magnitude below `2^k` trivially has span at most `k`.
If cancellation shrank `bitlen(S)` so that `k > p`, then
`d >= bitlen(S) - p = k` (a difference has no carry beyond
the higher window), again the first case. Effective
subtraction changes only the sign bookkeeping in the same
centred-modulo argument (the low part of a difference is the
difference of the low parts modulo `2^k`, with the same
`w > 2^(k-1)` restriction on the centred form). A residual
with at most `p` significant bits which is a multiple of
`u0` (a difference of two multiples of `u0`) and no larger
in magnitude than half an ulp of the largest finite (so its
top bit is within range) is representable, normal or
subnormal. The exhaustive binary16 pair run is the executed
check of this proof at `p = 11`.

(3) Mul split and residual extraction. The exact product
integer at scale `E = e_a + e_b` has at most `2p` bits.
For a normal head the same integer-rounding form gives
`k = bitlen(product) - p <= p`, so the centred residual,
an integer of magnitude at most `2^(k-1)` at scale `E`, has
at most `k <= p` significant bits; it fails
representability exactly when its lowest set bit lies below
`u0`, i.e. exactly the clause's "non-zero digits strictly
between `+-b^(emin-p+1)`" cell. For a subnormal or zero head
the kernel's exact test (significant bits, lowest set bit
against `u0`, top bit against `emax`) still decides: there
the residual is at most `u0/2` in magnitude when nonzero
after rounding at the `u0` grid, so a nonzero residual with
no bit below `u0` would have to be both a multiple of `u0`
and below `u0` in magnitude - impossible - hence every
unrepresentable case in this region also has a bit below
`u0` and lands in the same clause cell. Residual extraction
subtracts the decoded head from the exact integer at the
coarser of the two scales; each left shift is bounded by
the other value's bit length (the head is a nearest
neighbour, so the top-bit positions of exact and head
differ by at most one), at most 127 in the window case and
at most 106 for products, so the extraction is exact in the
same u128.

The P0 exemplar (`msf_pack_f64` in `src/msf_roundpack.c`) consumes a
128-bit significand plus one sticky bit, which is the interface every
row above is shaped to feed. Helpers are 32-bit-limb exact integers
(`src/msf_wide.c`); the target build acquires no arithmetic helper
symbols beyond integer ones, and the symbol scan in `tools/run.sh` is
the gate (SF-0 Section 5.3).
