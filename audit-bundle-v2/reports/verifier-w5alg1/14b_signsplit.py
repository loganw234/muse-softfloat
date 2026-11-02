"""14b_signsplit.py - split num mismatches into positive/negative input."""
import importlib.util
import sys

_spec = importlib.util.spec_from_file_location(
    "mydec", "scratch/verifier-w5alg1/10_mydecider.py")
mydec = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mydec)

for fmt, nbits in (("f32", 32), ("f64", 64)):
    pos_t = pos_m = neg_t = neg_m = 0
    with open("scratch/verifier-w5alg1/out/kern_%s.txt" % fmt) as fh:
        for line in fh:
            tk = line.split()
            _, f, inhx, mode, outhx, flhx = tk
            x = int(inhx, 16)
            c = mydec.classify(f, x)
            if c[0] != "num":
                continue
            got = (int(outhx, 16), int(flhx, 16))
            want = mydec.decide(f, x)[int(mode)]
            if c[1] == 0:
                pos_t += 1
                pos_m += (got != want)
            else:
                neg_t += 1
                neg_m += (got != want)
    print("%s positive-finite: total=%d mism=%d; negative-finite: total=%d mism=%d"
          % (fmt, pos_t, pos_m, neg_t, neg_m))
