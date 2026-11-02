"""15_specials.py - whole Clause 9.2.1 rSqrt table, three-way check.

Cells from study Sec 5.1 (clause-extract basis; the -0 cell is the
paired-sign cell decided from the extracts, never from MPFR):
  +0 -> +inf+02 | -0 -> -inf+02 | +inf -> +0 | -inf -> dqnan+01 |
  negative finite -> dqnan+01 | qNaN -> itself+00 | sNaN -> quieted+01
Payloads/signs bit-exact per SF-0 matrix. Compares kernel vs my
decider vs committed vector (where the input is committed).
"""
import importlib.util
import subprocess

ROOT = "worktrees/verify5-alg1/tests/vectors"
_spec = importlib.util.spec_from_file_location(
    "mydec", "scratch/verifier-w5alg1/10_mydecider.py")
mydec = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mydec)
MODES = ("te", "tz", "tp", "tn", "ta")

PAYLOADS = [1, 2, 3]


def specials_inputs(fmt):
    q = mydec.fmt_params(fmt)
    nbits = mydec.fmt_bits(fmt)
    t = q["t"]
    s = 1 << (nbits - 1)
    cells = [0, s]                                   # +-0
    cells += [q["emaxf"] << t, s | (q["emaxf"] << t)]  # +-inf
    cells += [s | (q["bias"] << t),                   # -1.0
              s | 1,                                  # smallest neg subnormal
              s | (1 << t),                           # neg min-norm-class edge
              s | (((q["emaxf"] - 1) << t) | ((1 << t) - 1)),
              s | (((q["emaxf"] - 1) << t))]           # largest neg finite
    for pl in PAYLOADS + [(1 << (t - 1)) - 1, (1 << t) - 1]:
        cells += [((q["emaxf"] << t) | q["quiet"] | pl),
                  ((q["emaxf"] << t) | q["quiet"] | pl | s),
                  ((q["emaxf"] << t) | pl),
                  ((q["emaxf"] << t) | pl | s)]
    return sorted(set(c for c in cells if 0 <= c < (1 << nbits)))


def load_committed(fmt):
    d = {}
    with open("%s/alg-%s.vec" % (ROOT, fmt)) as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            tk = line.split()
            d[(tk[1], tk[2])] = (int(tk[4], 16), int(tk[5], 16))
    return d


total = k_mism = 0
shown = 0
for fmt in ("f16", "f32", "f64"):
    xs = specials_inputs(fmt)
    with open("scratch/verifier-w5alg1/out/spec_%s.txt" % fmt, "w") as fh:
        for x in xs:
            fh.write("%x\n" % x)
    with open("scratch/verifier-w5alg1/out/kspec_%s.txt" % fmt, "w") as out:
        subprocess.run(
            ["scratch/verifier-w5alg1/out/vharness.exe", "list", fmt,
             "scratch/verifier-w5alg1/out/spec_%s.txt" % fmt],
            stdout=out, cwd=".")
    kern = {}
    with open("scratch/verifier-w5alg1/out/kspec_%s.txt" % fmt) as fh:
        for line in fh:
            tk = line.split()
            if len(tk) == 6 and tk[0] == "K":
                kern[("%x" % int(tk[2], 16), int(tk[3]))] = (
                    int(tk[4], 16), int(tk[5], 16))
    comm = load_committed(fmt)
    for x in xs:
        for mi, mode in enumerate(MODES):
            want = mydec.decide(fmt, x)[mi]
            got = kern.get(("%x" % x, mi))
            total += 1
            tag = ""
            c = comm.get((mode, "%x" % x))
            if got != want:
                k_mism += 1
                tag = " KERNEL-MISMATCH"
                if shown < 12:
                    shown += 1
                    print("SPECIAL-MISMATCH %s in=%x mode=%s kern=%x/%02x mine=%x/%02x comm=%s%s"
                          % (fmt, x, mode, got[0], got[1], want[0], want[1],
                             ("n/a" if c is None else "%x/%02x" % c), tag))
            if c is not None and (c != want):
                print("COMMIT-DISAGREES-WITH-TABLE %s in=%x mode=%s comm=%x/%02x mine=%x/%02x"
                      % (fmt, x, mode, c[0], c[1], want[0], want[1]))
print("specials: kernel-vs-table total=%d mismatches=%d" % (total, k_mism))
