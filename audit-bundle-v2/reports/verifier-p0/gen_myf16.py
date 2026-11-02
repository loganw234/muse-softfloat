"""verifier-p0 independent binary16 oracle -> own vector file.

Field definitions only (SF-0 2.5 polarity, S1 5.7.2 class order).
Never read tests/gen_vectors.py.
"""
import random

QBIT = 0x200
SMASK = 0x8000
PROV = "my:f16-exhaustive"


def fields(x):
    return (x >> 15) & 1, (x >> 10) & 0x1F, x & 0x3FF


def is_nan(x):
    _, e, f = fields(x)
    return e == 0x1F and f != 0


def cls(x):
    s, e, f = fields(x)
    if e == 0x1F:
        if f == 0:
            return 2 if s else 9
        return 1 if (f & QBIT) else 0
    if e == 0:
        if f == 0:
            return 5 if s else 6
        return 4 if s else 7
    return 3 if s else 8


def preds(x):
    s, e, f = fields(x)
    nan = e == 0x1F and f != 0
    return {
        "is_sign_minus": 1 if s else 0,
        "is_normal": 1 if (0 < e < 0x1F) else 0,
        "is_finite": 0 if e == 0x1F else 1,
        "is_zero": 1 if (e == 0 and f == 0) else 0,
        "is_subnormal": 1 if (e == 0 and f != 0) else 0,
        "is_infinite": 1 if (e == 0x1F and f == 0) else 0,
        "is_nan": 1 if nan else 0,
        "is_signaling": 1 if (nan and not (f & QBIT)) else 0,
        "is_canonical": 1,
    }


out = ["# verifier-p0 independent f16 exhaustive (own oracle, field definitions)"]
for x in range(65536):
    h = "%x" % x
    out.append("msf16_class - %s -> %x -- %s" % (h, cls(x), PROV))
    for op, v in preds(x).items():
        out.append("msf16_%s - %s -> %x -- %s" % (op, h, v, PROV))
    out.append("msf16_copy - %s -> %s -- %s" % (h, h, PROV))
    out.append("msf16_negate - %s -> %x -- %s" % (h, x ^ SMASK, PROV))
    out.append("msf16_abs - %s -> %x -- %s" % (h, x & 0x7FFF, PROV))
    out.append("msf16_radix - %s -> %x -- %s" % (h, 2, PROV))
    out.append("msf16_is754version1985 - -> %x -- %s" % (0, PROV))
    out.append("msf16_is754version2019 - -> %x -- %s" % (1, PROV))

# copysign: directed specials cross + seeded sample
specials = [0x0000, 0x8000, 0x0001, 0x8001, 0x03FF, 0x83FF, 0x0400, 0x8400,
            0x3C00, 0xBC00, 0x7BFF, 0xFBFF, 0x7C00, 0xFC00, 0x7C01, 0xFC01,
            0x7DFF, 0xFDFF, 0x7E00, 0xFE00, 0x7FFF, 0xFFFF, 0x3555, 0xBAAA]
for a in specials:
    for b in specials:
        out.append("msf16_copy_sign - %x %x -> %x -- %s"
                   % (a, b, (a & 0x7FFF) | (b & 0x8000), "my:copysign-directed"))
rng = random.Random(0xF16)
for _ in range(20000):
    a, b = rng.getrandbits(16), rng.getrandbits(16)
    out.append("msf16_copy_sign - %x %x -> %x -- %s"
               % (a, b, (a & 0x7FFF) | (b & 0x8000), "my:copysign-sample"))

# f32/f64 directed encodings from width-parametrized field oracle
def gen_width(bits, w, prefix):
    t = bits - 1 - w
    emax_val = (1 << w) - 1
    qb = 1 << (t - 1)
    sm = 1 << (bits - 1)
    vals = [0, sm, 1, sm | 1, (1 << t) - 1, sm | ((1 << t) - 1),
            1 << t, sm | (1 << t),
            ((emax_val - 1) << t) | ((1 << t) - 1),
            sm | ((emax_val - 1) << t) | ((1 << t) - 1),
            (emax_val << t), sm | (emax_val << t),
            (emax_val << t) | 1, (emax_val << t) | qb,
            (emax_val << t) | ((1 << t) - 1),
            sm | (emax_val << t) | ((1 << t) - 1),
            (1 << (bits - 1)) | 0x1234 & ((1 << t) - 1),
            0xAAAAAAAA & ((1 << bits) - 1), 0x55555555 & ((1 << bits) - 1),
            (1 << bits) - 1]
    res = []
    for x in vals:
        s = (x >> (bits - 1)) & 1
        e = (x >> t) & emax_val
        f = x & ((1 << t) - 1)
        nan = e == emax_val and f != 0
        if e == emax_val:
            c = (1 if (f & qb) else 0) if f else None
            c = c if f else None
            cc = (1 if (f & qb) else 0) if f else (2 if s else 9)
        elif e == 0:
            cc = (5 if s else 6) if f == 0 else (4 if s else 7)
        else:
            cc = 3 if s else 8
        h = "%x" % x
        res.append("%s_class - %s -> %x -- %s" % (prefix, h, cc, "my:directed-enc"))
        res.append("%s_is_nan - %s -> %x -- %s" % (prefix, h, 1 if nan else 0, "my:directed-enc"))
        res.append("%s_is_signaling - %s -> %x -- %s"
                   % (prefix, h, 1 if (nan and not (f & qb)) else 0, "my:directed-enc"))
        res.append("%s_is_canonical - %s -> 1 -- %s" % (prefix, h, "my:directed-enc"))
        res.append("%s_copy - %s -> %s -- %s" % (prefix, h, h, "my:directed-enc"))
        res.append("%s_negate - %s -> %x -- %s" % (prefix, h, x ^ sm, "my:directed-enc"))
        res.append("%s_abs - %s -> %x -- %s" % (prefix, h, x & ((1 << bits) - 1 - sm), "my:directed-enc"))
    return res

out += gen_width(32, 8, "msf32")
out += gen_width(64, 11, "msf64")
out.append("msf_is754version1985 - -> 0 -- my:versions")
out.append("msf_is754version2008 - -> 0 -- my:versions")
out.append("msf_is754version2019 - -> 1 -- my:versions")

with open(r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\verifier-p0\my-f16-exhaustive.vec",
          "w", newline="\n") as fh:
    fh.write("\n".join(out) + "\n")
print("wrote", len(out), "lines")
