"""Classify all f16 finite encodings: special vs kernel-path; predict
mismatch sets for (i) sin r_neg sign bug, (ii) cos neg-half -0 bug."""
import sys


def f16_fields(x):
    sign = (x >> 15) & 1
    e = (x >> 10) & 0x1F
    frac = x & 0x3FF
    if e == 0x1F:
        return sign, None, None, "nonfinite"
    if e == 0:
        if frac == 0:
            return sign, None, None, "zero"
        return sign, frac, -24, "finite"
    sig = frac | 0x400
    return sign, sig, e - 15 - 10, "finite"


n_fin = n_special = 0
sin_rneg = cos_neghalf = 0
examples = []
for x in range(0x10000):
    sign, sig, exp2, cls = f16_fields(x)
    if cls != "finite":
        continue
    n_fin += 1
    if exp2 is None:
        continue
    # integer?
    if exp2 >= 0:
        n_special += 1
        continue
    k = -exp2
    if k < 64:
        rem = sig & ((1 << k) - 1)
        ipart = sig >> k
    else:
        rem, ipart = sig, 0
    if rem == 0:
        n_special += 1
        continue
    if k < 64 and rem == (1 << (k - 1)):
        n_special += 1
        if x & 0x8000:
            cos_neghalf += 1
        continue
    if rem > (1 << (k - 1)) if k < 64 else False:
        sin_rneg += 1
        if len(examples) < 5:
            examples.append(x)
print(f"finite={n_fin} specials={n_special} kernel={n_fin - n_special}")
print(f"sin r_neg inputs={sin_rneg} -> x4 modes = {sin_rneg * 4}")
print(f"cos neg-half inputs={cos_neghalf} -> x4 modes = {cos_neghalf * 4}")
print(f"predicted total mismatches = {(sin_rneg + cos_neghalf) * 4}")
print("examples:", [hex(e) for e in examples])
