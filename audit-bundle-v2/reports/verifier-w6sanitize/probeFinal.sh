#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat || exit 9
echo "--- runner.c fix hunk (memchr/memcpy replacing strncpy) ---"
grep -n -A4 -B2 "memchr\|memcpy" worktrees/verify6-sanitize/tests/runner.c | head -30
echo "--- original copy git status (must be clean) ---"
git -c safe.directory=/c/Users/logan/source/repos/Muse-Softfloat/worktrees/verify6-sanitize -C worktrees/verify6-sanitize status --short | head -10
echo "(end status)"
echo "--- sanitizer seam: SANFLAGS use sites ---"
grep -n "SANFLAGS" worktrees/verify6-sanitize/tools/run.sh
