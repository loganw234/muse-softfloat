import datetime, hashlib, json, subprocess, sys
from pathlib import Path

REPO = Path("muse-softfloat")
BASE = "cdc40aec9b11eeab61ab3c6cc9940b5dbbac4a67"
JOBS = [
    ("w6-captions", "verifier-w6captions", "wave6-captions",
     "worktrees/verify6-captions", "scratch/lead/keys/w6-captions-draft.json"),
    ("w6-metrics", "verifier-w6metrics", "wave6-metrics",
     "worktrees/verify6-metrics", "scratch/lead/keys/w6-metrics-draft.json"),
]

def run(*args):
    p = subprocess.run(args, capture_output=True)
    if p.returncode != 0:
        sys.exit(f"FAIL {' '.join(args)}: {p.stderr.decode(errors='replace')[:500]}")
    return p.stdout

lines = []
for name, verifier, branch, wt_s, draft_s in JOBS:
    WT = Path(wt_s)
    key = json.loads(Path(draft_s).read_text(encoding="utf-8"))
    TIP = run("git", "-C", str(REPO), "rev-parse", branch).decode().strip()
    assert key["real_tip"] == TIP, (name, TIP)
    ns = run("git", "-C", str(REPO), "diff", "--name-status", BASE, TIP).decode()
    bad = [l for l in ns.splitlines() if not l.startswith(("M\t", "A\t"))]
    assert not bad, (name, bad)
    if WT.exists():
        sys.exit(f"{WT} exists")
    run("git", "-C", str(REPO), "worktree", "add", "--detach", str(WT.resolve()), BASE)
    run("git", "-C", str(WT), "checkout", TIP, "--", ".")
    for pl in key["plants"]:
        p = WT / pl["file"]
        data = p.read_bytes()
        old, new = pl["old"].encode(), pl["new"].encode()
        assert data.count(old) == 1, (name, pl["file"], data.count(old))
        p.write_bytes(data.replace(old, new))
        print(name, "planted:", pl["shape"])
    msg = run("git", "-C", str(REPO), "log", "-1", "--format=%B", TIP)
    msgfile = Path(f"scratch/lead/copy_{name}_msg.txt")
    msgfile.write_bytes(msg)
    run("git", "-C", str(WT), "add", "-A")
    run("git", "-C", str(WT), "commit", "-F", str(msgfile.resolve()))
    copy = run("git", "-C", str(WT), "rev-parse", "HEAD").decode().strip()
    assert run("git", "-C", str(WT), "rev-parse", "HEAD^").decode().strip() == BASE
    final = {"real_tip": TIP, "copy_commit": copy, "plants": key["plants"]}
    out = Path(f"scratch/lead/keys/key-{copy[:7]}.json")
    out.write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
    kh = hashlib.sha256(out.read_bytes()).hexdigest()
    line = (f"{kh}  {name} ({verifier}, copy {copy[:7]}, base {BASE[:7]}, "
            f"{datetime.date.today().isoformat()})")
    lines.append(line)
    print(name, "copy:", copy)
    print(name, "plant_keys line:", line)

Path("scratch/lead/copy_seal_keylines.txt").write_text(
    "\n".join(lines) + "\n", encoding="utf-8")
print("keylines written:", len(lines))
