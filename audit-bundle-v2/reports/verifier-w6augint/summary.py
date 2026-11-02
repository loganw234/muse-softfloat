import sys

for tree, log in [("base", "base"), ("new", "new")]:
    p = f"scratch/verifier-w6augint/{tree}/b-hostrun/{log}.log"
    d = open(p, encoding="utf-16").read().splitlines()
    print("==", tree)
    for l in d:
        if l.startswith("SUMMARY") or l.startswith("HOST_SHA256"):
            print(l)
    print("rows:", sum(1 for l in d if l.startswith("RAY")))
