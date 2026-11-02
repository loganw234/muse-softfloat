"""Probe1d: smoke total from committed VECS rows; standard extras from generator parts."""
import re, sys
from pathlib import Path
DUP = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
run = (DUP / "tools/run.sh").read_text(encoding="utf-8")
m = re.search(r'^VECS="(.*?)"\s*$', run, re.M | re.S)
vecs = m.group(1).split()
print("n VECS files:", len(vecs))
smoke = 0
for v in vecs:
    n = 0
    for l in open(DUP / v, encoding="utf-8", errors="replace"):
        s = l.strip()
        if s and not s.startswith("#"):
            n += 1
    smoke += n
print("smoke data rows (non-#, non-blank):", smoke)
# standard extras from generator parts
print("f16-exhaustive rows: 65536 encodings x (1 class + 9 preds + copy/negate/abs/radix=4) =",
      65536 * (1 + 9 + 4))
print("pack-sweep rows (argv N=200000):", 200000)
print("standard extras total:", 65536 * 14 + 200000)
print("smoke + extras:", smoke + 65536 * 14 + 200000)
