import shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "video"
B = ROOT / "muse-softfloat" / "video"
items = [
 "assemble.py", "README.md", "STORYBOARD.md", "out/assembly_v5.mp4",
 "segments/gate2_numbers.json", "segments/gitvisual.py", "segments/gitvisual5.mp4",
 "segments/history.json", "segments/idea.py", "segments/idea2-1440p.mp4",
 "segments/input_n256.json", "segments/intro3.mp4", "segments/intro_msg3.txt",
 "segments/intro_outro.py", "segments/measurements3.json", "segments/outro3.mp4",
 "segments/outro_msg3.txt", "segments/render_why.py", "segments/spectrum_n256.json",
 "segments/still3_period_bubble.png", "segments/still3_period_midzoom.png",
 "segments/still3_period_proof.png", "segments/twiddles_n256.json",
 "segments/why.py", "segments/why3-1440p.mp4",
]
for rel in items:
    s, d = A / rel, B / rel
    assert s.exists(), rel
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(s, d)
    print("synced", rel)
print("kept repo versions: data.py, render.py, data/")
