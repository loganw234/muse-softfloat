#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/scratch/lead/tmp" TMP="$PWD/scratch/lead/tmp" TEMP="$PWD/scratch/lead/tmp"
mkdir -p "$TMPDIR" scratch/lead/assembly
PY=.venv/Scripts/python.exe
FFMPEG=$($PY -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())")
cat > scratch/lead/assembly/concat2.txt <<'EOF'
file '../../study-video-intro/intro2.mp4'
file '../../study-video-gitvisual/gitvisual2.mp4'
file '../../study-video-intro/outro2.mp4'
EOF
"$FFMPEG" -y -f concat -safe 0 -i scratch/lead/assembly/concat2.txt \
  -c:v libx264 -pix_fmt yuv420p -r 30 scratch/lead/assembly/assembly_v2.mp4 \
  > scratch/lead/assembly/concat2.log 2>&1 || { tail -20 scratch/lead/assembly/concat2.log; exit 1; }
$PY video/probe.py scratch/lead/assembly/assembly_v2.mp4 || true
for t in 4.9 5.1 87.9 88.1; do
  "$FFMPEG" -y -ss $t -i scratch/lead/assembly/assembly_v2.mp4 -frames:v 1 "scratch/lead/assembly/join2_$t.png" >/dev/null 2>&1
done
$PY - <<'PYEOF'
from PIL import Image
for t in ("4.9","5.1","87.9","88.1"):
    im = Image.open(f"scratch/lead/assembly/join2_{t}.png").convert("RGB")
    px = im.get_flattened_data() if hasattr(im, "get_flattened_data") else list(im.getdata())
    n = len(px)
    avg = tuple(sum(c[i] for c in px)//n for i in range(3))
    from collections import Counter
    dom, cnt = Counter(px).most_common(1)[0]
    print(t, "avg", avg, "dominant", dom, f"{cnt}/{n}")
PYEOF
ls -la scratch/lead/assembly/assembly_v2.mp4
