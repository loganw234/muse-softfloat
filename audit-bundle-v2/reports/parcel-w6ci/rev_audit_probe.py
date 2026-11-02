#!/usr/bin/env python3
"""rev_audit_probe.py - byte-level audit data for the run.sh
awk/sed CR audit (parcel-w6ci revision round).

All reads are binary. "Linux awk last field" is modelled the
POSIX way: record split at LF, fields split on runs of
space/tab (default FS, leading blanks skipped), so a trailing
CR stays attached to the last field.
"""
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

WT = Path(r"C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-ci")


def line_stats(name):
    data = (WT / name).read_bytes()
    lines = data.split(b"\n")
    if lines and lines[-1] == b"":
        lines.pop()
    crlf = sum(1 for ln in lines if ln.endswith(b"\r"))
    print(f"{name}: bytes={len(data)} lines={len(lines)} crlf={crlf} lf_only={len(lines)-crlf}")
    return lines


def awk_fields(line_bytes):
    # default FS: split on runs of blank (space/tab); also newline
    # is a separator but records have no LF left here.
    parts = re.split(rb"[ \t]+", line_bytes.strip(b" \t"))
    return [p for p in parts if p != b""] or []


inputs = [
    "tests/vectors/encodings-f16.vec",
    "tests/vectors/encodings-f32.vec",
    "tests/vectors/pack64.vec",
    "tests/vectors/arith-f32.vec",
    "docs/COVERAGE.tsv",
]
print("== direct awk inputs ==")
all_lines = {}
for name in inputs:
    all_lines[name] = line_stats(name)

print("\n== COVERAGE.tsv shape ==")
cov = all_lines["docs/COVERAGE.tsv"]
hdr = None
for ln in cov:
    if ln.startswith(b"#"):
        continue
    hdr = ln.rstrip(b"\r").split(b"\t")
    break
print(f"header NF={len(hdr)}")
for i, h in enumerate(hdr, 1):
    print(f"  col {i}: {h.decode()}")
print(f"$9 header = {hdr[8].decode()!r}, $13 header = {hdr[12].decode()!r}, $NF header = {hdr[-1].decode()!r}")
data_nf = Counter(len(ln.rstrip(b"\r").split(b"\t")) for ln in cov if ln and not ln.startswith(b"#"))
print(f"data-row NF values: {dict(data_nf)}")

print("\n== control 2 first-match analysis (encodings-f32) ==")
target = b"exact-py:directed-encodings"
n_class = 0
first = None
for idx, ln in enumerate(all_lines["tests/vectors/encodings-f32.vec"], 1):
    f = awk_fields(ln)
    if not f or f[0] != b"msf32_class":
        continue
    n_class += 1
    old_match = f[-1] == target
    new_match = f[-1].rstrip(b"\r") == target if f[-1].endswith(b"\r") else f[-1] == target
    if new_match and first is None:
        # emulate mutation: arrow followed by 0/1
        for i, tok in enumerate(f):
            if tok == b"->" and i + 1 < len(f) and f[i + 1] in (b"0", b"1"):
                first = (idx, ln, i + 1, f[i + 1], old_match)
                break
print(f"msf32_class lines: {n_class}")
if first:
    idx, ln, pos, val, old_match = first
    print(f"first new-logic match: line {idx}, field {pos+1}={val.decode()} old_linux_match={old_match}")
    print(f"  line bytes: {ln!r}")
    print(f"  single-spaced no-tab: {b'  ' not in ln and 9 not in ln}")
else:
    print("no match found - PROBLEM")

print("\n== write_expect_counts inputs: every $VECS file ==")
runsh = (WT / "tools/run.sh").read_bytes().decode("utf-8")
m = re.search(r'^VECS="(.*)"$', runsh, re.M)
vecs = m.group(1).split()
print(f"VECS count: {len(vecs)}")
tag_variants = defaultdict(Counter)  # stripped tag -> Counter(raw last field)
crlf_files = []
lf_files = []
mixed_files = []
for v in vecs:
    lines = line_stats(v)
    crlf = sum(1 for ln in lines if ln.endswith(b"\r"))
    if crlf == len(lines):
        crlf_files.append(v)
    elif crlf == 0:
        lf_files.append(v)
    else:
        mixed_files.append(v)
    for ln in lines:
        if ln.startswith(b"#") or not ln.strip(b" \t\r"):
            continue
        f = awk_fields(ln)
        if f:
            raw = f[-1]
            tag_variants[raw.rstrip(b"\r")][raw] += 1
print(f"fully CRLF files ({len(crlf_files)}): {crlf_files}")
print(f"fully LF files ({len(lf_files)}): {lf_files}")
print(f"mixed files ({len(mixed_files)}): {mixed_files}")
split_tags = {t: c for t, c in tag_variants.items() if len(c) > 1}
print(f"distinct provenance tags (CR-stripped): {len(tag_variants)}")
print(f"tags split by CR variant on Linux awk (two sort groups): {len(split_tags)}")
for t, c in sorted(split_tags.items()):
    print(f"  {t.decode()}: { {k.decode('unicode_escape'): v for k, v in c.items()} }")
print("tags carrying CR under Linux awk:")
for t, c in sorted(tag_variants.items()):
    for raw, n in c.items():
        if raw.endswith(b"\r"):
            print(f"  {raw.decode('unicode_escape')!r} x{n}")
sys.exit(0)
