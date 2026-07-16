"""Dữ liệu & quy tắc dùng chung cho lookup.py và scan.py.
Nguồn: Phụ lục I-IV NĐ 24/2026/NĐ-CP; thủ tục NK tại NĐ 26/2026/NĐ-CP;
ngưỡng miễn trừ & phân cấp thẩm quyền cấp phép cập nhật theo NQ 19/2026/NQ-CP;
danh mục "quy định cũ" cho trạng thái chuyển tiếp Điều 30.4 lấy từ NĐ 113/2017,
NĐ 82/2022 (tiền chất + hạn chế SX-KD) và NĐ 33/2024 (hóa chất Bảng).
"""
import json
import re
from pathlib import Path

DATA = json.loads((Path(__file__).parent / "data" / "nd24_chemicals.json").read_text(encoding="utf-8"))
CAS_RE = re.compile(r"\b\d{2,7}-\d{2}-\d\b")

# Ba danh mục "quy định cũ" mà Điều 30.4/30.5 NĐ 26/2026 dẫn chiếu để xác định
# trạng thái chuyển tiếp cho hóa chất Phụ lục III: tiền chất công nghiệp + hạn chế
# SX-KD (NĐ 113/2017 hợp NĐ 82/2022) và hóa chất Bảng (NĐ 33/2024). Sinh từ
# extract_old.py. Lưu ý: Bảng 1 & 2 của NĐ 33 định nghĩa nhiều chất theo HỌ (không
# có CAS rời) nên tra theo CAS vẫn có thể sót -> giữ fail-safe (xem cas_status).
_OLD = json.loads((Path(__file__).parent / "data" / "old_cas.json").read_text(encoding="utf-8"))
OLD_TIEN_CHAT = set(_OLD["tien_chat_cong_nghiep"])
OLD_HAN_CHE = set(_OLD["han_che_sxkd"])
OLD_BANG = set(_OLD["hoa_chat_bang"])
OLD_ALL = OLD_TIEN_CHAT | OLD_HAN_CHE | OLD_BANG

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
    biệt, là điều kiện để thông quan (NĐ 26, Điều 14.2, 14.4). THẨM QUYỀN
    CẤP: từ 29/5/2026 theo NQ 19/2026/NQ-CP (phân cấp), Giấy phép XNK hóa
    chất KSĐB NHÓM 1 và Giấy phép nhập khẩu hóa chất cấm (phần thuộc thẩm
    quyền Bộ Công Thương) do UBND cấp tỉnh cấp thay vì Bộ Công Thương; hóa
    chất KSĐB Nhóm 2 (Bảng 2, 3) vẫn do Bộ Công Thương cấp. Hồ sơ: văn bản
    đề nghị, hóa đơn thương mại, Phiếu an toàn hóa chất, báo cáo tình hình
    XNK/sử dụng/tồn trữ theo giấy phép đã cấp, và Giấy phép sản xuất/kinh
    doanh hóa chất kiểm soát đặc biệt tương ứng (NĐ 26, Điều 14.5). Thời hạn
    giấy phép: 06 tháng, gia hạn 1 lần.
  - MIỄN Giấy phép XNK nếu hóa chất chỉ xuất hiện trong hỗn hợp ở nồng độ
    dưới ngưỡng: Nhóm 1 ≤1%, Nhóm 2 ≤5% khối lượng hỗn hợp (NĐ 26 Điều 21.2,
    ngưỡng cập nhật theo NQ 19/2026/NQ-CP) — hàng nguyên chất/nồng độ trên
    ngưỡng thì KHÔNG được miễn theo khoản này (nhưng vẫn có thể được miễn
    theo Điều 21 khoản 6/7/8 — xem "Các trường hợp được miễn trừ").
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
    "III": "⚠ BẮT BUỘC Giấy phép XNK — trừ khi nồng độ dưới ngưỡng miễn trừ (Điều 21) hoặc là chất mới do NĐ24 đưa vào được miễn xuất trình Giấy phép tới 31/12/2026 (Điều 30.4). Cấp phép: KSĐB Nhóm 1 & hóa chất cấm → UBND cấp tỉnh (từ 29/5/2026, NQ 19); Nhóm 2 → Bộ Công Thương",
    "IV": "Có ngưỡng tồn trữ — cần KH/BP ứng phó sự cố nếu vượt ngưỡng",
}

