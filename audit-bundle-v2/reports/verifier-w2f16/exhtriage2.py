import re
import sys
sys.path.insert(0, "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16")
from ref_f16 import is_snan_d
SC = "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w2f16"
pat = re.compile(r'msf16_\S+ \S+ ([0-9a-f]+) ')
for t in ("sqrt@te", "next_up@-", "next_down@-",
          "round_to_integral_ties_to_even@-", "round_to_integral_ties_to_away@-",
          "round_to_integral_toward_zero@-", "round_to_integral_toward_positive@-",
          "round_to_integral_toward_negative@-", "round_to_integral_exact@te"):
    n = 0
    nonsnan = []
    with open("%s/exh-%s.vec" % (SC, t)) as f:
        pass
    # replay captured? re-derive: check each input's class via ref
    import subprocess
    vec = "%s/exh-%s.vec" % (SC, t)
    out = subprocess.run(
        ["C:/Users/logan/source/repos/Muse-Softfloat/worktrees/verify2-f16/build/smoke/msf_runner.exe",
         "verify", vec], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if not line.startswith("FAIL"):
            continue
        m = pat.search(line)
        u = int(m.group(1), 16)
        if not is_snan_d(u):
            nonsnan.append(line.strip()[-100:])
        n += 1
    print(t, "fails:", n, "non-sNaN:", len(nonsnan))
    for s in nonsnan[:4]:
        print("   ", s)
