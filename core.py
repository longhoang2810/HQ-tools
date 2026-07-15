"""Dữ liệu & quy tắc dùng chung cho lookup.py và scan.py.
Nguồn: Phụ lục I-IV NĐ 24/2026/NĐ-CP + thủ tục NK tại NĐ 26/2026/NĐ-CP.
"""
import json
import re
from pathlib import Path

DATA = json.loads((Path(__file__).parent / "data" / "nd24_chemicals.json").read_text(encoding="utf-8"))
CAS_RE = re.compile(r"\b\d{2,7}-\d{2}-\d\b")

# ponytail: tóm tắt thủ tục chính, không thay thế văn bản gốc — luôn đọc kèm
# Điều được dẫn chiếu trước khi làm hồ sơ thật.
IMPORT_RULES = {
    "I": """Phụ lục I (hóa chất cơ bản trọng điểm) không tự nó phát sinh
  yêu cầu giấy phép riêng. Nếu hóa chất thuộc chương 28/29 Danh mục HS thì
  vẫn phải: (1) Khai báo hóa chất nhập khẩu qua Cổng một cửa quốc gia trước
  khi thông quan kèm hóa đơn thương mại + Phiếu an toàn hóa chất (NĐ 26,
  Điều 6); được miễn nếu nhập <10kg hoặc thuộc các trường hợp miễn trừ tại
  Điều 6.7.""",
    "II": """Phụ lục II (hóa chất sản xuất, kinh doanh có điều kiện):
  - Nhập khẩu để KINH DOANH: phải có Giấy chứng nhận đủ điều kiện kinh
    doanh hóa chất có điều kiện do UBND cấp tỉnh cấp (NĐ 26, Điều 8, 9, 10.2).
  - Nhập khẩu để tự sử dụng (không kinh doanh): không cần Giấy chứng nhận,
    nhưng phải công bố mục đích sử dụng trên Cơ sở dữ liệu chuyên ngành hóa
    chất (NĐ 26, Điều 10.3). Lưu ý: Điều 10.3 KHÔNG ấn định thời hạn và KHÔNG
    đặt việc công bố làm điều kiện thông quan — doanh nghiệp chủ động chọn
    thời điểm công bố; đây là nghĩa vụ với CSDL chuyên ngành, không phải cửa
    kiểm soát của cơ quan hải quan.
  - Bước BẮT BUỘC trước khi thông quan là khai báo hóa chất nhập khẩu qua
    Cổng một cửa quốc gia (NĐ 26, Điều 6); chính phản hồi khai báo mới có
    giá trị pháp lý để làm thủ tục thông quan (Điều 6.3.c). Cả hai trường hợp
    trên đều phải khai báo, trừ trường hợp được miễn trừ tại Điều 6.7.""",
    "III": """Phụ lục III (hóa chất cần kiểm soát đặc biệt — tiền chất công
  nghiệp / hóa chất Bảng 2, 3 / Công ước Rotterdam-Stockholm):
  - Bắt buộc có Giấy phép xuất khẩu, nhập khẩu hóa chất cần kiểm soát đặc
    biệt do Bộ Công Thương cấp, là điều kiện để thông quan (NĐ 26, Điều 14.2,
    14.4). Hồ sơ: văn bản đề nghị, hóa đơn thương mại, Phiếu an toàn hóa
    chất, báo cáo tình hình XNK/sử dụng/tồn trữ theo giấy phép đã cấp, và
    Giấy phép sản xuất/kinh doanh hóa chất kiểm soát đặc biệt tương ứng
    (NĐ 26, Điều 14.5). Thời hạn giấy phép: 06 tháng, gia hạn 1 lần.
  - MIỄN Giấy phép XNK nếu hóa chất chỉ xuất hiện trong hỗn hợp ở nồng độ
    dưới ngưỡng: Nhóm 1 <1%, Nhóm 2 <5% khối lượng hỗn hợp (NĐ 26, Điều
    21.2) — hàng nguyên chất/nồng độ trên ngưỡng thì KHÔNG được miễn.
  - Nếu NHẬP KHẨU để sản xuất sản phẩm/hàng hóa khác: phải lập tài khoản và
    công bố mục đích sử dụng trên Cơ sở dữ liệu chuyên ngành hóa chất KHI
    thực hiện việc nhập khẩu (NĐ 26, Điều 14.3). Điều 14.3 KHÔNG ấn định thời
    hạn cứng và KHÔNG phải điều kiện thông quan — khác với Giấy phép (Điều
    14.2 mới là điều kiện thông quan); doanh nghiệp chủ động thời điểm công bố.
  - Khi ĐƯA HÓA CHẤT VÀO SỬ DỤNG để sản xuất hàng hóa, dịch vụ: phải công bố
    loại hóa chất và mục đích sử dụng TRƯỚC 30 NGÀY tính đến lần sử dụng đầu
    tiên (hoặc khi thay đổi mục đích đã công bố) — mốc 30 ngày là mốc CỨNG
    gắn với khâu SỬ DỤNG, không phải khâu nhập khẩu (NĐ 26, Điều 15.1).
  - Nếu là tiền chất công nghiệp và XUẤT KHẨU (không phải nhập khẩu): cần
    thêm văn bản chấp thuận của Bộ Công an (NĐ 26, Điều 14.6.d).
  - CHUYỂN TIẾP (đang hiệu lực): hóa chất kiểm soát đặc biệt do NĐ 24 mới đưa
    vào Danh mục — KHÔNG thuộc Danh mục tiền chất/hạn chế SX-KD cũ (NĐ 113/2017,
    NĐ 82/2022) hay Danh mục hóa chất Bảng (NĐ 33/2024) — được MIỄN xuất trình
    hồ sơ Giấy phép XK/NK hóa chất kiểm soát đặc biệt đến trước 31/12/2026 (NĐ
    26, Điều 30.4). Tiền chất công nghiệp mới đưa vào được dùng Giấy chứng nhận
    đủ ĐK SX-KD cũ thay cho Giấy phép đến 31/12/2027 (Điều 30.5). Phải đối chiếu
    danh mục cũ để biết hóa chất có thuộc diện "mới" hay không.""",
    "IV": """Phụ lục IV (Bảng A — phải xây dựng Kế hoạch/Biện pháp phòng
  ngừa, ứng phó sự cố hóa chất): đây KHÔNG phải điều kiện nhập khẩu, mà là
  nghĩa vụ an toàn khi tồn trữ. Nếu khối lượng tồn trữ tại một thời điểm
  vượt ngưỡng ghi trong dữ liệu (cột threshold_kg), tổ chức phải có Kế
  hoạch phòng ngừa, ứng phó sự cố hóa chất được cơ quan có thẩm quyền phê
  duyệt hoặc Biện pháp tự ban hành (NĐ 24 Điều 3; NĐ 26 Điều 4.4). Vẫn áp
  dụng song song yêu cầu nhập khẩu của Phụ lục I/II/III nếu hóa chất đó
  cũng thuộc các phụ lục đó.""",
}

