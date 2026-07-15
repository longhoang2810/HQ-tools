#!/usr/bin/env python3
"""Parse the official markdown of Nghị định 24/2026/NĐ-CP (Phụ lục I-IV) into
data/nd24_chemicals.json: one row per (CAS, category) pair.

Input: nd24.md — bản chính thức, các Phụ lục ở dạng bảng markdown
    | STT | Tên khoa học (IUPAC) | Tên chất | Mã CAS | Công thức [| Ngưỡng] |

Nguồn cũ (nd24.txt, textutil one-cell-per-line) đã thay bằng bản md chính thức;
parser này bám cấu trúc bảng nên không còn phụ thuộc số dòng cứng như trước.
"""
import json
import re
import sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "nd24.md")
OUT = Path(__file__).parent / "data" / "nd24_chemicals.json"

CAS_RE = re.compile(r"\b\d{2,7}-\d{2}-\d\b")
STT_RE = re.compile(r"^\d+\.$")

# Errata: 2 mã CAS trong Phụ lục NĐ 24/2026 sai so với số CAS quốc tế (sai cả
# check-digit). Sửa tại đây để giữ nd24.md đúng nguyên văn nghị định; chạy lại
# extract.py là tự áp dụng, không sửa tay data JSON.
#   Canxi clorat Ca(ClO3)2: NĐ ghi 10037-74-3 -> đúng 10137-74-3 (PubChem CID 24978)
#   Selen dioxit SeO2:      NĐ ghi 7746-08-4  -> đúng 7446-08-4  (PubChem CID 24007)
# Mã 10118-77-6 (C7H9ClO4) cũng sai check-digit nhưng ĐÃ đối chiếu: đúng nguyên
# văn nghị định và không có CAS hợp lệ để thay. Giữ nguyên, KHÔNG đưa vào ERRATA.
ERRATA = {
    "10037-74-3": "10137-74-3",
    "7746-08-4": "7446-08-4",
}

CAT_I = "Phụ lục I – Hóa chất cơ bản thuộc lĩnh vực công nghiệp hóa chất trọng điểm"
CAT_II = "Phụ lục II › Mục 1 – Chất sản xuất, kinh doanh có điều kiện"
CAT_IV = "Phụ lục IV › Bảng A – Phải xây dựng Kế hoạch phòng ngừa, ứng phó sự cố hóa chất"
# Phụ lục III: nhãn category đổi theo phân nhóm (Nhóm 1/2 × tiền chất/Bảng/POP).
CAT_III_N1_A = "Phụ lục III › Nhóm 1 (IVB) › A – Tiền chất công nghiệp"
CAT_III_N1_B = "Phụ lục III › Nhóm 1 (IVB) › B – Hóa chất Bảng 2 (Công ước Vũ khí hóa học)"
CAT_III_N2_A = "Phụ lục III › Nhóm 2 (IVC) › A – Tiền chất công nghiệp"
CAT_III_N2_B = "Phụ lục III › Nhóm 2 (IVC) › B – Hóa chất Bảng 3 (Công ước Vũ khí hóa học)"
CAT_III_N2_C = "Phụ lục III › Nhóm 2 (IVC) › C – Hóa chất thuộc Công ước Rotterdam/Stockholm"

ANNEX_HDR = re.compile(r"^#\s+PHỤ LỤC (IV|III|II|I)\s*$")


def split_row(line):
    """markdown table row -> list of stripped cells, or None if not a table row."""
    s = line.strip()
    if not s.startswith("|"):
        return None
    return [c.strip() for c in s.strip("|").split("|")]


def is_separator(cells):
    return all(set(c) <= set("-: ") and c for c in cells) if cells else False


def parse():
    lines = SRC.read_text(encoding="utf-8").splitlines()
    records = []
    annex = None
    category = None
    collecting = True  # False sau khi vào Bảng B của PL IV (không còn CAS riêng lẻ)

    for line in lines:
        st = line.strip()

        m = ANNEX_HDR.match(st)
        if m:
            annex = m.group(1)
            category = {"I": CAT_I, "II": CAT_II, "IV": CAT_IV}.get(annex)
            collecting = annex != "IV"  # PL IV chỉ thu khi vào "Bảng A"
            continue

        # Phân nhóm trong PL III / PL IV (dòng đậm, không phải bảng)
        if annex == "III":
            if st.startswith("**1.1. Nhóm 1**"):
                category = CAT_III_N1_A
                continue
            if st.startswith("**1.2. Nhóm 2**"):
                category = CAT_III_N2_A
                continue
        if annex == "IV":
            if st.startswith("**1. Bảng A**"):
                collecting = True
                category = CAT_IV
                continue
            if st.startswith("**2. Bảng B**"):
                collecting = False
                continue

        cells = split_row(line)
        if not cells or is_separator(cells):
            continue
        c0 = cells[0]

        # Dòng chuyển phân nhóm nằm trong bảng (PL III)
        if annex == "III":
            joined = " ".join(cells)
            if c0.startswith("Hóa chất Bảng 2"):
                category = CAT_III_N1_B
                continue
            if c0.startswith("Hóa chất Bảng 3"):
                category = CAT_III_N2_B
                continue
            if "Rotterdam" in joined or "Stockholm" in joined:
                category = CAT_III_N2_C
                continue

        # Bỏ dòng tiêu đề bảng
        if c0 == "STT" or (len(cells) > 1 and cells[1].startswith("Tên")):
            continue
        if not collecting:
            continue

        # Dòng dữ liệu: STT(0) EN(1) VN(2) CAS(3) Công thức(4) [Ngưỡng(5)]
        if len(cells) < 4:
            continue
        cas_list = CAS_RE.findall(cells[3])
        if not cas_list:
            continue  # dòng '---' / ô CAS trống (chất không có 1 CAS đơn) -> bỏ
        name_en, name_vn = cells[1], cells[2]
        threshold = None
        if annex == "IV" and len(cells) > 5 and cells[5]:
            threshold = cells[5]
        for cas in cas_list:
            row = {
                "cas": ERRATA.get(cas, cas),
                "name_en": name_en,
                "name_vn": name_vn,
                "annex": annex,
                "category": category,
            }
            if threshold:
                row["threshold_kg"] = threshold
            records.append(row)
    return records


if __name__ == "__main__":
    records = parse()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(records)} (CAS, category) rows -> {OUT}")
