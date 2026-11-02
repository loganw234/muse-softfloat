from pathlib import Path
p = Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-filmretime\video\segments\idea.py")
data = p.read_bytes()
norm = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
p.write_bytes(norm)
print("crlf lines:", norm.count(b"\r\n"))
