#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/scratch/lead/tmp" TMP="$PWD/scratch/lead/tmp" TEMP="$PWD/scratch/lead/tmp"
mkdir -p "$TMPDIR" scratch/lead/assembly
PY=.venv/Scripts/python.exe
FFMPEG=$($PY -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())")
echo "ffmpeg: $FFMPEG"
cat > scratch/lead/assembly/concat.txt <<'EOF'
file '../../study-video-intro/intro2.mp4'
file '../../study-video-gitvisual/gitvisual.mp4'
file '../../study-video-intro/outro2.mp4'
EOF
# concat list paths are relative to the list file location
"$FFMPEG" -y -f concat -safe 0 -i scratch/lead/assembly/concat.txt \
  -c:v libx264 -pix_fmt yuv420p -r 30 scratch/lead/assembly/assembly_v1.mp4 \
  > scratch/lead/assembly/concat.log 2>&1 || { tail -20 scratch/lead/assembly/concat.log; exit 1; }
$PY video/probe.py scratch/lead/assembly/assembly_v1.mp4 || true
# join-frame grabs: end of intro (4.9s), start of git (5.1s), end of git (82.9s), start of outro (83.1s)
for t in 4.9 5.1 82.9 83.1; do
  "$FFMPEG" -y -ss $t -i scratch/lead/assembly/assembly_v1.mp4 -frames:v 1 "scratch/lead/assembly/join_$t.png" >/dev/null 2>&1
done
$PY - <<'PYEOF'
from PIL import Image
for t in ("4.9","5.1","82.9","83.1"):
    im = Image.open(f"scratch/lead/assembly/join_{t}.png").convert("RGB")
    px = list(im.getdata())
    n = len(px)
    avg = tuple(sum(c[i] for c in px)//n for i in range(3))
    print(t, "size", im.size, "avg", avg, "corner", px[0], px[-1])
PYEOF
ls -la scratch/lead/assembly/
