#!/usr/bin/env python3
# 80_cuts.py - LEG cuts/ties/specials: boundary-1/boundary/boundary+1 per
# cut per format + saturation cell + specials sweep, kernel vs own decider.
# Run with linux python3. Exit nonzero on any BAD/UNDECIDED.
import struct, subprocess, sys, os

D = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(D, "build", "vdriver.exe")
MODES = ["te", "tz", "tp", "tn", "ta"]

def pack(fmt, x):
    if fmt == 0: return struct.unpack("<H", struct.pack("<e", x))[0]
    if fmt == 1: return struct.unpack("<I", struct.pack("<f", x))[0]
    return struct.unpack("<Q", struct.pack("<d", x))[0]

def nxt(fmt, bits, delta):
    w = 16 if fmt == 0 else (32 if fmt == 1 else 64)
    mask = (1 << w) - 1
    if bits >> (w - 1):  # negative: value+deltaulp == bits-delta
        return (bits - delta) & mask
    return (bits + delta) & mask

def run_one(fi, fn, bits):
    w = 16 if fi == 0 else (32 if fi == 1 else 64)
    fmt = "%%0%dx" % (w // 4)
    p = subprocess.run([V, "one", str(fi), str(fn), fmt % (bits & ((1 << w) - 1))],
                       capture_output=True, text=True)
    bad, und = [], False
    for line in p.stdout.splitlines():
        t = line.split()
        if t[0] == "UNDECIDED":
            return None
        if len(t) == 4 and t[1].startswith("got=") and t[-1] == "BAD":
            bad.append((t[0], t[1], t[2]))
    return bad

fails = 0
total = 0
def check(fi, fn, bits, tag):
    global fails, total
    total += 1
    r = run_one(fi, fn, bits)
    if r is None:
        print("UNDECIDED fi=%d fn=%d %s %s" % (fi, fn, tag, hex(bits)))
        fails += 1
    elif r:
        for m, g, w_ in r:
            print("BAD fi=%d fn=%d %s %s %s: got=%s want=%s" % (fi, fn, tag, hex(bits), m, g, w_))
        fails += 1

EMAX = [15, 127, 1023]
EMIN = [-14, -126, -1022]
P = [11, 24, 53]
for fi in range(3):
    # exp2 cuts: T1 = emax+1, T2 = E_tie = emin-p
    for T, fn, tag in [(EMAX[fi] + 1, 0, "ov"), (EMIN[fi] - P[fi], 0, "zero")]:
        tb = pack(fi, float(T))
        for d in (-3, -1, 0, 1, 3):
            check(fi, fn, nxt(fi, tb, d), "%s%+d" % (tag, d))
    # exp2m1 cuts: T3 = emax+2, T4 = -(p+1)
    for T, fn, tag in [(EMAX[fi] + 2, 1, "ov"), (-(P[fi] + 1), 1, "sat")]:
        tb = pack(fi, float(T))
        for d in (-3, -1, 0, 1, 3):
            check(fi, fn, nxt(fi, tb, d), "%s%+d" % (tag, d))
    # saturation deep + zero-cut deep (both funcs where sensible)
    check(fi, 0, pack(fi, float(EMIN[fi] - P[fi] - 50)), "zero-deep")
    check(fi, 1, pack(fi, float(-(P[fi] + 50))), "sat-deep")
    check(fi, 0, pack(fi, float(EMAX[fi] + 50)), "ov-deep")
    check(fi, 1, pack(fi, float(EMAX[fi] + 50)), "ov-deep")
    # specials sweep (both funcs)
    w = 16 if fi == 0 else (32 if fi == 1 else 64)
    emaxf = (1 << (5 if fi == 0 else (8 if fi == 1 else 11))) - 1
    nfrac = P[fi] - 1
    inf = emaxf << nfrac
    qbit = 1 << (nfrac - 1)
    sign = 1 << (w - 1)
    specials = [0, sign, inf, inf | sign]
    for pl in (1, 2, qbit - 1, (1 << nfrac) - 1):
        for s in (0, sign):
            specials.append(inf | qbit | pl | s)
            specials.append(inf | pl | s)
    specials.append(inf | qbit)
    for fn in (0, 1):
        for x in specials:
            check(fi, fn, x, "special")

print("cuts/specials: %d checks %s" % (total, "ALL OK" if fails == 0 else "FAILURES=%d" % fails))
sys.exit(1 if fails else 0)
