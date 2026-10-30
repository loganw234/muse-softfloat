#!/usr/bin/env python3
"""Append verifier-w4seam plant grades to docs/metrics/plants.jsonl."""
import json
import pathlib

repo = pathlib.Path("C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat")
path = repo / "docs" / "metrics" / "plants.jsonl"
existing = path.read_bytes().decode("utf-8")
assert "verifier-w4seam" not in existing, "rows already appended"
key = "80c99a9bba993b5610f48c1f8050736f013b657f0a0f3a86dd4d5590193d7252"
work = "SF-1 Step 0a Tier 2 table/inventory seam (33 planned rows, 0 semantics)"
rows = [
    (1, "a reserved claim token admitted before its gate exists",
     "(a1) own C-ULP generator mutant exited 0; source and docstring named"),
    (2, "one minmax family loses its flags pointer in the table",
     "(b1) regen drift in 3 generated files at the maximum rows"),
    (3, "registered Tier 2 freeze weakened from equality to a floor",
     "(a3) verifier-invented +1-row inventory mutant accepted at 34 registered"),
    (4, "one generated coverage authority altered by hand",
     "(b2) regen diff at COVERAGE line 8 (berkeley vs mpfr-exact)"),
    (5, "documented provenance cap disagrees with the runner",
     "(a2) MAX_PROV 256 in VECTORS vs 128 at runner.c:119"),
]
with path.open("ab") as fh:
    for plant, shape, note in rows:
        row = {"wave": "wave4", "verifier": "verifier-w4seam", "work": work,
               "key_sha256": key, "plant": plant, "shape": shape,
               "grade": "caught", "graded_by": "lead",
               "checked_by": "integration", "note": note}
        fh.write((json.dumps(row) + "\n").encode("utf-8"))
print("appended 5 verifier-w4seam plant rows")
