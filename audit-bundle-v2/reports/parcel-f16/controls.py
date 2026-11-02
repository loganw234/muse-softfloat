"""Negative controls for parcel-f16 (brief Tests item 4).

1+2. Flip one result bit / one flag bit in a kept Berkeley file;
     the runner must refuse each.
3.   One-line mutation in a SCRATCH COPY of gen_vectors_f16.py
     (ties-to-even parity inverted in _round_inc_mag); the mutated
     directed replay must FAIL. The committed generator is never
     touched; the copy is deleted by this script after the run
     (that deletion is the revert).
Also: wrong-tininess build against the directed arith set, and the
unmutated regeneration of the mutated file as a positive control.
"""
import os, pathlib, subprocess, sys

WS = pathlib.Path("C:/Users/logan/source/repos/Muse-Softfloat")
WT = WS / "worktrees/w2-f16"
SCR = WS / "scratch/parcel-f16"
PY = str(WS / ".venv/Scripts/python.exe")
RUNNER = str(WT / "build/smoke/msf_runner.exe")
BEFORE = str(WT / "build/smoke/controls/msf_runner_tininess_before.exe")
CTL = SCR / "controls"
CTL.mkdir(parents=True, exist_ok=True)
LOG = SCR / "controls.log"
env = dict(os.environ)
env["TMPDIR"] = str(SCR / "tmp"); env["TMP"] = env["TMPDIR"]; env["TEMP"] = env["TMPDIR"]

lines = []
def emit(s):
    lines.append(s)
    print(s, flush=True)

def run(exe, vec):
    r = subprocess.run([exe, "verify", str(vec)], capture_output=True,
                       text=True, cwd=str(WT), env=env)
    tail = [l for l in r.stdout.splitlines()
            if l.startswith(("FAIL", "total", "VERDICT"))]
    return r.returncode, tail[:5]

ok = True

div = (WT / "build/w2/f16_div-te-l1.vec").read_text().splitlines()
data = [l for l in div if l and not l.startswith("#")]
hdr = [l for l in div if l.startswith("#")]
src = next(l for l in data if "->" in l)
tok = src.split()
ai = tok.index("->")

tok2 = list(tok); tok2[ai+1] = "%x" % (int(tok[ai+1], 16) ^ 1)
f1 = CTL / "berkeley-flip-result.vec"
f1.write_bytes(("\n".join(hdr + [" ".join(tok2)]) + "\n").encode())
rc, tail = run(RUNNER, f1)
refused = rc != 0 and any("FAIL" in t for t in tail)
ok = ok and refused
emit("control 1 flip-result-bit (Berkeley f16_div te line): rc=%d %s" %
     (rc, "REFUSED" if refused else "NOT-REFUSED"))
emit("  src: " + src)
emit("  mut: " + " ".join(tok2))
for t in tail: emit("  " + t)

tok3 = list(tok); tok3[ai+2] = "%02x" % (int(tok[ai+2], 16) ^ 0x10)
f2 = CTL / "berkeley-flip-flag.vec"
f2.write_bytes(("\n".join(hdr + [" ".join(tok3)]) + "\n").encode())
rc, tail = run(RUNNER, f2)
refused = rc != 0 and any("FAIL" in t for t in tail)
ok = ok and refused
emit("control 2 flip-flag-bit (same line, inexact bit): rc=%d %s" %
     (rc, "REFUSED" if refused else "NOT-REFUSED"))
emit("  mut: " + " ".join(tok3))
for t in tail: emit("  " + t)

# control 3: one-line mutation in a scratch copy of the generator
gen_src = (WT / "tests/gen_vectors_f16.py").read_text(encoding="utf-8")
needle = "return twice > den or (twice == den and q % 2 == 1)"
assert gen_src.count(needle) == 1
mutated = gen_src.replace(needle,
                          "return twice > den or (twice == den and q % 2 == 0)")
mut_gen = CTL / "gen_vectors_f16_MUTATED.py"
mut_gen.write_bytes(mutated.encode("utf-8"))
mut_out = CTL / "mutated-directed"
r = subprocess.run([PY, str(mut_gen), "directed", str(mut_out)],
                   capture_output=True, text=True, env=env)
emit("control 3 mutated generator run rc=%d" % r.returncode)
for l in r.stdout.splitlines()[-7:]:
    emit("  " + l)
rc_mut, tail_mut = run(RUNNER, mut_out / "arith-f16.vec")
fails_line = next((t for t in tail_mut if t.startswith("total")), "?")
refused = rc_mut != 0
ok = ok and refused
emit("control 3 mutated directed arith-f16.vec replay: rc=%d %s (%s)" %
     (rc_mut, "REFUSED (fails as required)" if refused else "NOT-REFUSED",
      fails_line))
for t in tail_mut: emit("  " + t)
rc_clean, tail_clean = run(RUNNER, SCR / "directed-test/arith-f16.vec")
emit("control 3 positive counterpart (unmutated arith-f16.vec): rc=%d (%s)" %
     (rc_clean, next((t for t in tail_clean if t.startswith("total")), "?")))
ok = ok and rc_clean == 0
# byte-compare mutated vs clean directed arith (must differ)
same = (mut_out / "arith-f16.vec").read_bytes() == \
       (SCR / "directed-test/arith-f16.vec").read_bytes()
emit("control 3 mutated file byte-identical to clean file: %s (must be False)" % same)
ok = ok and not same
# revert: remove the mutated generator copy (committed file untouched)
mut_gen.unlink()
emit("control 3 revert: scratch mutated generator deleted; committed "
     "tests/gen_vectors_f16.py untouched (mutation lived only in %s)" % mut_gen)
gen_now = (WT / "tests/gen_vectors_f16.py").read_text(encoding="utf-8")
emit("control 3 committed generator still has q %% 2 == 1 exactly once: %s" %
     (gen_now.count(needle) == 1))
ok = ok and gen_now.count(needle) == 1

# extra: wrong-tininess build against directed arith (positive+refusal pair)
rc_ok, _ = run(RUNNER, SCR / "directed-test/arith-f16.vec")
rc_bad, tail_bad = run(BEFORE, SCR / "directed-test/arith-f16.vec")
emit("extra wrong-tininess-build on directed arith-f16.vec: normal rc=%d, "
     "before-build rc=%d %s" %
     (rc_ok, rc_bad, "REFUSED" if rc_bad != 0 else "not refused (recorded)"))
for t in tail_bad: emit("  " + t)

emit("controls verdict: %s" % ("ALL REQUIRED REFUSALS OBSERVED" if ok
                               else "A REQUIRED REFUSAL IS MISSING"))
LOG.write_bytes(("\n".join(lines) + "\n").encode())
print("log:", LOG)
sys.exit(0 if ok else 1)
