import hashlib, json, os, sys
path = sys.argv[1]
before = open(path, "rb").read()
print(f"before bytes={len(before)} sha256={hashlib.sha256(before).hexdigest()}")
row = {
    "wave": "wave6",
    "work": "Wave 6 queue item 5 (first parcel): judge's Start here map in README.md (watch the 169 s silent v5 film, live WASM site, examples/host/build.sh then tools/run.sh smoke with the four Linux CI jobs named, demo/run_demo.sh host with its stale interval expectation named, RECORD + audit-bundle walk with plants 138/145 counted from docs/metrics/plants.jsonl at this base) plus the Wave 6 sweep of the Status and where-things-live sections (augmented consumption, examples, sanitize fifth budget, Linux CI); every map number re-derived from the tree and every map command run in the worktree (sanitize full is CI-only), standard PASS",
    "author": "parcel-w6judgemap",
    "base": "af364643549b305abbaaa7fc428ae2b16b0e1afd",
    "time_box_min": 240,
    "ceiling_lines": 0,
    "ceiling_text": "no line ceiling stated in brief w6-judgemap.md; owned-files list is the bound (README.md, this row)",
}
line = (json.dumps(row, ensure_ascii=False) + "\n").encode("utf-8")
with open(path, "ab") as f:
    f.write(line)
after = open(path, "rb").read()
assert after[: len(before)] == before, "prefix changed!"
assert len(after) == len(before) + len(line)
rows = [json.loads(ln) for ln in after.decode("utf-8").splitlines() if ln.strip()]
print(f"after bytes={len(after)} sha256={hashlib.sha256(after).hexdigest()} rows={len(rows)} last_author={rows[-1]['author']} waves_wave6={sum(1 for r in rows if r.get('wave')=='wave6')}")
