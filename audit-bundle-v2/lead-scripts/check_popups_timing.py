import importlib.util, json, subprocess, sys
from pathlib import Path

SNIP = """
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("gv", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
out = {
 "POPUP_WORDS": m.POPUP_WORDS, "POPUP_DWELL": m.POPUP_DWELL,
 "ARRIVALS": m.ARRIVALS, "T_BRIDGE": m.T_BRIDGE, "T_REPLAY": m.T_REPLAY,
 "SHIFT": m.SHIFT, "TOTAL": m.TOTAL, "T_BOX": m.T_BOX, "T_FADE": m.T_FADE,
 "GATES": [(g["id"], g["rank"], g["t0"], g["t1"]) for g in m.GATES],
 "LEGS": [list(x) for x in m.LEGS],
 "cursor_at_gates": [m.cursor_rank(g["t0"]) for g in m.GATES],
 "POPUP5": [[t, lines] for t, lines in m.POPUP5],
}
print(json.dumps(out))
"""
Path("scratch/lead/_gv_dump.py").write_text(SNIP, encoding="utf-8")

def dump(path):
    p = subprocess.run([sys.executable, "scratch/lead/_gv_dump.py", path],
                       capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"import fail {path}: {p.stderr[-500:]}")
    return json.loads(p.stdout.strip().splitlines()[-1])

base = dump("muse-softfloat/video/segments/gitvisual.py")
tip = dump("worktrees/w6-popups/video/segments/gitvisual.py")
for k in base:
    same = base[k] == tip[k]
    print(f"{k}: {'SAME' if same else 'DIFF'}")
    if not same and k != "POPUP5":
        print("  base:", base[k]); print("  tip :", tip[k])
print("tip POPUP5:")
for t, lines in tip["POPUP5"]:
    print(" ", t, "|", " / ".join(lines))
