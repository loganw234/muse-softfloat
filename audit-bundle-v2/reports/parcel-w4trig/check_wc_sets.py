"""Set-equality: harness-parsed wc input bit patterns vs the
spike's independently extracted sets (float.fromhex route)."""
import sys

ok = True
for fn in ("sinpi", "cospi"):
    mine = set()
    with open(f"scratch/parcel-w4trig/out/wc_{fn}_bits.txt") as fh:
        for line in fh:
            mine.add(line.strip())
    theirs = set()
    with open(f"scratch/tier2-trig-spike/out/wc_{fn}_f64bits.txt") as fh:
        for line in fh:
            theirs.add(line.strip())
    same = mine == theirs
    ok = ok and same
    print(f"{fn}: mine_unique={len(mine)} spike_unique={len(theirs)} "
          f"equal={same} only_mine={len(mine - theirs)} "
          f"only_spike={len(theirs - mine)}")
print("WC SETS", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
