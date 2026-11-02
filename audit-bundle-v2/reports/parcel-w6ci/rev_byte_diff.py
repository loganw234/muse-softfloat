#!/usr/bin/env python3
"""rev_byte_diff.py - byte-level comparisons for the
parcel-w6ci revision-round Linux-semantics proof.

Usage:
  rev_byte_diff.py check-runsh
  rev_byte_diff.py compare ORIGINAL CANDIDATE LABEL
  rev_byte_diff.py tags OLD_TAGS NEW_TAGS
"""
import sys
from collections import Counter
from pathlib import Path

WT = Path(r"C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-ci")
SC = Path(r"C:/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6ci")


def read(p):
    return Path(p).read_bytes()


def check_runsh():
    d = read(WT / "tools/run.sh")
    print(f"run.sh bytes={len(d)} CRLF={d.count(bytes([13, 10]))} rawCR={d.count(bytes([13]))}")
    needle = b'if (substr(t,length(t))=="' + bytes([92]) + b'r")'
    print(f"awk CR-escape idiom (backslash+r two chars) occurrences: {d.count(needle)}")
    assert d.count(bytes([13])) == 0 and d.count(needle) == 2


def compare(orig_path, cand_path, label):
    a, b = read(orig_path), read(cand_path)
    print(f"[{label}] orig={len(a)} bytes cand={len(b)} bytes same_len={len(a) == len(b)}")
    if len(a) == len(b):
        diffs = [i for i in range(len(a)) if a[i] != b[i]]
        print(f"[{label}] differing byte positions: {len(diffs)}")
        for i in diffs[:5]:
            print(f"[{label}]   offset {i}: orig {a[i:i+1]!r} -> cand {b[i:i+1]!r}")
    la = a.split(b"\n")
    lb = b.split(b"\n")
    print(f"[{label}] orig lines={len(la)} cand lines={len(lb)}")
    n = 0
    for i, (x, y) in enumerate(zip(la, lb), 1):
        if x != y:
            n += 1
            if n <= 3:
                print(f"[{label}]   line {i} orig: {x!r}")
                print(f"[{label}]   line {i} cand: {y!r}")
    print(f"[{label}] differing lines: {n}")
    crlf_c = sum(1 for ln in lb if ln.endswith(bytes([13])))
    print(f"[{label}] candidate CRLF-terminated lines: {crlf_c}")


def tags(old_path, new_path):
    old = [ln for ln in read(old_path).split(b"\n") if ln]
    new = [ln for ln in read(new_path).split(b"\n") if ln]
    cr = bytes([13])
    old_cr = sum(1 for ln in old if ln.endswith(cr))
    new_cr = sum(1 for ln in new if cr in ln)
    print(f"old tags={len(old)} ending-in-CR={old_cr}; new tags={len(new)} containing-CR={new_cr}")
    same = Counter(ln.rstrip(cr) for ln in old) == Counter(new)
    print(f"tag multiset (old CR-stripped) == new: {same}")
    print(f"old==new raw bytes: {read(old_path) == read(new_path)}")


def line(path, n, label):
    lines = read(path).split(b"\n")
    print(f"[{label}] line {n}: {lines[n - 1]!r}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "check-runsh":
        check_runsh()
    elif cmd == "line":
        line(sys.argv[2], int(sys.argv[3]), sys.argv[4])
    elif cmd == "compare":
        compare(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "tags":
        tags(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit(f"unknown cmd {cmd}")
