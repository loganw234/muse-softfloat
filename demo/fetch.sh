#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# fetch.sh - download the two pinned workload archives for the demo.
#
# Reads only the REBOUND and KissFFT rows of docs/metrics/fetches.jsonl,
# downloads into demo/cache/ (gitignored; this script refuses to run
# if that path would be tracked), verifies the archive sha256 and the
# licence sha256 against the fetches rows before extraction, and
# extracts.  No network beyond those two URLs.  --offline uses a
# pre-seeded cache only and says so; it never touches the network.
#
# Usage (from anywhere): bash demo/fetch.sh [--offline]
# The verification and extraction live in demo/fetch.py; this script
# owns the prerequisites and the tracked-cache refusal.
set -u
cd "$(dirname "$0")/.." || exit 9

OFFLINE=""
for arg in "$@"; do
    case "$arg" in
        --offline) OFFLINE="--offline" ;;
        *) echo "usage: bash demo/fetch.sh [--offline]"; exit 2 ;;
    esac
done

fail() { echo "fetch: FAIL - $1"; exit "${2:-1}"; }

# Python: $MSF_PYTHON, then python3, then python (portable for
# strangers; the workspace .venv is only used when named).
PY="${MSF_PYTHON:-}"
if [ -z "$PY" ]; then
    if command -v python3 >/dev/null 2>&1; then
        PY=python3
    elif command -v python >/dev/null 2>&1; then
        PY=python
    else
        fail "no Python found (need python3 or python on PATH, or MSF_PYTHON set)" 2
    fi
fi
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null \
    || fail "Python at $PY is unusable or older than 3.8" 2

[ -f docs/metrics/fetches.jsonl ] \
    || fail "docs/metrics/fetches.jsonl not found - run from a muse-softfloat checkout" 2

# Refuse if the cache would be tracked: fetched third-party source
# must never enter the repository.  Outside a git work tree (for
# example a `git archive` unpack) there is nothing to pollute; say
# the check was skipped instead of pretending it ran.
mkdir -p demo/cache
GIT_OK=0
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    GIT_OK=1
elif git -c safe.directory="$PWD" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git() { command git -c safe.directory="$PWD" "$@"; }
    GIT_OK=1
fi
if [ "$GIT_OK" = 1 ]; then
    [ -z "$(git ls-files -- demo/cache)" ] \
        || fail "demo/cache contains tracked files - refusing (fetched source must never be tracked)"
    probe=demo/cache/.fetch-probe
    : > "$probe"
    if git check-ignore -q "$probe"; then
        rm -f "$probe"
    else
        rm -f "$probe"
        fail "demo/cache/ is not gitignored here - refusing (add the demo/cache/ entry from .gitignore first)"
    fi
else
    echo "fetch: not inside a git work tree; tracked-cache check skipped"
fi

exec "$PY" demo/fetch.py --cache demo/cache \
    --fetches docs/metrics/fetches.jsonl $OFFLINE
