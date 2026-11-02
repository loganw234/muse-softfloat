#!/usr/bin/env bash
set -eu
cd /c/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-sanitize
S="-c safe.directory=C:/Users/logan/source/repos/Muse-Softfloat/worktrees/w6-sanitize"
git $S status --short
git $S add tests/runner.c
git $S diff --cached --check
git $S diff --cached --stat
git $S commit -F /c/Users/logan/source/repos/Muse-Softfloat/scratch/parcel-w6sanitize/commit-msg-rev.txt
git $S log -1 --format='TIP %H %s'
git $S status --short -b
