#!/usr/bin/env python3
"""Committed directed vectors for sinPi/cosPi (SF-1 Step 2c).

Expected values are decided by MPFR at 640-bit precision with
bracketed narrowing through the decider mode of
tests/trig_exhaustive.c (build it first; path from
MSF_TRIG_DECIDER or build/trig/trig_exhaustive.exe).
Provenance family: mpfr640-trig:* (one tag per input family).

The specials expectations are ALSO computed here from the
settled 9.2.1 table (ledger/parcel-w4trig.md design entry:
sinPi at an integer delivers a zero with the sign of x,
cosPi at a half-integer delivers +0 in every mode, NaNs via
the SF-0 2.5 matrix, +-inf -> invalid + default qNaN) and
generation REFUSES if the decider disagrees on any special -
the two implementations cross-check.

Input families per format/function (~1500 inputs each, all
four modes): specials (zeros, infinities, quiet/signaling
NaN payload samples), integer and half-integer anchors
(including the ulp>=1 region and both settled zero-sign
cells in every mode), a k/8 lattice with +-3 ulp neighbours
at several scales (bounce pairs around the anchors), tiny
and subnormal inputs (saturation family near +-1 for the
cos-shaped results), hardest-known excerpts (binary64:
measured-hardest patterns from the published worst-case
input sets, mechanically extracted by the Step 2b census -
inputs only, every value re-decided here; binary16/32: the
spike-measured hardest patterns and pi-convergent
neighbourhoods), and a seeded class sweep.

Usage: gen_vectors_trig.py OUTDIR   (writes trig-f16.vec,
trig-f32.vec, trig-f64.vec; byte-identical regeneration)
"""
import os
import random
import subprocess
import sys
from fractions import Fraction

FMTS = {
    "f16": (16, 5),
    "f32": (32, 8),
    "f64": (64, 11),
}
FNS = ("sin_pi", "cos_pi")
RMS = ("te", "tz", "tp", "tn")
INVALID = 0x01


def params(fmt):
    bits, w = FMTS[fmt]
    t = bits - 1 - w
    return {
        "bits": bits, "w": w, "t": t, "p": t + 1,
        "bias": (1 << (w - 1)) - 1,
        "emaxf": (1 << w) - 1,
        "sign": 1 << (bits - 1),
        "fracmask": (1 << t) - 1,
        "qbit": 1 << (t - 1),
        "inf": ((1 << w) - 1) << t,
        "one": (((1 << (w - 1)) - 1) << t),
    }


def fields(fmt, x):
    q = params(fmt)
    return ((x >> (q["bits"] - 1)) & 1,
            (x >> q["t"]) & q["emaxf"],
            x & q["fracmask"], q)


def encode_value(fmt, v: Fraction):
    """Exact encoding of a dyadic rational that fits the
    format, or None. Used only to BUILD directed inputs."""
    q = params(fmt)
    if v == 0:
        return 0
    sign = 1 if v < 0 else 0
    av = abs(v)
    m = av.numerator
    d = av.denominator
    if d & (d - 1):
        return None
    e = -(d.bit_length() - 1)  # av = m * 2^e exactly
    assert Fraction(m) * Fraction(2) ** e == av
    bl = m.bit_length()
    unbiased = e + bl - 1
    emin = 1 - q["bias"]
    if unbiased >= emin:
        if bl > q["p"]:
            return None
        frac = (m << (q["p"] - bl)) - (1 << (q["p"] - 1))
        ef = unbiased + q["bias"]
        if ef >= q["emaxf"]:
            return None
        return (sign << (q["bits"] - 1)) | (ef << q["t"]) | frac
    shift = emin - q["t"] - e
    if shift < 0:
        return None
    frac = m << shift
    if frac >= (1 << q["t"]) or frac == 0:
        return None
    return (sign << (q["bits"] - 1)) | frac


def neighbours(fmt, x, n=3):
    q = params(fmt)
    mask = (1 << q["bits"]) - 1
    out = []
    for d in range(-n, n + 1):
        y = x + d
        if 0 <= y <= mask:
            out.append(y)
    return out


