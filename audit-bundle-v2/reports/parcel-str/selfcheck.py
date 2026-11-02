import struct, sys
sys.path.insert(0, r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w3-str\tests")
import gen_vectors_str as g

bad = 0
def check(name, got, want):
    global bad
    if got != want:
        bad += 1
        print("FAIL", name, "got", got, "want", want)

def f64bits(x):
    return struct.unpack("<Q", struct.pack("<d", float(x)))[0]

for s in ["1.5", "0.1", "3.141592653589793", "1e300", "5e-324", "2.2250738585072014e-308",
          "1.7976931348623157e308", "0", "-2.5e-10", "123456789.123456789"]:
    bits, flags, c = g.from_decimal_ref(s, "te", "f64")
    check(f"from_dec {s}", bits, f64bits(s))
    check(f"from_dec {s} consumed", c, len(s))
for bits in [0, 0x3ff0000000000000, 0x400921fb54442d18, 1, 0x000fffffffffffff,
             0x7fefffffffffffff, 0x0010000000000000, 0x3cb0000000000000]:
    s, flags = g.to_decimal_ref(bits, (17,0,0), "te", "f64")
    b2, f2, c2 = g.from_decimal_ref(s, "te", "f64")
    check(f"roundtrip {bits:#x} via {s}", b2, bits)
    s2, _ = g.to_hex_ref(bits, -1, "te", "f64")
    b3, _, _ = g.from_hex_ref(s2, "te", "f64")
    check(f"hex roundtrip {bits:#x} via {s2}", b3, bits)
print("hex of pi bits:", g.to_hex_ref(0x400921fb54442d18, -1, "te", "f64"))
print("dec of max:", g.to_decimal_ref(0x7fefffffffffffff, (17,0,0), "te", "f64"))
print("dec 1.5 fix:", g.to_decimal_ref(0x3ff8000000000000, (5,1,0), "te", "f64"))
print("minsub dec20:", g.to_decimal_ref(1, (20,0,0), "te", "f64"))
print("from snan:", g.from_decimal_ref("-snan", "te", "f32"))
print("from infi:", g.from_decimal_ref("infi", "te", "f16"))
print("tie 2^53+1:", g.from_decimal_ref("9007199254740993", "te", "f64"), "%x" % (1<<10 << 42))
print("bad =", bad)