# Cờ ngắn gọn cho bảng tóm tắt (dùng khi quét nhiều CAS cùng lúc).
SHORT_FLAG = {
    "I": "Chỉ cần khai báo NK (nếu thuộc HS 28/29)",
    "II": "Không cần Giấy phép. NK để kinh doanh: cần GCN đủ điều kiện KD (Điều 10.2). NK để tự dùng: công bố mục đích sử dụng trên CSDL chuyên ngành — doanh nghiệp CHỦ ĐỘNG thời điểm, KHÔNG phải điều kiện thông quan (Điều 10.3). Bước bắt buộc trước thông quan là khai báo NK (Điều 6)",
    "III": "⚠ BẮT BUỘC Giấy phép XNK (Bộ Công Thương) — trừ khi nồng độ dưới ngưỡng miễn trừ (Điều 21), hoặc là chất mới do NĐ24 đưa vào được miễn xuất trình Giấy phép tới 31/12/2026 (Điều 30.4)",
    "IV": "Có ngưỡng tồn trữ — cần KH/BP ứng phó sự cố nếu vượt ngưỡng",
}

# Nguồn duy nhất cho mục "Các trường hợp được miễn trừ" — dùng chung cho
# CLI (lookup.py/scan.py) và trang HTML (build_html.py) để tránh lệch nội
# dung giữa hai nơi. Toàn văn: NĐ 26/2026/NĐ-CP.
EXEMPTIONS = [
    {
        "title": "1. Miễn khai báo hóa chất nhập khẩu",
        "cite": "Điều 6, khoản 7",
        "items": [
            "Hóa chất cần kiểm soát đặc biệt / hóa chất cấm đã được cấp Giấy phép nhập khẩu (khỏi khai báo riêng, vì đã qua thủ tục cấp phép).",
            "Nhập khẩu dưới 10 kg hóa chất thuộc chương 28, 29 Danh mục HS.",
            "Nhập khẩu dưới 1 kg hóa chất mới để thử nghiệm, đánh giá đặc tính hóa lý.",
            "Hỗn hợp chất không thuộc chương 28/29 nhưng có chứa hóa chất thuộc chương 28/29.",
        ],
    },
    {
        "title": "2. Miễn Giấy chứng nhận đủ điều kiện kinh doanh — Phụ lục II",
        "cite": "Điều 10, khoản 3",
        "items": [
            "Nhập khẩu hóa chất có điều kiện để tự sử dụng (không kinh doanh): không cần Giấy chứng nhận, chỉ cần công bố mục đích sử dụng trên Cơ sở dữ liệu chuyên ngành hóa chất.",
        ],
    },
    {
        "title": "3. Miễn theo ngưỡng nồng độ trong hỗn hợp chất",
        "cite": "Điều 21, khoản 1-3",
        "items": [
            "Khoản 1 — MIỄN CẤP Giấy chứng nhận, Giấy phép sản xuất, kinh doanh: áp dụng cho hóa chất có điều kiện, hóa chất cần kiểm soát đặc biệt có nồng độ dưới 0,1% khối lượng hỗn hợp chất.",
            "Khoản 2 — MIỄN CẤP Giấy phép xuất khẩu, nhập khẩu: áp dụng cho hóa chất cần kiểm soát đặc biệt Nhóm 1 có nồng độ dưới 1%, hoặc Nhóm 2 có nồng độ dưới 5% khối lượng hỗn hợp chất.",
            "Khoản 3 — MIỄN CẤP Giấy phép sản xuất, nhập khẩu: áp dụng cho hóa chất cấm có nồng độ dưới 0,1% khối lượng hỗn hợp chất.",
        ],
    },
    {
        "title": "4. Miễn trừ khác",
        "cite": "Điều 21, khoản 4 & 5",
        "items": [
            "(Điều 21.4) San chiết, pha chế hóa chất nhằm phục vụ TRỰC TIẾP cho hoạt động sản xuất nội bộ của chính tổ chức, cá nhân thực hiện việc san chiết, pha chế: miễn cấp Giấy chứng nhận / Giấy phép sản xuất, kinh doanh.",
            "(Điều 21.5) Tổ chức cho thuê đất KHÔNG kèm cơ sở vật chất để tồn trữ hóa chất; hoặc dịch vụ tồn trữ hóa chất có điều kiện / kiểm soát đặc biệt nồng độ dưới 0,1%: miễn Giấy chứng nhận đủ điều kiện hoạt động dịch vụ tồn trữ.",
        ],
    },
    {
        "title": "5. Miễn khi hóa chất nằm trong sản phẩm hoàn chỉnh",
        "cite": "Điều 21, khoản 6",
        "lead": (
            "MIỄN CẤP Giấy chứng nhận sản xuất, kinh doanh (với hóa chất có "
            "điều kiện) và Giấy phép sản xuất, kinh doanh, xuất khẩu, nhập "
            "khẩu (với hóa chất cần kiểm soát đặc biệt), khi hóa chất đó "
            "được chứa (không tách riêng) trong các sản phẩm sau:"
        ),
        "items": [
            "Dược phẩm, chế phẩm diệt khuẩn/côn trùng, thực phẩm, mỹ phẩm.",
            "Thức ăn chăn nuôi/thủy sản, thuốc thú y, thuốc BVTV, phân bón hữu cơ/sinh học/khoáng.",
            "Chất phóng xạ, vật liệu xây dựng, sơn, mực in.",
            "Sản phẩm gia dụng: keo dán, chất tẩy rửa, hóa mỹ phẩm.",
            "Xăng, dầu, condensate, naphta dùng chế biến xăng dầu.",
            "Pin, ắc quy, thiết bị y tế, thiết bị thí nghiệm.",
            "Lưu ý: được miễn giấy phép hóa chất KHÔNG miễn mọi nghĩa vụ — tổ chức, cá nhân nhập khẩu sản phẩm chứa hóa chất nguy hiểm vẫn phải công bố thông tin hàm lượng hóa chất nguy hiểm trước khi lưu thông (NĐ 26, Điều 28, 29).",
        ],
    },
]

