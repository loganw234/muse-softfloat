#!/usr/bin/env python3
"""Sqrt relabel files: theorem scope (homogeneous + widening)
vs full (incl. narrowing, where ties exist and relabel must
fail on exactly the tie lines)."""
import pathlib
import sys

wt = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])
NARROWING = {"msf16_sqrt_f32", "msf16_sqrt_f64", "msf32_sqrt_f64"}
th, full = [], []
for p in sorted((wt / "tests/vectors").glob("*.vec")):
    for line in p.read_text(encoding="utf-8").splitlines():
        t = line.split()
        if len(t) >= 2 and "_sqrt" in t[0] and t[1] == "te":
            t[1] = "ta"
            s = " ".join(t)
            full.append(s)
            if t[0] not in NARROWING:
                th.append(s)
for name, lines in (("sqrt_relabel_theorem.vec", th),
                    ("sqrt_relabel_full.vec", full)):
    with open(out / name, "w", newline="\n", encoding="utf-8") as fh:
        fh.write("# scratch gate: committed te sqrt lines relabeled ta\n")
        for s in lines:
            fh.write(s + "\n")
    print(name, len(lines), "lines")
