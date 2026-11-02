"""Probe2: timing freeze - import copy's gitvisual and parent's (from own git history)."""
import importlib.util, json, subprocess, sys
from pathlib import Path

DUP = Path(sys.argv[1]).resolve()
SEG = DUP / "video/segments"
sys.path.insert(0, str(DUP / "video"))
import style  # noqa: F401  (preload so both modules share)
import data  # noqa: F401
import scenes  # noqa: F401

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

gv_copy = load("gv_copy", SEG / "gitvisual.py")

# parent's file from the copy's own git history (allowed source)
parent_src = subprocess.run(
    ["git", "-C", str(DUP), "show", "f01dc96:video/segments/gitvisual.py"],
    capture_output=True, text=True, check=True).stdout
pdir = Path(sys.argv[2]).resolve() / "parent_seg"
pdir.mkdir(parents=True, exist_ok=True)
(pdir / "gitvisual_parent.py").write_text(parent_src, encoding="utf-8")
for f in ["history.json", "spectrum_n256.json", "input_n256.json",
          "augint_sample.json", "process_graph.json"]:
    (pdir / f).write_bytes((SEG / f).read_bytes())
gv_base = load("gv_base", pdir / "gitvisual_parent.py")

KEYS = ["POPUP_WORDS", "POPUP_DWELL", "ARRIVALS", "T_BRIDGE", "T_REPLAY",
        "SHIFT", "GATES", "LEGS", "TOTAL"]
dump = {}
for k in KEYS:
    c = getattr(gv_copy, k)
    b = getattr(gv_base, k)
    if k == "GATES":
        cf = [(g["id"], g["rank"], g["t0"], g["t1"]) for g in c]
        bf = [(g["id"], g["rank"], g["t0"], g["t1"]) for g in b]
        same = (cf == bf)
    else:
        cf, bf, same = c, b, (c == b)
    dump[k] = {"copy": cf, "base": bf, "same": same}
    print(f"--- {k} same={same}")
    print(f"  copy: {cf}")
    print(f"  base: {bf}")
print("POPUP5 copy:", json.dumps(gv_copy.POPUP5))
print("POPUP5 base:", json.dumps(gv_base.POPUP5))
print("ALL_SAME:", all(v["same"] for v in dump.values()))

# cursor: exactly on each gate rank at its t0; monotonic over [0, TOTAL]
print("--- cursor checks (copy module) ---")
ok = True
for g in gv_copy.GATES:
    r = gv_copy.cursor_rank(g["t0"])
    good = (r == g["rank"])
    ok &= good
    print(f"gate {g['id']}: rank={g['rank']} t0={g['t0']} cursor(t0)={r} {'OK' if good else 'HOLD-MISMATCH'}")
ts = [i * 0.5 for i in range(int(gv_copy.TOTAL * 2) + 1)]
rs = [gv_copy.cursor_rank(t) for t in ts]
mono = all(b >= a for a, b in zip(rs, rs[1:]))
print("monotonic:", mono, "min:", min(rs), "max:", max(rs))
ok &= mono
print("CURSOR_OK:", ok)
