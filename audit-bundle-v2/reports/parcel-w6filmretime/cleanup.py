from pathlib import Path
W = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-filmretime\video\segments")
# idea: drop the stray empty-list marker lines
p = W / "idea.py"; s = p.read_text(encoding="utf-8")
lines = s.splitlines(keepends=True)
out = []
i = 0
while i < len(lines):
    if lines[i].strip() == "_BLOCKS_END = [" and lines[i+1].strip() == "]":
        i += 2
        continue
    out.append(lines[i]); i += 1
assert "_BLOCKS_END" not in "".join(out)
p.write_text("".join(out), encoding="utf-8", newline="")
# why: restore two blank lines before def main
p = W / "why.py"; s = p.read_text(encoding="utf-8")
s = s.replace("    return img\n\ndef main()", "    return img\n\n\ndef main()")
p.write_text(s, encoding="utf-8", newline="")
# gitvisual: stale numeric comments on the moved timeline
p = W / "gitvisual.py"; s = p.read_text(encoding="utf-8")
rep = [
 ("interval epilogue gate, gate ranks [44, 69, 140], TOTAL 102.0 s,",
  "interval epilogue gate, gate ranks [44, 69, 140], TOTAL 108.0 s (wave6 dwell),"),
 ("T_BRIDGE = ARRIVALS[-1] + POPUP_DWELL[-1]          # 42.5 (v4: 28.6)",
  "T_BRIDGE = ARRIVALS[-1] + POPUP_DWELL[-1]          # 46.0 wave6 (v5: 42.5)"),
 ("T_REPLAY = math.ceil((T_BRIDGE + 2.4) * 2.0) / 2.0  # 45.0 (v4: 31.0)",
  "T_REPLAY = math.ceil((T_BRIDGE + 2.4) * 2.0) / 2.0  # 48.5 wave6 (v5: 45.0)"),
 ("SHIFT = T_REPLAY - 31.0                             # 14.0",
  "SHIFT = T_REPLAY - 31.0                             # 17.5 wave6 (v5: 14.0)"),
]
for a, b in rep:
    assert a in s, a
    s = s.replace(a, b)
p.write_text(s, encoding="utf-8", newline="")
print("cleaned")
