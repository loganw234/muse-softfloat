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

The P0 exemplar (`msf_pack_f64` in `src/msf_roundpack.c`) consumes a
128-bit significand plus one sticky bit, which is the interface every
row above is shaped to feed. Helpers are 32-bit-limb exact integers
(`src/msf_wide.c`); the target build acquires no arithmetic helper
symbols beyond integer ones, and the symbol scan in `tools/run.sh` is
the gate (SF-0 Section 5.3).
