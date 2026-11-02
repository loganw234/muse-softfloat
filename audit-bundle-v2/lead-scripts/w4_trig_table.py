#!/usr/bin/env python3
"""Register SF-1 Step 2c sinPi/cosPi families as planned Tier 2 rows."""
import pathlib
import sys

path = pathlib.Path(sys.argv[1]) / "tables" / "operations.tsv"
text = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
assert "\nsin_pi\t" not in text and "\ncos_pi\t" not in text, "already registered"
rows = [
    "\t".join(["sin_pi", "sinPi", "9.2", "math_un", "attr", "yes", "4",
               "mpfr-exact", "directed-hardest;wc-mpfr;seeded-random",
               "exact", "2", "C-754"]),
    "\t".join(["cos_pi", "cosPi", "9.2", "math_un", "attr", "yes", "4",
               "mpfr-exact", "directed-hardest;wc-mpfr;seeded-random",
               "exact", "2", "C-754"]),
]
if not text.endswith("\n"):
    text += "\n"
path.write_bytes((text + "\n".join(rows) + "\n").encode("utf-8"))
print("registered sin_pi + cos_pi (6 planned Tier 2 rows)")