def specials(fmt):
    q = params(fmt)
    s = q["sign"]
    payloads = [1, 2, 3, (1 << (q["t"] - 1)) - 1, 1 << (q["t"] - 2)]
    out = [0, s, q["inf"], q["inf"] | s]
    for p in payloads:
        out.append(q["inf"] | q["qbit"] | p)
        out.append(q["inf"] | q["qbit"] | p | s)
        out.append(q["inf"] | p)
        out.append(q["inf"] | p | s)
    out.append(q["inf"] | q["qbit"])
    return out


def anchors(fmt):
    out = set()
    vals = []
    for n in range(-9, 10):
        vals.append(Fraction(n))
        vals.append(Fraction(n) + Fraction(1, 2))
    q = params(fmt)
    step = 1 if fmt == "f16" else (2 if fmt == "f32" else 3)
    for k in range(2, q["p"] + 2, step):
        for base in (Fraction(2) ** k, Fraction(2) ** k + 1):
            vals.append(base)
            vals.append(-base)
            vals.append(base + Fraction(1, 2))
            vals.append(-base - Fraction(1, 2))
    for v in vals:
        x = encode_value(fmt, v)
        if x is not None:
            out.update(neighbours(fmt, x, 1))
    return sorted(out)


def lattice(fmt):
    out = set()
    scales = [Fraction(2) ** s for s in
              (-17, -8, -3, 0, 1, 4, 9, 16, 25)]
    for sc in scales:
        for m in range(-12, 13):
            x = encode_value(fmt, Fraction(m, 8) * sc)
            if x is not None:
                out.update(neighbours(fmt, x, 3))
    return sorted(out)


def tiny(fmt):
    q = params(fmt)
    s = q["sign"]
    out = set()
    for f in list(range(1, 10)) + [(1 << q["t"]) - i for i in range(1, 5)]:
        out.add(f)
        out.add(f | s)
    minnorm = 1 << q["t"]
    for d in range(-6, 7):
        out.add(minnorm + d)
        out.add((minnorm + d) | s)
    return sorted(out)


