import re
pat = re.compile(r'msf16_div te ([0-9a-f]+) ([0-9a-f]+) -> ([0-9a-f]+) ([0-9a-f]+)')
zdiv = 0
zdiv_ops = []
inv = 0
inv_bad = []
with open("C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16/div-te-full.log") as f:
    for line in f:
        if not line.startswith("FAIL"):
            continue
        m = pat.search(line)
        if not m:
            continue
        x, y, wv, wf = m.groups()
        if wf == "02":
            zdiv += 1
            if len(zdiv_ops) < 4:
                zdiv_ops.append(line.strip()[-120:])
        if wf == "01":
            inv += 1
            inv_bad.append(line.strip()[-120:])
print("flag02 cases:", zdiv)
for c in zdiv_ops:
    print("  Z:", c)
print("flag01(invalid) fail cases:", inv)
for c in inv_bad[:6]:
    print("  I:", c)
