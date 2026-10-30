import json, pathlib, collections, re

sess = pathlib.Path(r"C:\Users\logan\.local\share\muse\sessions\2026\10\26\01a17907-4147-7333-a565-56071da9d971")
files = [sess / "session.jsonl"] + sorted((sess / "subagent").glob("*/session.jsonl"))
print("files:", len(files))
for p in files[:3]:
    print(p.name if p.name != "session.jsonl" else "MAIN", p.parent.name, p.stat().st_size)

def walk(obj, prefix, keys, depth=0):
    if depth > 6: return
    if isinstance(obj, dict):
        for k, v in obj.items():
            keys[prefix + "/" + k] += 1
            walk(v, prefix + "/" + k, keys, depth + 1)
    elif isinstance(obj, list):
        for v in obj[:3]:
            walk(v, prefix + "[]", keys, depth + 1)

for p in files[:2] + files[-1:]:
    kinds = collections.Counter()
    payload_kinds = collections.Counter()
    top = collections.Counter()
    tokenish = collections.Counter()
    keypaths = collections.Counter()
    n = 0
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            o = json.loads(line)
        except Exception:
            continue
        n += 1
        if isinstance(o, dict):
            top.update(o.keys())
            payload = o.get("payload", o)
            if isinstance(payload, dict):
                payload_kinds[str(payload.get("kind"))] += 1
                ev = payload.get("event")
                if isinstance(ev, dict):
                    kinds[str(ev.get("kind"))] += 1
            walk(o, "", keypaths)
        # collect token-ish scalar keys/values
        def scan(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    lk = k.lower()
                    if any(s in lk for s in ("token", "model", "usage", "cost", "cache", "input", "output")):
                        tokenish[(k, type(v).__name__, str(v)[:40])] += 1
                    scan(v)
            elif isinstance(x, list):
                for v in x[:20]: scan(v)
        scan(o)
    print("\n==", p.parent.name, "lines", n)
    print("top keys:", dict(top.most_common(12)))
    print("payload kinds:", dict(payload_kinds.most_common(12)))
    print("event kinds:", dict(kinds.most_common(20)))
    print("tokenish (first 25):")
    for k, c in list(tokenish.items())[:25]:
        print("  ", c, k)
