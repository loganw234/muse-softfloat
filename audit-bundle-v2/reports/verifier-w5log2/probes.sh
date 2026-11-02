#!/usr/bin/env bash
# probes.sh - one-cell + family probes: all 6 ops x 5 modes.
set -u
export PATH=/c/msys64/mingw64/bin:$PATH
SCR=/c/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w5log2
PY=/c/Users/logan/source/repos/Muse-Softfloat/.venv/Scripts/python.exe
ulimit -v 4194304
cd "$SCR" || exit 9
"$PY" - > logs/cells.txt <<'EOF'
cells = []  # (fmt, fn, hex16)
def add(fmt, fn, h):
    cells.append((fmt, fn, h))
# specials: +0 -0 +inf -inf qnan snan(quietbit clear, payload 1)
add('f16','log2','0000'); add('f16','log2','8000')
add('f16','log2','7c00'); add('f16','log2','fc00')
add('f16','log2','7e00'); add('f16','log2','7c01')
add('f16','log2p1','0000'); add('f16','log2p1','8000')
add('f16','log2p1','7c00'); add('f16','log2p1','fc00')
add('f16','log2p1','7e00'); add('f16','log2p1','7c01')
add('f32','log2','00000000'); add('f32','log2','80000000')
add('f32','log2','7f800000'); add('f32','log2','ff800000')
add('f32','log2','7fc00000'); add('f32','log2','7f800001')
add('f32','log2p1','00000000'); add('f32','log2p1','80000000')
add('f32','log2p1','7f800000'); add('f32','log2p1','ff800000')
add('f32','log2p1','7fc00000'); add('f32','log2p1','7f800001')
add('f64','log2','0000000000000000'); add('f64','log2','8000000000000000')
add('f64','log2','7ff0000000000000'); add('f64','log2','fff0000000000000')
add('f64','log2','7ff8000000000000'); add('f64','log2','7ff0000000000001')
add('f64','log2p1','0000000000000000'); add('f64','log2p1','8000000000000000')
add('f64','log2p1','7ff0000000000000'); add('f64','log2p1','fff0000000000000')
add('f64','log2p1','7ff8000000000000'); add('f64','log2p1','7ff0000000000001')
# negative qnan payload (matrix (c) precedes (a): no invalid)
add('f64','log2','fff8000000000000')
# negatives incl -inf already; -1, -2, -max, smallest subnormal neg
add('f64','log2','bff0000000000000'); add('f64','log2','c000000000000000')
add('f64','log2','ffefffffffffffff'); add('f64','log2','8000000000000001')
add('f32','log2','bf800000'); add('f32','log2','c0000000')
add('f16','log2','bc00'); add('f16','log2','c000')
# powers of two incl subnormal x, 2^k ladders + neighbours
for k in range(-24, 16):
    add('f16','log2', '%04x' % ((0x0400+k*0x0400) & 0xffff) if -14 <= k <= 15 else '0001')
add('f16','log2','0001'); add('f16','log2','0002')
for k in range(-149, 128, 7):
    e = k + 127
    add('f32','log2', '%08x' % (0x00800000 if k < -126 else ((e << 23) & 0x7f800000)))
add('f32','log2','00000001'); add('f32','log2','00000002')
for k in (-1074, -1000, -100, -53, -52, -11, -1, 0, 1, 52, 53, 100, 1000, 1023):
    add('f64','log2', '%016x' % (0x1 if k == -1074 else ((k+1023) << 52)))
