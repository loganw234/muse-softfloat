import ast

data = open("worktrees/w4-trig/tests/gen_vectors_trig.py", "rb").read()
print("nulls:", data.count(b"\x00"), "len:", len(data))
src = data.decode("utf-8")
ast.parse(src)
print("parse ok")
