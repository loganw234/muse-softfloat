#!/bin/bash
# Discover session-store location from prior (non-fenced) verifier material.
set -u
ROOT="C:/Users/logan/source/repos/Muse-Softfloat"
ls "$ROOT/scratch/verifier-w5metrics/" 2>&1
echo "=== session-dir mentions ==="
grep -oh 'session-dir [^ ,;)]*' -r "$ROOT/scratch/verifier-w5metrics/" 2>/dev/null | sort -u | head -10
echo "=== extractor mentions in report ==="
grep -oh 'extract[^ ,;)]*' "$ROOT/scratch/verifier-w5metrics/report.md" 2>/dev/null | sort -u | head -10
echo "=== until mentions ==="
grep -oh 'until [^ ,;)]*' -r "$ROOT/scratch/verifier-w5metrics/" 2>/dev/null | sort -u | head -10
