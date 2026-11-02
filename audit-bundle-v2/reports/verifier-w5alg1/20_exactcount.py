"""20_exactcount.py - count exact positive-finite cases per format (study: 20 at f16)."""
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "mydec", "scratch/verifier-w5alg1/10_mydecider.py")
mydec = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mydec)

for fmt, nbits in (("f16", 16),):
    q = mydec.fmt_params(fmt)
    t = q["t"]
    n_exact = n_pos = 0
    for x in range(1 << nbits):
        c = mydec.classify(fmt, x)
        if c[0] != "num" or c[1] != 0:
            continue
        n_pos += 1
        if mydec.decide(fmt, x)[0][1] == 0:
            n_exact += 1
    print("%s positive-finite=%d exact=%d" % (fmt, n_pos, n_exact))
