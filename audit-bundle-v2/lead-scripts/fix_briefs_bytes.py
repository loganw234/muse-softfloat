import json
import pathlib
import subprocess
import sys

wt = pathlib.Path(sys.argv[1])
base = subprocess.check_output(
    ["git", "-C", str(wt), "show", "400b271:docs/metrics/briefs.jsonl"])
row = {
    "wave": "polish",
    "work": "Post-close stale-information cleanup from the Spark audit (site plant figures, README video master, BOARD link/clones, attribute count, path qualifications; frozen audit bundle untouched)",
    "author": "lead-polish1",
    "base": "400b27147518a1b9e704776c6df1f8150681a8e9",
    "time_box_min": 240,
    "ceiling_lines": 0,
    "ceiling_text": "brief ledger/briefs/polish-stale1.md owned-files list is the bound; regenerated site data/header excluded",
}
out = base
if not out.endswith(b"\n"):
    out += b"\n"
out += (json.dumps(row) + "\n").encode("utf-8")
target = wt / "docs/metrics/briefs.jsonl"
target.write_bytes(out)
check = target.read_bytes()
assert check[:len(base)] == base, "base bytes not preserved as prefix"
rows = [json.loads(x) for x in check.decode("utf-8").splitlines() if x.strip()]
print(f"briefs rows={len(rows)} base_bytes={len(base)} prefix_preserved=True")
assert rows[-1]["author"] == "lead-polish1"
