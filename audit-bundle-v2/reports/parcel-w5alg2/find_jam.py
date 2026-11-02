#!/usr/bin/env python3
"""Search for binary64 jam witnesses for the hypot kernel design.

Family: A = 2^52 (a = 1.0), d = ea-eb = 9, lsh = 16, net = -2.
Window radicand R = A^2 * 2^16 + (B^2 >> 2), ew even, exp2 = -60.
Want R = Z^2 - 1 with Z = 2^60 + t  =>  B^2 = t*2^63 + 4t^2 - 3,
B odd in [2^52, 2^53).  For each hit, packed floor (Q=Z-1,
sticky=1) vs jam (Q=Z, sticky=0) via proto_alg.round_pack;
record hits where any mode's (bits, flags) differ.
Also verifies the full C-sim (floor and jam) on the encoding
pair (1.0, B*2^-61) gives those triples.
"""
import sys
sys.path.insert(0, r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\sf2-algebraic")
from math import isqrt
from proto_alg import round_pack, decode

RMS = ("te", "tz", "tp", "tn")
A = 1 << 52
EXP2 = -60

def sim(fmt, abits, bbits, jam):
    _, _, asig, aexp = decode(fmt, abits)
    _, _, bsig, bexp = decode(fmt, bbits)
    # order by magnitude (a is 1.0 here, always >= b in this family)
    ma, ea, mb, eb = asig, aexp, bsig, bexp
    sa, sb = ma * ma, mb * mb
    la2 = sa.bit_length()
    lsh = 121 - la2
    a_win = sa << lsh
    net = lsh - 2 * (ea - eb)
    if net >= 0:
        b_win, tail = sb << net, False
    else:
        k = -net
        dropped = sb & ((1 << k) - 1) if k < 256 else sb
        if jam:
            b_win = (sb >> k) | (1 if dropped else 0)
            tail = False
        else:
            b_win, tail = sb >> k, dropped != 0
    tot = a_win + b_win
    ew = 2 * ea - lsh
    pdrop = False
    if ew & 1:
        if jam:
            R = (tot >> 1) | (tot & 1)
        else:
            R, pdrop = tot >> 1, bool(tot & 1)
        ew += 1
    else:
        R = tot
    Q = isqrt(R)
    rem = R - Q * Q
    sticky = (rem != 0) if jam else (tail or pdrop or rem != 0)
    return [round_pack(fmt, 0, Q, ew // 2, sticky, rm) for rm in RMS], (Q, ew // 2, sticky)

def enc64(sig, exp):
    # value sig * 2^exp, sig in [2^52, 2^53): normal encoding
    e_unbiased = exp + 52
    return ((e_unbiased + 1023) << 52) | (sig - (1 << 52))

hits = 0
found = []
t = (1 << 41) + 1
t_end = t + 60_000_000
while t < t_end and len(found) < 8:
    b2 = (t << 63) + 4 * t * t - 3
    B = isqrt(b2)
    if B * B == b2 and (B & 1) and (1 << 52) <= B < (1 << 53):
        hits += 1
        Z = (1 << 60) + t
        fl = [round_pack("f64", 0, Z - 1, EXP2, True, rm) for rm in RMS]
        jm = [round_pack("f64", 0, Z, EXP2, False, rm) for rm in RMS]
        if fl != jm:
            a_bits = enc64(A, -52)          # 1.0
            b_bits = enc64(B, -61)          # B * 2^-61
            pf, tf = sim("f64", a_bits, b_bits, False)
            pj, tj = sim("f64", a_bits, b_bits, True)
            assert pf == fl and pj == jm, (t, pf, fl, pj, jm)
            diff = [rm for rm, x, y in zip(RMS, fl, jm) if x != y]
            found.append((t, B, a_bits, b_bits, diff))
            print(f"WITNESS t={t} B={B} a={a_bits:016x} b={b_bits:016x} modes={diff}")
            print(f"  floor={fl}")
            print(f"  jam  ={jm}")
    t += 2
print(f"square hits={hits} witnesses={len(found)} scanned_t_up_to={t}")
for t, B, a_bits, b_bits, diff in found:
    print(f"PAIR f64 {a_bits:016x} {b_bits:016x}  # t={t} B={B} modes={','.join(diff)}")
