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
import unicodedata
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent / "nd24.md")
OUT = Path(__file__).parent / "data" / "nd24_chemicals.json"
# Mục Phụ lục III chỉ có TÊN, ô mã CAS ghi '---' (họ chất: "Asen và các hợp chất
# của asen", các họ Bảng 2 dạng N,N-Dialkyl...). Không tra theo CAS được, nhưng
# BỎ HẲN thì trang im lặng về chúng -> tách ra file riêng để cảnh báo.
OUT_NO_CAS = Path(__file__).parent / "data" / "nd24_pl3_no_cas.json"
# Chất nằm dưới dòng "Ngoại trừ:" của Phụ lục III — nghị định loại trừ khỏi mục
# đó. Không vào bảng tra (không phải hóa chất Bảng 2), nhưng giữ lại để trang nói
# được VÌ SAO một mã có mặt trong bảng Phụ lục III mà kết luận lại không phải PL III.
OUT_EXCLUDED = Path(__file__).parent / "data" / "nd24_pl3_ngoai_tru.json"

CAS_RE = re.compile(r"\b\d{2,7}-\d{2}-\d\b")
STT_RE = re.compile(r"^\d+\.$")
# Dòng "Ngoại trừ:" trong Phụ lục III: các dòng CAS NGAY DƯỚI nó là chất được
# LOẠI TRỪ khỏi mục ngay trên, không phải chất thuộc mục. Nguyên văn Công ước CWC
# (Bảng 2 B.4 miễn trừ Fonofos; B.10 miễn trừ DMAE/DEAE). Đọc nhầm chiều là bắt
# doanh nghiệp xin Giấy phép cho chất nghị định đã nói rõ là không phải xin.
# Khối ngoại trừ kết thúc ở mục có STT kế tiếp.
EXEMPT_RE = re.compile(r"Ngoại trừ|Exemptions?:", re.I)

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
# (IVB)/(IVC) là mã phân loại tiền chất ma túy — trong nghị định chỉ chú thích
# cho mục A – Tiền chất công nghiệp, KHÔNG gắn cho mục B/C (hóa chất Công ước).
CAT_III_N1_A = "Phụ lục III › Nhóm 1 (IVB) › A – Tiền chất công nghiệp"
CAT_III_N1_B = "Phụ lục III › Nhóm 1 › B – Hóa chất Bảng 2 (Công ước Vũ khí hóa học)"
CAT_III_N2_A = "Phụ lục III › Nhóm 2 (IVC) › A – Tiền chất công nghiệp"
CAT_III_N2_B = "Phụ lục III › Nhóm 2 › B – Hóa chất Bảng 3 (Công ước Vũ khí hóa học)"
CAT_III_N2_C = "Phụ lục III › Nhóm 2 › C – Hóa chất thuộc Công ước Rotterdam/Stockholm"
# Nhóm 1 còn tiêu đề "Hóa chất khác" sau mục B. Thiếu nhánh này thì 113 chất
# (Benzen, Benzal clorua, Axit methoxy axetic...) mang category của khối trước nó
# -> trang nói Benzen là "Hóa chất Bảng 2 (Công ước Vũ khí hóa học)": sai căn cứ.
CAT_III_N1_KHAC = "Phụ lục III › Nhóm 1 › Hóa chất khác"

ANNEX_HDR = re.compile(r"^#\s+PHỤ LỤC (IV|III|II|I)\s*$")


def split_row(line):
    """markdown table row -> list of stripped cells, or None if not a table row."""
    s = line.strip()
    if not s.startswith("|"):
        return None
    return [c.strip() for c in s.strip("|").split("|")]


def is_separator(cells):
    return all(set(c) <= set("-: ") and c for c in cells) if cells else False


def _co_dau(s):
    """Chuỗi có dấu tiếng Việt (kể cả 'đ')."""
    return any(unicodedata.combining(c) for c in unicodedata.normalize("NFD", s)) or "đ" in s.lower()


