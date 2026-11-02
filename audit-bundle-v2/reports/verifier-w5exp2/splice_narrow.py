#!/usr/bin/env python3
# splice_narrow.py - replace old v_narrow (line range) with new certified version.
import sys, os
D = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(D, "mydecider.c")
snip = os.path.join(D, "narrow_snippet.c")
with open(src) as fh:
    lines = fh.readlines()
with open(snip) as fh:
    newfn = fh.read()
# locate old function: from the comment line to the line before v_escalations
start = next(i for i, l in enumerate(lines) if l.startswith("/* Narrow computed pair"))
end = next(i for i, l in enumerate(lines) if l.startswith("unsigned long v_escalations;"))
# back up one blank line: end-2 should be the closing brace; verify
assert lines[end - 2].rstrip() == "}", lines[end - 2]
newfn = newfn.replace("static int v_narrow_cert(int fi, mpfr_t vW, long W, int compExactW,",
                      "static int v_narrow(int fi, mpfr_t vW, long W, int compExactW,")
assert "static int v_narrow(" in newfn
# gate the RN/RNA overflow-midpoint check on !compExactW (true value known: no check needed)
old_chk = "        if (!exact && overflow && (m == 0 || m == 4)) {"
new_chk = "        if (!exact && !compExactW && overflow && (m == 0 || m == 4)) {"
assert old_chk in newfn
newfn = newfn.replace(old_chk, new_chk)
lines[start:end - 1] = [newfn]
with open(src, "w") as fh:
    fh.writelines(lines)
print("spliced ok")
