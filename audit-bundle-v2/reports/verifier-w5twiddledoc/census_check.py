"""Recompute the 8,856-field census from the driver loop semantics.

Mirrors demo/twiddle_gate.c: for each leg, indices kept are
i in [0, n) with (stride == 1 or i % stride == 0 or i == n-1);
each kept twiddle contributes 2 fields (r and i).

Legs (from main()): gate_complex(1024, fwd+inv, 1),
gate_fftr(1024, fwd+inv, 1), gate_complex(4096, fwd+inv, 37),
gate_fftr(4096, fwd+inv, 37), gate_complex(256, fwd, 1),
gate_fftr(256, fwd, 1). fftr = substate (m = n/2 entries) +
super-twiddles (m/2 entries). Usage: census_check.py <gate-log>.
"""
import sys


def kept(n, stride):
    return sum(1 for i in range(n)
               if stride == 1 or i % stride == 0 or i == n - 1)


def cpx(n, stride):
    return kept(n, stride) * 2  # 2 fields per twiddle


def fftr(n, stride):
    m = n // 2
    return (kept(m, stride) + kept(m // 2, stride)) * 2


legs = [
    ("1024 complex fwd+inv", 2 * cpx(1024, 1)),
    ("1024 fftr fwd+inv", 2 * fftr(1024, 1)),
    ("4096 complex fwd+inv s37", 2 * cpx(4096, 37)),
    ("4096 fftr fwd+inv s37", 2 * fftr(4096, 37)),
    ("256 complex fwd", cpx(256, 1)),
    ("256 fftr fwd", fftr(256, 1)),
]
total = 0
for name, fields in legs:
    print("%-24s %d" % (name, fields))
    total += fields
print("recomputed total: %d" % total)

log = open(sys.argv[1]).read()
last = [ln for ln in log.splitlines() if ln.startswith("PROVENANCE")][-1]
print("gate says: " + last)
n = int(last.split("checked_fields=")[1].split()[0])
mm = int(last.split("mismatches=")[1])
assert total == 8856, "census recompute is not 8856: %d" % total
assert n == total, "gate count %d != recomputed %d" % (n, total)
assert mm == 0, "mismatches nonzero"
print("CENSUS-OK 8856/0")
