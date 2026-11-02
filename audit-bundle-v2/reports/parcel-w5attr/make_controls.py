#!/usr/bin/env python3
"""Build the scratch negative-control artifacts:
- mutant msf_string.c with the dec_round_inc ta arm removed
- mutant msf_string.c with the to_hex ta arm removed
- sqrt te->ta relabel replay file from committed vectors
- one flipped relabeled trig expectation
Usage: make_controls.py WORKTREE OUTDIR
"""
import pathlib
import sys

wt = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)

src = (wt / "src/msf_string.c").read_text(encoding="utf-8")
dec_arm = ("    case MSF_IROUND_TIES_TO_AWAY:\n"
           "        return gt_half || eq_half;\n")
hex_arm = ("            case MSF_IROUND_TIES_TO_AWAY:\n"
           "                inc = dropped >= half;\n"
           "                break;\n")
assert src.count(dec_arm) == 1, "dec arm not found once"
assert src.count(hex_arm) == 1, "hex arm not found once"
(out / "msf_string_mutant_dec.c").write_text(
    src.replace(dec_arm, ""), encoding="utf-8", newline="\n")
(out / "msf_string_mutant_hex.c").write_text(
    src.replace(hex_arm, ""), encoding="utf-8", newline="\n")
print("mutants written")

n = 0
with open(out / "sqrt_relabel.vec", "w", newline="\n",
          encoding="utf-8") as fh:
    fh.write("# scratch gate: committed te sqrt lines relabeled ta\n")
    for p in sorted((wt / "tests/vectors").glob("*.vec")):
        for line in p.read_text(encoding="utf-8").splitlines():
            t = line.split()
            if len(t) >= 2 and "_sqrt" in t[0] and t[1] == "te":
                t[1] = "ta"
                fh.write(" ".join(t) + "\n")
                n += 1
print("sqrt relabel lines:", n)

trig = (wt / "tests/vectors/trig-f32.vec").read_text(
    encoding="utf-8").splitlines()
flipped = 0
with open(out / "trig_flipped.vec", "w", newline="\n",
          encoding="utf-8") as fh:
    for line in trig:
        t = line.split()
        if (not flipped and len(t) >= 6 and t[1] == "ta"
                and t[-1].endswith("-ta-relabel")):
            i = t.index("->")
            t[i + 1] = "%x" % (int(t[i + 1], 16) + 1)
            line = " ".join(t)
            flipped = 1
        fh.write(line + "\n")
print("trig flipped lines:", flipped)
assert flipped
