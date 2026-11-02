import sys
for p in sys.argv[1:]:
    d = open(p, "rb").read()
    print(p, len(d), "CR=", d.count(b"\r"))
