#!/usr/bin/env python3
"""Append verifier-w4minmax plant grades to docs/metrics/plants.jsonl."""
import json
import pathlib

repo = pathlib.Path("C:/Users/logan/source/repos/Muse-Softfloat/muse-softfloat")
path = repo / "docs" / "metrics" / "plants.jsonl"
existing = path.read_bytes().decode("utf-8")
assert "verifier-w4minmax" not in existing, "rows already appended"
key = "0483c3c40ea64d9b94bc5b4d92e17f6de7cc2ddfbd3b95269a95d5d10ab4422a"
work = "SF-1 Step 1: Clause 9.6 min/max + 9.7 payloads (33 rows)"
rows = [
    (1, "Number forms signal invalid for the wrong NaN class",
     "(b2) 3888 directed fails; sNaN case silent, qNaN case invalid"),
    (2, "signed-zero ordering reversed in value comparison",
     "(b1) 48 directed fails; minimum(+0,-0) delivered +0"),
    (3, "payload setters swap the quiet and signaling encodings",
     "(b3) 30 directed fails; set_payload(1) built a signaling encoding"),
    (4, "reference generator rejects the maximum admissible payload",
     "(b4) independent reference disagreed on exactly 2 of 196608; regen crash at round-trip assert"),
    (5, "one committed getPayload expectation corrupted",
     "(b5) payload-f16.vec:2 expects +0 where runner correctly delivers -1"),
]
with path.open("ab") as fh:
    for plant, shape, note in rows:
        row = {"wave": "wave4", "verifier": "verifier-w4minmax", "work": work,
               "key_sha256": key, "plant": plant, "shape": shape,
               "grade": "caught", "graded_by": "lead",
               "checked_by": "integration", "note": note}
        fh.write((json.dumps(row) + "\n").encode("utf-8"))
print("appended 5 verifier-w4minmax plant rows")
