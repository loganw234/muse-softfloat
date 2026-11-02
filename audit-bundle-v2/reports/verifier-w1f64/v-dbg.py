import sys
sys.path.insert(0, "scratch/verifier-w1f64")
src = open("scratch/verifier-w1f64/v-exact.py").read()
src = src.split("def rnorm64")[0]
exec(src)
print("case1 %x %02x" % ref_scaleb(0x3FE0000000000000, 0x4330000000000000, "tz"))
print("case2 %x %02x" % ref_scaleb(0x3FF0000000000000, 0x4330000000000000, "tz"))
print("case3 %x %02x" % ref_scaleb(0x7FF8000000000000, 0x7FF0000000000001, "te"))
dx = decode(0x3FE0000000000000)
print("dec x sign=%d cls=%s val=%s" % (dx["sign"], dx["cls"], dx["val"]))
dn = decode(0x4330000000000000)
print("dec n sign=%d cls=%s val=%s" % (dn["sign"], dn["cls"], dn["val"]))
