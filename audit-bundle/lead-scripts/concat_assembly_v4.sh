#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/../.." || exit 9
export PATH="/c/Program Files/Git/mingw64/bin:/c/Program Files/Git/usr/bin:/usr/bin:$PATH"
export TMPDIR="$PWD/scratch/lead/tmp" TMP="$PWD/scratch/lead/tmp" TEMP="$PWD/scratch/lead/tmp"
mkdir -p "$TMPDIR" scratch/lead/assembly
PY=.venv/Scripts/python.exe
FFMPEG=$($PY -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())")
# intro2 5.0 + idea 14.5 + why2 32.0 + gitvisual4 88.0 + outro2 6.0 = 145.5s @1440p
"$FFMPEG" -y \
  -i scratch/study-video-intro/intro2.mp4 \
  -i scratch/study-video-idea/idea-1440p.mp4 \
  -i scratch/study-video-why/why2-1440p.mp4 \
  -i scratch/study-video-gitvisual/gitvisual4.mp4 \
  -i scratch/study-video-intro/outro2.mp4 \
  -filter_complex "[0:v]scale=2560:1440:flags=lanczos,setsar=1[v0];[1:v]setsar=1[v1];[2:v]setsar=1[v2];[3:v]setsar=1[v3];[4:v]scale=2560:1440:flags=lanczos,setsar=1[v4];[v0][v1][v2][v3][v4]concat=n=5:v=1:a=0[v]" \
  -map "[v]" -c:v libx264 -pix_fmt yuv420p -r 30 scratch/lead/assembly/assembly_v4.mp4 \
  > scratch/lead/assembly/concat4.log 2>&1 || { tail -20 scratch/lead/assembly/concat4.log; exit 1; }
$PY video/probe.py scratch/lead/assembly/assembly_v4.mp4 || true
for t in 4.9 5.1 19.4 19.6 51.4 51.6 139.4 139.6; do
  "$FFMPEG" -y -ss $t -i scratch/lead/assembly/assembly_v4.mp4 -frames:v 1 "scratch/lead/assembly/join4_$t.png" >/dev/null 2>&1
done
$PY - <<'PYEOF'
from PIL import Image
from collections import Counter
for t in ("4.9","5.1","19.4","19.6","51.4","51.6","139.4","139.6"):
    im = Image.open(f"scratch/lead/assembly/join4_{t}.png").convert("RGB")
    px = im.get_flattened_data() if hasattr(im, "get_flattened_data") else list(im.getdata())
    dom, cnt = Counter(px).most_common(1)[0]
    print(t, "dominant", dom, f"{cnt}/{len(px)}")
PYEOF
ls -la scratch/lead/assembly/assembly_v4.mp4
