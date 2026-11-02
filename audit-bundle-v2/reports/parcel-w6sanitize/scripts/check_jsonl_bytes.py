path = r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w6-sanitize\docs\metrics\briefs.jsonl"
d = open(path, "rb").read()
print(len(d), "CR", d.count(b"\r"), "LF", d.count(b"\n"), "CRLF", d.count(b"\r\n"), "tail", repr(d[-30:]))
