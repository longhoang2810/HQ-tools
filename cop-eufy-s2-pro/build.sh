#!/usr/bin/env bash
# Xuất STL cho tất cả chi tiết + ảnh xem trước.
#   ./build.sh          -> chỉ xuất STL vào stl/
#   ./build.sh preview  -> xuất thêm ảnh vào img/
set -euo pipefail
cd "$(dirname "$0")"

SCAD=${SCAD:-openscad}
SRC=cop-eufy-s2-pro.scad
mkdir -p stl

for p in base lid cap handle pin; do
    echo "==> stl/$p.stl"
    "$SCAD" --export-format=binstl -D "part=\"$p\"" -o "stl/$p.stl" "$SRC" 2>&1 \
        | grep -E "Volumes|WARNING|ERROR" || true
done
echo
echo 'Mỗi chi tiết phải báo "Volumes: 2" (1 khối đặc + 1 khối ngoài).'
echo 'Nếu ra 3 trở lên là model bị rời mảnh — kiểm tra lại thông số.'

if [ "${1:-}" = "preview" ]; then
    mkdir -p img
    RENDER="$SCAD --render -D seg=96 --projection=p --colorscheme=Tomorrow --imgsize=1000,850"
    [ -n "${DISPLAY:-}" ] || RENDER="xvfb-run -a $RENDER"     # máy không có màn hình
    echo "==> img/dong.png";  $RENDER --camera=0,0,0,62,0,35,560   -D 'part="all"'  -o img/dong.png  "$SRC" >/dev/null
    echo "==> img/mo.png";    $RENDER --camera=0,0,10,60,0,145,620 -D 'part="open"' -o img/mo.png    "$SRC" >/dev/null
    echo "==> img/matcat.png"; $RENDER --camera=0,0,-10,72,0,205,520 -D 'part="cut"' -o img/matcat.png "$SRC" >/dev/null
fi
