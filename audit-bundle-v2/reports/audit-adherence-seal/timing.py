"""Timing: key-hash commit vs copy vs verifier session start vs merge/landing.
Run: MSF_PYTHON timing.py
"""
import json, subprocess, os

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "muse-softfloat")

def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                          capture_output=True, text=True).stdout.strip()

KEYS = {
 "polish-stale1": ("fa8a27a", "c558fb5", "f766e0f", "50aac59"),
 "w6-augint": ("2221ace", "9010f60", "47a405f", "537b08e"),
 "w6-ci": ("3cec27c", "9010f60", "6675fec", "537b08e"),
 "w6-examples": ("4bed622", "03f18a8", "b85e037", "af36464"),
 "w6-sanitize": ("549832e", "03f18a8", "4486cb5", "af36464"),
 "w6-judgemap": ("ee0c8b9", "7752e58", "870b82f", "97e10a4"),
 "w6-filmretime": ("a1e83d9", "98c58db", "3dfa3d8", "8ce5f27"),
 "w6-popups": ("8507695", "06808c9", "f36e171", "8fe10da"),
 "w6-captions": ("c537e0d", "a2241fc", "5b9fff3", "751d1d6"),
 "w6-metrics": ("fe04000", "a2241fc", "47f5ea7", "751d1d6"),
}

# usage.jsonl: verifier session start times at HEAD
usage = {}
with open(os.path.join(REPO, "docs", "metrics", "usage.jsonl"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        a = r.get("agent", "")
        if a.startswith("verifier-w6") or a.startswith("verifier-polish1"):
            usage.setdefault(a, []).append((r.get("started_at", r.get("start", "?")),
                                            r.get("ended_at", r.get("end", "?")),
                                            r.get("model", "?")))

print(f"{'parcel':14} {'copy_time':22} {'keycommit_time':22} {'session_start':22} {'merge_time':22} {'grade_land':22}")
for name, (copy, keyc, merge, land) in KEYS.items():
    ct = git("log", "-1", "--format=%ci %h %s", copy)
    kt = git("log", "-1", "--format=%ci %h", keyc)
    mt = git("log", "-1", "--format=%ci", merge)
    lt = git("log", "-1", "--format=%ci", land)
    print(f"{name:14} {ct[:22]:22} {kt[:22]:22} ...")
    for agent, rows in sorted(usage.items()):
        if name.replace("w6-", "w6").replace("-", "") in agent.replace("-", "") or \
           ("polish1" in name and "polish1" in agent) or \
           (name.split("-", 1)[1] in agent):
            for s, e, m in rows:
                print(f"    usage {agent}: start={s} end={e} model={m}")
print("\n--- key commit precedes copy? (want copy created, THEN hash committed, THEN dispatch) ---")
for name, (copy, keyc, merge, land) in KEYS.items():
    ct = git("log", "-1", "--format=%ct", copy)
    kt = git("log", "-1", "--format=%ct", keyc)
    print(f"{name:14} copy={ct} keycommit={kt} key_after_copy={kt >= ct}")
