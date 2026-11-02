#!/usr/bin/env python3
"""Streaming per-session inventory of the lead session subtree (+ top-level mirrors).

Counting only: stores role labels, brief/scratch path labels, stamps, usage
sums, tool counts, sha256. No prompt/prose text is retained beyond labels.
Mirrors tools/extract_session_metrics.py counting rules for cross-checking;
final appended numbers come from the sanctioned extractor, not from here.
"""
import collections
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

STORE = Path(r"C:\Users\logan\.local\share\muse\sessions")
LEAD = STORE / "2026" / "10" / "26" / "01a17907-4147-7333-a565-56071da9d971"
OUT = Path(__file__).with_name("inventory1.json")
USAGE_FIELDS = ("input_tokens", "output_tokens", "cached_tokens",
                "cache_write_tokens", "cache_read_tokens", "reasoning_tokens")
RE_ROLE = re.compile(r"Role:\s*\**\s*([A-Za-z0-9][A-Za-z0-9_-]*)")
RE_YOUARE = re.compile(r"You are ([a-z][a-z0-9]+(?:-[a-z0-9]+)+)")
RE_BRIEF = re.compile(r"ledger/briefs/([A-Za-z0-9_.-]+\.md)")
RE_SCRATCH = re.compile(r"scratch/([a-z0-9][a-z0-9_-]*)/")
RE_WORKTREE = re.compile(r"worktrees/([a-z0-9][a-z0-9_-]*)/")


def iso(micros):
    return datetime.fromtimestamp(micros / 1_000_000, tz=timezone.utc).astimezone().isoformat(timespec="seconds")


def strings_deep(obj, out, limit):
    if len(out) >= limit:
        return
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            strings_deep(v, out, limit)
    elif isinstance(obj, list):
        for v in obj:
            strings_deep(v, out, limit)


def scan(path, is_main):
    stamps_min = stamps_max = None
    tool_ids = set()
    usage = collections.defaultdict(lambda: collections.Counter())
    msgs = collections.Counter()
    seen = set()
    prompts = []
    label_hits = []
    h = hashlib.sha256()
    nrec = 0
    with open(path, "rb") as f:
        for raw in f:
            h.update(raw)
            line = raw.strip()
            if not line:
                continue
            nrec += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                label_hits.append(f"UNPARSEABLE line {nrec}")
                continue
            if not isinstance(rec, dict):
                continue
            ts = rec.get("recorded_at")
            if isinstance(ts, int):
                stamps_min = ts if stamps_min is None else min(stamps_min, ts)
                stamps_max = ts if stamps_max is None else max(stamps_max, ts)
            payload = rec.get("payload")
            if not isinstance(payload, dict):
                continue
            ev = payload.get("event")
            if not isinstance(ev, dict):
                continue
            kind = ev.get("kind")
            if kind == "started" and isinstance(ev.get("prompt"), str):
                if len(prompts) < 2:
                    prompts.append(ev["prompt"])
            elif kind == "assistant_tool_calls_committed":
                for call in ev.get("tool_calls") or []:
                    cid = call.get("call_id") or call.get("id")
                    if cid:
                        tool_ids.add(cid)
            elif kind == "model_completed":
                u = ev.get("usage")
                model = ev.get("model")
                if not isinstance(u, dict) or not isinstance(model, str):
                    label_hits.append("model_completed without usage/model")
                    continue
                key = (ts, model, ev.get("duration_ms")) + tuple(u.get(f) for f in USAGE_FIELDS)
                if key in seen:
                    continue
                seen.add(key)
                for fld in USAGE_FIELDS:
                    usage[model][fld] += u.get(fld, 0) or 0
                msgs[model] += 1
            # label evidence from early records only (prompts + first tool args)
            if nrec <= 60 and len(label_hits) < 12:
                strs = []
                strings_deep(ev, strs, 30)
                for s in strs:
                    for pat, tag in ((RE_YOUARE, "youare"), (RE_BRIEF, "brief"),
                                     (RE_SCRATCH, "scratch"), (RE_WORKTREE, "worktree")):
                        m = pat.search(s)
                        if m:
                            hit = f"{tag}:{m.group(1)}"
                            if hit not in label_hits:
                                label_hits.append(hit)
    head = "\n".join(prompts)
    internal = (not is_main) and "reminder observer" in head.lower()
    m = re.search(r"Role:\s*([A-Za-z0-9_-]+)", head)
    role_label = m.group(1) if m else None
    m2 = RE_ROLE.search(head)
    role_label2 = m2.group(1) if m2 else None
    youare = RE_YOUARE.search(head)
    return {
        "session": path.parent.name,
        "is_main": is_main,
        "internal_reminder": internal,
        "role_label_extractor": role_label,
        "role_label_relaxed": role_label2,
        "youare": youare.group(1) if youare else None,
        "labels": label_hits,
        "start": iso(stamps_min) if stamps_min is not None else None,
        "end": iso(stamps_max) if stamps_max is not None else None,
        "tool_uses": len(tool_ids),
        "records": nrec,
        "bytes": path.stat().st_size,
        "sha256_12": h.hexdigest()[:12],
        "usage_by_model": {k: dict(v) for k, v in usage.items()},
        "messages_by_model": dict(msgs),
    }


def main():
    files = [(LEAD / "session.jsonl", True)]
    files += [(p, False) for p in sorted((LEAD / "subagent").glob("*/session.jsonl"))]
    rows = []
    for i, (p, is_main) in enumerate(files):
        r = scan(p, is_main)
        r["rel"] = str(p.relative_to(STORE))
        rows.append(r)
        if (i + 1) % 50 == 0:
            print(f"scanned {i+1}/{len(files)}", flush=True)
    # top-level mirrors: light scan for duplicate detection
    mirrors = []
    sub_ids = {r["session"] for r in rows if not r["is_main"]}
    for main in sorted(STORE.rglob("session.jsonl")):
        rel = main.relative_to(STORE)
        if "subagent" in rel.parts or main.parent == LEAD:
            continue
        r = scan(main, True)
        r["rel"] = str(rel)
        r["also_subagent"] = r["session"] in sub_ids
        mirrors.append(r)
    OUT.write_text(json.dumps({"lead_subtree": rows, "top_mirrors": mirrors}, indent=1), encoding="utf-8")
    work = [r for r in rows if not r["internal_reminder"]]
    print(f"lead subtree files={len(rows)} work={len(work)} internal={len(rows)-len(work)}")
    print(f"top-level mirrors={len(mirrors)} of which also subagent={sum(1 for m in mirrors if m['also_subagent'])}")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
