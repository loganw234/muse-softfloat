import subprocess
d=subprocess.run(["git","-c","safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f32","-C","worktrees/w1-f32","show","HEAD:tables/implemented.tsv"],capture_output=True).stdout
print("blob len",len(d),"CRLF",d.count(b"\r\n"),"LF",d.count(b"\n"))
for f in ["src/msf32.c","docs/COVERAGE.tsv","tables/operations.tsv"]:
    d=subprocess.run(["git","-c","safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w1-f32","-C","worktrees/w1-f32","show",f"HEAD:{f}"],capture_output=True).stdout
    print(f, len(d), "CRLF", d.count(b"\r\n"), "LF", d.count(b"\n"))
import pathlib
for f in ["src/msf32.c","tables/implemented.tsv"]:
    d=pathlib.Path("worktrees/w1-f32",f).read_bytes()
    print("work",f,len(d),"CRLF",d.count(b"\r\n"),"LF",d.count(b"\n"))
