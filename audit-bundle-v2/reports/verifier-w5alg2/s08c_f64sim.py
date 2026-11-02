#!/usr/bin/env python3
"""s08c_f64sim.py - f64 model-level jam adjudication.

Random f64 finite pairs: for each, window_sim in floor-full / jam /
dropped forms + pack_pure, vs exact truth (decide). Counts:
floor-full vs truth (mandated form soundness), jam vs truth,
jam vs floor-full (the addendum equivalence), dropped vs truth
(the copy's actual feed), cross-square witnesses (Qj=Qf+1 on dirty
input), jam-sticky-0-on-inexact (fabricated exactness).
"""
import random
import sys
sys.path.insert(0, "scratch/verifier-w5alg2")
from mydecide import decide, window_sim, pack_pure  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2000000
SEED = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x64ad
rng = random.Random(SEED)
fi = 2
n = ff_bad = jam_bad = drop_bad = jvf = cross = jamfab = 0
cross_ex = []
first_jam = []
while n < N:
    a = rng.getrandbits(64)
    b = rng.getrandbits(64)
    if ((a >> 52) & 0x7ff) == 0x7ff or ((b >> 52) & 0x7ff) == 0x7ff:
        continue
    n += 1
    Qf, stf, _, ewf, tail, pdrop, _ = window_sim(fi, a, b, "floor-full")
    Qj, stj, _, ewj, _, _, _ = window_sim(fi, a, b, "jam")
    truth = decide(fi, a, b)
    pf = pack_pure(fi, ewf // 2, Qf, stf)
    pj = pack_pure(fi, ewj // 2, Qj, stj)
    Qd, std, _, ewd, _, _, _ = window_sim(fi, a, b, "dropped")
    pd = pack_pure(fi, ewd // 2, Qd, std)
    if any(x != y for x, y in zip(pf, truth)):
        ff_bad += 1
    if any(x != y for x, y in zip(pj, truth)):
        jam_bad += 1
        if len(first_jam) < 5:
            first_jam.append((a, b, pj, truth))
    if any(x != y for x, y in zip(pd, truth)):
        drop_bad += 1
    if any(x != y for x, y in zip(pj, pf)):
        jvf += 1
    if Qj == Qf + 1 and (tail or pdrop):
        cross += 1
        if len(cross_ex) < 5:
            cross_ex.append((a, b, tail, pdrop))
    if stj == 0 and truth[0][1] & 0x10:
        jamfab += 1
    if n % 500000 == 0:
        print(f"  {n}/{N} done", flush=True)
print(f"F64SIM: pairs={n}")
print(f"floor-full vs truth: {ff_bad}")
print(f"jam vs truth: {jam_bad}")
print(f"dropped vs truth: {drop_bad}")
print(f"jam vs floor-full: {jvf}")
print(f"cross-square witnesses: {cross}")
print(f"jam fabricated-exact: {jamfab}")
for a, b, pj, truth in first_jam:
    print(f"  JAMBAD a={a:x} b={b:x} jam={pj} truth={truth}")
for a, b, t, p in cross_ex:
    print(f"  CROSS a={a:x} b={b:x} tail={t} pdrop={p}")
