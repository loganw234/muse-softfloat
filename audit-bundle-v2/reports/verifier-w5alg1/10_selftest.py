import importlib.util
_spec = importlib.util.spec_from_file_location(
    "mydec", "scratch/verifier-w5alg1/10_mydecider.py")
mydec = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mydec)
decide = mydec.decide

CASES = [
    # (fmt, inhex, expected [(outhex, flags)] x5 or None to just print)
    ("f16", 0x3C00, [(0x3C00, 0)] * 5),   # rSqrt(1) = 1 exact
    ("f16", 0x4400, [(0x3800, 0)] * 5),   # rSqrt(4) = 0.5 exact
    ("f16", 0x0000, [(0x7C00, 2)] * 5),   # +0 -> +inf divzero
    ("f16", 0x8000, [(0xFC00, 2)] * 5),   # -0 -> -inf divzero
    ("f16", 0x7C00, [(0x0000, 0)] * 5),   # +inf -> +0
    ("f16", 0xFC00, [(0x7E00, 1)] * 5),   # -inf -> qNaN invalid
    ("f16", 0xBC00, [(0x7E00, 1)] * 5),   # -1 -> qNaN invalid
    ("f16", 0x7E00, [(0x7E00, 0)] * 5),   # qNaN preserved
    ("f16", 0x7D00, [(0x7F00, 1)] * 5),   # sNaN quieted + invalid
    ("f16", 0xFC01, [(0xFE01, 1)] * 5),   # neg sNaN quieted, sign kept
    ("f16", 0x0001, [(0x6C00, 0)] * 5),   # rSqrt(2^-24) = 2^12 exact
    ("f32", 0x3F800000, [(0x3F800000, 0)] * 5),
    ("f64", 0x3FF0000000000000, [(0x3FF0000000000000, 0)] * 5),
    ("f64", 0x4000000000000000, [(0x3FE0000000000000, 0)] * 5),  # rSqrt(2)... exact? no: 1/sqrt(2) inexact
]

fails = 0
for fmt, x, want in CASES:
    got = decide(fmt, x)
    if fmt == "f64" and x == 0x4000000000000000:
        print("INFO f64 rsqrt(2.0) te:", "%x" % got[0][0], "%02x" % got[0][1])
        continue
    if got != want:
        fails += 1
        print("FAIL", fmt, "%x" % x, "got", [(("%x" % b), f) for b, f in got])
    else:
        print("ok", fmt, "%x" % x)
print("selftest fails:", fails)
