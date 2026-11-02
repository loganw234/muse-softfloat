#!/bin/bash
cd /c/Users/logan/source/repos/Muse-Softfloat
python - <<'EOF'
import json
ops = json.load(open("worktrees/verify5-site/site/ops.json"))
print("nonrunnable:", sum(1 for o in ops if not o["runnable"]))
print("exp2/aug ops:", [o["name"] for o in ops if "exp2" in o["name"] or "aug" in o["name"]])
EOF
echo "--- css url( count ---"
grep -c "url(" worktrees/verify5-site/site/style.css || echo "no-url-paren"
echo "--- index ids ---"
grep -o 'id="[a-z-]*"' worktrees/verify5-site/site/index.html | sort -u
echo "--- header flags ---"
sed -n '70,75p' worktrees/verify5-site/include/muse_softfloat.h
echo "--- app flag defs ---"
grep -n "0x0" worktrees/verify5-site/site/app.js | head -5
