import json, pathlib

sess = pathlib.Path(r"C:\Users\logan\.local\share\muse\sessions\2026\10\26\01a17907-4147-7333-a565-56071da9d971")
files = sorted((sess / "subagent").glob("*/session.jsonl"))

def events(p):
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        try: o = json.loads(line)
        except Exception: continue
        yield o

def shorten(x, n=220):
    s = repr(x)
    return s if len(s) <= n else s[:n] + "..."

for p in files[:2] + files[-1:]:
    print("\n=====", p.parent.name)
    shown = set()
    for o in events(p):
        payload = o.get("payload") or {}
        kind = payload.get("kind") if isinstance(payload, dict) else None
        ev = payload.get("event") if isinstance(payload, dict) else None
        evk = ev.get("kind") if isinstance(ev, dict) else None
        for want in ("metadata", "run_model"):
            if kind == want and want not in shown:
                shown.add(want)
                print(want, shorten(payload, 600))
        if evk == "started" and "started" not in shown:
            shown.add("started")
            print("started keys:", sorted(ev.keys()) if isinstance(ev, dict) else type(ev))
            print("started:", shorten({k: ev.get(k) for k in list(ev)[:12]} if isinstance(ev, dict) else ev, 700))
        if evk == "assistant_tool_calls_committed" and "calls" not in shown:
            shown.add("calls")
            print("calls ev keys:", sorted(ev.keys()))
            print("calls ev:", shorten(ev, 700))
        # find usage dicts anywhere
        def find_usage(x, path=""):
            if isinstance(x, dict):
                if "usage_id" in x and "usage" in str(x.get("kind", "")):
                    pass
                for k, v in x.items():
                    if k == "usage" and isinstance(v, dict) and "usage-dict" not in shown:
                        shown.add("usage-dict")
                        print("usage at", path + "/" + k, "in evk", evk, "payloadkind", kind, ":", shorten(v, 400))
                        print("  sibling keys:", sorted(x.keys())[:20])
                    find_usage(v, path + "/" + k)
            elif isinstance(x, list):
                for i, v in enumerate(x[:8]): find_usage(v, path + f"[{i}]")
        find_usage(o)
        if "ts" not in shown and "recorded_at" in o:
            shown.add("ts")
            print("recorded_at sample:", o.get("recorded_at"), type(o.get("recorded_at")).__name__)
    print("shown:", sorted(shown))
