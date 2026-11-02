import sys
sys.path.insert(0, "tests")
import gen_vectors_aug as g
from fractions import Fraction

for fmt in ("f16", "f32", "f64"):
    q = g.params(fmt)
    p, emin = q["p"], q["emin"]
    found = []
    base = 1 << (p - 1)
    for ea in range(emin + p - 3, emin + p + 4):
        for sa in [base + d for d in range(0, 200, 13)] + [(1 << p) - 1 - d for d in range(0, 200, 17)]:
            a = g.encode_exact(fmt, 0, sa, ea - p + 1)
            if a is None:
                continue
            for sb in [base + d for d in range(0, 200, 7)] + [(1 << p) - 1 - d for d in range(0, 200, 11)]:
                for eb in (-1, 0, 1):
                    b = g.encode_exact(fmt, 0, sb, eb - p + 1)
                    if b is None:
                        continue
                    h, t, fl, info = g.ref_augmented(fmt, a, b, "mul")
                    if info["kind"] == "mul-inexact-tail" and abs(g.value_of(fmt, t)) == Fraction(2) ** emin:
                        found.append((a, b, h, t, fl))
                        break
                if found:
                    break
            if found:
                break
        if found:
            break
    print(fmt, found[:1])