EXEMPTIONS_WARNING = (
    "Phụ lục III (hóa chất cần kiểm soát đặc biệt) CHỈ được miễn Giấy phép "
    "xuất/nhập khẩu khi nồng độ trong hỗn hợp dưới ngưỡng ở mục 3 trên "
    "(Điều 21.2) — hàng nguyên chất hoặc nồng độ trên ngưỡng luôn bắt buộc "
    "có Giấy phép do Bộ Công Thương cấp (Điều 14.2), dù nhập để kinh doanh "
    "hay tự sử dụng."
)

NOTE_GAP = """Lưu ý: bộ dữ liệu này trích từ NĐ 24/2026 (Phụ lục I-IV) — KHÔNG
  bao trùm danh mục "hóa chất cấm" (Mục 4 NĐ 26) hay "Hóa chất Bảng 1" của
  Công ước vũ khí hóa học, vì hai văn bản này không liệt kê CAS cụ thể cho
  nhóm đó (chỉ có Bảng 2, Bảng 3). Nếu hóa chất có thể là Bảng 1 hoặc hóa
  chất cấm, kiểm tra thủ công NĐ 26 Điều 16-18 và Điều 3 Luật Hóa chất."""

ANNEX_ORDER = ["III", "II", "I", "IV"]  # ưu tiên hiển thị mức kiểm soát cao nhất trước


