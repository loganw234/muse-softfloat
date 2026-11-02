"""verifier-p0 u128 adversarial differential vs Python ints."""
import random
import subprocess

M = (1 << 128) - 1


def gen():
    vals = [0, 1, 2, (1 << 64) - 1, 1 << 64, (1 << 64) + 1,
            (1 << 32) - 1, 1 << 32, M, M - 1, M >> 1, 1 << 127,
            (1 << 127) + 1, 0xFFFFFFFFFFFFFFFF, 0x123456789ABCDEF0,
            0xFEDCBA9876543210FEDCBA9876543210 & M]
    rng = random.Random(0x128)
    vals += [rng.getrandbits(128) for _ in range(60)]
    lines = []
    vals64 = [v & ((1 << 64) - 1) for v in vals] + [rng.getrandbits(64) for _ in range(60)]
    for _ in range(400):
        a = rng.choice(vals64)
        b = rng.choice(vals64)
        lines.append(("mul %016x %016x" % (a, b),
                      "%032x" % ((a * b) & M)))
    for a in vals:
        for n in [0, 1, 2, 31, 32, 33, 63, 64, 65, 95, 96, 97, 126, 127]:
            lines.append(("shl %032x %d" % (a, n), "%032x" % ((a << n) & M)))
            lines.append(("shr %032x %d" % (a, n), "%032x" % ((a >> n) & M)))
            for st in [0, 1]:
                lo = a & ((1 << n) - 1) if n else 0
                jam = ((a >> n) | (1 if (lo or st) else 0)) & M
                lines.append(("jam %032x %d %d" % (a, n, st), "%032x" % jam))
            lines.append(("clz %032x" % a,
                          "%d" % (128 - a.bit_length() if a else 128)))
    # mul adversarial: max*max and high-bit u64 products
    U64 = (1 << 64) - 1
    for (a, b) in [(U64, U64), (U64, 2), (1 << 63, 2), (1 << 63, 1 << 63),
                   (U64, 1 << 63), (0xFFFFFFFF, 0xFFFFFFFF)]:
        lines.append(("mul %016x %016x" % (a, b), "%032x" % ((a * b) & M)))
    return lines


lines = gen()
inp = "".join(l + "\n" for (l, _) in lines)
p = subprocess.run(
    [r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-p0\vpack_probe.exe"],
    input=inp, capture_output=True, text=True, timeout=120)
assert p.returncode == 0, p.stderr[:500]
out = p.stdout.splitlines()
assert len(out) == len(lines), (len(out), len(lines))
bad = 0
for ((l, exp), got) in zip(lines, out):
    if got.strip() != exp:
        bad += 1
        if bad <= 15:
            print("MISMATCH", l, "C=" + got, "py=" + exp)
print("u128: %d cases, %d mismatches" % (len(lines), bad))
