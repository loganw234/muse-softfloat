import pathlib
t=pathlib.Path("worktrees/w1-f64/docs/studies/SF-0.md").read_text().splitlines()
# print sections 2,3,4,5,7 ranges by heading startswith
keep=False
for line in t:
    if line.startswith("## "):
        keep=line[3:].split(".")[0] in ("2","3","4","5","7")
    if keep:
        print(line)
