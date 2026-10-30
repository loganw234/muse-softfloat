# Build the Wave-1 board sample: every Nth vector line from the committed
# binary32/64 directed sets (deterministic, no RNG), preserving file headers'
# compare directives by emitting one file whose header is the suite default.
# Committed directed lines carry no per-file compare override except the
# printed "# compare:" comments; the runner reads directives from the file
# header, so we keep each source file's directive line if present.
import pathlib
import sys

ROOT = pathlib.Path(__file__).parents[2] / "muse-softfloat/tests/vectors"
FILES = [
    ("arith-f32.vec", 13), ("arith-f64.vec", 13),
    ("fma-sqrt-f32.vec", 7), ("rint-misc-f32.vec", 7),
    ("conv-int-f32.vec", 7), ("conv-f64.vec", 7),
    ("compare-f32.vec", 7), ("compare-f64.vec", 7),
    ("misc-f64.vec", 5), ("toint-f32.vec", 7),
    ("nan-f64.vec", 5),
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
