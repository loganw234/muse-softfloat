#!/usr/bin/env python3
"""Parse every nonblank line of the given JSONL files."""
import json
import pathlib
import sys

for name in sys.argv[1:]:
    path = pathlib.Path(name)
    rows = 0
    for lno, line in enumerate(path.read_bytes().decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        json.loads(line)
        rows += 1
    print("%s: %d JSON rows parse" % (path, rows))
