#!/usr/bin/env python3
"""Quét mô tả hàng hóa của doanh nghiệp (thường liệt kê nhiều chất + mã CAS
trong một đoạn văn/hỗn hợp), tự động tách hết mã CAS và tra từng mã theo
Phụ lục I-IV NĐ 24/2026/NĐ-CP + yêu cầu nhập khẩu NĐ 26/2026/NĐ-CP.

Công cụ không tự nhận diện % hàm lượng trong mô tả (khai báo tự do dễ ghi
lộn xộn, đoán nhầm % dễ dẫn tới kết luận miễn trừ sai) — hóa chất Phụ lục
III luôn báo "Cần Giấy phép"; đối chiếu ngưỡng miễn trừ nồng độ (Điều 21)
bằng tài liệu khai báo gốc, xem mục "Các trường hợp được miễn trừ" cuối kết quả.

Cách dùng (công chức hải quan chỉ cần copy-paste mô tả DN):
    python3 scan.py                # dán mô tả, xong bấm Ctrl+D (Ctrl+Z rồi Enter trên Windows)
    python3 scan.py mota.txt       # hoặc trỏ vào 1 file mô tả
    python3 scan.py "Hỗn hợp gồm Metanol (67-56-1), ..."   # hoặc truyền thẳng làm tham số
"""
import sys
from pathlib import Path

from core import (
    cas_status,
    extract_cas,
    format_exemptions,
    format_report,
    highest_annex,
    rows_for,
)

ANNEX_LABEL = {"I": "PL I", "II": "PL II", "III": "PL III", "IV": "PL IV", None: "—"}
NO_DATA = "(không có trong dữ liệu)"


def read_input():
    if len(sys.argv) > 1:
        arg = " ".join(sys.argv[1:])
        p = Path(arg)
        if p.is_file():
            return p.read_text(encoding="utf-8", errors="ignore")
        return arg
    print("Dán mô tả hàng hóa vào đây, xong bấm Ctrl+D:", file=sys.stderr)
    return sys.stdin.read()


def name_of(cas):
    rows = rows_for(cas)
    return rows[0]["name_vn"] if rows else NO_DATA


def print_summary(entries):
    print(f"Tìm thấy {len(entries)} mã CAS trong mô tả:\n")
    # Đo bề rộng cột trên CHÍNH những chuỗi sẽ in ra (kể cả NO_DATA). Trước đây
    # chỉ đo tên các chất CÓ dữ liệu, nên một mã CAS không tra ra là NO_DATA (24
    # ký tự) tràn cột và đẩy lệch "Phụ lục"/"Trạng thái" của đúng dòng đó.
    names = {c: name_of(c) for c in entries}
    name_w = min(max(max((len(n) for n in names.values()), default=10), 8), 40)
    header = f"{'CAS':<14}{'Tên chất':<{name_w}}  {'Phụ lục':<8}  Trạng thái"
    print(header)
    print("-" * len(header))
    for cas in entries:
        _, text = cas_status(cas)
        print(f"{cas:<14}{names[cas][:name_w]:<{name_w}}  {ANNEX_LABEL.get(highest_annex(cas), '—'):<8}  {text}")
    print()


def main():
    text = read_input()
    entries = extract_cas(text)
    if not entries:
        print("Không tìm thấy mã CAS nào (định dạng NNN-NN-N) trong mô tả đã dán.")
        sys.exit(1)

    print_summary(entries)
    print("=" * 70)
    for cas in entries:
        print(format_report(cas))
        print("-" * 70)

    print()
    print(format_exemptions())


if __name__ == "__main__":
    main()
