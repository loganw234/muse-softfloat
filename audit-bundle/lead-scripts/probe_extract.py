import json, pathlib, sys

seed = pathlib.Path("scratch/lead/seed-phase0.txt").read_bytes()
print("SEED first bytes:", repr(seed[:80]))
print("SEED first line:", repr(seed.split(b"\n",1)[0][:60]))

base = pathlib.Path(r"C:\Users\logan\.local\share\muse\sessions\2026\10\26\01a17907-4147-7333-a565-56071da9d971\subagent")
jobs = {
 "distill-parcelround-cases.md": "01a17926-8df6-7dc2-8de7-a179fbf2a499",
 "distill-honest.md": "01a17926-905e-7c63-9f6b-6040f0d6ba09",
 "distill-examples.md": "01a17926-92b9-78f0-a27b-f9f476a10eae",
 "distill-qro-round6.md": "01a17926-9485-75c2-b335-6e44f6afff07",
}

def strings(obj, out):
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values(): strings(v, out)
    elif isinstance(obj, list):
        for v in obj: strings(v, out)

outdir = pathlib.Path("reading-scratch"); outdir.mkdir(exist_ok=True)
for fname, sid in jobs.items():
    p = base / sid / "session.jsonl"
    texts = []
    keys = None
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        try: obj = json.loads(line)
        except Exception: continue
        if keys is None and isinstance(obj, dict): keys = sorted(obj.keys())
        s = []
        strings(obj, s)
        texts.extend(s)
    # the report is the longest string mentioning the closing section, else longest overall
    marked = [t for t in texts if "brief got wrong" in t and len(t) > 2000]
    cand = max(marked or texts, key=len) if texts else ""
    (outdir / fname).write_text(cand, encoding="utf-8")
    print(fname, "keys0=", keys, "texts=", len(texts), "picked_chars=", len(cand))