# Measured-hardest input patterns (spike Section 2/3
# measurements; inputs only - values decided by MPFR below).
HARDEST = {
    "f64": {
        "sin_pi": [0x3CDF339AB57731D3, 0x3D33C059D39F1D61],
        "cos_pi": [0x3E78242846E3D0AF, 0x3F2B17C08C8AB938],
    },
    "f32": {"sin_pi": [], "cos_pi": []},
    "f16": {
        "sin_pi": [0x0071, 0x8071],
        "cos_pi": [0x2334, 0xA334],
    },
}
HARDEST_EXT = {
    "f64": {
        "sin_pi": [0x3CDF339AB57731D3, 0x3D33C059D39F1D61, 0x3D014D4375C40C51, 0x3D566343CFEA22CD, 0xBFE1E4DEE8168D6B, 0xBFDC36422FD2E52A, 0x3FE1E4DEE8168D6B, 0x3FDC36422FD2E52A, 0x3D101057F17CEBA6, 0x3DDAD53F8DB92AF0, 0x3DAA8851B86F2C07, 0x3F47338C5CC7D7C8, 0x3E21A232520B30B8, 0x3E6C6B0698C28D70, 0x3F97F01B487F25A6, 0x3DE2C15B0E2BECE3, 0x3EAD9A3AE588D66E, 0x3FA7A1E846E4E346, 0x3D023946EFEC49A8, 0x3DB053FAD95A3298, 0x3DD25142C0254B86, 0x3EA5F3AAA98D64BB, 0x3EFC40F5F6F7312D, 0x3D77FE08F5284726, 0x3D5A65DAB603E8B2, 0x3F52872CD25F2925, 0x001B44453E2404E7, 0xBFCE99D785D705F5, 0x3FCE99D785D705F5, 0x3E633624C2454BB9, 0x3F22B5F60D43677A, 0x3ECD7CC83E61CBE7, 0x3CCEFE2D4AA2D140, 0x3D991A75C23A207F, 0x3ED1924F277EBC40, 0x3F5731F6C0520517, 0x4004D1245667CB39, 0x40032EDBA99834C7, 0x3FE34491599F2CE4, 0x3FD976DD4CC1A638, 0x3DB52F224A74F956, 0x3EEC215EAFD4639D, 0x3CAD342812CE31FB, 0x3F1B98F3BF70E3B6, 0x3E5E4B120B7CD0CC, 0x3F75A56887BE3F23, 0x3E31E23451360F11, 0x3DD6FE509010E3C6, 0x3F05D93564304470, 0x3D3F31E9057DD0CC, 0xBFAAF661A8AF86DA, 0x3FAAF661A8AF86DA, 0x3F56063E6AD702B4, 0x3D239785114BAE2D, 0x3CACB82F5DA3A6B6, 0x3DDAE859C3537F4D, 0x3F340E173F72A36D, 0x3E86C9F29F599930, 0x3F95F230FA0B27D8, 0x3FC16747DF915497, 0x3CD405E28FFACCC8, 0x3E77FE3A23038269, 0x3EE98E5DD17E1E20, 0x3D209A606E188BC7, 0xBFA2F6C4A60085CD, 0x3FA2F6C4A60085CD, 0x3D109F8252784340, 0x3CEDBE22847498A9, 0x3F63B0578EC6EBA8, 0x3DEB0BC9CC64068F, 0x3E536B0F6E36A406, 0x3E8A4BE221363F8D, 0x3F232550F04BDA91, 0x3E1BC8EF6C8159E0, 0x3DFD0CA30163B96F, 0x3E8CFAA1DF3FACB1, 0x3EEC4AA20C681596, 0x3E556B80301DD491, 0x3E9049BEAD920AFE, 0x3EBE64391E1B5975, 0x3CE65B704AF8CA16, 0x3DC39B90212E4697, 0x3EF3638F2B028E92, 0x3F6C9A310E367ED2, 0x3F73454736D795B9, 0x3E797267383BF965, 0x3D0ECCEDB62EC785, 0x3EDEE04A62426C77, 0x3D4F18017EF6F2C3, 0x3ECE2C63435C3C35, 0x3DD1B3E699A79FD3, 0x3D49F3F0E08AF3D4, 0x3D5687CB87119F0D, 0x3F1BE87F6B8D2560, 0x001BC03DF34E902C, 0x000DE01EF9A74816, 0x0006F00F7CD3A40B, 0x3F18571410742C01, 0x3F849542683BCADF, 0x3E781A31C7702F65, 0x3F589F23D737C0E1, 0x3F3014EF8DCA042C, 0x3F0F36965410AFCE, 0x3F6C1F8D0F703975, 0x3F6003EC8286A4FB, 0x3CE02B4CD5FB638C, 0x3EEC896682191179, 0x3DA62CA372C670B9, 0x3ED238A49345AAA5, 0x3EC45331BFCFAAB3, 0x432FFFFFFFFFFFFF, 0x432FFFFFFFFFFFFD, 0x407FE80000000000, 0x407FD80000000000, 0x407FC80000000000, 0x407FB80000000000, 0x407FA80000000000, 0x407F980000000000, 0x407F880000000000, 0x407F780000000000, 0x407F680000000000, 0x407F580000000000, 0x407F480000000000, 0x407F380000000000, 0x407F280000000000, 0x407F180000000000, 0x407F080000000000, 0x407EF80000000000],
        "cos_pi": [0x3E78242846E3D0AF, 0x3F5F3BEB28414801, 0x3EBF9A45CE01134F, 0x3FEE1B2117E97295, 0x3FAE4DEE8168D6B0, 0x3F2B17C08C8AB938, 0x3FBA67C4D04A9236, 0x3F12D86BFD76D86E, 0x3F4C46D82AA5DABD, 0x3F272C570C20E4B5, 0x3EFD58F60E905D1C, 0x3ECA8A057FD76CD3, 0x3FC0341B9DB1CFF3, 0x3F0DBED8085C7978, 0x3F436A6CC8F63FD3, 0x3F553D1101816A31, 0x3F72F3C7872C959B, 0x3F9B0FDEDBCE51ED, 0x3F6396D4BE3EAD8C, 0x400F2EDBA99834C7, 0x4008D1245667CB39, 0x40072EDBA99834C7, 0x4000D1245667CB39, 0x3FFE5DB75330698E, 0x3FF1A248ACCF9672, 0x3FECBB6EA660D31C, 0x3FBA248ACCF96720, 0x3FB82E06677256D1, 0x3F8AB801085D697B, 0x3E99D9CE0957F1C8, 0x3FC69C0E1DFBF177, 0x3FB381FBD2A5E55E, 0x3E7192CF274B2B70, 0x3EBE93146B977607, 0x3E6D08C9C56A2390, 0x3EE64444D2D051E1, 0x3E9E0F44F549F896, 0x3ED70C3E3F71BD49, 0x3F883D1FC2E1ACE6, 0x3F3A8407FE55410A, 0x3F44E6C918D64E69, 0x3EAC49D5E552F7E8, 0x3E933FCB58AD4293, 0x3EE5725295C952EB, 0x3E64FFB1A7269827, 0x3ED9CBFF3284A4FB, 0x3EC48BC559945371, 0x3E842C022A200C36, 0x3E7AE77CC45F8687, 0x3F65BBEF584E580D, 0x3F731CAD58B29A9E, 0x3EB595AB6556FA30, 0x3F4FF108349596A7, 0x3F20DEF8514D697A, 0x3F7BA2C9DBA2216D, 0x3E430E5CDED67CAF, 0x3EFB018020FC41C3, 0x3F8DF2319C8B713D, 0x3E54B00CB56DBC65, 0x3EA4429F488819DA, 0x3E96E68F1AA4BD96, 0x3F98A83F06A14E8B, 0x3FB2C16E6705F29D, 0x3F75B4C5C663D05E, 0x3FB8BC9D4D4867BA, 0x3F7395E0B8DBF828, 0x3EDFD7F6CE68F482, 0x3EF8E05EBD2DAD28, 0x3E459B8B1F4ECC99, 0x3EE96D5D2A023E6A, 0x3ED1F23A5C935FBB, 0x3F76889A45771046, 0x3F87EEC189ED3DDA, 0x3F4D39D50E68302F, 0x3F38229AD52981D5, 0x3F4B27F67841133C, 0x3F670DF9F77D7BC5, 0x3FB10D4D8BEDE766, 0x3FA2EAD4214DDBF3, 0x3EF95AD096669072, 0x3EA764E72E6FC601, 0x3EBAF085138FCFBE, 0x3ECE31DA2E760BA6, 0x3F5B1F76A9EBB24B, 0x3EFEB98E6C83B9BA, 0x3E49F8167CDF5123, 0x3F14C79BF81F84AE, 0x3F9AFA164888F8B6, 0x3F5FAF171C84BB9E, 0x3FEE9D268484D89F, 0x3FA62D97B7B27610, 0x3F8BA42A05808076, 0x3F8D902CA79FAB44, 0x3F6EA5B9AD933336, 0x3F02A4BF311496E2, 0x3FDF93792DA37AD1, 0x3F7C2101E8599E2F, 0x3EC351E4F6334AD4, 0x3FAAFC98FDD86AD5, 0x3E445F306DC9C883, 0x3F5FEA72C9D0EA12, 0x3E97DC0486703DFE, 0x3FDBB59E68DA6E1D, 0x3F2C6A9149E4D3D1, 0x3EB3FCBCDA7A963C, 0x3FE60887C848515F, 0x3FD3EEF06F6F5D42, 0x3F04C898E32C3D17, 0x404FCE79BDA5E1EF, 0x404FB186425A1E11, 0xFFEFFFFFFFFFFFFF, 0xBFF0000000000000, 0x8010000000000000, 0x800FFFFFFFFFFFFF, 0x8000000000000001, 0x8000000000000000, 0x7FEFFFFFFFFFFFFF, 0x4335F4721C0FFFFF, 0x4330000000000001, 0x407FE00000000000, 0x407FD00000000000, 0x407FC00000000000, 0x407FB00000000000, 0x407FA00000000000, 0x407F900000000000, 0x407F800000000000, 0x407F700000000000, 0x407F600000000000],
    },
    "f32": {
        "sin_pi": [0x00000071, 0x3D9D3E52, 0x3ED4F153, 0x39FE6F24, 0x37538517, 0x3D8073E0, 0x36BA0B62, 0x3E4B4DF6, 0x3E04508A, 0x37B36BC6, 0x3E13A7CA, 0x39FD590C, 0x3B0EF05A, 0x3B73217F, 0x3A129652, 0x3EC7A519, 0x3D3BA788, 0x3C6735D6, 0x3E633EF9, 0x36BB9188, 0x3E3A01EB, 0x3E92379C, 0x3F534A47, 0x3D439873, 0x3D88265A, 0x3B5D57D8, 0x37485C00, 0x3F47C08A, 0x3DAD1207, 0x39100000, 0x3B4A0AA8, 0x39F6647A, 0x3E034CFC, 0x3F2DCAA3, 0x3EA46ABA, 0x3F76A017, 0x39CD9D98, 0x3E4BF0C0, 0x3F747B9A, 0x3F0C9EA6, 0x3EE6C2B4, 0x3B0894AE, 0x00003880, 0x3EB89BC3, 0x3EED7610, 0x3B37E2C7, 0x37C9B273, 0x370573D5, 0x36A6FC2E, 0x3C48CE61, 0x3A0BB0F0, 0x3F2BA0D0, 0x39A43759, 0x37A4D81E, 0x3DBBECD3, 0x3BB81703, 0x3B384D00, 0x3E5C75A4, 0x3D437280, 0x39718E54, 0x3F5067D8, 0x3C75D7F0, 0x3EBCB9DD, 0x3EBB2F1E],
        "cos_pi": [0x18000000, 0x17E20000, 0x17C0E400, 0x16100000, 0x15A00000, 0x15400000, 0x15318000, 0x14800000, 0x14620000, 0x1440E400, 0x12900000, 0x12200000, 0x11C00000, 0x11B18000, 0x11000000, 0x10E20000, 0x10C0E400, 0x0F100000, 0x0EA00000, 0x0E400000, 0x0E318000, 0x0D800000, 0x0D620000, 0x0D40E400, 0x0B900000, 0x0B200000, 0x0AC00000, 0x0AB18000, 0x0A000000, 0x09E20000, 0x09C0E400, 0x08100000, 0x07A00000, 0x07400000, 0x07318000, 0x06800000, 0x06620000, 0x0640E400, 0x04900000, 0x04200000, 0x03C00000, 0x03B18000, 0x03000000, 0x02E20000, 0x02C0E400, 0x01100000, 0x00A00000, 0x00600000, 0x0058C000, 0x00200000, 0x001C4000, 0x00181C80, 0x00024000, 0x00014000, 0x0000C000, 0x0000B180, 0x00004000, 0x00003880, 0x00003039, 0x00000480, 0x00000280, 0x00000180, 0x00000163, 0x00000080],
    },
    "f16": {"sin_pi": [], "cos_pi": []},
}


