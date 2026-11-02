#!/usr/bin/env python3
# 25_selftest.py - validate MY decider + kernel on hand-computed cells.
# Input/output hex for dyadic values computed here with struct (exact);
# expectations from the brief's specials/tie table. Run with linux python3.
import struct, subprocess, sys, os

D = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(D, "build", "vdriver.exe")
MODES = ["te", "tz", "tp", "tn", "ta"]

def f16(x): return struct.unpack("<H", struct.pack("<e", x))[0]
def f32(x): return struct.unpack("<I", struct.pack("<f", x))[0]
def f64(x): return struct.unpack("<Q", struct.pack("<d", x))[0]

U16, U32, U64 = 0x1, 0x1, 0x1
cells = []
def cell(fi, fn, bits, exp):
    # exp: dict mode -> (wantbits, wantflags)
    cells.append((fi, fn, bits, exp))

# ---- f64 specials ----
P1, M1 = f64(1.0), f64(-1.0)
cell(2, 0, f64(0.0),  {m: (P1, 0x00) for m in MODES})
cell(2, 0, f64(-0.0), {m: (P1, 0x00) for m in MODES})
cell(2, 1, f64(0.0),  {m: (f64(0.0), 0x00) for m in MODES})
cell(2, 1, f64(-0.0), {m: (f64(-0.0), 0x00) for m in MODES})
cell(2, 0, 0x7FF0000000000000, {m: (0x7FF0000000000000, 0x00) for m in MODES})
cell(2, 0, 0xFFF0000000000000, {m: (0x0, 0x00) for m in MODES})
cell(2, 1, 0x7FF0000000000000, {m: (0x7FF0000000000000, 0x00) for m in MODES})
cell(2, 1, 0xFFF0000000000000, {m: (M1, 0x00) for m in MODES})
cell(2, 0, 0x7FF8000000000001, {m: (0x7FF8000000000001, 0x00) for m in MODES})
cell(2, 0, 0x7FF0000000000001, {m: (0x7FF8000000000001, 0x01) for m in MODES})
# ---- f64 tie -1075 (2^-1075 = u/2) ----
T = f64(-1075.0)
cell(2, 0, T, {"te": (0x0, 0x18), "ta": (U64, 0x18), "tp": (U64, 0x18),
               "tz": (0x0, 0x18), "tn": (0x0, 0x18)})
# ---- f64 exp2m1(-54): mag 1-2^-54 midpoint ----
M = f64(-54.0)
cell(2, 1, M, {"te": (M1, 0x10), "ta": (M1, 0x10), "tn": (M1, 0x10),
               "tz": (0xBFEFFFFFFFFFFFFF, 0x10), "tp": (0xBFEFFFFFFFFFFFFF, 0x10)})
# ---- f64 exp2m1(54): 2^54-1 midpoint of spacing-2 binade ----
P = f64(54.0)
cell(2, 1, P, {"te": (f64(2.0**54), 0x10), "ta": (f64(2.0**54), 0x10),
               "tp": (f64(2.0**54), 0x10),
               "tz": (f64(2.0**54 - 2.0), 0x10), "tn": (f64(2.0**54 - 2.0), 0x10)})
# ---- f64 exact integers ----
cell(2, 0, f64(10.0), {m: (f64(1024.0), 0x00) for m in MODES})
cell(2, 1, f64(53.0), {m: (f64(2.0**53 - 1.0), 0x00) for m in MODES})
cell(2, 1, f64(10.0), {m: (f64(1023.0), 0x00) for m in MODES})
cell(2, 1, f64(-53.0), {m: ((struct.unpack("<Q", struct.pack("<d", -(1.0 - 2.0**-53))))[0], 0x00) for m in MODES})
# ---- f64 overflow exp2(1024) ----
O = f64(1024.0)
cell(2, 0, O, {"te": (0x7FF0000000000000, 0x14), "ta": (0x7FF0000000000000, 0x14),
               "tp": (0x7FF0000000000000, 0x14),
               "tz": (0x7FEFFFFFFFFFFFFF, 0x14), "tn": (0x7FEFFFFFFFFFFFFF, 0x14)})
# ---- f64 zero cut exp2(-1100) ----
Z = f64(-1100.0)
cell(2, 0, Z, {"te": (0x0, 0x18), "tz": (0x0, 0x18), "tn": (0x0, 0x18),
               "tp": (U64, 0x18), "ta": (0x0, 0x18)})
