#!/bin/bash
# Probe J4: verify the negation pattern got[rm]==flip(want[mirror(rm)]).
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
ROOT=/c/Users/logan/source/repos/Muse-Softfloat
PY=$ROOT/.venv/Scripts/python.exe
V=$ROOT/scratch/verifier-w4trig
cd "$ROOT" || exit 9
"$PY" - <<'EOF'
ROOT = "C:/Users/logan/source/repos/Muse-Softfloat"
V = ROOT + "/scratch/verifier-w4trig/"
MIR = {"te": "te", "tz": "tz", "tp": "tn", "tn": "tp"}
mm = {}
for line in open(V + "out/wc_sin_full.log"):
    if not line.startswith("MISMATCH"):
        continue
    t = line.split()
    fn, rm, hx, got, want = t[2], t[3], t[4][3:], t[5][4:], t[6][5:]
    mm.setdefault(int(hx, 16), {})[rm] = (got, want)
bad = shown = 0
for x, d in mm.items():
    if set(d) != {"te", "tz", "tp", "tn"}:
        bad += 1
        continue
    for rm in ("te", "tz", "tp", "tn"):
        g = int(d[rm][0].split("/")[0], 16)
        w = int(d[MIR[rm]][1].split("/")[0], 16)
        if g ^ w != (1 << 63):
            bad += 1
            if shown < 3:
                print("NONEG", hex(x), d)
                shown += 1
            break
print(f"inputs={len(mm)} non-negation-pattern={bad}")
# dump set vs mechanical parse set
import struct
dump = set(int(l.strip(), 16) for l in open(V + "tmp/wc_sin.dump"))
mine = set()
for line in open(ROOT + "/scratch/oracles/core-math-3b2163bb87c222c7db17a721425fbef31e98fd94/src/binary64/sinpi/sinpi.wc"):
    s = line.split("#", 1)[0].split()
    if not s:
        continue
    assert len(s) == 1
    try:
        mine.add(struct.unpack("<Q", struct.pack("<d", float.fromhex(s[0])))[0])
    except ValueError:
        pass
mine = {b for b in mine if ((b >> 52) & 0x7FF) != 0x7FF}
print(f"dump={len(dump)} mine={len(mine)} symdiff={len(dump ^ mine)}")
EOF
