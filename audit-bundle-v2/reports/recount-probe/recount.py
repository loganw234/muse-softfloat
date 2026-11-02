"""Independent recount probe: token/tool/minute counts from Muse transcripts.

Reads one session.jsonl file. Top-level lines may either carry the record
directly (payload.event.kind) or wrap inner records inside
children[].record_json JSON strings; both shapes are unwrapped.
Counts, per the probe spec:
  - lines where payload.event.kind == "model_completed" (no dedup),
  - sums of usage fields over those events only,
  - distinct tool call ids in assistant_tool_calls_committed events,
  - first/last recorded_at overall, converted to local time,
  - model strings seen on model_completed events.
"""
import json
import sys
from datetime import datetime, timezone

USAGE_FIELDS = (
    "input_tokens",
    "output_tokens",
    "cached_tokens",
    "cache_read_tokens",
    "cache_write_tokens",
    "reasoning_tokens",
)


def unwrap(line_obj):
    """Yield record dicts: the line itself plus any nested record_json."""
    stack = [line_obj]
    while stack:
        obj = stack.pop()
        if isinstance(obj, dict):
            yield obj
            children = obj.get("children")
            if isinstance(children, list):
                for child in children:
                    if isinstance(child, dict):
                        raw = child.get("record_json")
                        if isinstance(raw, str):
                            try:
                                stack.append(json.loads(raw))
                            except json.JSONDecodeError:
                                pass


def iso_local(micros):
    return datetime.fromtimestamp(
        micros / 1_000_000, tz=timezone.utc
    ).astimezone().isoformat(timespec="seconds")


if __name__ == "__main__":
    target = sys.argv[1]
    n_lines = 0
    n_completed = 0
    sums = {f: 0 for f in USAGE_FIELDS}
    missing_usage = 0
    models = {}
    tool_ids = set()
    tool_events = 0
    stamps_all = []
    stamps_completed = []

    with open(target, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            n_lines += 1
            try:
                top = json.loads(line)
            except json.JSONDecodeError:
                continue
            for rec in unwrap(top):
                ts = rec.get("recorded_at")
                ts_ok = isinstance(ts, int) and not isinstance(ts, bool)
                if ts_ok:
                    stamps_all.append(ts)
                payload = rec.get("payload")
                if not isinstance(payload, dict):
                    continue
                ev = payload.get("event")
                if not isinstance(ev, dict):
                    continue
                kind = ev.get("kind")
                if kind == "model_completed":
                    n_completed += 1
                    if ts_ok:
                        stamps_completed.append(ts)
                    models[ev.get("model")] = models.get(ev.get("model"), 0) + 1
                    usage = ev.get("usage")
                    if not isinstance(usage, dict):
                        missing_usage += 1
                        continue
                    for fld in USAGE_FIELDS:
                        val = usage.get(fld, 0)
                        if isinstance(val, int) and not isinstance(val, bool):
                            sums[fld] += val
                elif kind == "assistant_tool_calls_committed":
                    tool_events += 1
                    for call in ev.get("tool_calls") or []:
                        if isinstance(call, dict):
                            cid = call.get("call_id") or call.get("id")
                            if cid:
                                tool_ids.add(cid)

    print("file: " + target)
    print("top_level_lines: %d" % n_lines)
    print("model_completed_count: %d" % n_completed)
    print("model_completed_without_usage_dict: %d" % missing_usage)
    for fld in USAGE_FIELDS:
        print("sum_%s: %d" % (fld, sums[fld]))
    print("assistant_tool_calls_committed_events: %d" % tool_events)
    print("distinct_tool_call_ids: %d" % len(tool_ids))
    if stamps_all:
        print("first_recorded_at_raw: %d" % min(stamps_all))
        print("last_recorded_at_raw: %d" % max(stamps_all))
        print("first_recorded_at_local: %s" % iso_local(min(stamps_all)))
        print("last_recorded_at_local: %s" % iso_local(max(stamps_all)))
    if stamps_completed:
        print("first_model_completed_local: %s" % iso_local(min(stamps_completed)))
        print("last_model_completed_local: %s" % iso_local(max(stamps_completed)))
    print("models_on_model_completed:")
    for model, cnt in sorted(models.items(), key=lambda kv: str(kv[0])):
        print("  %r: %d" % (model, cnt))
