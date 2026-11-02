"""Corroborate TWIDDLES.md Section 4 control numbers by direct log diffs.

Compares scratch/parcel-w4kissfft/out/hashes-{main,flip,unpatched,
fast,fastfma}.txt KF rows and prints per-file change counts.
Usage: controls_check.py (no args; paths fixed to the trail).
"""
import pathlib

out = pathlib.Path("scratch/parcel-w4kissfft/out")


def kf(name):
    rows = [ln for ln in (out / name).read_text().splitlines()
            if ln.startswith("KF ")]
    return rows


main = kf("hashes-main.txt")
print("main KF rows: %d" % len(main))
for name in ("hashes-flip.txt", "hashes-unpatched.txt",
             "hashes-fast.txt", "hashes-fastfma.txt"):
    other = kf(name)
    diff = [a for a, b in zip(main, other) if a != b]
    print("%-20s rows=%d changed=%d" % (name, len(other), len(diff)))
    for d in diff[:13]:
        print("  CHANGED: " + d.split(" ", 4)[1] + " "
              + d.split(" ", 4)[2] + " " + d.split(" ", 4)[3])