def ten_viet(cells):
    """Ô tên tiếng Việt của một dòng bảng.

    Theo tiêu đề bảng thì cột 2 là "Tên chất"/"Tên hóa chất theo tiếng Việt",
    nhưng nd24.md (và bản gốc docx) có chỗ ĐẢO — mục 27 ghi tên Việt ở cột 1 —
    nên bám cột cứng là ra tên tiếng Anh. Chọn theo dấu tiếng Việt; cả hai ô
    không dấu (mục 45 "Biphenyl (PCB)", 81 "Polychlorinated" — hai ô giống hệt
    nhau) thì lấy cột 2 như tiêu đề nói.
    """
    en, vn = cells[1], cells[2]
    if _co_dau(vn):
        return vn
    if _co_dau(en):
        return en
    return vn or en


def parse():
    lines = SRC.read_text(encoding="utf-8").splitlines()
    records = []
    no_cas = []
    excluded = []
    annex = None
    category = None
    collecting = True  # False sau khi vào Bảng B của PL IV (không còn CAS riêng lẻ)
    prev_names = ("", "")  # tên dòng dữ liệu gần nhất — cho dòng tiếp diễn chỉ có CAS
    last_stt = None
    exempt_of = None  # STT của mục đang liệt kê "Ngoại trừ", None nếu không ở trong khối đó

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
            if c0.startswith("Hóa chất khác"):
                category = CAT_III_N1_KHAC
                continue
            if "Rotterdam" in joined or "Stockholm" in joined:
                category = CAT_III_N2_C
                continue

        # Bỏ dòng tiêu đề bảng
        if c0 == "STT" or (len(cells) > 1 and cells[1].startswith("Tên")):
            continue
        if not collecting:
            continue

        # Khối "Ngoại trừ" (chỉ PL III): mở khi gặp dòng Ngoại trừ, đóng khi sang
        # mục có STT kế tiếp. Chất trong khối bị LOẠI khỏi mục -> không phải PL III.
        if annex == "III":
            if STT_RE.match(c0):
                exempt_of = None  # mục mới -> hết khối ngoại trừ của mục trước
                last_stt = c0
            if EXEMPT_RE.search(" ".join(cells[1:3])):
                exempt_of = last_stt
                continue
            if exempt_of and CAS_RE.search(cells[3] if len(cells) > 3 else ""):
                for cas in CAS_RE.findall(cells[3]):
                    excluded.append(
                        {
                            "cas": ERRATA.get(cas, cas),
                            "ten": cells[2] or cells[1],
                            "ngoai_tru_khoi": exempt_of,
                            "category": category,
                        }
                    )
                continue

        # Dòng dữ liệu: STT(0) EN(1) VN(2) CAS(3) Công thức(4) [Ngưỡng(5)]
        if len(cells) < 4:
            continue
        cas_list = CAS_RE.findall(cells[3])
        if not cas_list:
            # Ô CAS ghi '---': mục là HỌ chất/nhóm chất, nghị định không cho một
            # mã CAS đơn. Chỉ giữ dòng có STT (mục thật, không phải dòng tiếp diễn
            # "và các muối proton hóa tương ứng" hay tiêu đề con).
            if annex == "III" and STT_RE.match(c0) and (cells[1] or cells[2]):
                no_cas.append({"stt": c0, "ten": ten_viet(cells), "category": category})
            continue  # dòng '---' / ô CAS trống -> không vào bảng tra theo CAS
        name_en, name_vn = cells[1], cells[2]
        # Dòng tiếp diễn (|  |  |  | <CAS> |  |): CAS thứ 2+ của chất ở dòng trên,
        # kế thừa tên — không thì 6 mã CAS ra tên rỗng, lookup in "CAS ...:  ()".
        if not name_en and not name_vn:
            name_en, name_vn = prev_names
        else:
            prev_names = (name_en, name_vn)
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
    return records, no_cas, excluded


if __name__ == "__main__":
    records, no_cas, excluded = parse()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(records)} (CAS, category) rows -> {OUT}")
    OUT_NO_CAS.write_text(json.dumps(no_cas, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(no_cas)} mục Phụ lục III không có mã CAS -> {OUT_NO_CAS}")
    OUT_EXCLUDED.write_text(json.dumps(excluded, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(excluded)} chất bị Phụ lục III ghi NGOẠI TRỪ -> {OUT_EXCLUDED}")
