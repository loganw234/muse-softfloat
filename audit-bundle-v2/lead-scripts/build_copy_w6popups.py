import datetime, hashlib, json, subprocess, sys
from pathlib import Path

BASE = "f01dc96055f24b4aa5450bdadabf44fa5308abb9"
REPO = Path("muse-softfloat")
WT = Path("worktrees/verify6-popups")
DRAFT = Path("scratch/lead/keys/w6-popups-draft.json")

def run(*args, cwd=None):
    p = subprocess.run(args, cwd=cwd, capture_output=True)
    if p.returncode != 0:
        sys.exit(f"FAIL {' '.join(args)}: {p.stderr.decode(errors='replace')[:500]}")
    return p.stdout

TIP = run("git", "-C", str(REPO), "rev-parse", "wave6-popups").decode().strip()
print("real tip:", TIP)

ns = run("git", "-C", str(REPO), "diff", "--name-status", BASE, TIP).decode()
bad = [l for l in ns.splitlines() if not l.startswith(("M\t", "A\t"))]
assert not bad, bad
print("name-status clean:", len(ns.splitlines()), "files")

if WT.exists():
    sys.exit(f"{WT} already exists")
run("git", "-C", str(REPO), "worktree", "add", "--detach", str(WT.resolve()), BASE)
run("git", "-C", str(WT), "checkout", TIP, "--", ".")

key = json.loads(DRAFT.read_text(encoding="utf-8"))
for pl in key["plants"]:
    p = WT / pl["file"]
    data = p.read_bytes()
    old, new = pl["old"].encode(), pl["new"].encode()
    assert data.count(old) == 1, (pl["file"], data.count(old))
    p.write_bytes(data.replace(old, new))
    print("planted:", pl["shape"])

msg = Path("scratch/lead/copy_w6popups_msg.txt")
run("git", "-C", str(WT), "add", "-A")
run("git", "-C", str(WT), "commit", "-F", str(msg.resolve()))
copy = run("git", "-C", str(WT), "rev-parse", "HEAD").decode().strip()
parent = run("git", "-C", str(WT), "rev-parse", "HEAD^").decode().strip()
assert parent == BASE, parent
print("copy commit:", copy)

final = {"real_tip": TIP, "copy_commit": copy, "plants": key["plants"]}
out = Path(f"scratch/lead/keys/key-{copy[:7]}.json")
out.write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
kh = hashlib.sha256(out.read_bytes()).hexdigest()
today = datetime.date.today().isoformat()
line = f"{kh}  w6-popups (verifier-w6popups, copy {copy[:7]}, base {BASE[:7]}, {today})"
Path("scratch/lead/copy_w6popups_keyline.txt").write_text(line + "\n", encoding="utf-8")
print("key file:", out)
print("plant_keys line:", line)
