#!/usr/bin/env python3
"""Trích các Danh mục CAS của Nghị định 113/2017/NĐ-CP cần cho quy tắc chuyển
tiếp NĐ 26/2026 (Điều 30.4/30.5) vào data/nd113_old_cas.json.

Điều 30.4 xác định hóa chất KSĐB (NĐ 24) được MIỄN xuất trình Giấy phép tới
31/12/2026 nếu KHÔNG thuộc: Danh mục hóa chất hạn chế SX-KD và Danh mục tiền
chất công nghiệp (NĐ 113/2017, NĐ 82/2022) và Danh mục hóa chất Bảng (NĐ
33/2024). Ở đây chỉ trích được hai danh mục của NĐ 113/2017:
  - Tiền chất công nghiệp (Nhóm 1 + Nhóm 2) — cuối Phụ lục I của NĐ 113.
  - Hóa chất hạn chế sản xuất, kinh doanh — Phụ lục II của NĐ 113.
KHÔNG có NĐ 82/2022 và NĐ 33/2024 -> tập "cũ" này KHÔNG đầy đủ; công cụ chỉ
dùng nó để KHẲNG ĐỊNH 'cũ', không dùng để kết luận 'mới' (xem core.py).
"""
import json
import re
from pathlib import Path

SRC = Path(__file__).parent / "nd113.md"
OUT = Path(__file__).parent / "data" / "nd113_old_cas.json"
CAS_RE = re.compile(r"\b\d{2,7}-\d{2}-\d\b")


def cas_between(lines, start_pred, end_pred):
    """Thu mọi CAS từ dòng thỏa start_pred (đầu tiên) đến dòng thỏa end_pred."""
    out, collecting = [], False
    for l in lines:
        if not collecting and start_pred(l):
            collecting = True
            continue
        if collecting and end_pred(l):
            break
        if collecting:
            out.extend(CAS_RE.findall(l))
    return out


def main():
    lines = SRC.read_text(encoding="utf-8").splitlines()

    # Bắt ĐÚNG dòng đánh dấu bảng "| | Tiền chất công nghiệp(2) nhóm 1 | ... |",
    # không bắt câu định nghĩa ở Điều 3 ("a) Tiền chất công nghiệp Nhóm 1 gồm...").
    tien_chat = cas_between(
        lines,
        lambda l: l.strip().startswith("|") and "Tiền chất công nghiệp" in l and "nhóm 1" in l.lower(),
        lambda l: l.strip() == "# PHỤ LỤC II",
    )
    han_che = cas_between(
        lines,
        lambda l: l.strip() == "# PHỤ LỤC II",
        lambda l: l.strip() == "# PHỤ LỤC III",
    )

    data = {
        "source": "NĐ 113/2017/NĐ-CP",
        "note": (
            "Chỉ gồm Danh mục tiền chất công nghiệp (Nhóm 1+2) và Danh mục hóa "
            "chất hạn chế SX-KD (Phụ lục II) của NĐ 113/2017. Chưa gồm NĐ "
            "82/2022 và Danh mục hóa chất Bảng NĐ 33/2024 -> không đủ để kết "
            "luận 'mới'."
        ),
        "tien_chat_cong_nghiep": sorted(set(tien_chat)),
        "han_che_sxkd": sorted(set(han_che)),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(
        f"tiền chất: {len(data['tien_chat_cong_nghiep'])} CAS, "
        f"hạn chế: {len(data['han_che_sxkd'])} CAS -> {OUT}"
    )


if __name__ == "__main__":
    main()
