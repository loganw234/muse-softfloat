import re
from pathlib import Path
p = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-filmretime\video\segments\why.py")
s = p.read_text(encoding="utf-8")
orig = s
# delete scene_title entirely
s2, n = re.subn(r"def scene_title\(d, t\):.*?(?=\r?\ndef scene_workloads)", "", s, flags=re.S)
assert n == 1, n
s = s2
# replace frame()
new_frame = '''def frame(t: float) -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    if t < O_SPEC:
        return img
    if t < O_O1:
        scene_spec(d, 8.0 + (t - O_SPEC))
    elif t < O_O2:
        scene_opt1(d, 13.5 + (t - O_O1))
    elif t < O_O3:
        scene_opt2(d, 18.5 + (t - O_O2))
    elif t < O_SETTLE:
        scene_opt3(d, 24.0 + (t - O_O3))
    else:
        scene_settle(d, 28.0 + (t - O_SETTLE))
    if t >= FADE_T:
        a = S.ease_in_out(min(1.0, (t - FADE_T) / 0.25))
        img = Image.blend(img, Image.new("RGB", (W, H), WHITE), a)
    return img
'''
s2, n = re.subn(r"def frame\(t: float\) -> Image\.Image:.*?(?=\r?\ndef main)", new_frame, s, flags=re.S)
assert n == 1, n
s = s2
s2, n = re.subn(r"first_white = int\(\(FADE_T - SHIFT \+ 0\.25\) \* FPS\) \+ 1",
                "first_white = int((FADE_T + 0.25) * FPS) + 1", s)
assert n == 1, n
s = s2
assert "SHIFT" not in s, [l for l in s.splitlines() if "SHIFT" in l]
assert "scene_title" not in s and "T_H" not in s and "T_SUB" not in s
p.write_text(s, encoding="utf-8", newline="")
print("patched why, bytes", len(orig), "->", len(s))
