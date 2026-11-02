"""counters.py - re-derive every README/site number from the tree.

Read-only against worktrees/w5-readme3. Explicit allowed paths only.
Prints a deterministic report; the bash wrapper tees it to
scratch/parcel-w5readme3/out/counters.txt.
"""
import collections
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[2]
WT = WS / "worktrees" / "w5-readme3"


def head(t):
    print(f"\n=== {t} ===")


head("git base")
out = subprocess.run(
    ["git", "-c", f"safe.directory={WT}", "-C", str(WT),
     "rev-parse", "HEAD", "--abbrev-ref", "HEAD"],
    capture_output=True, text=True)
print(out.stdout.strip())
out = subprocess.run(
    ["git", "-c", f"safe.directory={WT}", "-C", str(WT),
     "rev-parse", "--short", "HEAD"],
    capture_output=True, text=True)
print("short:", out.stdout.strip())

# --- COVERAGE.tsv (header-aware, mirrors run.sh inventory_check) ---
head("COVERAGE.tsv")
lines = (WT / "docs" / "COVERAGE.tsv").read_text(
    encoding="utf-8", errors="replace").splitlines()
hdr = None
rows = []
for ln in lines:
    if not ln or ln.startswith("#"):
        continue
    f = ln.split("\t")
    if hdr is None:
        hdr = f
        print("header:", f)
        continue
    rows.append(dict(zip(hdr, f)))
print("rows:", len(rows))
print("tier:", dict(collections.Counter(r["tier"] for r in rows)))
print("status:", dict(collections.Counter(r["status"] for r in rows)))
print("tier x status:", dict(collections.Counter(
    (r["tier"], r["status"]) for r in rows)))
print("claim:", dict(collections.Counter(r["claim"] for r in rows)))
t2 = [r for r in rows if r["tier"] == "2"]
print("tier2 by std_name:", dict(sorted(collections.Counter(
    r["std_name"] for r in t2).items())))
print("tier2 by clause:", dict(sorted(collections.Counter(
    r["clause"] for r in t2).items())))
print("rounding tokens (attr col):", dict(collections.Counter(
    r["rounding"] for r in rows)))
attr_rows = [r for r in rows if r["rounding"] == "attr"]
print("attr-carrying rows:", len(attr_rows))
fixed = [r for r in rows if r["rounding"] == "fixed"]
print("fixed rows:", len(fixed), [r["name"] for r in fixed])
aug_cov = [r["name"] for r in rows if "augmented" in r["name"]]
print("augmented coverage rows:", len(aug_cov), aug_cov)
explog_cov = [r["name"] for r in rows
              if any(k in r["name"] for k in ("exp2", "log2"))]
print("explog coverage rows:", len(explog_cov), explog_cov)

# --- dispatch census: old regex (build_data.py today) vs new ---
head("msf_dispatch.h MSF_OPS census")
text = (WT / "tests" / "msf_dispatch.h").read_text(
    encoding="utf-8", errors="replace")
i = text.find("static const msf_op_desc_t MSF_OPS[]")
j = text.find("};", i)
body = text[i:j]
old_pat = re.compile(
    r'\{\s*"([^"]+)",\s*"([^"]+)",\s*(MSF_SIG_\w+),\s*(MSF_RK_\w+),'
    r'\s*\{\s*(MSF_AK_\w+),\s*(MSF_AK_\w+),\s*(MSF_AK_\w+)\s*\},'
    r'\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\w+)\s*\}')
new_pat = re.compile(
    r'\{\s*"([^"]+)",\s*"([^"]+)",\s*(MSF_SIG_\w+),\s*(MSF_RK_\w+),'
    r'\s*\{\s*(MSF_AK_\w+),\s*(MSF_AK_\w+),\s*(MSF_AK_\w+)\s*\},'
    r'\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\w+),'
    r'\s*(\w+)\s*\}')
old_hits = list(old_pat.finditer(body))
new_hits = list(new_pat.finditer(body))
print(f"old-regex hits: {len(old_hits)} (build_data.py as committed)")
print(f"new-regex hits (with pair_call): {len(new_hits)}")
single = pair = dead = 0
sig_counter = collections.Counter()
pair_names = []
dead_names = []
for m in new_hits:
    sig = m.group(3)
    call, pcall = m.group(13), m.group(14)
    sig_counter[sig] += 1
    if call != "0" and pcall == "0":
        single += 1
    elif call == "0" and pcall != "0":
        pair += 1
        pair_names.append(m.group(1))
    elif call == "0" and pcall == "0":
        dead += 1
        dead_names.append((m.group(1), sig))
    else:
        print("UNEXPECTED both-call row:", m.group(1))
print(f"single-result runnable (call!=0): {single}")
print(f"aug pair (call==0, pair_call!=0): {pair} {pair_names}")
print(f"non-hex-drivable (call==0, pair_call==0): {dead}")
print("dead by sig:", dict(collections.Counter(s for _, s in dead_names)))
print("dead names:", [n for n, _ in dead_names])
print("AUG_PAIR sig count:", sig_counter.get("MSF_SIG_AUG_PAIR", 0))
explog_disp = [m.group(1) for m in new_hits
               if any(k in m.group(1) for k in ("exp2", "log2"))]
print("explog dispatch rows:", len(explog_disp), explog_disp)

