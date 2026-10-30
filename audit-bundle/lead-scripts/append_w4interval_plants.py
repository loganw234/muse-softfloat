#!/usr/bin/env python3
"""Append verifier-w4interval plant grades to docs/metrics/plants.jsonl."""
import json
import pathlib

repo = pathlib.Path("C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat")
path = repo / "docs" / "metrics" / "plants.jsonl"
existing = path.read_bytes().decode("utf-8")
assert "verifier-w4interval" not in existing, "rows already appended"
key = "4fd3df3ba40dfce9d11a93677796414e68a7c212bef5f58b84bccbc03a30aa43"
work = "SF-1 Step 1c interval workload host proof: staged sphere, 9.6 box, torus bracketing"
rows = [
    (1, "lower endpoints rounded to nearest instead of downward",
     "(b1) 485 hard containment violations on independent Fraction audit"),
    (2, "stage-3 proof guard no longer trips on overflow",
     "(a2) source read vs design entry; behaviourally masked by INVALID, still named"),
    (3, "a banned Number form enters the containment path",
     "(a1) min64 msf64_minimum_number; source-scan gate fails on shipped core"),
    (4, "exact discriminant oracle adds instead of subtracts",
     "(b2) regeneration crashes at fam_limb assertion; formula named at gen:69"),
    (5, "one frozen catalogue exact decision corrupted",
     "(b3) TSV row id 2 MISS contradicts positive exact_extra and recompute"),
]
with path.open("ab") as fh:
    for plant, shape, note in rows:
        row = {"wave": "wave4", "verifier": "verifier-w4interval", "work": work,
               "key_sha256": key, "plant": plant, "shape": shape,
               "grade": "caught", "graded_by": "lead",
               "checked_by": "integration", "note": note}
        fh.write((json.dumps(row) + "\n").encode("utf-8"))
print("appended 5 verifier-w4interval plant rows")
