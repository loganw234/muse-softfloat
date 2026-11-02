import re
files = {
    "sqrt": "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16/triage-sqrt@te.log",
    "next_up": "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16/triage-next_up@-.log",
    "rint_te": "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16/triage-round_to_integral_ties_to_even@-.log",
    "rint_exact": "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16/triage-round_to_integral_exact@te.log",
}
pat = re.compile(r'\| (\S+) (\S+) ([0-9a-f]+) -> ([0-9a-f]+) ([0-9a-f]+)')
for name, path in files.items():
    nan_in = fin_in = 0
    fin_samples = []
    nan_samples = []
    with open(path) as f:
        for line in f:
            if not line.startswith("FAIL"):
                continue
            m = pat.search(line)
            if not m:
                continue
            op, rm, operand, want, wfl = m.groups()
            u = int(operand, 16)
            e = (u >> 10) & 0x1F
            fr = u & 0x3FF
            if e == 0x1F and fr != 0:
                nan_in += 1
                if len(nan_samples) < 3:
                    nan_samples.append(line.strip()[-110:])
            else:
                fin_in += 1
                if len(fin_samples) < 5:
                    fin_samples.append(line.strip()[-110:])
    print("== %s: NaN-input fails=%d finite-input fails=%d" % (name, nan_in, fin_in))
    for s in nan_samples:
        print("   NAN:", s)
    for s in fin_samples:
        print("   FIN:", s)
