#!/usr/bin/env python3
"""s09_vectors.py - replay committed hypot vector lines.

For every committed hypot line in alg-{f16,f32,f64}.vec: fastdec vs
file expectation (is the committed expectation right?), and kernel
floor vs file expectation (does the kernel deliver it?). Counts per
family tag and format; te!=ta census; subnormal-output census.
"""
import subprocess
import sys
import os

sys.path.insert(0, "scratch/verifier-w5alg2")
from fastdec import decide_fast  # noqa: E402
from mydecide import FMTS  # noqa: E402

OUT = "scratch/verifier-w5alg2/out"
EXE = OUT + "/harness_floor.exe"

FILES = [(0, "worktrees/verify5-alg2/tests/vectors/alg-f16.vec"),
         (1, "worktrees/verify5-alg2/tests/vectors/alg-f32.vec"),
         (2, "worktrees/verify5-alg2/tests/vectors/alg-f64.vec")]
RMIDX = {"te": 0, "tz": 1, "tp": 2, "tn": 3, "ta": 4}


def main():
    tot_mm_file = tot_mm_kern = tot = 0
    te_ne_ta_file = 0
    sub_out = 0
    by_fam = {}
    first_file = []
    first_kern = []
    kern_jobs = []  # (key, fi, a, b)
    for fi, fn in FILES:
        f = FMTS[fi]
        ew = f["w"] - 1 - f["t"]
        fam_lines = {}
        with open(fn) as fh:
            for line in fh:
                t = line.split()
                if len(t) < 8 or "hypot" not in t[0]:
                    continue
                rm, a, b = t[1], int(t[2], 16), int(t[3], 16)
                rb, rf, tag = int(t[5], 16), int(t[6], 16), t[7]
                mine = decide_fast(fi, a, b)[RMIDX[rm]]
                tot += 1
                fam = tag.split(":")[-1] if ":" in tag else tag
                by_fam.setdefault((fi, fam), [0, 0, 0])
                by_fam[(fi, fam)][0] += 1
                if (mine[0], mine[1]) != (rb, rf):
                    tot_mm_file += 1
                    by_fam[(fi, fam)][1] += 1
                    if len(first_file) < 8:
                        first_file.append((fn, rm, a, b, rb, rf, mine, tag))
                # te!=ta census needs pair grouping; approximate here
                kern_jobs.append((fn, rm, fi, a, b, rb, rf, tag))
                ef = (rb >> f["t"]) & ((1 << ew) - 1)
                if ef == 0 and (rb & ((1 << f["t"]) - 1)) != 0:
                    sub_out += 1
        # te!=ta census per pair from file: group by (a,b)
        seen = {}
        with open(fn) as fh:
            for line in fh:
                t = line.split()
                if len(t) < 8 or "hypot" not in t[0]:
                    continue
                seen.setdefault((t[2], t[3]), {})[t[1]] = (t[5], t[6])
        for (a, b), m in seen.items():
            if m.get("te") != m.get("ta"):
                te_ne_ta_file += 1
    # kernel replay in chunks
    BLOB = 20000
    for i in range(0, len(kern_jobs), BLOB):
        chunk = kern_jobs[i:i + BLOB]
        blob = "".join(f"{fi} {a:x} {b:x}\n" for _, _, fi, a, b, _, _, _
                       in chunk)
        kh = subprocess.run([EXE, "hypot"], input=blob, capture_output=True,
                            text=True)
        if kh.returncode != 0:
            raise RuntimeError(kh.stderr[-2000:])
        for (fn, rm, fi, a, b, rb, rf, tag), line in zip(chunk, kh.stdout.splitlines()):
            t = line.split()
            kb, kf = int(t[2 * RMIDX[rm]], 16), int(t[2 * RMIDX[rm] + 1], 16)
            if (kb, kf) != (rb, rf):
                tot_mm_kern += 1
                f = FMTS[fi]
                fam = tag.split(":")[-1] if ":" in tag else tag
                by_fam[(fi, fam)][2] += 1
                if len(first_kern) < 10:
                    first_kern.append((fn, rm, a, b, rb, rf, kb, kf, tag))
    print(f"VECTORS: hypot lines={tot}")
    print(f"  fastdec-vs-file mismatches={tot_mm_file} "
          f"{'PASS' if tot_mm_file == 0 else 'FAIL'}")
    print(f"  kernel-vs-file mismatches={tot_mm_kern} "
          f"{'PASS' if tot_mm_kern == 0 else 'FAIL'}")
    print(f"  file te!=ta pairs={te_ne_ta_file}")
    print(f"  file subnormal-output lines={sub_out}")
    for (fi, fam), (n, mf, mk) in sorted(by_fam.items()):
        print(f"  fi={fi} fam={fam}: lines={n} fastdec-mm={mf} kernel-mm={mk}")
    for fn, rm, a, b, rb, rf, mine, tag in first_file:
        print(f"  FILE-MM {fn} {rm} a={a:x} b={b:x} file={rb:x}/{rf:02x} "
              f"mine={mine[0]:x}/{mine[1]:02x} {tag}")
    for fn, rm, a, b, rb, rf, kb, kf, tag in first_kern:
        print(f"  KERN-MM {fn} {rm} a={a:x} b={b:x} file={rb:x}/{rf:02x} "
              f"kern={kb:x}/{kf:02x} {tag}")
    return 0 if (tot_mm_file == 0 and tot_mm_kern == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