def seeded(fmt, fn, n, seed):
    q = params(fmt)
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        x = rng.getrandbits(q["bits"])
        _, e, _, _ = fields(fmt, x)
        if e == q["emaxf"]:
            continue
        out.append(x)
    return out


def expected_special(fmt, fn, x):
    """Settled-table expectation (bits, flags) x4 modes, or
    None when x is not special. Independent Python restatement."""
    sign, e, frac, q = fields(fmt, x)
    sbit = sign << (q["bits"] - 1)
    is_cos = fn == "cos_pi"
    if e == q["emaxf"]:
        if frac == 0:
            r = q["inf"] | q["qbit"]
            return [(r, INVALID)] * 4
        r = x | q["qbit"]
        fl = 0 if frac & q["qbit"] else INVALID
        return [(r, fl)] * 4
    if e == 0 and frac == 0:
        r = q["one"] if is_cos else sbit
        return [(r, 0)] * 4
    if e == 0:
        sig, ex = frac, (1 - q["bias"]) - q["t"]
    else:
        sig, ex = frac | (1 << q["t"]), e - q["bias"] - q["t"]
    v = Fraction(sig) * Fraction(2) ** ex
    av = abs(v)
    fl_int = av.numerator // av.denominator
    rem = av - fl_int
    if rem == 0:
        if is_cos:
            r = q["one"] | (((fl_int & 1)) << (q["bits"] - 1))
        else:
            r = sbit
        return [(r, 0)] * 4
    if rem == Fraction(1, 2):
        if is_cos:
            return [(0, 0)] * 4
        r = q["one"] | ((sign ^ (fl_int & 1)) << (q["bits"] - 1))
        return [(r, 0)] * 4
    return None


