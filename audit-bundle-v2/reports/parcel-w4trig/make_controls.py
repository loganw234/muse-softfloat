"""Negative-control vector mutants for the trig bundle.
Each mutant corrupts committed expectations in a way that a
specific kernel defect would produce; the runner must refuse
every mutant while accepting the unmutated source lines."""
from fractions import Fraction

ROOT = "C:/Users/logan/source/repos/Muse-Softfloat"
SRC = ROOT + "/worktrees/w4-trig/tests/vectors/trig-f32.vec"
OUT = ROOT + "/scratch/parcel-w4trig/out/controls"
import os
os.makedirs(OUT, exist_ok=True)

lines = []
for line in open(SRC, encoding="utf-8"):
    if line.startswith("#") or not line.strip():
        continue
    t = line.split()
    # op rm in -> out flags prov
    lines.append(t)


def val32(x):
    sign = (x >> 31) & 1
    e = (x >> 23) & 0xFF
    frac = x & 0x7FFFFF
    if e == 0xFF:
        return None
    if e == 0:
        v = Fraction(frac) * Fraction(2) ** -149
    else:
        v = Fraction(frac | 0x800000) * Fraction(2) ** (e - 127 - 23)
    return -v if sign else v


def nearest_int_parity(v):
    av = abs(v)
    fl = av.numerator // av.denominator
    if av - fl > Fraction(1, 2):
        fl += 1
    return fl & 1


def emit(name, rows):
    path = f"{OUT}/{name}.vec"
    with open(path, "w", newline="\n", encoding="utf-8") as fh:
        fh.write(f"# negative control mutant {name} (scratch)\n")
        for t in rows:
            fh.write(" ".join(t) + "\n")
    print(f"{name}: {len(rows)} lines")
    return path


# POS: unmutated subset (first 400 lines) must PASS
emit("pos_subset", [list(t) for t in lines[:400]])

# NC1 quadrant sign flip: sin_pi results get sign flipped
# exactly where the nearest-integer parity is odd.
rows = []
for t in lines:
    t = list(t)
    if t[0] == "msf32_sin_pi":
        v = val32(int(t[2], 16))
        if v is not None and nearest_int_parity(v) == 1:
            o = int(t[4], 16) ^ 0x80000000
            t[4] = f"{o:x}"
    rows.append(t)
emit("nc_quadrant_sign", rows)

# NC2 delta-branch sign error: cos_pi tiny inputs whose
# directed result is the neighbour below 1 become 1.0
# (delivering 1+delta as if delta were negative).
rows = []
hit = 0
for t in lines:
    t = list(t)
    if t[0] == "msf32_cos_pi" and t[1] in ("tz", "tn"):
        o = int(t[4], 16)
        if o in (0x3F7FFFFF, 0xBF7FFFFF):
            t[4] = "3f800000" if o == 0x3F7FFFFF else "bf800000"
            hit += 1
    rows.append(t)
emit("nc_delta_sign", rows)
print("  delta mutants touched:", hit)

# NC3 directed neighbour on the wrong side: tn results moved
# one ulp toward +infinity (magnitude step by direction).
rows = []
for t in lines:
    t = list(t)
    if t[1] == "tn" and t[5] != "00":
        o = int(t[4], 16)
        e = (o >> 23) & 0xFF
        if e != 0xFF and o & 0x7FFFFFFF:
            o = o + 1 if not (o >> 31) else o - 1
            t[4] = f"{o:x}"
    rows.append(t)
emit("nc_directed_side", rows)

# NC4 non-integer reduction input: integer-anchor sin lines
# get their INPUT nudged one encoding step while the exact
# zero expectation stays (a kernel skipping exact reduction
# checks would still have to produce a nonzero value).
rows = []
hit = 0
for t in lines:
    t = list(t)
    if t[0] == "msf32_sin_pi" and t[4] in ("0", "80000000") and t[5] == "00":
        x = int(t[2], 16)
        v = val32(x)
        if v is not None and v != 0 and v.denominator == 1:
            t[2] = f"{x + 1:x}"
            hit += 1
    rows.append(t)
emit("nc_noninteger_reduction", rows)
print("  reduction mutants touched:", hit)
