from pathlib import Path
p = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-filmretime\video\segments\intro_outro.py")
s = p.read_text(encoding="utf-8")
marker = '(HERE / "measurements3.json").write_text(json.dumps(meas, indent=1))'
i = s.index(marker) + len(marker)
tail = chr(10) + '    nl = chr(10)' + chr(10)
tail += '    (HERE / "intro_msg3.txt").write_text(INTRO_MSG + nl)' + chr(10)
tail += '    (HERE / "outro_msg3.txt").write_text(REPLY_1 + nl + nl + REPLY_2 + nl)' + chr(10)
tail += '    print("done")' + chr(10)
p.write_text(s[:i] + tail, encoding="utf-8", newline="")
print("fixed tail")
