#!/usr/bin/env python3
# 08_diff.py - own exact differential for the 24 berkeley-check rows.
# Runs pinned testfloat_gen f16 streams (level 1, seed 1), widens one
# operand exactly (own code, value-asserted), derives all 12 check
# predicates per dest (direct + swapped + complemented), cross-checks
# every derived expectation against the independent exact reference,
# and writes runner-ready vector files.
import os
import subprocess
import sys

import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "indref03", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "03_indref.py"))
indref03 = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(indref03)
D, P2, T, EB = indref03.D, indref03.P2, indref03.T, indref03.EB
bias, ref_compare = indref03.bias, indref03.ref_compare

GEN = ("C:/Users/logan/source/repos/Muse-Softfloat/scratch/oracles/"
       "TestFloat-3e/build/Linux-x86_64-GCC/testfloat_gen.exe")


def widen(dest, b16):
    d = D("f16", b16)
    t, ebn = T[dest], EB[dest]
    if d.cls == "zero":
        return d.sign << (t + ebn)
    if d.cls == "inf":
        return (d.sign << (t + ebn)) | (((1 << ebn) - 1) << t)
    if d.cls in ("snan", "qnan"):
        return ((d.sign << (t + ebn)) | (((1 << ebn) - 1) << t)
                | (d.payload << (t - 10)))
    # finite: value-preserving construction
    expf = (b16 >> 10) & 0x1F
    frac = b16 & 0x3FF
    if expf == 0:  # subnormal -> normal in f32/f64
        k = frac.bit_length() - 1
        # value = frac * 2^-24; top bit k: unbiased exponent e = k - 24
        e = k - 24
        expf2 = e + (2 ** (ebn - 1) - 1)
        frac2 = (frac - (1 << k)) << (t - k)
    else:
        expf2 = expf - 15 + (2 ** (ebn - 1) - 1)
        frac2 = frac << (t - 10)
    out = (d.sign << (t + ebn)) | (expf2 << t) | frac2
    w = D(dest, out)
    assert w.cls == "finite" and w.val == d.val, (hex(b16), hex(out))
    return out


def xlate(b):
    m = 0
    if b & 1:
        m |= 0x10
    if b & 2:
        m |= 0x08
    if b & 4:
        m |= 0x04
    if b & 8:
        m |= 0x02
    if b & 16:
        m |= 0x01
    return m


STREAMS = ["f16_eq", "f16_eq_signaling", "f16_le", "f16_lt",
           "f16_le_quiet", "f16_lt_quiet"]

# stream -> [(check_pred, take_direct, complement)]
PLAN = {
    "f16_eq": [("quiet_equal", True, False), ("quiet_not_equal", True, True)],
    "f16_eq_signaling": [("signaling_equal", True, False),
                         ("signaling_not_equal", True, True)],
    "f16_le": [("signaling_less_equal", True, False),
               ("signaling_greater_equal", False, False)],
    "f16_lt": [("signaling_less", True, False),
               ("signaling_greater", False, False)],
    "f16_le_quiet": [("quiet_less_equal", True, False),
                     ("quiet_greater_equal", False, False)],
    "f16_lt_quiet": [("quiet_less", True, False),
                     ("quiet_greater", False, False)],
}

MASKSIG = {
    "quiet_equal": (2, 0), "quiet_not_equal": (1 | 4 | 8, 0),
    "signaling_equal": (2, 1), "signaling_not_equal": (1 | 4 | 8, 1),
    "quiet_less": (1, 0), "quiet_less_equal": (1 | 2, 0),
    "quiet_greater": (4, 0), "quiet_greater_equal": (4 | 2, 0),
    "signaling_less": (1, 1), "signaling_less_equal": (1 | 2, 1),
    "signaling_greater": (4, 1), "signaling_greater_equal": (4 | 2, 1),
}


def run_stream(fn):
    cmd = [GEN, "-level", "1", "-seed", "1", fn]
    p = subprocess.run(cmd, capture_output=True, text=True, check=True)
    cases = []
    for line in p.stdout.splitlines():
        tok = line.split()
        if len(tok) < 3:
            continue
        ops, r, f = tok[:-2], tok[-2], tok[-1]
        cases.append((int(ops[0], 16), int(ops[1], 16), int(r, 16),
                      xlate(int(f, 16))))
    return cases


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    total = agree = 0
    per = {}
    for dest in ("f32", "f64"):
        lines = []
        for fn in STREAMS:
            cases = run_stream(fn)
            per[fn] = len(cases)
            for (x, y, r, f) in cases:
                for (pred, direct, comp) in PLAN[fn]:
                    if direct:
                        a, b = widen(dest, x), y
                    else:
                        a, b = widen(dest, y), x
                    er = (1 - r) if comp else r
                    mask, sig = MASKSIG[pred]
                    mr, mf = ref_compare(dest, a, "f16", b, mask, sig)
                    total += 1
                    if (mr, mf) != (er, f):
                        print("TRANSFORM-DISAGREE %s %s %x %x: berk=%d/%02x exact=%d/%02x"
                              % (dest, pred, a, b, er, f, mr, mf))
                    else:
                        agree += 1
                    lines.append("msf%s_compare_%s_f16 - %x %x -> %d %02x "
                                 "exact-py-vx:berkeley-diff-%s"
                                 % ("32" if dest == "f32" else "64", pred,
                                    a, b, er, f, fn))
        with open("%s/diff-%s.vec" % (outdir, dest), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write("# generated by verifier-w2xf 08_diff.py - own differential\n")
            fh.write("\n".join(lines) + "\n")
        print("dest %s: %d lines" % (dest, len(lines)))
    print("streams:", per)
    print("transform==exact: %d/%d" % (agree, total))


if __name__ == "__main__":
    main(sys.argv[1])
