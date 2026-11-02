"""Independent recount of one agent transcript (escalation-test)."""
import json

SID = "01a17930-d09e-7dc1-8a62-373544613a4c"
CUTOFF = "2026-10-26T11:31:34-07:00"
BASE = "C:/Users/logan/.local/share/muse/sessions/2026/10/26/01a17907-4147-7333-a565-56071da9d971"

from datetime import datetime
cut = round(datetime.fromisoformat(CUTOFF).timestamp() * 1_000_000)

path = f"{BASE}/subagent/{SID}/session.jsonl"
usage_in = usage_out = cached = msgs = 0
tool_ids = set()
stamps = []
dups = 0
seen = set()
for line in open(path, encoding="utf-8"):
    line = line.strip()
    if not line:
        continue
    rec = json.loads(line)
    ts = rec.get("recorded_at")
    if isinstance(ts, int) and ts > cut:
        continue
    if isinstance(ts, int):
        stamps.append(ts)
    ev = (rec.get("payload") or {}).get("event") or {}
    if ev.get("kind") == "assistant_tool_calls_committed":
        for c in ev.get("tool_calls") or []:
            cid = c.get("call_id") or c.get("id")
            if cid:
                tool_ids.add(cid)
    elif ev.get("kind") == "model_completed":
        u = ev["usage"]
        key = (ts, ev.get("model"), ev.get("duration_ms"),
               tuple(u.get(f) for f in ("input_tokens", "output_tokens", "cached_tokens",
                                        "cache_write_tokens", "cache_read_tokens", "reasoning_tokens")))
        if key in seen:
            dups += 1
            continue
        seen.add(key)
        usage_in += u["input_tokens"]
        usage_out += u["output_tokens"]
        cached += u["cached_tokens"]
        msgs += 1

committed = [json.loads(l) for l in open(
    "muse-softfloat/docs/metrics/usage.jsonl", encoding="utf-8") if "escalation-test" in l][0]
passes = [json.loads(l) for l in open(
    "muse-softfloat/docs/metrics/passes.jsonl", encoding="utf-8") if "escalation-test" in l][0]
print("recount: in=%d out=%d cached=%d msgs=%d tools=%d dups=%d stamps=%d..%d" % (
    usage_in, usage_out, cached, msgs, len(tool_ids), dups, min(stamps), max(stamps)))
print("committed usage:", committed["input_tokens"], committed["output_tokens"],
      committed["cached_tokens"], committed["messages"])
print("committed pass tools:", passes["tool_uses"], "start:", passes["start"], "end:", passes["end"])
ok = (usage_in == committed["input_tokens"] and usage_out == committed["output_tokens"]
      and cached == committed["cached_tokens"] and msgs == committed["messages"]
      and len(tool_ids) == passes["tool_uses"])
print("MATCH" if ok else "MISMATCH")
