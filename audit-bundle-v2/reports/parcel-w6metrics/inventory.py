#!/usr/bin/env python3
"""Streaming per-session inventory of the lead subtree at the Wave 6 cutoff.

Counting/labels only (role labels, brief/scratch/worktree path labels from
early records); no prompt prose retained. Mirrors the extractor's counting
rules; final numbers come from tools/extract_session_metrics.py.
Adapted from scratch/parcel-w5metrics/inventory1.py with an --until cutoff.
"""
import collections, hashlib, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

STORE = Path(r"C:\Users\logan\.local\share\muse\sessions")
LEAD = STORE / "2026" / "10" / "26" / "01a17907-4147-7333-a565-56071da9d971"
OUT = Path(__file__).with_name("inventory.json")
UNTIL = round(datetime.fromisoformat("2026-10-30T16:08:00-07:00").timestamp() * 1_000_000)
USAGE_FIELDS = ("input_tokens", "output_tokens", "cached_tokens",
                "cache_write_tokens", "cache_read_tokens", "reasoning_tokens")
RE_YOUARE = re.compile(r"You are ([a-z][a-z0-9]+(?:-[a-z0-9]+)+)")
RE_PARCEL = re.compile(r"\b(parcel-[a-z0-9]+|verifier-[a-z0-9]+|study-[a-z0-9-]+|lead-[a-z0-9]+|fix-[a-z0-9]+|rechecker-?[a-z0-9]*|auditor-[a-z0-9-]+|surveyor-[a-z0-9]+|reader-[a-z0-9-]+|video-[a-z0-9]+|ias15-[a-z]+)\b")
RE_BRIEF = re.compile(r"ledger/briefs/([A-Za-z0-9_.-]+\.md)")
RE_SCRATCH = re.compile(r"scratch/([a-z0-9][a-z0-9_-]*)/")
RE_WORKTREE = re.compile(r"worktrees/([a-z0-9][a-z0-9_-]*)/")

def iso(micros):
    return datetime.fromtimestamp(micros / 1_000_000, tz=timezone.utc).astimezone().isoformat(timespec="seconds")

def strings_deep(obj, out, limit):
    if len(out) >= limit: return
    if isinstance(obj, str): out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values(): strings_deep(v, out, limit)
    elif isinstance(obj, list):
        for v in obj: strings_deep(v, out, limit)

def scan(path, is_main):
    smin = smax = None
    tool_ids = set()
    usage = collections.defaultdict(lambda: collections.Counter())
    msgs = collections.Counter()
    seen = set(); prompts = []; label_hits = []
    h = hashlib.sha256(); nrec = 0; ncut = 0
    with open(path, "rb") as f:
        for raw in f:
            h.update(raw)
            line = raw.strip()
            if not line: continue
            nrec += 1
            try: rec = json.loads(line)
            except json.JSONDecodeError:
                label_hits.append(f"UNPARSEABLE line {nrec}"); continue
            if not isinstance(rec, dict): continue
            ts = rec.get("recorded_at")
            if isinstance(ts, int) and ts > UNTIL:
                ncut += 1; continue
            if isinstance(ts, int):
                smin = ts if smin is None else min(smin, ts)
                smax = ts if smax is None else max(smax, ts)
            payload = rec.get("payload")
            if not isinstance(payload, dict): continue
            ev = payload.get("event")
            if not isinstance(ev, dict): continue
            kind = ev.get("kind")
            if kind == "started" and isinstance(ev.get("prompt"), str):
                if len(prompts) < 2: prompts.append(ev["prompt"])
            elif kind == "assistant_tool_calls_committed":
                for call in ev.get("tool_calls") or []:
                    cid = call.get("call_id") or call.get("id")
                    if cid: tool_ids.add(cid)
            elif kind == "model_completed":
                u = ev.get("usage"); model = ev.get("model")
                if not isinstance(u, dict) or not isinstance(model, str): continue
                key = (ts, model, ev.get("duration_ms")) + tuple(u.get(f) for f in USAGE_FIELDS)
                if key in seen: continue
                seen.add(key)
                for fld in USAGE_FIELDS: usage[model][fld] += u.get(fld, 0) or 0
                msgs[model] += 1
            if nrec <= 80 and len(label_hits) < 16:
                strs = []; strings_deep(ev, strs, 30)
                for s in strs:
                    for pat, tag in ((RE_BRIEF, "brief"), (RE_SCRATCH, "scratch"), (RE_WORKTREE, "worktree")):
                        m = pat.search(s)
                        if m:
                            hit = f"{tag}:{m.group(1)}"
                            if hit not in label_hits: label_hits.append(hit)
    head = "\n".join(prompts)
    internal = (not is_main) and "reminder observer" in head.lower()
    m = re.search(r"Role:\s*\**\s*([A-Za-z0-9][A-Za-z0-9_-]*)", head)
    youare = RE_YOUARE.search(head)
    parcelhits = []
    for mm in RE_PARCEL.finditer(head[:4000]):
        if mm.group(1) not in parcelhits: parcelhits.append(mm.group(1))
    return {
        "session": path.parent.name, "is_main": is_main,
        "internal_reminder": internal,
        "role_label": m.group(1) if m else None,
        "youare": youare.group(1) if youare else None,
        "parcel_hits_head": parcelhits[:6],
        "labels": label_hits,
        "start": iso(smin) if smin is not None else None,
        "end": iso(smax) if smax is not None else None,
        "tool_uses": len(tool_ids), "records": nrec, "records_after_cutoff": ncut,
        "bytes": path.stat().st_size, "sha256_12": h.hexdigest()[:12],
        "usage_by_model": {k: dict(v) for k, v in usage.items()},
        "messages_by_model": dict(msgs),
    }

def main():
    files = [(LEAD / "session.jsonl", True)]
    files += [(p, False) for p in sorted((LEAD / "subagent").glob("*/session.jsonl"))]
    rows = []
    for i, (p, is_main) in enumerate(files):
        rows.append(scan(p, is_main))
        if (i + 1) % 50 == 0: print(f"scanned {i+1}/{len(files)}", flush=True)
    OUT.write_text(json.dumps({"lead_subtree": rows}, indent=1), encoding="utf-8")
    work = [r for r in rows if not r["internal_reminder"]]
    live = [r for r in work if r["start"] is not None]
    print(f"lead subtree files={len(rows)} work={len(work)} internal={len(rows)-len(work)} with-records-at-cutoff={len(live)}")
    print(f"wrote {OUT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
