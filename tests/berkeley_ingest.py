#!/usr/bin/env python3
"""Stream Berkeley TestFloat vectors into our vector format.

The ingest hop (SF-0 Sections 4.1, 4.3): runs the pinned
testfloat_gen (docs/metrics/fetches.jsonl), translates Berkeley flag
bits to MSF order, and stamps each line's provenance. Nothing is
stored: vectors are generated per gate into the build directory.

    berkeley_ingest.py --fn f64_add --rm te|tz|tp|tn|ta|named \
        [--level 1|2] [--seed 1] [--take N] --out FILE

Berkeley function to our instantiation, measured at P0/Wave-1 prep:
- gen rounds via -r<mode>; testfloat_gen generates the exact=false
  semantics for roundToInt and the integer conversions (no inexact
  flag ever appears for those), so they map to our NAMED forms. The
  *Exact* variants have no Berkeley generator and are refused here;
  their authority is mpfr-exact (docs/COVERAGE.tsv).
- NaN payloads in Berkeley expectations follow its 8086-SSE
  specialization, not the SF-0 2.5 matrix, so arithmetic files carry
  `# compare=nan-class`; integer conversions carry
  `# compare=berkeley-int` (delivered integer on invalid is the
  project rule, Berkeley's is the indefinite pattern - measured).
- Boolean results are written 0/1 by testfloat_gen already.
"""
import argparse
import os
import pathlib
import subprocess
import sys

RM_GEN = {"te": "-rnear_even", "tz": "-rminMag", "tn": "-rmin",
          "tp": "-rmax", "ta": "-rnear_maxMag"}
RM_NAME = {"te": "ties_to_even", "tz": "toward_zero", "tn": "toward_negative",
           "tp": "toward_positive", "ta": "ties_to_away"}

# Berkeley flag bits -> MSF flag bits (measured from its header):
# inexact 1->0x10, underflow 2->0x08, overflow 4->0x04,
# infinite/div0 8->0x02, invalid 16->0x01.
def xlate_flags(b):
    m = 0
    if b & 1: m |= 0x10
    if b & 2: m |= 0x08
    if b & 4: m |= 0x04
    if b & 8: m |= 0x02
    if b & 16: m |= 0x01
    return m


def map_fn(fn, rm):
    """Return (our_op, our_rm_token, compare_mode) or raise."""
    if "_to_" in fn:
        src, dst = fn.split("_to_", 1)
        if dst in ("i32", "i64", "ui32", "ui64"):
            if rm not in RM_NAME:
                raise SystemExit("integer conversions need a named --rm")
            itok = ("u" + dst[2:]) if dst.startswith("ui") else dst
            return "msf%s_to_%s_%s" % (src[1:], itok, RM_NAME[rm]), "-", "berkeley-int"
        if src in ("i32", "i64", "ui32", "ui64"):
            itok = ("u" + src[2:]) if src.startswith("ui") else src
            return "msf%s_from_%s" % (dst[1:], itok), rm, "nan-class"
        return "msf%s_from_%s" % (dst[1:], src), rm, "nan-class"
    fmt, op = fn.split("_", 1)
    if op == "roundToInt":
        if rm not in RM_NAME:
            raise SystemExit("roundToInt needs a named --rm")
        return "msf%s_round_to_integral_%s" % (fmt[1:], RM_NAME[rm]), "-", "nan-class"
    if op in ("add", "sub", "mul", "div", "sqrt", "rem"):
        ours = "remainder" if op == "rem" else op
        return "msf%s_%s" % (fmt[1:], ours), ("-" if op == "rem" else rm), "nan-class"
    if op == "mulAdd":
        return "msf%s_fma" % fmt[1:], rm, "nan-class"
    # Berkeley's historical set is asymmetric (measured by both Wave 1
    # parcels independently): eq is the QUIET equality and the
    # signaling spelling carries the suffix, while le/lt are the
    # signaling forms with _quiet suffixed variants.
    cmp_map = {
        "eq": "compare_quiet_equal", "eq_signaling": "compare_signaling_equal",
        "le": "compare_signaling_less_equal", "lt": "compare_signaling_less",
        "le_quiet": "compare_quiet_less_equal", "lt_quiet": "compare_quiet_less",
    }
    if op in cmp_map:
        return "msf%s_%s" % (fmt[1:], cmp_map[op]), "-", "exact"
    raise SystemExit("no ingest mapping for Berkeley function %s "
                     "(Exact variants have no Berkeley generator)" % fn)


def gen_path():
    env = os.environ.get("MSF_TESTFLOAT_GEN")
    if env:
        return env
    cand = (pathlib.Path(__file__).resolve().parent.parent.parent
            / "scratch/oracles/TestFloat-3e/build/Linux-x86_64-GCC/testfloat_gen.exe")
    if cand.exists():
        return str(cand)
    cand2 = cand.with_suffix("")
    if cand2.exists():
        return str(cand2)
    raise SystemExit("testfloat_gen not found; set MSF_TESTFLOAT_GEN "
                     "(fetch record: docs/metrics/fetches.jsonl)")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fn", required=True)
    ap.add_argument("--rm", required=True, choices=list(RM_GEN) + ["-"])
    ap.add_argument("--level", type=int, default=1)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--take", type=int, default=0, help="first N cases (0=all)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv[1:])

    rm_for_map = "te" if a.rm == "-" else a.rm
    our_op, our_rm, compare = map_fn(a.fn, rm_for_map)
    cmd = [gen_path(), "-level", str(a.level), "-seed", str(a.seed)]
    if a.rm != "-":
        cmd.append(RM_GEN[a.rm])
    cmd.append(a.fn)
    prov = "berkeley:testfloat_gen-%s-%s-l%d-s%d" % (a.fn, a.rm, a.level, a.seed)
    print("ingest: %s -> %s (compare=%s)" % (" ".join(cmd), our_op, compare))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    n = 0
    with open(a.out, "w", encoding="utf-8", newline="\n") as out:
        out.write("# generated by tests/berkeley_ingest.py from pinned testfloat_gen\n")
        out.write("# compare=%s\n" % compare)
        for line in proc.stdout:
            tok = line.split()
            if len(tok) < 3:
                continue
            ops, result, flags = tok[:-2], tok[-2], tok[-1]
            out.write("%s %s %s -> %s %02x %s\n" % (
                our_op, our_rm, " ".join(x.lower() for x in ops),
                result.lower(), xlate_flags(int(flags, 16)), prov))
            n += 1
            if a.take and n >= a.take:
                proc.terminate()
                break
    proc.wait()
    print("ingest: wrote %d cases to %s" % (n, a.out))
    return 0 if n > 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
