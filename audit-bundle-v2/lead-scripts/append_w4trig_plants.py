#!/usr/bin/env python3
"""Append verifier-w4trig plant grades to docs/metrics/plants.jsonl."""
import json
import pathlib

repo = pathlib.Path("C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat")
path = repo / "docs" / "metrics" / "plants.jsonl"
existing = path.read_bytes().decode("utf-8")
assert "verifier-w4trig" not in existing, "rows already appended"
key = "ec0d8227f3af5cb748b0dfc8e4134d321b62ec3c7d04457cfea5e0ccef3325b0"
work = "SF-1 Step 2c: correctly rounded sinPi/cosPi (6 rows)"
rows = [
    (1, "cosPi half-integer zero takes the sign of x",
     "(b2) smallest f16 0xb800; 4096 f16 + 4 worst-case lines"),
    (2, "nearest-integer remainder sign dropped from sinPi result sign",
     "(b1) exact-negation pattern; also broke -Werror builds (r_neg unused)"),
    (3, "stage-1 error interval narrowed far inside its proven bound",
     "(b3) independent Ek re-derivation: needs <=146, header claimed 200; no replay misfire"),
    (4, "sine coefficient generator uses the wrong factorial",
     "(a) regeneration skew on all 39 sine rows; constants themselves verified exact"),
    (5, "one committed special-case flag expectation corrupted",
     "(a) trig-f64.vec:3 expects inexact for sinPi(+0); regeneration produces 00"),
]
with path.open("ab") as fh:
    for plant, shape, note in rows:
        row = {"wave": "wave4", "verifier": "verifier-w4trig", "work": work,
               "key_sha256": key, "plant": plant, "shape": shape,
               "grade": "caught", "graded_by": "lead",
               "checked_by": "integration", "note": note}
        fh.write((json.dumps(row) + "\n").encode("utf-8"))
print("appended 5 verifier-w4trig plant rows")
