import datetime, hashlib, json, subprocess, sys
from pathlib import Path

BASE = "101b4aa98fc9f53005778fb424197d7ec7d26c82"
TIP = "1cfed360d2a456199810a605bcdb078fa731af19"
MSG_SRC = "77ad6ab"
REPO = Path("muse-softfloat")
WT = Path("worktrees/verify6-filmretime")
DRAFT = Path("scratch/lead/keys/w6-filmretime-draft.json")

def run(*args, cwd=None, inp=None):
    p = subprocess.run(args, cwd=cwd, input=inp, capture_output=True)
    if p.returncode != 0:
        sys.exit(f"FAIL {' '.join(args)}: {p.stderr.decode(errors='replace')[:500]}")
    return p.stdout

# prior-key sanity: final key file hashes to the committed plant_keys line
prior = Path("scratch/lead/keys/key-ee0c8b9.json").read_bytes()
h = hashlib.sha256(prior).hexdigest()
assert h == "4dcf5c2af438bbdb36a859747d2038a351dc27d2449838c288877efa9e4ba6bd", h
print("prior key-hash convention confirmed")

# no deletions/renames between base and tip (squash via checkout is exact)
ns = run("git", "-C", str(REPO), "diff", "--name-status", BASE, TIP).decode()
bad = [l for l in ns.splitlines() if not l.startswith(("M\t", "A\t"))]
assert not bad, bad
print("name-status clean:", len(ns.splitlines()), "files")

if WT.exists():
    sys.exit(f"{WT} already exists")
run("git", "-C", str(REPO), "worktree", "add", "--detach", str(WT.resolve()), BASE)
run("git", "-C", str(WT), "checkout", TIP, "--", ".")

key = json.loads(DRAFT.read_text(encoding="utf-8"))
assert key["real_tip"] == TIP
for pl in key["plants"]:
    p = WT / pl["file"]
    data = p.read_bytes()
    old, new = pl["old"].encode(), pl["new"].encode()
    assert data.count(old) == 1, (pl["file"], data.count(old))
    p.write_bytes(data.replace(old, new))
    print("planted:", pl["file"], "-", pl["shape"])

msg = run("git", "-C", str(REPO), "log", "-1", "--format=%B", MSG_SRC)
msgfile = Path("scratch/lead/copy_w6filmretime_msg.txt")
msgfile.write_bytes(msg)
run("git", "-C", str(WT), "add", "-A")
st = run("git", "-C", str(WT), "status", "--porcelain").decode()
print("staged files:", len(st.splitlines()))
run("git", "-C", str(WT), "commit", "-F", str(msgfile.resolve()))
copy = run("git", "-C", str(WT), "rev-parse", "HEAD").decode().strip()
parent = run("git", "-C", str(WT), "rev-parse", "HEAD^").decode().strip()
assert parent == BASE, parent
print("copy commit:", copy)

final = {"real_tip": TIP, "copy_commit": copy, "plants": key["plants"]}
out = Path(f"scratch/lead/keys/key-{copy[:7]}.json")
out.write_text(json.dumps(final, indent=2) + "\n", encoding="utf-8")
kh = hashlib.sha256(out.read_bytes()).hexdigest()
today = datetime.date.today().isoformat()
line = f"{kh}  w6-filmretime (verifier-w6filmretime, copy {copy[:7]}, base {BASE[:7]}, {today})"
Path("scratch/lead/copy_w6filmretime_keyline.txt").write_text(line + "\n", encoding="utf-8")
print("key file:", out)
print("plant_keys line:", line)
