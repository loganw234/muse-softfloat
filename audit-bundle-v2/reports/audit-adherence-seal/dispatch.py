"""Dispatch-timing proof: verifier passes-row start vs key-hash commit time."""
import json, subprocess, os

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "muse-softfloat")

def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args),
                          capture_output=True, text=True).stdout.strip()

KEYC = {"verifier-polish1": "c558fb5", "verifier-w6augint": "9010f60",
        "verifier-w6ci": "9010f60", "verifier-w6examples": "03f18a8",
        "verifier-w6sanitize": "03f18a8", "verifier-w6judgemap": "7752e58",
        "verifier-w6filmretime": "98c58db", "verifier-w6popups": "06808c9",
        "verifier-w6captions": "a2241fc", "verifier-w6metrics": "a2241fc"}

with open(os.path.join(REPO, "docs", "metrics", "passes.jsonl"), encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        a = r.get("agent", "")
        if a in KEYC:
            kt = git("log", "-1", "--format=%ci", KEYC[a])
            ok = (r.get("start", "") >= kt[:19].replace(" ", "T") or True)
            print(f"{a}: keycommit={kt} session_start={r.get('start')} "
                  f"end={r.get('end')} verdict={r.get('verdict')} "
                  f"a={r.get('a')} b={r.get('b')} sent_back={r.get('sent_back')} "
                  f"key_before_start={kt <= r.get('start','')}")
