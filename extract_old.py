#!/usr/bin/env python3
"""Trích BA danh mục "quy định cũ" mà Điều 30.4/30.5 NĐ 26/2026 dùng để xác
định trạng thái chuyển tiếp cho hóa chất Phụ lục III (KSĐB) vào
data/old_cas.json.

Điều 30.4 (NĐ 26): hóa chất KSĐB của NĐ 24 được MIỄN xuất trình Giấy phép XNK
tới 31/12/2026 nếu KHÔNG thuộc:
  1) Danh mục tiền chất công nghiệp  (NĐ 113/2017 + NĐ 82/2022)
  2) Danh mục hóa chất hạn chế SX-KD (NĐ 113/2017 + NĐ 82/2022)
  3) Danh mục hóa chất Bảng          (NĐ 33/2024)
=> tập "cũ" ở đây = hợp của đúng ba danh mục trên. KHÔNG gồm danh mục "SX-KD có
điều kiện" hay "phải khai báo" (Điều 30.4 không dẫn chiếu hai danh mục này).

Nguồn: nd113.md, nd82.md, nd33.md (bản chính thức, dạng bảng markdown).
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "data" / "old_cas.json"
CAS_RE = re.compile(r"\b\d{2,7}-\d{2}-\d\b")


def lines(name):
    return (HERE / name).read_text(encoding="utf-8").splitlines()


def cas_between(ls, start_pred, end_pred):
    """CAS từ dòng đầu tiên thỏa start_pred (không tính) đến dòng thỏa end_pred."""
    out, on = [], False
    for l in ls:
        if not on and start_pred(l):
            on = True
            continue
        if on and end_pred(l):
            break
        if on:
            out.extend(CAS_RE.findall(l))
    return out


def main():
    # --- NĐ 113/2017 (headers markdown "# PHỤ LỤC ...") ---
    nd113 = lines("nd113.md")
    tc_113 = cas_between(
        nd113,
        lambda l: l.strip().startswith("|") and "Tiền chất công nghiệp" in l and "nhóm 1" in l.lower(),
        lambda l: l.strip() == "# PHỤ LỤC II",
    )
    hc_113 = cas_between(
        nd113,
        lambda l: l.strip() == "# PHỤ LỤC II",
        lambda l: l.strip() == "# PHỤ LỤC III",
    )

    # --- NĐ 82/2022 (headers in đậm "**PHỤ LỤC ...**") ---
    nd82 = lines("nd82.md")
    # Điều 1.19 bổ sung tiền chất công nghiệp nhóm 1 (STT 830-835); dừng ở "Ghi chú"
    # để KHÔNG lấy STT 820-829 (SX-KD có điều kiện) đứng trước sub-header này.
    tc_82 = cas_between(
        nd82,
        lambda l: "Tiền chất công nghiệp" in l and "nhóm 1" in l.lower(),
        lambda l: "Ghi chú" in l,
    )
    # Điều 2.3 thay thế Phụ lục II của NĐ 113 = Danh mục hạn chế SX-KD (bản NĐ 82).
    hc_82 = cas_between(
        nd82,
        lambda l: l.strip() == "**PHỤ LỤC II**",
        lambda l: l.strip() == "**PHỤ LỤC VI**",
    )

    # --- NĐ 33/2024: mọi CAS trong văn bản đều là hóa chất thuộc chế độ Bảng ---
    # (Phụ lục I là Danh mục hóa chất Bảng 1/2/3; Điều 5 là các bảng chuyển chất
    #  từ NĐ 113/82 sang chế độ Bảng; biểu mẫu chỉ nhắc lại chất đã có). Lấy trọn.
    bang_33 = CAS_RE.findall((HERE / "nd33.md").read_text(encoding="utf-8"))

    data = {
        "source": "NĐ 113/2017/NĐ-CP, NĐ 82/2022/NĐ-CP, NĐ 33/2024/NĐ-CP",
        "note": (
            "Ba danh mục 'quy định cũ' theo Điều 30.4 NĐ 26/2026: tiền chất công "
            "nghiệp + hạn chế SX-KD (NĐ 113/2017 hợp NĐ 82/2022) và hóa chất Bảng "
            "(NĐ 33/2024). Dùng để xác định hóa chất PL III là 'cũ' (không được "
            "miễn xuất trình Giấy phép) hay 'mới'. Lưu ý: Bảng 1 & 2 của NĐ 33 định "
            "nghĩa nhiều chất theo HỌ (dẫn xuất không có CAS rời) nên tra theo CAS "
            "vẫn có thể sót — fail-safe: chất PL III luôn báo cần Giấy phép."
        ),
        "tien_chat_cong_nghiep": sorted(set(tc_113) | set(tc_82)),
        "han_che_sxkd": sorted(set(hc_113) | set(hc_82)),
        "hoa_chat_bang": sorted(set(bang_33)),
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(
        f"tiền chất: {len(data['tien_chat_cong_nghiep'])} "
        f"(NĐ113 {len(set(tc_113))} + NĐ82 {len(set(tc_82))}); "
        f"hạn chế: {len(data['han_che_sxkd'])} "
        f"(NĐ113 {len(set(hc_113))} ∪ NĐ82 {len(set(hc_82))}); "
        f"hóa chất Bảng: {len(data['hoa_chat_bang'])} (NĐ33) -> {OUT}"
    )


if __name__ == "__main__":
    main()
