files = [
    "worktrees/w4-trig/src/msf_math.c",
    "worktrees/w4-trig/tools/gen_trig_tables.py",
    "worktrees/w4-trig/tests/gen_vectors_trig.py",
    "worktrees/w4-trig/tests/trig_exhaustive.c",
]
tot = 0
for f in files:
    n = len(open(f, encoding="utf-8").readlines())
    tot += n
    print(f"{n:5d} {f}")
print(f"{tot:5d} total hand-written (ceiling 4500)")
gen = len(open("worktrees/w4-trig/src/msf_trig_tables.h", encoding="utf-8").readlines())
print(f"{gen:5d} generated table header (excluded)")
