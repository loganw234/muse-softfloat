#!/usr/bin/env bash
cd /c/Users/logan/source/repos/Muse-Softfloat/muse-softfloat || exit 9
grep -n 'expect\|prov exact-str\|total\|VERDICT' build/standard/verify.log | head -30