add('f64','log2','0000000000000001'); add('f64','log2','0000000000000002')
add('f64','log2','0010000000000000')  # 2^-1022 min normal
add('f32','log2','00800000')
add('f16','log2','0400')
# log2(1)=+0, log2(2)=1 exacts
add('f16','log2','3c00'); add('f16','log2','4000')
add('f32','log2','3f800000'); add('f32','log2','40000000')
add('f64','log2','3ff0000000000000'); add('f64','log2','4000000000000000')
# log2p1 2^k-1 forms: x=-1/2 -> -1, x=1 -> 1, x=3 -> 2, x=-3/4, x=7
add('f64','log2p1','bfe0000000000000'); add('f64','log2p1','3ff0000000000000')
add('f64','log2p1','4008000000000000'); add('f64','log2p1','bfe8000000000000')
add('f64','log2p1','401c000000000000')
add('f32','log2p1','bf000000'); add('f32','log2p1','3f800000')
add('f16','log2p1','b800'); add('f16','log2p1','3c00')
# pole -1 + flag, and -1 +- ulp ladders
add('f64','log2p1','bff0000000000000')
add('f64','log2p1','bfefffffffffffff'); add('f64','log2p1','bff0000000000001')
add('f64','log2p1','bff0000000000002'); add('f64','log2p1','bfeffffffffffffe')
add('f32','log2p1','bf800000')
add('f32','log2p1','bf7fffff'); add('f32','log2p1','bf800001')
add('f16','log2p1','bc00')
add('f16','log2p1','bbff'); add('f16','log2p1','bc01')
# domain x < -1: -1-ulp, -2, -inf covered, -max
add('f64','log2p1','bff0000000000001'); add('f64','log2p1','c000000000000000')
add('f32','log2p1','bf800001'); add('f16','log2p1','bc01')
# sqrt2 recentring boundary: sig straddling floor(sqrt2*2^(p-1))
import math
sq = math.sqrt(2)
for fmt, p, eb, fb in (('f16',11,15,10),('f32',24,127,23),('f64',53,1023,52)):
    base = int(sq * 2**(p-1))
    for d in (-2,-1,0,1,2):
        frac = (base + d) & ((1 << (p-1)) - 1)
        for e in (-3, -1, 0, 7):
            bits = ((e + eb) << fb) | frac
            w = 2*fb//2 if fmt=='f16' else (16 if fmt=='f32' else 32)
            ww = {'f16':4,'f32':8,'f64':16}[fmt]
            add(fmt,'log2', '%0*x' % (ww, bits))
            add(fmt,'log2p1', '%0*x' % (ww, bits))
# tiny-|x| path: |x| = 2^-8 boundary +- ulp, subnormal tiny, signs
tiny = [
 ('f64','3f70000000000000'),('f64','3f6fffffffffffff'),('f64','3f70000000000001'),
 ('f64','bf70000000000000'),('f64','0000000000000001'),('f64','8000000000000001'),
 ('f64','3e70000000000000'),('f64','0010000000000000'),
 ('f32','3d800000'),('f32','3d7fffff'),('f32','3d800001'),
 ('f32','bd800000'),('f32','00000001'),('f32','80000001'),
 ('f16','3400'),('f16','33ff'),('f16','3401'),
 ('f16','b400'),('f16','0001'),('f16','8001'),
]
for fmt, h in tiny:
    add(fmt,'log2p1',h)
    add(fmt,'log2',h)
# hardest cells named in the parcel ledger
add('f64','log2','7fe61555f75885b4')
add('f64','log2p1','44ee499f19ecc9fb')
# near-1 ladders 1+-ulp
add('f64','log2','3fefffffffffffff'); add('f64','log2','3ff0000000000001')
add('f64','log2p1','3fefffffffffffff'); add('f64','log2p1','3ff0000000000001')
add('f64','log2p1','bfefffffffffffff')
# sticky-attractor: log2p1(x=2^k) across range incl 1022-class, +-neighbours
for k in (-1074, -1022, -100, -9, -8, -1, 0, 1, 52, 100, 1000, 1022):
    add('f64','log2p1', '%016x' % (0x1 if k == -1074 else ((k+1023) << 52)))
    if k > -1074:
        add('f64','log2p1', '%016x' % ((((k+1023) << 52)) + 1))
        add('f64','log2p1', '%016x' % ((((k+1023) << 52)) - 1))
with open('/tmp/n.txt','w') as fh:
    fh.write('')
print(len(cells))
for fmt, fn, h in cells:
    print(fmt, fn, h)
EOF
echo "generated $(head -1 logs/cells.txt) cells"
