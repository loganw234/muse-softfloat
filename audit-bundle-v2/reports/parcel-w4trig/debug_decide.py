import subprocess

EXE = "worktrees/w4-trig/build/trig/trig_exhaustive.exe"
rows = []
with open("scratch/tier2-trig-spike/out/wc_sinpi_redecided.txt") as fh:
    for line in fh:
        t = line.split()
        if len(t) == 6 and t[1] != "NONFINITE":
            rows.append(t[0])
        if len(rows) >= 20:
            break
print(rows[:3])
inp = "".join(f"msf64_sin_pi {r}\n" for r in rows)
p = subprocess.run([EXE, "decide"], input=inp, capture_output=True, text=True)
print("rc", p.returncode)
print(p.stdout[:2000])
print("STDERR", p.stderr[:500])
