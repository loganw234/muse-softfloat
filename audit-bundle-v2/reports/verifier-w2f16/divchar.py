import re
val = flagonly = 0
flagcases = {}
valcases = []
pat = re.compile(r'got ([0-9a-f]+)/([0-9a-f]+) want ([0-9a-f]+)/([0-9a-f]+)')
with open("C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16/div-te-full.log") as f:
    for line in f:
        if not line.startswith("FAIL"):
            continue
        m = pat.search(line)
        if not m:
            continue
        gv, gf, wv, wf = m.groups()
        if gv != wv:
            val += 1
            if len(valcases) < 8:
                valcases.append(line.strip()[-120:])
        else:
            flagonly += 1
            key = (gf, wf)
            flagcases[key] = flagcases.get(key, 0) + 1
print("value-mismatch:", val)
for c in valcases:
    print("  V:", c)
print("flag-only-mismatch:", flagonly)
for k in sorted(flagcases):
    print("  got/want:", k, flagcases[k])
