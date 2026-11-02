#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/scratch/lead/tmp" TMP="$PWD/scratch/lead/tmp" TEMP="$PWD/scratch/lead/tmp"
mkdir -p "$TMPDIR" scratch/lead/assembly
PY=.venv/Scripts/python.exe
FFMPEG=$($PY -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())")
# 1440p canvas; intro/outro (1080p masters) lanczos-upscaled, why+gitvisual native 1440p
"$FFMPEG" -y \
  -i scratch/study-video-intro/intro2.mp4 \
  -i scratch/study-video-why/why-1440p.mp4 \
  -i scratch/study-video-gitvisual/gitvisual3.mp4 \
  -i scratch/study-video-intro/outro2.mp4 \
  -filter_complex "[0:v]scale=2560:1440:flags=lanczos,setsar=1[v0];[1:v]setsar=1[v1];[2:v]setsar=1[v2];[3:v]scale=2560:1440:flags=lanczos,setsar=1[v3];[v0][v1][v2][v3]concat=n=4:v=1:a=0[v]" \
  -map "[v]" -c:v libx264 -pix_fmt yuv420p -r 30 scratch/lead/assembly/assembly_v3.mp4 \
  > scratch/lead/assembly/concat3.log 2>&1 || { tail -20 scratch/lead/assembly/concat3.log; exit 1; }
$PY video/probe.py scratch/lead/assembly/assembly_v3.mp4 || true
for t in 4.9 5.1 20.9 21.1 108.9 109.1; do
  "$FFMPEG" -y -ss $t -i scratch/lead/assembly/assembly_v3.mp4 -frames:v 1 "scratch/lead/assembly/join3_$t.png" >/dev/null 2>&1
done
$PY - <<'PYEOF'
from PIL import Image
from collections import Counter
for t in ("4.9","5.1","20.9","21.1","108.9","109.1"):
    im = Image.open(f"scratch/lead/assembly/join3_{t}.png").convert("RGB")
    px = im.get_flattened_data() if hasattr(im, "get_flattened_data") else list(im.getdata())
    dom, cnt = Counter(px).most_common(1)[0]
    print(t, im.size, "dominant", dom, f"{cnt}/{len(px)}")
PYEOF
ls -la scratch/lead/assembly/assembly_v3.mp4
