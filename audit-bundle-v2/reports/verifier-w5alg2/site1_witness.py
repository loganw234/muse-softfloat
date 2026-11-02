#!/usr/bin/env python3
"""site1_witness.py - hunt a site-1 cross-square witness.

Site 1 (sb alignment, ew even): need tot_floor + 1 = M^2 with the +1
coming from the jam (b_win_floor even, tail = 1). With a_win = S^2
(lsh even), M = S + t: b_win_floor = 2*S*t + t^2 - 1 =: V must be
even, and [V*2^k, V*2^k + 2^k) must contain a perfect square sb with
nonzero low part (tail). Search random sig_a x t x k.
"""
import random
import sys
from math import isqrt

sys.path.insert(0, "scratch/verifier-w5alg2")
from mydecide import window_sim, pack_pure, decide, decode  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000000
rng = random.Random(0x51e)
found = 0
tried = 0
for _ in range(N):
    sig_a = rng.randrange(1 << 52, 1 << 53) | 1
    sa = sig_a * sig_a
    la2 = sa.bit_length()
    lsh = 121 - la2
    if lsh % 2 != 0:
        continue
    S = sig_a << (lsh // 2)
    for t in (1, 2, 3, 4):
        V = 2 * S * t + t * t - 1
        if V % 2 != 0 or V <= 0:
            continue
        for k in range(1, 46):
            lo = V << k
            if lo + (1 << k) > (1 << 106):
                break
            r0 = isqrt(lo)
            for sq in (r0, r0 + 1, r0 + 2):
                sb = sq * sq
                if lo <= sb < lo + (1 << k) and sb != lo:
                    # tail = sb - lo in [1, 2^k): dirty; b_win even (V even)
                    tried += 1
                    # build the pair: a = sig_a * 2^ea, b: sb root sig_b = sq
                    # need gap: k = lsh - 2*(ea-eb) -> ea - eb = (lsh + k... solve
                    # net = lsh - 2*(ea-eb) = -k -> ea - eb = (lsh + k)//2; lsh+k even?
                    if (lsh + k) % 2 != 0:
                        continue
                    gap = (lsh + k) // 2
                    # pick eb, ea = eb + gap within f64 range, a normal
                    eb = -1000
                    ea = eb + gap
                    if not (-1074 - 52 <= ea <= 1023 - 52 and -1074 - 52 <= eb <= 1023 - 52):
                        continue
                    # encode a = sig_a * 2^ea, b = sq * 2^eb as f64
                    from mydecide import encode_value
                    from fractions import Fraction
                    try:
                        a = encode_value(2, Fraction(sig_a) * Fraction(2) ** ea)
                        b = encode_value(2, Fraction(sq) * Fraction(2) ** eb)
                    except AssertionError:
                        continue
                    Qf, stf, _, ewf, tail, pdrop, _ = window_sim(2, a, b, "floor-full")
                    Qj, stj, _, ewj, _, _, _ = window_sim(2, a, b, "jam")
                    if Qj == Qf + 1 and (tail or pdrop):
                        pf = pack_pure(2, ewf // 2, Qf, stf)
                        pj = pack_pure(2, ewj // 2, Qj, stj)
                        truth = decide(2, a, b)
                        print(f"WITNESS a={a:x} b={b:x} M={Qj:x} "
                              f"floor==truth:{pf == truth} jam==truth:{pj == truth} "
                              f"jam==floor:{pj == pf}")
                        found += 1
                        if found >= 3:
                            sys.exit(0)
print(f"done: candidates-checked={tried} witnesses={found}")
