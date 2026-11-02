"""Independent recounts at HEAD: plants grades, key-hash match, passes/usage/
briefs/escalations shapes, merges/parcels/verifiers/studies counts,
tokens arithmetic, captions/stills artefacts.
Run: MSF_PYTHON claims.py
"""
import json, subprocess, os
from collections import Counter

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "muse-softfloat")
WS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")

def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                          capture_output=True, text=True).stdout.strip()

def load(name):
    rows = []
    with open(os.path.join(REPO, "docs", "metrics", name), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

plants = load("plants.jsonl")
grades = Counter(r.get("grade") for r in plants)
print(f"plants rows={len(plants)} grades={dict(grades)} "
      f"caught={grades.get('caught',0)}/{len(plants)}")
print("  by wave:", dict(Counter((r.get("wave"), r.get("grade")) for r in plants)))

# key hashes in plants rows vs plant_keys.sha256
keylines = {}
with open(os.path.join(REPO, "docs", "metrics", "plant_keys.sha256"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            h, rest = line.split("  ", 1)
            keylines.setdefault(h, rest)
mismatch = 0
for r in plants:
    kh = r.get("key_sha256", "")
    if kh and kh not in keylines:
        mismatch += 1
        print(f"  KEY MISMATCH: {r.get('verifier')} plant {r.get('plant')} {kh[:12]}")
print(f"plants rows with key not in plant_keys.sha256: {mismatch}")
print(f"plant_keys entries: {len(keylines)}")

passes = load("passes.jsonl")
usage = load("usage.jsonl")
briefs = load("briefs.jsonl")
escs = load("escalations.jsonl")
print(f"\npasses={len(passes)} usage={len(usage)} briefs={len(briefs)} escalations={len(escs)}")
nosb = [i for i, r in enumerate(passes) if "sent_back" not in r]
print(f"passes rows missing sent_back: {len(nosb)} (first idx {nosb[:5]})")
print("passes sent_back values:", dict(Counter(r.get("sent_back", "<MISSING>") for r in passes)))
print("escalations waves:", dict(Counter(r.get("wave") for r in escs)))

# tokens arithmetic: frozen 1196128770 + appended at cdc40ae cutoff
tot_in = sum(r.get("input_tokens", 0) for r in usage)
tot_out = sum(r.get("output_tokens", 0) for r in usage)
tot_cached = sum(r.get("cached_tokens", 0) for r in usage)
print(f"\nusage sums: in={tot_in} out={tot_out} cached={tot_cached} billed~{tot_in+tot_out}")
print("merge-claimed refreshed billed total: 1418065198 (frozen 1196128770 + appended 221936428)")

# merges to main (first-parent merges over whole history)
merges = git("log", "--format=%h", "--first-parent", "--merges").split()
print(f"\nfirst-parent merges on main: {len(merges)}")
allmerges = git("log", "--format=%h", "--merges").split()
print(f"all merges reachable: {len(allmerges)}")

# ledger counts (workspace ledger, excluding fenced lead.md)
import glob
parcels = [p for p in glob.glob(os.path.join(WS, "ledger", "parcel-*.md"))]
verifs = [p for p in glob.glob(os.path.join(WS, "ledger", "verifier-*.md"))]
studies = [p for p in glob.glob(os.path.join(WS, "ledger", "study-*.md"))]
print(f"ledger parcel files: {len(parcels)}")
print(f"ledger verifier files: {len(verifs)}")
print(f"ledger study files: {len(studies)}")

# captions artefacts
srt = os.path.join(REPO, "video", "out", "assembly_v6.srt")
with open(srt, encoding="utf-8") as f:
    cues = [l for l in f.read().split("\n\n") if l.strip()]
print(f"\nsrt cue blocks: {len(cues)}")
stills = glob.glob(os.path.join(REPO, "video", "out", "stills_v6", "*"))
print(f"stills_v6 files: {len(stills)}")
