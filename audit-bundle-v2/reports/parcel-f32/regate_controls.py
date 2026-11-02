"""Regate negative controls for parcel-f32 (brief item 4, re-run after
lead fix b37fb12). Writes small mutated files, runs the runner, logs
refusal evidence. Control 4 also classifies every wrong-tininess
failure: post-fix the before-rounding build must fail only the
complementary boundary subset (got 0x18, want 0x10, delivered at the
smallest normal) - never the directions the old delivered-value
build missed (want 0x18)."""
import pathlib, re, subprocess, sys

WS = pathlib.Path("C:/Users/logan/source/repos/Muse-Softfloat")
WT = WS / "worktrees/w1-f32"
RUNNER = str(WT / "build/smoke/msf_runner.exe")
BEFORE = str(WT / "build/smoke/controls/msf_runner_tininess_before.exe")
CTL = WS / "scratch/parcel-f32/controls"
CTL.mkdir(parents=True, exist_ok=True)
LOG = WS / "scratch/parcel-f32/regate-controls.log"

def run(exe, vec):
    r = subprocess.run([exe, "verify", str(vec)], capture_output=True, text=True, cwd=str(WT))
    tail = [l for l in r.stdout.splitlines() if l.startswith(("FAIL", "total", "VERDICT"))]
    return r.returncode, tail[:4]

lines = []
def emit(s):
    lines.append(s)
    print(s, flush=True)

mul = (WT / "build/w1/f32_mul-tz-l1.vec").read_text().splitlines()
data = [l for l in mul if l and not l.startswith("#")]
hdr = [l for l in mul if l.startswith("#")]

# Control 1: flipped result bit in a Berkeley file
src = next(l for l in data if "->" in l)
tok = src.split()
ai = tok.index("->")
tok2 = list(tok); tok2[ai+1] = "%x" % (int(tok[ai+1], 16) ^ 1)
f1 = CTL / "berkeley-flip-result.vec"
f1.write_bytes(("\n".join(hdr + [" ".join(tok2)]) + "\n").encode())
rc, tail = run(RUNNER, f1)
emit("control flip-result-bit (Berkeley mul tz line): rc=%d %s" % (rc, "REFUSED" if rc != 0 else "NOT-REFUSED"))
emit("  src: " + src)
for t in tail: emit("  " + t)

# Control 2: flipped flag bit
tok3 = list(tok); tok3[ai+2] = "%02x" % (int(tok[ai+2], 16) ^ 0x10)
f2 = CTL / "berkeley-flip-flag.vec"
f2.write_bytes(("\n".join(hdr + [" ".join(tok3)]) + "\n").encode())
rc, tail = run(RUNNER, f2)
emit("control flip-flag-bit: rc=%d %s" % (rc, "REFUSED" if rc != 0 else "NOT-REFUSED"))
for t in tail: emit("  " + t)

# Control 3: wrong-NaN-payload expectation: pass under nan-class, fail under exact
nanline = None
for l in data:
    t = l.split(); i = t.index("->")
    res = int(t[i+1], 16)
    if ((res >> 23) & 0xff) == 0xff and (res & 0x7fffff) != 0 and (res & 0x400000):
        nanline = l
        ntok, nai = t, i
        break
assert nanline, "no qNaN-result line in mul tz file"
wtok = list(ntok)
res = int(ntok[nai+1], 16)
wtok[nai+1] = "%x" % (res ^ 0x00000002)
for mode in ["nan-class", "exact"]:
    f = CTL / ("nanpayload-%s.vec" % mode)
    f.write_bytes(("# generated control file\n# compare=%s\n%s\n" % (mode, " ".join(wtok))).encode())
    rc, tail = run(RUNNER, f)
    emit("control wrong-nan-payload compare=%s: rc=%d %s" % (mode, rc, "PASSES (expected)" if rc == 0 else "REFUSED"))
    emit("  line: " + " ".join(wtok))
    for t in tail: emit("  " + t)

# Control 4: wrong-tininess build vs my directed arith file (smallest-normal add)
rc_ok, tail_ok = run(RUNNER, WT / "tests/vectors/arith-f32.vec")
r_bad = subprocess.run([BEFORE, "verify", str(WT / "tests/vectors/arith-f32.vec")],
                       capture_output=True, text=True, cwd=str(WT))
rc_bad = r_bad.returncode
fail_lines = [l for l in r_bad.stdout.splitlines() if l.startswith("FAIL")]
emit("control wrong-tininess-build on directed arith-f32.vec: normal rc=%d, before-build rc=%d %s" % (rc_ok, rc_bad, "REFUSED" if rc_bad != 0 else "NOT-REFUSED"))
for t in fail_lines[:4]: emit("  " + t)
tot = [l for l in r_bad.stdout.splitlines() if l.startswith(("total", "VERDICT"))]
for t in tot: emit("  " + t)
# Classify every failure: complementary subset = got ../18 want ../10 at
# smallest-normal magnitude (00800000 with either sign); result bits equal.
import collections
cls = collections.Counter()
for l in fail_lines:
    m = re.search(r"got ([0-9a-f]+)/([0-9a-f]+) want ([0-9a-f]+)/([0-9a-f]+)", l)
    if not m:
        cls["unparsed"] += 1
        continue
    gr, gf, wr, wf = m.groups()
    key = "got%s-want%s" % (gf, wf)
    if gr != wr:
        key += "-RESULT-DIFFERS"
    if (int(wr, 16) & 0x7fffffff) != 0x00800000:
        key += "-not-min-normal"
    cls[key] += 1
emit("  wrong-tininess classification over %d FAIL lines: %s" % (len(fail_lines), dict(cls)))
comp_ok = (len(fail_lines) > 0 and set(cls) == {"got18-want10"})
emit("  complementary-subset-only: %s" % ("YES" if comp_ok else "NO"))

LOG.write_bytes(("\n".join(lines) + "\n").encode())
bad = 0
print("log:", LOG)