def rows_for(cas):
    return [r for r in DATA if r["cas"] == cas]


def extract_cas(text):
    """Trả về danh sách mã CAS duy nhất xuất hiện trong text, theo thứ tự gặp."""
    seen, out = set(), []
    for m in CAS_RE.findall(text):
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out


def annexes_for(cas):
    return {r["annex"] for r in rows_for(cas)}


def highest_annex(cas):
    """Phụ lục có mức kiểm soát cao nhất mà CAS này thuộc về (III > II > I > IV)."""
    present = annexes_for(cas)
    for a in ANNEX_ORDER:
        if a in present:
            return a
    return None


def cas_status(cas):
    """Trạng thái hiển thị cho 1 CAS. Trả (badge, text, note) — badge in
    {"ok","warn","unknown"}.

    ponytail: không tự nhận diện % hàm lượng từ mô tả (khai báo tự do dễ bị
    ghi sai định dạng/lộn xộn, đoán nhầm % có thể dẫn tới kết luận miễn
    trừ sai) — hóa chất Phụ lục III luôn báo "Cần Giấy phép"; cán bộ tự đối
    chiếu ngưỡng miễn trừ nồng độ ở Điều 21 (xem EXEMPTIONS/format_exemptions)
    bằng tài liệu khai báo gốc.
    """
    rows = rows_for(cas)
    if not rows:
        return ("unknown", "Không rõ", None)
    annex = highest_annex(cas)
    if annex != "III":
        return ("ok", "Không cần Giấy phép", None)
    return ("warn", "Cần Giấy phép", None)


def format_exemptions():
    lines = ["CÁC TRƯỜNG HỢP ĐƯỢC MIỄN TRỪ (NĐ 26/2026/NĐ-CP)", ""]
    for group in EXEMPTIONS:
        lines.append(f"{group['title']} ({group['cite']})")
        if "lead" in group:
            lines.append(f"  {group['lead']}")
        for item in group["items"]:
            lines.append(f"  - {item}")
        lines.append("")
    lines.append(EXEMPTIONS_WARNING)
    return "\n".join(lines)


def format_report(cas):
    rows = rows_for(cas)
    lines = []
    if not rows:
        lines.append(f"Không tìm thấy CAS {cas} trong Phụ lục I-IV của NĐ 24/2026/NĐ-CP.")
        lines.append(NOTE_GAP)
        return "\n".join(lines)
    lines.append(f"CAS {cas}: {rows[0]['name_vn']} ({rows[0]['name_en']})\n")
    seen_annex = set()
    for r in rows:
        lines.append(f"- {r['category']}")
        if "threshold_kg" in r:
            lines.append(f"  Ngưỡng khối lượng tồn trữ: {r['threshold_kg']} kg")
        seen_annex.add(r["annex"])
    lines.append("")
    for annex in ["I", "II", "III", "IV"]:
        if annex in seen_annex:
            lines.append(f"== Yêu cầu nhập khẩu (Phụ lục {annex}) ==")
            lines.append(IMPORT_RULES[annex])
            lines.append("")
    return "\n".join(lines)
