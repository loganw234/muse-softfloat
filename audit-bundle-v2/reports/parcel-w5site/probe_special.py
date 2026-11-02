import re
t = open(r'C:\Users\logan\source\repos\Muse-Softfloat\worktrees\w5-site\tests\msf_dispatch.h').read()
i = t.find('static const msf_op_desc_t MSF_OPS[]'); j = t.find('};', i)
rows = re.findall(r'\{\s*"([^"]+)",\s*"([^"]+)",\s*(MSF_SIG_\w+),\s*(MSF_RK_\w+),\s*\{\s*(MSF_AK_\w+),\s*(MSF_AK_\w+),\s*(MSF_AK_\w+)\s*\},\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\w+)\s*\}', t[i:j])
for r in rows:
    if r[2] in ('MSF_SIG_VERSION_OP','MSF_SIG_FLAG_OP','MSF_SIG_RADIX_OP','MSF_SIG_CLASS_OP','MSF_SIG_SCALEB','MSF_SIG_LOGB','MSF_SIG_CHAR_FROM') or r[3] in ('MSF_RK_SPECIAL','MSF_RK_INT','MSF_RK_CLASS'):
        print(r)