def opname(fmt, fn):
    return f"msf{fmt[1:]}_{fn}"


def build_inputs(fmt, fn):
    fams = []
    fams.append(("specials", specials(fmt)))
    fams.append(("anchors", anchors(fmt)))
    fams.append(("lattice", lattice(fmt)))
    fams.append(("tiny", tiny(fmt)))
    hard = HARDEST[fmt][fn] + HARDEST_EXT[fmt][fn]
    hard_x = []
    for x in hard:
        hard_x.extend(neighbours(fmt, x, 1))
    fams.append(("hardest", sorted(set(hard_x))))
    seed = 20261027 + (0 if fn == "sin_pi" else 1111) + int(fmt[1:])
    have = sum(len(v) for _, v in fams)
    fams.append(("seeded", seeded(fmt, fn, max(0, 1500 - have), seed)))
    seen = set()
    out = []
    for fam, xs in fams:
        for x in xs:
            if x not in seen:
                seen.add(x)
                out.append((fam, x))
    return out


def main():
    outdir = sys.argv[1]
    exe = os.environ.get(
        "MSF_TRIG_DECIDER",
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "..", "build", "trig", "trig_exhaustive.exe"))
    if not os.path.exists(exe):
        print(f"decider not found: {exe} (set MSF_TRIG_DECIDER)",
              file=sys.stderr)
        return 2
    jobs = []
    for fmt in FMTS:
        for fn in FNS:
            for fam, x in build_inputs(fmt, fn):
                jobs.append((fmt, fn, fam, x))
    inp = "".join(f"{opname(fmt, fn)} {x:x}\n"
                  for fmt, fn, _, x in jobs)
    proc = subprocess.run([exe, "decide"], input=inp,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stdout.write(proc.stdout[-2000:])
        print("decider failed", file=sys.stderr)
        return 1
    decided = {}
    for line in proc.stdout.splitlines():
        t = line.split()
        if len(t) == 10:
            decided[(t[0], t[1])] = [
                (int(t[2], 16), int(t[3], 16)),
                (int(t[4], 16), int(t[5], 16)),
                (int(t[6], 16), int(t[7], 16)),
                (int(t[8], 16), int(t[9], 16)),
            ]
    if len(decided) != len(jobs):
        print(f"decider returned {len(decided)} of {len(jobs)}",
              file=sys.stderr)
        return 1
    files = {fmt: [] for fmt in FMTS}
    for fmt, fn, fam, x in jobs:
        op = opname(fmt, fn)
        exp = decided[(op, f"{x:x}")]
        mine = expected_special(fmt, fn, x)
        if mine is not None and mine != exp:
            print(f"SPECIAL DISAGREE {op} {x:x}: settled {mine} "
                  f"decider {exp}", file=sys.stderr)
            return 1
        for rm, (rb, rf) in zip(RMS, exp):
            files[fmt].append(
                f"{op} {rm} {x:x} -> {rb:x} {rf:02x} mpfr640-trig:{fam}")
    os.makedirs(outdir, exist_ok=True)
    total = 0
    for fmt in FMTS:
        path = os.path.join(outdir, f"trig-{fmt}.vec")
        with open(path, "w", newline="\n", encoding="utf-8") as fh:
            fh.write("# generated by tests/gen_vectors_trig.py"
                     " - do not edit (regenerate)\n")
            fh.write("# expectations: MPFR 640-bit bracketed"
                     " decider (tests/trig_exhaustive.c)\n")
            for line in files[fmt]:
                fh.write(line + "\n")
        total += len(files[fmt])
        print(f"wrote {path}: {len(files[fmt])} lines")
    print(f"total {total} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
