#!/usr/bin/env bash
R=/c/Users/logan/source/repos/Muse-Softfloat
export PATH="/c/msys64/mingw64/bin:/c/msys64/usr/bin:$PATH"
cd "$R/worktrees/verify3-str" || exit 9
echo "=== copy status (expect clean):"
git -c safe.directory="$R/worktrees/verify3-str" status --short
git -c safe.directory="$R/worktrees/verify3-str" stash list | head -3
echo "=== deliverables:"
ls -la "$R/ledger/verifier-w3str.md" "$R/scratch/verifier-w3str/report.md"
echo "=== evidence artifacts:"
ls "$R/scratch/verifier-w3str/"*.log "$R/scratch/verifier-w3str/"*.vec 2>/dev/null | head -8
ls "$R/scratch/verifier-w3str/adv" "$R/scratch/verifier-w3str/fuzz" "$R/scratch/verifier-w3str/exh" "$R/scratch/verifier-w3str/mpfrslice" "$R/scratch/verifier-w3str/fixed" 2>/dev/null
