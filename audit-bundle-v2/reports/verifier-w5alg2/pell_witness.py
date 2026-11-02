#!/usr/bin/env python3
"""pell_witness.py - construct a cross-square witness for the jam site.

Need: a_win + 1 = M^2 with a_win = sa * 2^lsh in [2^120, 2^121),
sa = sig^2 a perfect square with sig < 2^53 (f64), lsh = 121-bitlen(sa),
lsh odd (so ew = 2ea - lsh can be made even... actually ew parity is
free via ea), i.e. M^2 - sig^2 * 2^lsh = 1 with lsh odd:
Pell X^2 - 2*Y^2 = 1 with X = M, Y = sig * 2^((lsh-1)/2).

Search fundamental-solution powers (3+2sqrt2)^k = X_k + Y_k sqrt2
for one with v2(Y_k) >= 7 and consistent sig/lsh. Then build the
f64 pair: a from (sig, ea), b tiny with sb>>k = 0 and tail = 1.
"""
import sys
sys.path.insert(0, "scratch/verifier-w5alg2")
from mydecide import window_sim, pack_pure, decide  # noqa: E402

# powers of the fundamental unit: (X + Y sqrt2) = (3 + 2 sqrt2)^k ... use (1+sqrt2)^{2k}
# generate via recurrence: X' = 3X + 4Y, Y' = 2X + 3Y (multiply by 3+2sqrt2)
X, Y = 3, 2
sols = []
for k in range(1, 60):
    if X >= (1 << 59) and X <= (1 << 62):
        v = (Y & -Y).bit_length() - 1 if Y else 99
        sols.append((k, X, Y, v))
    X, Y = 3 * X + 4 * Y, 2 * X + 3 * Y

print(f"Pell solutions in range: {len(sols)}")
for k, X, Y, v in sols[:40]:
    print(f"  k={k} X~2^{X.bit_length() - 1} v2(Y)={v}")
    if v < 7:
        continue
    j = v
    sig = Y >> j
    if sig >= (1 << 53) or sig <= 0:
        continue
    sa = sig * sig
    la2 = sa.bit_length()
    lsh = 121 - la2
    if lsh % 2 == 0 or (lsh - 1) // 2 != j:
        continue
    print(f"  CANDIDATE k={k} sig={sig:x} lsh={lsh} j={j} X={X}")
    # verify M^2 - sa*2^lsh == 1
    assert X * X - sa * (1 << lsh) == 1, "pell identity"
    # build pair: a_win must equal sa*2^lsh with M^2 = a_win+1.
    # ea free: pick ew even: ew = 2*ea - lsh even always (lsh odd -> 2ea-lsh odd!). 
    # lsh odd forces ew odd -> parity shift always on. rad = tot>>1.
    # want rad_floor = (a_win + 0)>>1 even with rad+1 = square?
    # rad_floor = a_win>>1 = (M^2-1)>>1 = (M^2-1)/2 (M odd). rad+1 = (M^2+1)/2, not square in general.
    print("  (lsh odd forces parity shift; sb-site witness needs ew even: use sb-shift site with tot even instead)")
