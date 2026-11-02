#!/usr/bin/env python3
"""s04b_arms.py - sticky-assembly arm census over the f16 pool sweep.

For every (pool, b) pair: classify finite pairs by (tail, pdrop,
rem-zero) arms from window_sim, and compare packed forms:
floor-full vs truth, jam vs truth, dropped vs truth, jam vs floor.
Counts printed. This is the audit of the sticky assembly arm by arm
plus the jam-equivalence search input at binary16.
"""
import sys
import os
sys.path.insert(0, "scratch/verifier-w5alg2")
from mydecide import specials, decide, window_sim, pack_pure  # noqa: E402

POOL = [0x0000, 0x8000, 0x0001, 0x8001, 0x0002, 0x03ff, 0x0400,
        0x3c00, 0xbc00, 0x3555, 0x7bff, 0x7c00, 0xfc00, 0x7e00,
        0xfe00, 0x7d55, 0x7c01, 0xfc01, 0x0003, 0x03fd]

fi = 0
n_fin = 0
tail_n = pdrop_n = rem0_n = 0
tail_and_rem0 = pdrop_and_rem0 = 0
ff_bad = jam_bad = drop_bad = 0  # packed != truth, any of 5 modes
jam_vs_ff = 0  # packed jam != packed floor-full
cross_sq = 0   # R+1 perfect square with (tail|pdrop) [witness family]
cross_sq_ex = []  # examples
rem0_jam_exact = 0  # jam sticky==0 while truth inexact (fabricated exact)
first_bad = []


def packed_diff(x, y):
    return any(px != py for px, py in zip(x, y))


for pv in POOL:
    for b in range(65536):
        if specials(fi, pv, b) is not None:
            continue
        n_fin += 1
        Qf, stf, radf, ewf, tail, pdrop, remnz = window_sim(fi, pv, b, "floor-full")
        Qj, stj, radj, ewj, _, _, _ = window_sim(fi, pv, b, "jam")
        rem0 = not remnz
        tail_n += 1 if tail else 0
        pdrop_n += 1 if pdrop else 0
        rem0_n += 1 if rem0 else 0
        if tail and rem0:
            tail_and_rem0 += 1
        if pdrop and rem0:
            pdrop_and_rem0 += 1
        truth = decide(fi, pv, b)
        pf = pack_pure(fi, ewf // 2, Qf, stf)
        pj = pack_pure(fi, ewj // 2, Qj, stj)
        Qd, std, _, ewd, _, _, _ = window_sim(fi, pv, b, "dropped")
        pd = pack_pure(fi, ewd // 2, Qd, std)
        if packed_diff(pf, truth):
            ff_bad += 1
            if len(first_bad) < 5:
                first_bad.append((pv, b, "floor-full", pf, truth))
        if packed_diff(pj, truth):
            jam_bad += 1
            if len(first_bad) < 10:
                first_bad.append((pv, b, "jam", pj, truth))
        if packed_diff(pd, truth):
            drop_bad += 1
        if packed_diff(pj, pf):
            jam_vs_ff += 1
        # cross-square witness: jam changed the root upward with a
        # dirty context (tail|pdrop), i.e. R+1 a perfect square
        if Qj == Qf + 1 and (tail or pdrop):
            cross_sq += 1
            if len(cross_sq_ex) < 5:
                cross_sq_ex.append((pv, b, tail, pdrop))
        if stj == 0 and truth[0][1] & 0x10:
            rem0_jam_exact += 1
    print(f"pool {pv:04x}: done", flush=True)

print(f"ARMS-F16: finite pairs={n_fin}")
print(f"tail=1: {tail_n}; pdrop=1: {pdrop_n}; rem==0: {rem0_n}")
print(f"tail=1 & rem==0 (fabricated-exact class): {tail_and_rem0}")
print(f"pdrop=1 & rem==0 (fabricated-exact class): {pdrop_and_rem0}")
print(f"floor-full packed != truth: {ff_bad}")
print(f"jam packed != truth: {jam_bad}")
print(f"dropped packed != truth: {drop_bad}")
print(f"jam packed != floor-full packed: {jam_vs_ff}")
print(f"cross-square witnesses (Qj=Qf+1, dirty): {cross_sq}")
print(f"jam sticky==0 on inexact truth: {rem0_jam_exact}")
for pv, b, w, t, p_ in cross_sq_ex:
    print(f"  witness a={pv:04x} b={b:04x} tail={t} pdrop={p_}")
for pv, b, form, got, want in first_bad:
    print(f"  BAD-{form} a={pv:04x} b={b:04x} got={got} want={want}")