# ---- f32 tie -150 ----
T32 = f32(-150.0)
cell(1, 0, T32, {"te": (0x0, 0x18), "ta": (U32, 0x18), "tp": (U32, 0x18),
                 "tz": (0x0, 0x18), "tn": (0x0, 0x18)})
cell(1, 1, f32(-25.0), {"te": (f32(-1.0), 0x10), "ta": (f32(-1.0), 0x10),
                        "tn": (f32(-1.0), 0x10),
                        "tz": (0xBF7FFFFF, 0x10), "tp": (0xBF7FFFFF, 0x10)})
cell(1, 1, f32(-24.0), {m: (0xBF7FFFFF, 0x00) for m in MODES})
cell(1, 1, f32(25.0), {"te": (f32(2.0**25), 0x10), "ta": (f32(2.0**25), 0x10),
                       "tp": (f32(2.0**25), 0x10),
                       "tz": (f32(2.0**25 - 2.0), 0x10), "tn": (f32(2.0**25 - 2.0), 0x10)})
cell(1, 0, f32(0.0), {m: (f32(1.0), 0x00) for m in MODES})
cell(1, 1, f32(-0.0), {m: (f32(-0.0), 0x00) for m in MODES})
# ---- f16 tie -25 ----
T16 = f16(-25.0)
cell(0, 0, T16, {"te": (0x0, 0x18), "ta": (U16, 0x18), "tp": (U16, 0x18),
                 "tz": (0x0, 0x18), "tn": (0x0, 0x18)})
cell(0, 1, f16(-12.0), {"te": (f16(-1.0), 0x10), "ta": (f16(-1.0), 0x10),
                        "tn": (f16(-1.0), 0x10),
                        "tz": (0xBBFF, 0x10), "tp": (0xBBFF, 0x10)})
cell(0, 1, f16(-11.0), {m: (0xBBFF, 0x00) for m in MODES})
cell(0, 1, f16(11.0), {m: (f16(2047.0), 0x00) for m in MODES})
cell(0, 1, f16(12.0), {"te": (f16(4096.0), 0x10), "ta": (f16(4096.0), 0x10),
                       "tp": (f16(4096.0), 0x10),
                       "tz": (f16(4094.0), 0x10), "tn": (f16(4094.0), 0x10)})
cell(0, 0, 0x7C00, {m: (0x7C00, 0x00) for m in MODES})
cell(0, 0, 0xFC00, {m: (0x0, 0x00) for m in MODES})
cell(0, 1, 0xFC00, {m: (0xBC00, 0x00) for m in MODES})
cell(0, 0, 0x7E01, {m: (0x7E01, 0x00) for m in MODES})
cell(0, 0, 0x7C01, {m: (0x7E01, 0x01) for m in MODES})

fails = 0
for (fi, fn, bits, exp) in cells:
    w = 16 if fi == 0 else (32 if fi == 1 else 64)
    fmt = "%%0%dx" % (w // 4)
    p = subprocess.run([V, "one", str(fi), str(fn), fmt % bits],
                       capture_output=True, text=True)
    kgot, dgot = {}, {}
    for line in p.stdout.splitlines():
        t = line.split()
        if len(t) == 4 and t[0] in MODES and t[1].startswith("got="):
            gb, gf = t[1].split("=")[1].split("/")
            wb2, wf2 = t[2].split("=")[1].split("/")
            kgot[t[0]] = (int(gb, 16), int(gf, 16))
            dgot[t[0]] = (int(wb2, 16), int(wf2, 16))
    for m, (wb, wf) in exp.items():
        if dgot.get(m) != (wb, wf):
            print("DECIDER MISS fi=%d fn=%d bits=%s %s: decider=%s hand=(%x,%02x)" %
                  (fi, fn, fmt % bits, m, dgot.get(m), wb, wf))
            fails += 1
        if kgot.get(m) != (wb, wf):
            print("KERNEL MISS fi=%d fn=%d bits=%s %s: kernel=%s hand=(%x,%02x)" %
                  (fi, fn, fmt % bits, m, kgot.get(m), wb, wf))
            fails += 1
print("cells=%d %s" % (len(cells), "ALL OK" if fails == 0 else "FAILURES=%d" % fails))
sys.exit(1 if fails else 0)
