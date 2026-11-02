#!/usr/bin/env python3
"""Construct binary64 jam witnesses by solving the cross-square
congruence directly (the one-parameter scan is a factor-pair
equation with finitely many solutions - see find_jam.py log).

Family: lsh=16 (A in [2^52, sqrt2*2^52), la2=105), net=-2 (d=9),
R = A^2*2^16 + (B^2>>2), ew even.  Jam-cross condition R = Z^2-1.
With u = Z-256A (~2^41), v = Z+256A:  B^2 = 4uv - 3, and
A = (B^2 - 4u^2 + 3) / (2048u) must be an integer in range.
So B^2 = 4u^2 - 3 (mod 2048u).  Choose u prime, u = 1 (mod 3)
(so -3 is a QR mod u), Tonelli-Shanks mod u, brute roots mod
2048, CRT mod 2048u, lift B into [2^52, 2^53), check A range,
then verify packed floor-vs-jam divergence with the full sim.
"""
import sys
sys.path.insert(0, r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\sf2-algebraic")
from math import isqrt
from proto_alg import round_pack, decode

RMS = ("te", "tz", "tp", "tn")

def is_prime(n):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True

def tonelli(n, p):
    n %= p
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c = s, pow(z, q, p)
    t, r = pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 1, t * t % p
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r

def crt(r1, m1, r2, m2):
    # x = r1 (mod m1), x = r2 (mod m2), coprime moduli
    inv = pow(m1, -1, m2)
    return (r1 + m1 * ((r2 - r1) * inv % m2)) % (m1 * m2)

def sim(fmt, abits, bbits, jam):
    _, _, asig, aexp = decode(fmt, abits)
    _, _, bsig, bexp = decode(fmt, bbits)
    ma, ea, mb, eb = asig, aexp, bsig, bexp
    sa, sb = ma * ma, mb * mb
    lsh = 121 - sa.bit_length()
    a_win = sa << lsh
    net = lsh - 2 * (ea - eb)
    if net >= 0:
        b_win, tail = sb << net, False
    else:
        k = -net
        dropped = sb & ((1 << k) - 1)
        if jam:
            b_win, tail = (sb >> k) | (1 if dropped else 0), False
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
    return [round_pack(fmt, 0, Q, ew // 2, sticky, rm) for rm in RMS]

def enc64(sig, exp):
    return ((exp + 52 + 1023) << 52) | (sig - (1 << 52))

found = []
candidates = 0
u = (1 << 41) + 1
primes_tried = 0
while len(found) < 6 and primes_tried < 60:
    if u % 3 == 1 and is_prime(u):
        primes_tried += 1
        ru = tonelli(-3, u)
        assert ru is not None, u
        target2048 = (4 * u * u - 3) % 2048
        roots2048 = [x for x in range(1, 2048, 2) if (x * x) % 2048 == target2048]
        M = 2048 * u
        for r2 in roots2048:
            for r1 in (ru, u - ru):
                r = crt(r2, 2048, r1, u)
                B = r
                if B < (1 << 52):
                    B += ((1 << 52) - B + M - 1) // M * M
                while B < (1 << 53):
                    if B & 1:
                        num = B * B - 4 * u * u + 3
                        if num % M == 0:
                            A = num // M
                            if (1 << 52) <= A and A * A < (1 << 105):
                                candidates += 1
                                a_bits, b_bits = enc64(A, -52), enc64(B, -61)
                                pf = sim("f64", a_bits, b_bits, False)
                                pj = sim("f64", a_bits, b_bits, True)
                                if pf != pj:
                                    diff = [rm for rm, x, y in zip(RMS, pf, pj) if x != y]
                                    found.append((u, A, B, a_bits, b_bits, diff))
                                    print(f"WITNESS u={u} A={A} B={B} a={a_bits:016x} b={b_bits:016x} modes={diff}")
                                    print(f"  floor={pf}")
                                    print(f"  jam  ={pj}")
                    B += M
    u += 2
print(f"primes_tried={primes_tried} cross_candidates={candidates} witnesses={len(found)}")
for u_, A, B, a_bits, b_bits, diff in found:
    print(f"PAIR f64 {a_bits:016x} {b_bits:016x}  # A={A} B={B} modes={','.join(diff)}")
