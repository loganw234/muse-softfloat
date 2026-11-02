import pathlib
p = pathlib.Path(r"C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w3-str\tests\gen_vectors_str.py")
data = p.read_bytes()
a = b'path.write_text("".join(line + "\\n" for line in lines), encoding="utf-8")'
b = b'path.write_bytes("".join(line + "\\n" for line in lines).encode("utf-8"))'
assert data.count(a) == 1, data.count(a)
data = data.replace(a, b)
c = b'Path(outfile).write_text("".join(l + "\\n" for l in lines), encoding="utf-8")'
d = b'Path(outfile).write_bytes("".join(l + "\\n" for l in lines).encode("utf-8"))'
assert data.count(c) == 2, data.count(c)
data = data.replace(c, d)
p.write_bytes(data)
print("LF-safe writes:", data.count(b"write_bytes"))
