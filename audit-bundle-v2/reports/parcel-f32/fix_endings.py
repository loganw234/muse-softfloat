import pathlib
p=pathlib.Path("worktrees/w1-f32/tables/implemented.tsv")
d=p.read_bytes()
orig_len=1718
head, tail = d[:orig_len], d[orig_len:]
assert b"\r" not in tail
tail2=tail.replace(b"\n", b"\r\n")
p.write_bytes(head+tail2)
d=p.read_bytes()
print("len",len(d),"CRLF",d.count(b"\r\n"),"LF",d.count(b"\n"))
