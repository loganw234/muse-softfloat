import struct, sys
sys.path.insert(0, r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w3-str\tests")
import gen_vectors_str as g

S = r"C:\Users\logan\source\repos\Muse-Softfloat\scratch\parcel-str"

def f64bits(x):
    return struct.unpack("<Q", struct.pack("<d", x))[0]

# 1) bulk from-decimal f64 te lines: CPython float() (correctly
#    rounded strtod) decides independently of my pack_ratio.
n = bad = skipped = 0
with open(S + r"\bulk\from-decimal-600k.vec", encoding="utf-8") as f:
    for line in f:
        tok = line.split()
        if len(tok) != 8 or not tok[0].startswith("msf64_") or tok[1] != "te":
            continue
        s = tok[2][3:]
        want = int(tok[4], 16)
        try:
            got = f64bits(float(s))
        except (ValueError, OverflowError):
            skipped += 1
            continue
        # float() consumes the whole string or raises; only compare
        # where our grammar also consumes everything
        _, _, c = g.from_decimal_ref(s, "te", "f64")
        if c != len(s):
            skipped += 1
            continue
        n += 1
        if got != want:
            bad += 1
            if bad <= 5:
                print("PYFLOAT MISMATCH", s, hex(got), hex(want))
        if n >= 40000:
            break
print(f"pyfloat from-decimal f64 te: compared={n} skipped={skipped} mismatches={bad}")

# 2) bulk to-decimal f64 outputs with precision >= 17 scientific:
#    float(OUT) must reproduce A exactly (round-trip via CPython).
n = bad = 0
with open(S + r"\bulk\to-decimal-700k.vec", encoding="utf-8") as f:
    for line in f:
        tok = line.split()
        if len(tok) != 9 or not tok[0].startswith("msf64_") or tok[1] != "te":
            continue  # round-trip is a nearest-attribute property (5.12.2)
        spec = tok[3][5:].split(",")
        prec, style = int(spec[0]), int(spec[1])
        if prec < 17:
            continue
        a = int(tok[2][2:], 16)
        out = tok[5][4:]
        d = g.decode("f64", a)
        if d["cls"] in ("qnan", "snan"):
            continue
        n += 1
        if f64bits(float(out)) != a:
            bad += 1
            if bad <= 5:
                print("PYFLOAT RT MISMATCH", hex(a), out, hex(f64bits(float(out))))
        if n >= 40000:
            break
print(f"pyfloat to-decimal f64 roundtrip: compared={n} mismatches={bad}")
sys.exit(1 if bad else 0)
