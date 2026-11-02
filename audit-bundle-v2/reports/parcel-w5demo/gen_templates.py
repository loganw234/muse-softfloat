#!/usr/bin/env python3
"""Authoring aid (scratch only): append the wrapper templates to
demo/make_ias15_extract.py from the ias15-pico scratch extract,
swapping the scratch-only header framings for demo-accurate ones.
The resulting repo file is self-contained; this script documents
how its template literals were produced and is not shipped."""
import pathlib

WS = pathlib.Path("C:/Users/logan/source/repos/Muse-Softfloat")
SRC = WS / "scratch" / "ias15" / "extract"
DST = WS / "worktrees" / "w5-demo" / "demo" / "make_ias15_extract.py"

SWAPS = {
    "reb_min.h": (
        "/* reb_min.h - minimal simulation/integrator declarations for the\n"
        " * IAS15 extraction. SCRATCH ONLY: this tree is derived from REBOUND\n"
        " * 5.2.2 (commit 262a9cce102c69ca2cf7f3c6c1264e5e60002b7d, archive\n"
        " * sha256 9221d38a7a3f6a5d134e4b92e7dc63648c6dfe01eb1753a3e570c24a384a2887),\n"
        " * GPL-3.0-or-later, and must never enter muse-softfloat. See\n"
        " * scratch/ias15/fetch.md and ledger/ias15-pico.md design entry.\n",
        "/* reb_min.h - minimal simulation/integrator declarations for the\n"
        " * IAS15 extraction. GENERATED into the demo cache by\n"
        " * demo/make_ias15_extract.py; never commit this file. The extract\n"
        " * is derived from REBOUND 5.2.2 (commit\n"
        " * 262a9cce102c69ca2cf7f3c6c1264e5e60002b7d, archive sha256\n"
        " * 9221d38a7a3f6a5d134e4b92e7dc63648c6dfe01eb1753a3e570c24a384a2887,\n"
        " * pinned in docs/metrics/fetches.jsonl), GPL-3.0-or-later.\n"),
    "sim_min.c": (
        "/* sim_min.c - minimal simulation wrapper for the IAS15 extraction.\n"
        " * SCRATCH ONLY (REBOUND 5.2.2 derived, GPL-3.0-or-later; see\n"
        " * reb_min.h). Replicates,",
        "/* sim_min.c - minimal simulation wrapper for the IAS15 extraction.\n"
        " * GENERATED into the demo cache by demo/make_ias15_extract.py;\n"
        " * never commit this file (REBOUND 5.2.2 side, GPL-3.0-or-later;\n"
        " * see reb_min.h). Replicates,"),
    "ias15x.c": (
        "/* ias15x.c - implements the board glue's opaque IAS15 API\n"
        " * (worktrees/w-ias15/board/ias15_api.h) over the extracted REBOUND\n"
        " * subset. SCRATCH ONLY (GPL-3.0-or-later side; see reb_min.h). Build",
        "/* ias15x.c - implements the board glue's opaque IAS15 API\n"
        " * (board/ias15_api.h) over the extracted REBOUND subset.\n"
        " * GENERATED into the demo cache by demo/make_ias15_extract.py;\n"
        " * never commit this file (GPL-3.0-or-later side; see reb_min.h).\n"
        " * Build"),
}

texts = {}
for fname, (old, new) in SWAPS.items():
    raw = (SRC / fname).read_bytes().decode("utf-8")
    norm = raw.replace("\r\n", "\n")
    if norm != raw:
        print("%s: CRLF normalized (%d -> %d bytes)" % (fname, len(raw), len(norm)))
    n = norm.count(old)
    assert n == 1, (fname, n)
    text = norm.replace(old, new)
    assert "scratch" not in text.lower(), fname
    assert "'''" not in text, fname
    assert "\\" not in text, (fname, "backslash present - needs repr")
    assert text.endswith("\n"), fname
    texts[fname] = text
    print("%s: %d chars, header swapped" % (fname, len(text)))

tail = []
tail.append("")
tail.append("")
tail.append("# ---- wrapper templates -------------------------------------")
tail.append("# Project-authored for this extract interface (arena wrapper,")
tail.append("# API implementation, declarations).  Emitted verbatim into")
tail.append("# the demo cache next to the extracted GPL sources; the")
tail.append("# generated files are never committed.")
tail.append("")
for var, fname in (("REB_MIN_H", "reb_min.h"), ("SIM_MIN_C", "sim_min.c"),
                   ("IAS15X_C", "ias15x.c")):
    tail.append("%s = '''%s'''" % (var, texts[fname]))
    tail.append("")
tail.append("")
tail.append('if __name__ == "__main__":')
tail.append("    sys.exit(main(sys.argv))")
tail.append("")

with open(DST, "a", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(tail))
print("appended templates to", DST)
