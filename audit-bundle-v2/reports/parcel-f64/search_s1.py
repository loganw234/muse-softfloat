import pathlib, sys, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
terms=sys.argv[1:]
p=pathlib.Path("scratch/S1/extract/combined.txt")
lines=p.read_text(encoding="utf-8",errors="ignore").splitlines()
for term in terms:
    print("="*20, term)
    for i,l in enumerate(lines):
        if term.lower() in l.lower():
            start=max(0,i-3); end=min(len(lines),i+12)
            print(f"--- line {i+1}")
            for j in range(start,end):
                print(lines[j])
            print()
            # limit
    print()
