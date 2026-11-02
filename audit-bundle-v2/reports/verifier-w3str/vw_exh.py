#!/usr/bin/env python3
"""vw_exh.py - f16-exhaustive to-dec (3 specs) + to-hex (exact) probe sets."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vw_ref import ref_to_decimal, ref_to_hex


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "vw-exh-todec.vec"), "w", newline="\n") as f:
        f.write("# f16 exhaustive to-dec - do not edit\n")
        n = 0
        for a in range(0x10000):
            for spec in ((5, 0, 0), (9, 0, 0), (17, 0, 0)):
                o, L, fl = ref_to_decimal("f16", a, *spec, "te")
                f.write("msf16_to_decimal te A=%04x SPEC=%d,%d,%d -> OUT=%s LEN=%d %02x vw:exh\n" %
                        (a, spec[0], spec[1], spec[2], o, L, fl))
                n += 1
    print("todec %d" % n)
    with open(os.path.join(outdir, "vw-exh-tohex.vec"), "w", newline="\n") as f:
        f.write("# f16 exhaustive to-hex exact-enough - do not edit\n")
        for a in range(0x10000):
            o, L, fl = ref_to_hex("f16", a, -1, "te")
            f.write("msf16_to_hex te A=%04x SPEC=-1 -> OUT=%s LEN=%d %02x vw:exh\n" %
                    (a, o, L, fl))
    print("tohex 65536")


if __name__ == "__main__":
    main(sys.argv[1])
