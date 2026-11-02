#!/usr/bin/env python3
"""Session-store structure inventory: names/sizes/mtimes only, no content."""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

STORE = Path(r"C:\Users\logan\.local\share\muse\sessions")
OUT = Path(__file__).with_name("inventory0.json")


def iso(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone().isoformat(timespec="seconds")


def main():
    if not STORE.is_dir():
        print(f"STORE MISSING: {STORE}")
        return 1
    top = []
    total_bytes = 0
    n_main = n_sub = 0
    biggest = []
    for date_dir in sorted(STORE.rglob("*")):
        if date_dir.name == "session.jsonl":
            pass
    # top-level session dirs: YYYY/MM/DD/<id>/session.jsonl
    for main in sorted(STORE.rglob("session.jsonl")):
        rel = main.relative_to(STORE)
        size = main.stat().st_size
        total_bytes += size
        biggest.append((size, str(rel)))
        if "subagent" in rel.parts:
            n_sub += 1
        else:
            n_main += 1
    biggest.sort(reverse=True)
    print(f"store={STORE}")
    print(f"main session.jsonl={n_main} subagent session.jsonl={n_sub} total={n_main+n_sub}")
    print(f"total bytes={total_bytes:,}")
    print("biggest 15:")
    for size, rel in biggest[:15]:
        print(f"  {size:>14,}  {rel}")
    # per top-dir summary
    tops = {}
    for main in sorted(STORE.rglob("session.jsonl")):
        rel = main.relative_to(STORE)
        if "subagent" in rel.parts:
            continue
        d = main.parent
        subs = sorted((d / "subagent").glob("*/session.jsonl")) if (d / "subagent").is_dir() else []
        tops[str(rel.parent)] = {
            "main_bytes": main.stat().st_size,
            "main_mtime": iso(main.stat().st_mtime),
            "n_subagents": len(subs),
            "sub_bytes": sum(p.stat().st_size for p in subs),
        }
    print(f"top-level session dirs={len(tops)}")
    for k in sorted(tops):
        t = tops[k]
        print(f"  {k} main={t['main_bytes']:,} mtime={t['main_mtime']} subs={t['n_subagents']} sub_bytes={t['sub_bytes']:,}")
    OUT.write_text(json.dumps({"tops": tops, "n_main": n_main, "n_sub": n_sub,
                                 "total_bytes": total_bytes}, indent=1), encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