# Nghĩa vụ song song NGOÀI Giấy phép XNK (cho hóa chất KHÔNG thuộc PL III) —
# để trạng thái "xanh" không bị đọc là "không phải làm gì". Dùng chung CLI/HTML.
OBLIGATIONS = {
    "II": "Phụ lục II — GCN đủ điều kiện KD (nếu NK để KD) hoặc công bố mục đích sử dụng (nếu tự dùng)",
    "IV": "Phụ lục IV — Kế hoạch/Biện pháp ứng phó sự cố nếu tồn trữ vượt ngưỡng",
}

# Nguồn duy nhất cho mục "Các trường hợp được miễn trừ" — dùng chung cho
# CLI (lookup.py/scan.py) và trang HTML (build_html.py) để tránh lệch nội
# dung giữa hai nơi. Nguồn: NĐ 26/2026/NĐ-CP Điều 21.
# ponytail: các ngưỡng nồng độ dưới đây cập nhật theo NQ 19/2026/NQ-CP (hiệu
# lực 29/4/2026, hết hiệu lực 01/3/2027) — KHÔNG phải giá trị gốc của NĐ 26.
# NQ 19 nới: khoản 1 & 5 (<0,1% → ≤1%), khoản 2 đổi biên (< → ≤), GIỮ khoản 3
# (<0,1%), và thêm khoản 7, 8, 9. Phân cấp thẩm quyền cấp phép (Bộ Công Thương
# → UBND cấp tỉnh cho KSĐB Nhóm 1 & hóa chất cấm) hiệu lực 29/5/2026 (chậm 30
# ngày — Điều 3 + Phụ lục I NQ 19). Tới 01/3/2027 nếu chưa có VBQPPL thường
# thay thế thì đối chiếu lại NĐ 26 gốc (khoản 1/5 = <0,1%).
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
        "title": "3. Miễn theo ngưỡng nồng độ — theo TỪNG loại giấy / hoạt động",
        "cite": "Điều 21, khoản 1-3 (ngưỡng khoản 1/2 cập nhật theo NQ 19/2026/NQ-CP)",
        "items": [
            "Khoản 1 — MIỄN CẤP Giấy chứng nhận / Giấy phép SẢN XUẤT, KINH DOANH: hóa chất có điều kiện và hóa chất cần kiểm soát đặc biệt có hàm lượng ≤ 1% khối lượng hỗn hợp chất. (NQ 19 nới từ <0,1%.)",
            "Khoản 2 — MIỄN CẤP Giấy phép XUẤT KHẨU, NHẬP KHẨU: hóa chất cần kiểm soát đặc biệt Nhóm 1 có hàm lượng ≤ 1%, hoặc Nhóm 2 có hàm lượng ≤ 5% khối lượng hỗn hợp chất. (NQ 19 đổi biên < thành ≤.)",
            "Khoản 3 — MIỄN CẤP Giấy phép SẢN XUẤT, NHẬP KHẨU hóa chất cấm có nồng độ < 0,1% khối lượng hỗn hợp chất. (NQ 19 GIỮ NGUYÊN ngưỡng gốc NĐ 26.)",
        ],
    },
    {
        "title": "4. Miễn trừ khác",
        "cite": "Điều 21, khoản 4 & 5",
        "items": [
            "(Điều 21.4) San chiết, pha chế hóa chất nhằm phục vụ TRỰC TIẾP cho hoạt động sản xuất nội bộ của chính tổ chức, cá nhân thực hiện việc san chiết, pha chế: miễn cấp Giấy chứng nhận / Giấy phép sản xuất, kinh doanh.",
            "(Điều 21.5) Tổ chức cho thuê đất KHÔNG kèm cơ sở vật chất để tồn trữ hóa chất; hoặc dịch vụ tồn trữ hóa chất có điều kiện / kiểm soát đặc biệt hàm lượng ≤ 1%: miễn Giấy chứng nhận đủ điều kiện hoạt động dịch vụ tồn trữ. (NQ 19 nới từ <0,1%.)",
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
    {
        "title": "6. Miễn Giấy phép XNK bổ sung & miễn xuất trình hồ sơ (NQ 19 thêm mới)",
        "cite": "Điều 21, khoản 7-9 (NQ 19/2026/NQ-CP bổ sung, NĐ 26 gốc chỉ tới khoản 6)",
        "items": [
            "Khoản 7 — MIỄN CẤP Giấy phép XUẤT KHẨU, NHẬP KHẨU hóa chất cần kiểm soát đặc biệt dùng trong lĩnh vực thí nghiệm, khối lượng ≤ 1mg/lần nhập khẩu.",
            "Khoản 8 — MIỄN CẤP Giấy phép XUẤT KHẨU, NHẬP KHẨU hóa chất cần kiểm soát đặc biệt với xuất khẩu, nhập khẩu tại chỗ; và mua bán hóa chất giữa doanh nghiệp trong khu hải quan riêng với doanh nghiệp nội địa.",
            "Khoản 9 — MIỄN XUẤT TRÌNH hồ sơ về Giấy phép sản xuất, kinh doanh hóa chất cần kiểm soát đặc biệt, đến trước 31/12/2026, khi XNK hóa chất thuộc Danh mục KSĐB của NĐ 24 mà trước đây KHÔNG là hạn chế SX-KD và không là tiền chất công nghiệp theo NĐ 113/2017 & NĐ 82/2022. (Đây là miễn xuất trình hồ sơ Giấy phép SX-KD — khác Điều 30.4 vốn miễn xuất trình Giấy phép XK/NK; trạng thái từng CAS xem mục 'Trạng thái chuyển tiếp'.)",
        ],
    },
]

EXEMPTIONS_WARNING = (
    "Phụ lục III (hóa chất cần kiểm soát đặc biệt): hàng nguyên chất hoặc "
    "nồng độ trên ngưỡng luôn bắt buộc có Giấy phép xuất/nhập khẩu (Điều "
    "14.2) — TRỪ khi rơi vào một trong các trường hợp miễn ở Điều 21: nồng "
    "độ dưới ngưỡng (khoản 2: Nhóm 1 ≤1%, Nhóm 2 ≤5%), hóa chất nằm trong "
    "sản phẩm hoàn chỉnh (khoản 6), thí nghiệm ≤1mg (khoản 7), hoặc XNK tại "
    "chỗ (khoản 8). THẨM QUYỀN CẤP: từ 29/5/2026 theo NQ 19/2026/NQ-CP, Giấy "
    "phép của KSĐB Nhóm 1 và hóa chất cấm (phần thuộc Bộ Công Thương) do UBND "
    "cấp tỉnh cấp; hóa chất KSĐB Nhóm 2 vẫn do Bộ Công Thương cấp."
)

NOTE_GAP = """Lưu ý: bộ dữ liệu này trích từ NĐ 24/2026 (Phụ lục I-IV) — KHÔNG
  bao trùm danh mục "hóa chất cấm" (Mục 4 NĐ 26) hay "Hóa chất Bảng 1" của
  Công ước vũ khí hóa học, vì hai văn bản này không liệt kê CAS cụ thể cho
  nhóm đó (chỉ có Bảng 2, Bảng 3). Nếu hóa chất có thể là Bảng 1 hoặc hóa
  chất cấm, kiểm tra thủ công NĐ 26 Điều 16-18 và Điều 3 Luật Hóa chất."""

ANNEX_ORDER = ["III", "II", "I", "IV"]  # ưu tiên hiển thị mức kiểm soát cao nhất trước


def rows_for(cas):
    return [r for r in DATA if r["cas"] == cas]


def _kg(threshold):
    """'5.000' -> 5000, '150 (net)' -> 150. Dùng để so sánh ngưỡng theo số."""
    return int(re.sub(r"\D", "", threshold.split("(")[0]))


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
    present = annexes_for(cas)
    if "III" in present:
        return ("warn", "Cần Giấy phép", None)
    # Không thuộc PL III: không cần Giấy phép XNK, nhưng vẫn có thể có nghĩa vụ
    # Phụ lục II (GCN/công bố) và/hoặc Phụ lục IV (KH ứng phó sự cố) — nêu rõ
    # để "xanh" không bị đọc là "không phải làm gì".
    extra = [OBLIGATIONS[a] for a in ("II", "IV") if a in present]
    if extra:
        note = "Không cần Giấy phép XNK, nhưng có nghĩa vụ khác: " + "; ".join(extra) + "."
        return ("ok", "Không cần Giấy phép XNK — có nghĩa vụ khác", note)
    return ("ok", "Không cần Giấy phép", None)


def transitional_status(cas):
    """Trạng thái chuyển tiếp NĐ 26 Điều 30.4/30.5 cho hóa chất Phụ lục III
    (kiểm soát đặc biệt). Trả (state, text) hoặc None nếu CAS không thuộc PL III.

    state:
      - "cu"  : có trong ≥1 trong ba danh mục cũ -> KHÔNG được miễn Điều 30.4.
      - "moi" : không trùng CAS ở cả ba danh mục -> đủ căn cứ áp dụng miễn Điều 30.4.

    Đã tích hợp đủ ba danh mục Điều 30.4 dẫn chiếu (tiền chất + hạn chế SX-KD theo
    NĐ 113/2017 hợp NĐ 82/2022; hóa chất Bảng NĐ 33/2024). Vẫn giữ fail-safe: verdict
    chính của PL III luôn là 'Cần Giấy phép' (cas_status), đây chỉ là ghi chú chuyển
    tiếp; và Bảng 1/2 định nghĩa theo HỌ chất nên 'moi' chưa loại trừ tuyệt đối.
    """
    if "III" not in annexes_for(cas):
        return None
    if cas in OLD_ALL:
        which = []
        if cas in OLD_TIEN_CHAT:
            which.append("tiền chất công nghiệp")
        if cas in OLD_HAN_CHE:
            which.append("hạn chế SX-KD")
        if cas in OLD_BANG:
            which.append("hóa chất Bảng (NĐ 33/2024)")
        return (
            "cu",
            "Hóa chất CŨ — đã có trong danh mục cũ ("
            + " & ".join(which)
            + "). KHÔNG thuộc diện miễn xuất trình Giấy phép của Điều 30.4; vẫn cần "
            "Giấy phép, nhưng có thể dùng giấy tờ cũ thay thế: tiền chất công nghiệp "
            "-> Giấy chứng nhận đủ điều kiện (Điều 30.5, đến 31/12/2027); hóa chất "
            "Bảng / hạn chế SX-KD -> Giấy phép SX-KD đã cấp (Điều 30.6, đến khi hết "
            "hạn). Đối chiếu văn bản gốc.",
        )
    return (
        "moi",
        "Không trùng CAS ở CẢ BA danh mục cũ đã tích hợp (tiền chất công nghiệp & "
        "hạn chế SX-KD theo NĐ 113/2017 + NĐ 82/2022; hóa chất Bảng theo NĐ 33/2024) "
        "-> ĐỦ CĂN CỨ áp dụng miễn xuất trình Giấy phép XNK tới 31/12/2026 (Điều "
        "30.4). LƯU Ý: đây là miễn XUẤT TRÌNH giấy phép, không phải miễn Giấy phép; "
        "và Bảng 1 & 2 của NĐ 33 định nghĩa nhiều chất theo HỌ (dẫn xuất không có CAS "
        "rời) — nếu chất thuộc một họ CWC thì vẫn là hóa chất Bảng, đối chiếu công "
        "thức khi nghi ngờ.",
    )


def transitional_flag_short(cas):
    """Cờ ngắn cho bảng quét (scan). None nếu không phải PL III."""
    st = transitional_status(cas)
    if not st:
        return None
    state, _ = st
    if state == "cu":
        return "Chuyển tiếp Điều 30.4: hóa chất CŨ (có trong NĐ 113/2017, NĐ 82/2022 hoặc Bảng NĐ 33/2024) — KHÔNG được miễn, vẫn cần Giấy phép"
    return "Chuyển tiếp Điều 30.4: đủ căn cứ MIỄN xuất trình Giấy phép tới 31/12/2026 (không thuộc 3 danh mục cũ NĐ 113/82/33) — lưu ý Bảng 1/2 định nghĩa theo họ chất"


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
    # Một chất có thể được liệt kê ở Phụ lục IV với nhiều ngưỡng tồn trữ khác
    # nhau tùy phân loại (hóa chất KSĐB / hóa chất cấm). Dữ liệu không mang nhãn
    # phân loại theo từng ngưỡng -> cảnh báo thay vì đoán.
    iv_thr = {r["threshold_kg"] for r in rows if r["annex"] == "IV" and "threshold_kg" in r}
    if len(iv_thr) > 1:
        ordered = sorted(iv_thr, key=_kg)
        lines.append(
            f"  ⚠ Chất này có nhiều ngưỡng tồn trữ Phụ lục IV khác nhau "
            f"({', '.join(ordered)} kg) tùy phân loại (hóa chất cần kiểm soát "
            f"đặc biệt / hóa chất cấm) — xác định đúng phân loại để áp ngưỡng "
            f"phù hợp; nếu chưa rõ, ngưỡng thấp nhất ({ordered[0]} kg) là mức "
            f"thận trọng."
        )
    lines.append("")
    for annex in ["I", "II", "III", "IV"]:
        if annex in seen_annex:
            lines.append(f"== Yêu cầu nhập khẩu (Phụ lục {annex}) ==")
            lines.append(IMPORT_RULES[annex])
            lines.append("")
            if annex == "III":
                st = transitional_status(cas)
                if st:
                    lines.append("-- Trạng thái chuyển tiếp (NĐ 26, Điều 30.4/30.5) --")
                    lines.append(st[1])
                    lines.append("")
    return "\n".join(lines)
