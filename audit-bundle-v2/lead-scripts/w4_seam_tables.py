#!/usr/bin/env python3
"""Mechanical SF-1 Step 0a table edit for worktrees/w4-seam.

Appends tier/claim to every existing family (Tier 1 `required`),
registers the 11 SF-1 Step 1 families as Tier 2 `C-754` planned
rows, and updates the column documentation. Refuses to run twice.
"""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
PATH = ROOT / "tables" / "operations.tsv"
text = PATH.read_bytes().decode("utf-8").replace("\r\n", "\n")
lines = text.split("\n")
if lines and lines[-1] == "":
    lines.pop()

header_i = next(i for i, ln in enumerate(lines) if ln.startswith("op\t"))
header = lines[header_i].split("\t")
expected = ["op", "std_name", "clause", "sig", "rounding", "flags",
            "wave", "authority", "vectors", "comparison"]
assert header == expected, header

doc_anchor = "#               fixed in the header (saturation; NaN delivers zero),"
assert doc_anchor in lines
insert_at = lines.index(doc_anchor) + 2  # after the comparison doc block
doc = [
    "#   tier        1 = SF-0 required surface; 2 = SF-1 recommended",
    "#               surface. Tier 2 families register only as",
    "#               binary16/32/64 bundles (SF-1 format parity).",
    "#   claim       closed claim token (gen_tables.py refuses others):",
    "#               required (tier 1) or C-754 (tier 2 at this step);",
    "#               reserved SF-1 tokens join only with their gates",
]
lines[insert_at:insert_at] = doc
header_i += len(doc)
lines[header_i] = "\t".join(header + ["tier", "claim"])

out = []
for i, ln in enumerate(lines):
    if i <= header_i or not ln or ln.startswith("#"):
        out.append(ln)
        continue
    cells = ln.split("\t")
    assert len(cells) == 10, ln
    out.append("\t".join(cells + ["1", "required"]))

tier2 = [
    ("minimum", "minimum", "9.6", "minmax", "none", "yes",
     "directed-classes;exhaustive-f16-boundary"),
    ("maximum", "maximum", "9.6", "minmax", "none", "yes",
     "directed-classes;exhaustive-f16-boundary"),
    ("minimum_number", "minimumNumber", "9.6", "minmax", "none", "yes",
     "directed-classes;exhaustive-f16-boundary"),
    ("maximum_number", "maximumNumber", "9.6", "minmax", "none", "yes",
     "directed-classes;exhaustive-f16-boundary"),
    ("minimum_magnitude", "minimumMagnitude", "9.6", "minmax", "none", "yes",
     "directed-classes;exhaustive-f16-boundary"),
    ("maximum_magnitude", "maximumMagnitude", "9.6", "minmax", "none", "yes",
     "directed-classes;exhaustive-f16-boundary"),
    ("minimum_magnitude_number", "minimumMagnitudeNumber", "9.6", "minmax",
     "none", "yes", "directed-classes;exhaustive-f16-boundary"),
    ("maximum_magnitude_number", "maximumMagnitudeNumber", "9.6", "minmax",
     "none", "yes", "directed-classes;exhaustive-f16-boundary"),
    ("get_payload", "getPayload", "9.7", "payload_un", "none", "no",
     "exhaustive-f16;directed-encodings"),
    ("set_payload", "setPayload", "9.7", "payload_un", "none", "no",
     "exhaustive-f16;directed-encodings"),
    ("set_payload_signaling", "setPayloadSignaling", "9.7", "payload_un",
     "none", "no", "exhaustive-f16;directed-encodings"),
]
for op, std, clause, sig, rounding, flags, vectors in tier2:
    out.append("\t".join([op, std, clause, sig, rounding, flags, "4",
                          "project-exact", vectors, "exact", "2", "C-754"]))

PATH.write_bytes(("\n".join(out) + "\n").encode("utf-8"))
print("operations.tsv: %d family rows (81 tier1 + 11 tier2)" %
      (len(out) - header_i - 1))
