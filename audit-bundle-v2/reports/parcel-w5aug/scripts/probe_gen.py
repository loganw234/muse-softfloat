import sys
import time
sys.path.insert(0, "tests")
import gen_vectors_aug as g

fmt = sys.argv[1] if len(sys.argv) > 1 else "f16"
t0 = time.time()
lines, fam = g.generate_fmt(fmt)
print(fmt, len(lines), "%.1fs" % (time.time() - t0))
for k in sorted(fam):
    print("  %-24s %s" % (k, fam[k]))
print("\n".join(lines[:5]))
