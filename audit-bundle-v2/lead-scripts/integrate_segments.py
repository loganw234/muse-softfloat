import re, shutil, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SEG = ROOT / "video" / "segments"
SEG.mkdir(parents=True, exist_ok=True)

copies = [
 ("scratch/study-video-intro/render_v3.py", "intro_outro.py"),
 ("scratch/study-video-why/render_why.py", "render_why.py"),
 ("scratch/study-video-idea/render_idea2.py", "idea.py"),
 ("scratch/study-video-why/render_why3.py", "why.py"),
 ("scratch/study-video-gitvisual/render_gitvisual5.py", "gitvisual.py"),
 ("scratch/study-video-gitvisual/history.json", "history.json"),
 ("scratch/study-video-gitvisual/gate2_numbers.json", "gate2_numbers.json"),
 ("scratch/study-kissfft-visual/spectrum_n256.json", "spectrum_n256.json"),
 ("scratch/study-kissfft-visual/input_n256.json", "input_n256.json"),
 ("scratch/study-kissfft-visual/twiddles_n256.json", "twiddles_n256.json"),
]
for src, dst in copies:
    s = ROOT / src
    if not s.exists():
        print("MISSING", src); sys.exit(1)
    shutil.copyfile(s, SEG / dst)
    print("copied", dst)

def patch(fname, pairs):
    p = SEG / fname
    t = p.read_text(encoding="utf-8")
    for old, new in pairs:
        assert t.count(old) == 1, (fname, old, t.count(old))
        t = t.replace(old, new)
    p.write_text(t, encoding="utf-8")
    print("patched", fname)

patch("idea.py", [
 ('WHY = HERE.parent / "study-video-why"', 'WHY = HERE  # production: base lib lives beside this file'),
])
patch("gitvisual.py", [
 ('ROOT / "scratch/study-kissfft-visual/spectrum_n256.json"', 'HERE / "spectrum_n256.json"'),
 ('ROOT / "scratch/study-kissfft-visual/input_n256.json"', 'HERE / "input_n256.json"'),
])
# heads-up: any other scratch references left in copied scripts?
for f in SEG.glob("*.py"):
    for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        if "scratch" in line and not line.strip().startswith("#"):
            print("LEFTOVER", f.name, i, line.strip()[:140])
print("done")
