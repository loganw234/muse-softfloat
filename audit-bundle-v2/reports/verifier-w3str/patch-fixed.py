#!/usr/bin/env python3
"""Apply the three one-line diagnostic fixes to the scratch TU copy."""
p = "C:/Users/logan/source/repos/Muse-Softfloat/scratch/verifier-w3str/fixed/msf_string_fixed.c"
s = open(p, newline="").read()
a = "    case MSF_IROUND_TIES_TO_EVEN:\n        return gt_half || eq_half;"
b = "    case MSF_IROUND_TIES_TO_EVEN:\n        return gt_half || (eq_half && (last_kept & 1));"
assert s.count(a) == 1, "tie site"
s = s.replace(a, b)
a2 = '    if (match_ci(s + i, "snan")) {\n        *consumed = i + 3u;'
b2 = '    if (match_ci(s + i, "snan")) {\n        *consumed = i + 4u;'
assert s.count(a2) == 1, "snan site"
s = s.replace(a2, b2)
a3 = "exp2 = (int64_t)pexp - 2 * frac_digits + extra_exp;"
b3 = "exp2 = (int64_t)pexp - 4 * frac_digits + extra_exp;"
assert s.count(a3) == 1, "hex site"
s = s.replace(a3, b3)
open(p, "w", newline="").write(s)
print("patched 3 sites")
