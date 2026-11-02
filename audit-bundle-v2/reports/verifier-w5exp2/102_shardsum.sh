#!/usr/bin/env bash
# 102_shardsum.sh - summarize shard log without inline pipes.
set -u
D="$(dirname "$0")"
grep -E "shard S|f32 range:|seed:|wall" "$D/70_f32shards.log" > "$D/102_shardsum.txt" 2>&1 || true
cat "$D/102_shardsum.txt"
