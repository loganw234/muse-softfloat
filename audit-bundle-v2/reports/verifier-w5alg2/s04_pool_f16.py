#!/usr/bin/env python3
"""s04_pool_f16.py - binary16 second-operand sweep: fixed boundary pool
as first operand x all 65,536 encodings as second operand, kernel floor
build vs fastdec (== mydecide, self-tested). Counts printed; mismatch
pairs saved for arm-by-arm classification."""
import subprocess
import sys
import os

OUT = "scratch/verifier-w5alg2/out"
EXE = OUT + "/harness_floor.exe"
FASTDEC = "scratch/verifier-w5alg2/fastdec.py"
PY = os.environ.get("MSF_PYTHON", "python")
POOL = [0x0000, 0x8000, 0x0001, 0x8001, 0x0002, 0x03ff, 0x0400,
        0x3c00, 0xbc00, 0x3555, 0x7bff, 0x7c00, 0xfc00, 0x7e00,
        0xfe00, 0x7d55, 0x7c01, 0xfc01, 0x0003, 0x03fd]
RMS = ("te", "tz", "tp", "tn", "ta")

CHUNK = 65536  # one full second-operand sweep per chunk


def gen_input(pool_val):
    return "".join(f"0 {pool_val:04x} {b:04x}\n" for b in range(65536))


def main():
    total = mm = 0
    n_on = {r: 0 for r in RMS}
    mm_on = {r: 0 for r in RMS}
    first = []
    with open(f"{OUT}/s04_pool_f16_mism.txt", "w") as mf:
        for pv in POOL:
            blob = gen_input(pv)
            kh = subprocess.run([EXE, "hypot"], input=blob,
                                capture_output=True, text=True)
            if kh.returncode != 0:
                raise RuntimeError(kh.stderr[-2000:])
            fd = subprocess.run([PY, FASTDEC], input=blob,
                                capture_output=True, text=True)
            if fd.returncode != 0:
                raise RuntimeError(fd.stderr[-2000:])
            kl, fl = kh.stdout.splitlines(), fd.stdout.splitlines()
            assert len(kl) == len(fl) == 65536, (len(kl), len(fl))
            for b, kline, fline in zip(range(65536), kl, fl):
                kt, ft = kline.split(), fline.split()
                for i in range(5):
                    lb, lf = int(kt[2 * i], 16), int(kt[2 * i + 1], 16)
                    rb, rf = int(ft[2 * i], 16), int(ft[2 * i + 1], 16)
                    total += 1
                    n_on[RMS[i]] += 1
                    if lb != rb or lf != rf:
                        mm += 1
                        mm_on[RMS[i]] += 1
                        if len(first) < 10:
                            first.append((pv, b, i, lb, lf, rb, rf))
                        mf.write(f"0 {pv:04x} {b:04x} rm={RMS[i]} "
                                 f"kernel={lb:04x}/{lf:02x} "
                                 f"mine={rb:04x}/{rf:02x}\n")
            print(f"pool {pv:04x}: done", flush=True)
    print(f"POOL-F16: pool={len(POOL)} pairs={len(POOL)*65536} "
          f"decisions={total} mismatches={mm} "
          f"{'PASS' if mm == 0 else 'FAIL'}")
    print("per-mode decisions: " + " ".join(f"{r}={n_on[r]}" for r in RMS))
    print("per-mode mismatches: " + " ".join(f"{r}={mm_on[r]}" for r in RMS))
    for pv, b, i, lb, lf, rb, rf in first:
        print(f"  a={pv:04x} b={b:04x} rm={RMS[i]} "
              f"kernel={lb:04x}/{lf:02x} mine={rb:04x}/{rf:02x}")
    return 0 if mm == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
