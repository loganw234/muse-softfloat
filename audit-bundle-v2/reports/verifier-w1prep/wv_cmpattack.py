#!/usr/bin/env python3
"""wv_cmpattack.py - attack the runner's per-file compare directives (own files).
Runner: muse-softfloat/build/standard/msf_runner.exe (freshly built by run.sh).
Each attack asserts the runner refuses (rc!=0 + VERDICT: FAIL) or accepts.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path("muse-softfloat")
RUNNER = ROOT / "build/standard/msf_runner.exe"
W = pathlib.Path("scratch/verifier-w1prep/tmp/cmp")
W.mkdir(parents=True, exist_ok=True)
results = []


def run(vec_text, name):
    p = W / name
    p.write_text(vec_text, encoding="utf-8")
    proc = subprocess.run([str(RUNNER), "verify", str(p)], capture_output=True, text=True)
    out = proc.stdout + proc.stderr
    verdict = "PASS" if "VERDICT: PASS" in out else ("FAIL" if "VERDICT: FAIL" in out else "???")
    return proc.returncode, verdict, out


def check(label, cond, detail):
    results.append("%s: %s [%s]" % (label, "OK" if cond else "NOT-REFUSED/BROKEN", detail))
    return cond


ok = True
# pick a real pack line with nonzero flags from committed pack64.vec
pack_lines = [l for l in (ROOT / "tests/vectors/pack64.vec").read_text().splitlines()
              if l and not l.startswith("#")]
nz = next(l for l in pack_lines if l.split()[-2] != "00")
tok = nz.split()
real_flags = tok[-2]
bad_flags = "00" if real_flags != "00" else "10"
flipped = " ".join(tok[:-2] + [bad_flags, tok[-1]]) + "\n"

# A. flags still compared under nan-class: flip flags on a pack line -> must FAIL
rc, v, out = run("# compare=nan-class\n" + flipped, "a_nanflag.vec")
ok &= check("A nan-class still compares flags exactly", rc != 0 and v == "FAIL", "rc=%d verdict=%s" % (rc, v))

# B. sNaN result rejected where quiet expected under nan-class -> must FAIL
rc, v, out = run("# compare=nan-class\nmsf16_copy - 7d00 -> 7e00 -- wv:snan-vs-quiet\n", "b_snan.vec")
ok &= check("B nan-class rejects sNaN where quiet expected", rc != 0 and v == "FAIL", "rc=%d verdict=%s" % (rc, v))

# B2. positive: quiet result where quiet expected under nan-class -> PASS
# (7e00/7e55 are quiet f16 NaNs: exp all-ones, quiet bit 0x200 set)
rc, v, out = run("# compare=nan-class\nmsf16_copy - 7e00 -> 7e55 -- wv:quiet-ok\n", "b2_quiet.vec")
ok &= check("B2 nan-class accepts quiet for quiet-expectation", rc == 0 and v == "PASS", "rc=%d verdict=%s" % (rc, v))

# C. berkeley-int still compares result when invalid NOT signaled -> must FAIL
bad_result = " ".join(tok[:-3] + ["deadbeefdeadbeef", tok[-2], tok[-1]]) + "\n"
rc, v, out = run("# compare=berkeley-int\n" + bad_result, "c_berkint.vec")
ok &= check("C berkeley-int compares result w/o invalid", rc != 0 and v == "FAIL", "rc=%d verdict=%s" % (rc, v))

# C2'. flags still compared under berkeley-int even when invalid expected:
# correct result, expect flags 01 (invalid) while the pack op really yields nz flags -> FAIL.
# (No currently-implemented op can really set invalid, so the result-skip half
# cannot fire end-to-end yet; this proves the flags half still bites.)
real_line = nz + "\n"
flagflip_inv = " ".join(nz.split()[:-2] + ["01", nz.split()[-1]]) + "\n"
rc, v, out = run("# compare=berkeley-int\n" + flagflip_inv, "c2_berkint_inv.vec")
ok &= check("C2 berkeley-int still compares flags w/ invalid expected", rc != 0 and v == "FAIL", "rc=%d verdict=%s" % (rc, v))

# D. directive mid-file affects only later lines: a quiet/quiet payload-diff line
# BEFORE the directive is judged exact -> FAIL (proves no retroactive masking).
rc, v, out = run("msf16_copy - 7e00 -> 7e55 -- wv:pre-directive\n# compare=nan-class\nmsf16_copy - 7e00 -> 7e55 -- wv:post-directive\n",
                 "d_scoping.vec")
ok &= check("D directive not retroactive (pre line fails)", rc != 0 and v == "FAIL", "rc=%d verdict=%s" % (rc, v))

# D2. directive then reset to exact: masked line passes, exact line passes -> PASS
rc, v, out = run("# compare=nan-class\nmsf16_copy - 7e00 -> 7e55 -- wv:masked-ok\n# compare=exact\nmsf16_copy - 7e00 -> 7e00 -- wv:exact-ok\n",
                 "d2_rescope.vec")
ok &= check("D2 directive scoped + reset works", rc == 0 and v == "PASS", "rc=%d verdict=%s" % (rc, v))

# E. real flags compared: flipped flags on pack line under default exact -> FAIL
rc, v, out = run(flipped, "e_flagflip.vec")
ok &= check("E flags compared for real (exact)", rc != 0 and v == "FAIL", "rc=%d verdict=%s" % (rc, v))

open("scratch/verifier-w1prep/wv_cmpattack.txt", "w", encoding="utf-8").write("\n".join(results) + "\n")
print("\n".join(results))
sys.exit(0 if ok else 1)
