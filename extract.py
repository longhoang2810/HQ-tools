#!/usr/bin/env python3
"""Parse the linearized text of Nghi dinh 24/2026/ND-CP (Phu luc I-IV) into
data/nd24_chemicals.json: one row per (CAS, category) pair.

Input: nd24.txt, produced by:
    textutil -convert txt -output nd24.txt "24_2026_ND-CP_....docx"
# ponytail: textutil is macOS-only. If regenerating elsewhere, swap in any
# docx->text conversion that keeps one table cell per line (order preserved).
"""
import json
import re
import sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "nd24.txt")
OUT = Path(__file__).parent / "data" / "nd24_chemicals.json"

CAS_RE = re.compile(r"^\d{2,7}-\d{2}-\d$")
STT_RE = re.compile(r"^\d+\.$")
THRESHOLD_RE = re.compile(r"^[\d.]+(\s*\(net\))?$")

# Errata: 2 mã CAS trong Phụ lục NĐ 24/2026 sai so với số CAS quốc tế (số ghi
# trong nghị định sai cả check-digit). Sửa tại đây để giữ nd24.txt đúng nguyên
# văn nghị định; chạy lại extract.py là tự áp dụng, không sửa tay data JSON.
#   Canxi clorat Ca(ClO3)2: NĐ ghi 10037-74-3 -> đúng 10137-74-3 (PubChem CID 24978)
#   Selen dioxit SeO2:      NĐ ghi 7746-08-4  -> đúng 7446-08-4  (PubChem CID 24007)
# Mã 10118-77-6 (C7H9ClO4) cũng sai check-digit nhưng ĐÃ đối chiếu: đúng nguyên
# văn nghị định và không có CAS hợp lệ để thay (10118-77-1 không tồn tại). Giữ
# nguyên theo nghị định, KHÔNG đưa vào ERRATA (đây là lỗi trong văn bản gốc).
ERRATA = {
    "10037-74-3": "10137-74-3",
    "7746-08-4": "7446-08-4",
}

lines = SRC.read_text(encoding="utf-8").splitlines()

# Section boundaries found by inspecting the headers in nd24.txt (1-indexed
# line numbers from the doc -> 0-indexed slice bounds below).
SECTIONS = [
    (36, 231, "I", "Phụ lục I – Hóa chất cơ bản thuộc lĩnh vực công nghiệp hóa chất trọng điểm"),
    (240, 4200, "II", "Phụ lục II › Mục 1 – Chất sản xuất, kinh doanh có điều kiện"),
    (4217, 4327, "III", "Phụ lục III › Nhóm 1 (IVB) › A – Tiền chất công nghiệp"),
    (4330, 5068, "III", "Phụ lục III › Nhóm 1 (IVB) › B – Hóa chất Bảng 2 (Công ước Vũ khí hóa học)"),
    (5074, 5170, "III", "Phụ lục III › Nhóm 2 (IVC) › A – Tiền chất công nghiệp"),
    (5178, 5273, "III", "Phụ lục III › Nhóm 2 (IVC) › B – Hóa chất Bảng 3 (Công ước Vũ khí hóa học)"),
    (5276, 5571, "III", "Phụ lục III › Nhóm 2 (IVC) › C – Hóa chất thuộc Công ước Rotterdam/Stockholm"),
    (5588, 7250, "IV", "Phụ lục IV › Bảng A – Phải xây dựng Kế hoạch phòng ngừa, ứng phó sự cố hóa chất"),
]


def parse_section(body, annex, category):
    records = []
    # split body into chunks starting at each STT line ("12.")
    starts = [i for i, l in enumerate(body) if STT_RE.match(l.strip())]
    starts.append(len(body))
    for a, b in zip(starts, starts[1:]):
        chunk = [l.strip() for l in body[a + 1:b] if l.strip()]
        if len(chunk) < 2:
            continue
        name_en, name_vn = chunk[0], chunk[1]
        rest = chunk[2:]
        cas_list = [x for x in rest if CAS_RE.match(x)]
        threshold = None
        if annex == "IV" and rest and THRESHOLD_RE.match(rest[-1]) and not CAS_RE.match(rest[-1]):
            threshold = rest[-1]
        if not cas_list:
            continue  # "---" placeholder rows: no single CAS, skip (see grep note in README)
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


all_records = []
for start, end, annex, category in SECTIONS:
    body = lines[start - 1:end - 1]
    all_records.extend(parse_section(body, annex, category))

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(all_records, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(all_records)} (CAS, category) rows -> {OUT}")
