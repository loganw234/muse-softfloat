"""Cross-check: exact-duplicate model_completed events (lead dedup key) and
whether nested children record_json carries any counted events or
out-of-range stamps the lead's top-level-only loop would miss."""
import json
import sys
from collections import Counter

USAGE_INT_FIELDS = ("input_tokens", "output_tokens", "cached_tokens",
                    "cache_write_tokens", "cache_read_tokens",
                    "reasoning_tokens")


def unwrap(top):
    out = [top]
    stack = [top]
    while stack:
        obj = stack.pop()
        if isinstance(obj, dict):
            for child in obj.get("children") or []:
                if isinstance(child, dict):
                    raw = child.get("record_json")
                    if isinstance(raw, str):
                        try:
                            inner = json.loads(raw)
                        except json.JSONDecodeError:
                            continue
                        out.append(inner)
                        stack.append(inner)
    return out


def key_of(rec):
    payload = rec.get("payload") or {}
    ev = payload.get("event") or {}
    usage = ev.get("usage") or {}
    return ((rec.get("recorded_at"), ev.get("model"), ev.get("duration_ms"))
            + tuple(usage.get(f) for f in USAGE_INT_FIELDS))


for target in sys.argv[1:]:
    top_completed = 0
    all_completed = 0
    keys = []
    top_stamps = []
    all_stamps = []
    top_tools = set()
    all_tools = set()
    with open(target, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                top = json.loads(line)
            except json.JSONDecodeError:
                continue
            recs = unwrap(top)
            for i, rec in enumerate(recs):
                ts = rec.get("recorded_at")
                if isinstance(ts, int) and not isinstance(ts, bool):
                    all_stamps.append(ts)
                    if i == 0:
                        top_stamps.append(ts)
                payload = rec.get("payload")
                if not isinstance(payload, dict):
                    continue
                ev = payload.get("event")
                if not isinstance(ev, dict):
                    continue
                kind = ev.get("kind")
                if kind == "model_completed":
                    all_completed += 1
                    keys.append(key_of(rec))
                    if i == 0:
                        top_completed += 1
                elif kind == "assistant_tool_calls_committed":
                    ids = {c.get("call_id") or c.get("id")
                           for c in ev.get("tool_calls") or []
                           if isinstance(c, dict)}
                    ids.discard(None)
                    all_tools |= ids
                    if i == 0:
                        top_tools |= ids
    dup = sum(c - 1 for c in Counter(keys).values() if c > 1)
    print("file: " + target.rsplit("/", 2)[-2])
    print("top_level_model_completed=%d unwrapped_model_completed=%d "
          "exact_dupes_under_lead_key=%d" % (top_completed, all_completed, dup))
    print("top_level_tools=%d unwrapped_tools=%d" % (len(top_tools), len(all_tools)))
    print("top_stamps_min=%d top_stamps_max=%d" % (min(top_stamps), max(top_stamps)))
    print("all_stamps_min=%d all_stamps_max=%d" % (min(all_stamps), max(all_stamps)))
