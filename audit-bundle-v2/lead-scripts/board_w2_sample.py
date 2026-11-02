# Wave-2 board sample: every Nth line from committed binary16 and
# cross-format directed sets (deterministic).
import pathlib
import sys

ROOT = pathlib.Path(__file__).parents[2] / "muse-softfloat/tests/vectors"
FILES = [
    ("arith-f16.vec", 17), ("fma-sqrt-f16.vec", 9), ("conv-int-f16.vec", 9),
    ("toint-f16.vec", 9), ("rint-misc-f16.vec", 9), ("compare-f16.vec", 11),
    ("arith-xf.vec", 9), ("fma-sqrt-xf.vec", 7), ("conv-xf.vec", 7),
    ("compare-xf.vec", 9), ("traps-xf.vec", 3),
]
out = []
for name, step in FILES:
    lines = [l for l in (ROOT / name).read_text().splitlines()
             if l.strip() and not l.startswith("#")]
    picked = lines[::step]
    out.extend(picked)
    print("%s: %d of %d" % (name, len(picked), len(lines)))
hdr = (ROOT / "arith-f64.vec").read_text().splitlines()[0:2]
pathlib.Path(sys.argv[1]).write_text("\n".join(hdr + out) + "\n")
print("total %d -> %s" % (len(out), sys.argv[1]))