# --- vectors: counted lines + shapes ---
head("tests/vectors counted lines")
total = 0
per_file = {}
shape = collections.Counter()
aug_lines = explog_lines = 0
by_op_lines = collections.Counter()
for p in sorted((WT / "tests" / "vectors").glob("*.vec")):
    n = 0
    for raw in p.read_text(encoding="utf-8", errors="replace").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        n += 1
        tok = s.split()
        by_op_lines[tok[0]] += 1
        if "augmented" in tok[0]:
            aug_lines += 1
            shape[("aug", len(tok))] += 1
        elif any(k in tok[0] for k in ("exp2", "log2")):
            explog_lines += 1
            shape[("explog", len(tok))] += 1
        else:
            shape[("other", len(tok))] += 1
    per_file[p.name] = n
    total += n
    print(f"{p.name}: {n}")
print("TOTAL counted vector lines:", total)
print("aug lines:", aug_lines, " explog lines:", explog_lines)
print("token-shape census:", dict(sorted(shape.items(), key=str)))
print("distinct ops in vectors:", len(by_op_lines))
# what old build_data would do with an aug line if called runnable:
demo = "msf32_augmented_add - 00000000 00000000 -> 11111111 22222222 18 prov".split()
arrow = demo.index("->")
print("aug-misparse demo (old sampler fields): args=", demo[2:arrow],
      "result=", demo[arrow + 1], "flags<-tail=", demo[arrow + 2],
      "prov<-flags=", demo[arrow + 3], " (real prov dropped:", demo[-1], ")")

# --- plants ---
head("docs/metrics/plants.jsonl")
plants = [json.loads(x) for x in (WT / "docs" / "metrics" / "plants.jsonl")
          .read_text(encoding="utf-8").splitlines() if x.strip()]
caught = sum(1 for p in plants if p.get("grade") == "caught")
print(f"plants: {caught} caught of {len(plants)}")
bw = {}
for p in plants:
    w = bw.setdefault(p["wave"], [0, 0])
    w[1] += 1
    if p.get("grade") == "caught":
        w[0] += 1
print("by wave:", bw)
print("grades:", dict(collections.Counter(p.get("grade") for p in plants)))

# --- current site data (stale baseline) ---
head("site/data.json + ops/sample as committed at base")
data = json.loads((WT / "site" / "data.json").read_text(encoding="utf-8"))
print(json.dumps(data, indent=1)[:1500])
ops = json.loads((WT / "site" / "ops.json").read_text(encoding="utf-8"))
print("ops.json entries:", len(ops),
      " runnable:", sum(1 for o in ops if o["runnable"]),
      " explog:", sum(1 for o in ops if "exp2" in o["name"] or "log2" in o["name"]),
      " aug:", sum(1 for o in ops if "augmented" in o["name"]))
sample = json.loads((WT / "site" / "vectors-sample.json").read_text(encoding="utf-8"))
print("vectors-sample entries:", len(sample),
      " ops covered:", len({s["op"] for s in sample}))
print("replay-log.txt:", (WT / "site" / "replay-log.txt").read_text(
    encoding="utf-8").strip())
wasm = WT / "site" / "msf.wasm"
h = hashlib.sha256(wasm.read_bytes()).hexdigest()
print(f"msf.wasm at base: {wasm.stat().st_size} bytes sha256 {h}")

# --- src inventories ---
head("src inventories: disk vs run.sh vs site/build.py")
disk = sorted(p.name for p in (WT / "src").glob("*.c"))
print("disk src/*.c:", disk)
runsh = (WT / "tools" / "run.sh").read_text(encoding="utf-8", errors="replace")
m = re.search(r'^SRC="([^"]+)"', runsh, re.M)
print("run.sh SRC:", m.group(1).split() if m else "NOT FOUND")
buildpy = (WT / "site" / "build.py").read_text(encoding="utf-8")
m = re.search(r'SRC\s*=\s*\[([^\]]+)\]', buildpy)
print("site/build.py SRC:", re.findall(r'"([^"]+)"', m.group(1)) if m else "NOT FOUND")

# --- README stale numbers ---
head("README.md numbers as committed at base")
rd = (WT / "README.md").read_text(encoding="utf-8")
for pat in [r"822[^.]*", r"171,423", r"61 of 65", r"39 Tier 2",
            r"783/783", r"255", r"2,001/2,001", r"12 configuration"]:
    for mm in re.finditer(pat, rd):
        print(repr(pat), "->", rd[max(0, mm.start() - 30):mm.end() + 30].replace("\n", " "))

# --- public header augmented API ---
head("include/muse_softfloat.h augmented API")
hdr_txt = (WT / "include" / "muse_softfloat.h").read_text(
    encoding="utf-8", errors="replace")
for mm in re.finditer(r".*augmented.*", hdr_txt):
    print(mm.group(0).strip()[:160])
for mm in re.finditer(r".*pair_t.*", hdr_txt):
    print(mm.group(0).strip()[:160])

# --- zig archive hash (reuse proof) ---
head("scratch WASM toolchain (Zig, per parcel-w5site recipe)")
z = WS / "scratch" / "parcel-w5site" / "zig-x86_64-windows-0.17.0.zip"
if z.exists():
    hh = hashlib.sha256()
    with open(z, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            hh.update(chunk)
    print(f"{z.name}: {z.stat().st_size} bytes sha256 {hh.hexdigest()}")
    print("recorded:       100268137 bytes sha256 "
          "b5663f69581dcf391293fbf16c06cb80d81d806545ce618b4d0bab7f0eb8c428")
else:
    print("zip ABSENT")
exe = WS / "scratch" / "parcel-w5site" / "zig-x86_64-windows-0.17.0" / "zig.exe"
print("zig.exe exists:", exe.exists())
print("emsdk dirs in parcel-w5site scratch:",
      [p.name for p in (WS / "scratch" / "parcel-w5site").iterdir()
       if "emsdk" in p.name.lower() or "emscripten" in p.name.lower()])
print("\nCOUNTERS DONE")
