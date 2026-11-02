import pathlib, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
lines=pathlib.Path("scratch/S1/extract/combined.txt").read_text(encoding="utf-8",errors="ignore").splitlines()
a=int(sys.argv[1]); b=int(sys.argv[2])
for i in range(a-1,b):
    print(i+1, lines[i])
