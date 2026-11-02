"""verifier-p0 flag-ops differential: ANY-of-group model vs implementation."""
import itertools
import subprocess

ALL = 0x1F


def any_test(state, group):
    return 1 if (state & group & ALL) else 0


def py_raise(state, group):
    return state | (group & ALL)


def py_lower(state, group):
    return state & ~(group & ALL) & 0xFFFFFFFF


def restore(state, saved, group):
    g = group & ALL
    return ((state & ~g) | (saved & g)) & 0xFFFFFFFF


def save(state):
    return state & ALL


lines, expect = [], []
swatches = [0x00, 0x01, 0x02, 0x03, 0x05, 0x0A, 0x10, 0x1F, 0x20, 0xFF,
            0x100, 0xFFFFFFFF]
for s in swatches:
    for g in swatches:
        lines.append("test %x %x" % (s, g)); expect.append("%d" % any_test(s, g))
        lines.append("saved %x %x" % (s, g)); expect.append("%d" % any_test(s, g))
        lines.append("raise %x %x" % (s, g)); expect.append("%x" % py_raise(s, g))
        lines.append("lower %x %x" % (s, g)); expect.append("%x" % py_lower(s, g))
        lines.append("save %x" % s); expect.append("%x" % save(s))
for s in swatches:
    for sv in [0x00, 0x1F, 0x0B, 0xFF]:
        for g in swatches:
            lines.append("restore %x %x %x" % (s, sv, g))
            expect.append("%x" % restore(s, sv, g))
lines.append("versions"); expect.append("0 0 1 0 0 1 0 0 1 0 0 1")

p = subprocess.run(
    [r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-p0\vflag_probe.exe"],
    input="\n".join(lines) + "\n", capture_output=True, text=True, timeout=60)
assert p.returncode == 0, p.stderr[:500]
out = p.stdout.splitlines()
assert len(out) == len(lines), (len(out), len(lines))
bad = 0
for (l, e, g) in zip(lines, expect, out):
    if g.strip() != e:
        bad += 1
        if bad <= 15:
            print("MISMATCH", l, "C=" + g, "anymodel=" + e)
print("flags: %d cases, %d mismatches" % (len(lines), bad))
# the ANY-vs-ALL discriminator: state has SOME but not ALL group bits
disc = [("test 2 3", "1"), ("test 1 3", "1"), ("test 10 1f", "1"),
        ("test 0 1f", "0"), ("test 1f 0", "0")]
print("discriminators (any-model says):", disc)
