"""make_dump.py SRC DST - produce a scratch-only instrumented copy
of interval_workload.c that dumps the stage-3 term lists under
-IW_DUMP_EXPANSIONS. Anchor-based; each anchor must occur once.
"""
import sys

HELPER = '''
#ifdef IW_DUMP_EXPANSIONS
#include <stdio.h>
static void iw_dump(const char *tag, const msf64_t *v, int n)
{
    int i;
    printf("EXP %s %d", tag, n);
    for (i = 0; i < n; i++) printf(" %016llx", (unsigned long long)v[i]);
    printf("\\n");
}
#endif
'''

src = open(sys.argv[1], encoding="ascii", newline="").read()

def once(anchor):
    assert src.count(anchor) == 1, f"anchor not unique: {anchor[:60]!r}"

a1 = '#include "interval_workload.h"\n'
once(a1)
src = src.replace(a1, a1 + HELPER)

a2 = ("    la.n = distill(ctx, la.v, la.n, &fl);\n"
      "    lb.n = distill(ctx, lb.v, lb.n, &fl);\n"
      "    lc.n = distill(ctx, lc.v, lc.n, &fl);\n")
once(a2)
src = src.replace(a2, a2 +
    "#ifdef IW_DUMP_EXPANSIONS\n"
    "    iw_dump(\"A\", la.v, la.n); iw_dump(\"B\", lb.v, lb.n);"
    " iw_dump(\"C\", lc.v, lc.n);\n"
    "#endif\n")

a3 = "    if (la.bad || lb.bad || lc.bad || ld.bad || guard_tripped(fl)) {\n"
once(a3)
src = src.replace(a3,
    "#ifdef IW_DUMP_EXPANSIONS\n"
    "    iw_dump(\"D\", ld.v, ld.n);\n"
    "#endif\n" + a3)

with open(sys.argv[2], "w", encoding="ascii", newline="") as f:
    f.write(src)
print("instrumented copy written:", sys.argv[2])
