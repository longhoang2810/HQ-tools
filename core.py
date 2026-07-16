"""Dữ liệu & quy tắc dùng chung cho lookup.py và scan.py.
Nguồn: Phụ lục I-IV NĐ 24/2026/NĐ-CP; yêu cầu giấy tờ khi XNK tại NĐ 26/2026/NĐ-CP;
ngưỡng miễn trừ cập nhật theo NQ 19/2026/NQ-CP.

PHẠM VI: công cụ trả lời "hóa chất này CẦN GIẤY GÌ", nên luôn gọi đúng tên từng
loại giấy. Bốn loại giấy có thể gặp:
  1. Giấy phép xuất khẩu, nhập khẩu hóa chất KSĐB   -> khâu XNK (Phụ lục III)
  2. Giấy chứng nhận đủ điều kiện SX-KD hóa chất có điều kiện -> khâu SX-KD (PL II)
  3. Giấy phép sản xuất, kinh doanh hóa chất KSĐB   -> khâu SX-KD (PL III)
  4. Giấy chứng nhận đủ điều kiện hoạt động tồn trữ -> khâu tồn trữ dịch vụ
KHÔNG đưa vào: hồ sơ gồm những gì, trình tự, thủ tục cấp, thẩm quyền cấp — đó là
việc của cơ quan cấp phép, không phải câu hỏi "chất này cần giấy gì".
"""
import json
import re
import textwrap
from pathlib import Path

DATA = json.loads((Path(__file__).parent / "data" / "nd24_chemicals.json").read_text(encoding="utf-8"))
CAS_RE = re.compile(r"\b\d{2,7}-\d{2}-\d\b")

# ponytail: tóm tắt yêu cầu giấy tờ, không thay thế văn bản gốc — luôn đọc kèm
# Điều được dẫn chiếu trước khi làm hồ sơ thật.
#
# MỖI Ý = MỘT GẠCH ĐẦU DÒNG, KHÔNG bẻ dòng cứng trong chuỗi. Trước đây đây là
# chuỗi nhiều dòng đã bẻ sẵn + thụt lề, nên trang HTML (white-space: pre-wrap)
# hiện ra thụt lề giữa câu, xuống dòng loạn; và assert `"x y" in rule` đỏ oan vì
# cụm từ bị ngắt. Để người render tự ngắt dòng theo bề rộng của họ.
# Không nhắc lại chi tiết miễn trừ ở đây — đã có mục "Các trường hợp được miễn trừ".
IMPORT_RULES = {
    "I": [
        "Không phát sinh giấy phép riêng.",
        "Nếu thuộc chương 28/29 Danh mục HS: phải khai báo hóa chất nhập khẩu qua Cổng một cửa quốc gia trước thông quan, kèm hóa đơn thương mại và Phiếu an toàn hóa chất (Điều 6). Miễn khai báo nếu nhập dưới 10 kg (Điều 6.7).",
    ],
    "II": [
        "Nhập khẩu để KINH DOANH: phải có Giấy chứng nhận đủ điều kiện sản xuất, kinh doanh hóa chất có điều kiện (Điều 8, 9, 10.2).",
        "Nhập khẩu để TỰ DÙNG: không cần Giấy chứng nhận; chỉ công bố mục đích sử dụng trên Cơ sở dữ liệu chuyên ngành hóa chất (Điều 10.3).",
        "Việc công bố KHÔNG phải điều kiện thông quan và không có thời hạn cứng — doanh nghiệp chủ động chọn thời điểm công bố (Điều 10.3).",
        "Điều kiện thông quan là khai báo hóa chất nhập khẩu qua Cổng một cửa quốc gia (Điều 6); phản hồi khai báo mới có giá trị pháp lý để làm thủ tục (Điều 6.3.c).",
    ],
    "III": [
        "PHẢI CÓ: Giấy phép xuất khẩu, nhập khẩu hóa chất cần kiểm soát đặc biệt — đây là điều kiện thông quan (Điều 14.2).",
        "Đã được cấp Giấy phép nhập khẩu thì MIỄN khai báo hóa chất (Điều 6.7.a) — không phải khai báo riêng nữa.",
        "Các trường hợp được miễn Giấy phép XNK (ngưỡng nồng độ, sản phẩm hoàn chỉnh, thí nghiệm, XNK tại chỗ): xem mục \"Các trường hợp được miễn trừ\" bên dưới (Điều 21).",
        "Nhập khẩu để sản xuất sản phẩm khác: lập tài khoản và công bố mục đích sử dụng trên Cơ sở dữ liệu chuyên ngành KHI nhập khẩu (Điều 14.3) — không có thời hạn cứng, không phải điều kiện thông quan.",
        "Đưa vào SỬ DỤNG lần đầu, hoặc đổi mục đích đã công bố: phải công bố TRƯỚC 30 NGÀY — mốc cứng này gắn với khâu SỬ DỤNG, không phải khâu nhập khẩu (Điều 15.1).",
        "Xuất khẩu tiền chất công nghiệp: cần thêm văn bản chấp thuận của Bộ Công an (Điều 14.6.d).",
        "Phân biệt giấy: Giấy phép XNK (khâu XNK) khác Giấy phép sản xuất, kinh doanh hóa chất KSĐB (khâu SX-KD). Thuộc Phụ lục III là luôn cần Giấy phép XNK khi xuất/nhập khẩu.",
    ],
    "IV": [
        "KHÔNG phải điều kiện nhập khẩu — đây là nghĩa vụ an toàn khi tồn trữ.",
        "Tồn trữ tại một thời điểm vượt ngưỡng: phải có Kế hoạch phòng ngừa, ứng phó sự cố hóa chất được cơ quan có thẩm quyền phê duyệt, hoặc Biện pháp tự ban hành (NĐ 24 Điều 3; NĐ 26 Điều 4.4).",
        "Vẫn áp dụng song song yêu cầu của Phụ lục I/II/III nếu chất cũng thuộc các phụ lục đó.",
    ],
}

# Ẩn khối phụ lục nào khi phụ lục khác đã có mặt. Điều 6.7.a: hóa chất KSĐB đã
# được cấp Giấy phép nhập khẩu thì MIỄN khai báo -> với chất Phụ lục III, khối
# Phụ lục I (vốn chỉ nói về khai báo) là thừa và gây hiểu nhầm "phải khai báo".
# Nhúng sang JS (build_html.py) để CLI và HTML dùng CHUNG một quy tắc.
SUPPRESS_ANNEX = {"III": ["I"]}


def annexes_to_explain(present):
    """Các phụ lục cần in phần 'Yêu cầu nhập khẩu', theo thứ tự, đã bỏ khối bị ẩn."""
    hidden = {h for a in present for h in SUPPRESS_ANNEX.get(a, [])}
    return [a for a in ["I", "II", "III", "IV"] if a in present and a not in hidden]

# Bảng tóm tắt chỉ hiện verdict (pill). KHÔNG còn cờ tóm tắt kèm mỗi dòng: nội
# dung của chúng lặp lại y nguyên IMPORT_RULES, vốn đã hiện ngay dưới bảng cho
# MỌI phụ lục mà chất thuộc về. Giữ hai nơi = hai nguồn phải đồng bộ tay.
#
# Chữ verdict — nguồn DUY NHẤT, dùng chung CLI và HTML (build_html.py nhúng qua
# JSON). Từng lệch thật: JS hard-code "Cần Giấy phép" trong khi core.py đã đổi
# thành tên đầy đủ -> trang HTML mất luôn phần "giấy gì". Đừng viết tay lại trong JS.
VERDICT = {
    "unknown": "Không rõ",
    "pl3": "Cần Giấy phép XNK hóa chất KSĐB",
    "other_obligation": "Không cần Giấy phép XNK — có nghĩa vụ khác",
    "none": "Không cần Giấy phép XNK",
    "note_prefix": "Không cần Giấy phép XNK, nhưng có nghĩa vụ khác: ",
}

# Nghĩa vụ song song NGOÀI Giấy phép XNK (cho hóa chất KHÔNG thuộc PL III) —
# để trạng thái "xanh" không bị đọc là "không phải làm gì". Dùng chung CLI/HTML.
OBLIGATIONS = {
    "II": "Phụ lục II — Giấy chứng nhận đủ điều kiện SX-KD hóa chất có điều kiện (nếu NK để kinh doanh) hoặc công bố mục đích sử dụng (nếu NK để tự dùng)",
    "IV": "Phụ lục IV — Kế hoạch/Biện pháp ứng phó sự cố nếu tồn trữ vượt ngưỡng",
}

# Nguồn duy nhất cho mục "Các trường hợp được miễn trừ" — dùng chung cho
# CLI (lookup.py/scan.py) và trang HTML (build_html.py) để tránh lệch nội
# dung giữa hai nơi. Nguồn: NĐ 26/2026/NĐ-CP Điều 21.
# ponytail: các ngưỡng nồng độ dưới đây theo NQ 19/2026/NQ-CP — KHÔNG phải giá
# trị gốc của NĐ 26. NQ 19 nới: khoản 1 & 5 (<0,1% → ≤1%), khoản 2 đổi biên
# (< → ≤), GIỮ khoản 3 (<0,1%), và thêm khoản 7, 8 (NĐ 26 gốc chỉ tới khoản 6).
#
# CƠ CHẾ (vì sao dùng số của NQ 19 dù NĐ 26 vẫn ghi <0,1%): NQ 19 không sửa chữ
# trong NĐ 26 mà ĐÈ LÊN khi áp dụng — Điều 8.4 NQ 19: "nếu quy định về thẩm
# quyền... điều kiện kinh doanh, trình tự, thủ tục trong Nghị quyết này khác với
# các VBQPPL có liên quan thì thực hiện theo quy định tại Nghị quyết này". Ngưỡng
# Điều 21 nằm ở Phụ lục III NQ 19 ("cắt giảm, đơn giản hóa TTHC") nên thuộc diện
# được đè. Hiệu lực 29/4/2026; NQ 19 tự hết hiệu lực 01/3/2027, hoặc SỚM HƠN khi
# có nghị định quy định cùng nội dung có hiệu lực (Điều 8.3) — khi đó phải đối
# chiếu lại NĐ 26 gốc: khoản 1/5 = <0,1%, khoản 2 = <1% (Nhóm 1) / <5% (Nhóm 2),
# và bỏ khoản 7, 8.
#
# NQ 19 KHÔNG thêm/bớt hóa chất nào (không chứa mã CAS); phần phân cấp thẩm quyền
# cấp phép của NQ 19 là "hồ sơ, trình tự, thủ tục" -> ngoài phạm vi công cụ này.
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
        "title": "6. Miễn Giấy phép XNK bổ sung (NQ 19 thêm mới)",
        "cite": "Điều 21, khoản 7-8 (NQ 19/2026/NQ-CP bổ sung, NĐ 26 gốc chỉ tới khoản 6)",
        "items": [
            "Khoản 7 — MIỄN CẤP Giấy phép XUẤT KHẨU, NHẬP KHẨU hóa chất cần kiểm soát đặc biệt dùng trong lĩnh vực thí nghiệm, khối lượng ≤ 1mg/lần nhập khẩu.",
            "Khoản 8 — MIỄN CẤP Giấy phép XUẤT KHẨU, NHẬP KHẨU hóa chất cần kiểm soát đặc biệt với xuất khẩu, nhập khẩu tại chỗ; và mua bán hóa chất giữa doanh nghiệp trong khu hải quan riêng với doanh nghiệp nội địa.",
        ],
    },
]

EXEMPTIONS_WARNING = (
    "Phụ lục III (hóa chất cần kiểm soát đặc biệt): hàng nguyên chất hoặc "
    "nồng độ trên ngưỡng luôn bắt buộc có Giấy phép xuất khẩu, nhập khẩu hóa "
    "chất cần kiểm soát đặc biệt (Điều 14.2) — TRỪ khi rơi vào một trong các "
    "trường hợp miễn ở Điều 21: nồng độ dưới ngưỡng (khoản 2: Nhóm 1 ≤1%, "
    "Nhóm 2 ≤5%), hóa chất nằm trong sản phẩm hoàn chỉnh (khoản 6), thí "
    "nghiệm ≤1mg (khoản 7), hoặc XNK tại chỗ (khoản 8)."
)

NOTE_GAP = (
    'Không có trong dữ liệu KHÔNG có nghĩa là không cần giấy: bộ dữ liệu này trích từ '
    'Phụ lục I-IV NĐ 24/2026, không bao trùm danh mục "hóa chất cấm" (Mục 4 NĐ 26) hay '
    '"Hóa chất Bảng 1" của Công ước vũ khí hóa học — hai văn bản này không liệt kê CAS '
    'cụ thể cho nhóm đó (chỉ có Bảng 2, Bảng 3). Kiểm tra thủ công NĐ 26 Điều 16-18 và '
    'Điều 3 Luật Hóa chất.'
)

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
        return ("unknown", VERDICT["unknown"], None)
    present = annexes_for(cas)
    if "III" in present:
        return ("warn", VERDICT["pl3"], None)
    # Không thuộc PL III: không cần Giấy phép XNK, nhưng vẫn có thể có nghĩa vụ
    # Phụ lục II (Giấy chứng nhận/công bố) và/hoặc Phụ lục IV (KH ứng phó sự cố)
    # — nêu rõ để "xanh" không bị đọc là "không phải làm gì".
    extra = [OBLIGATIONS[a] for a in ("II", "IV") if a in present]
    if extra:
        return ("ok", VERDICT["other_obligation"], VERDICT["note_prefix"] + "; ".join(extra) + ".")
    return ("ok", VERDICT["none"], None)


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
        # CLI in báo cáo đứng một mình (lookup.py) nên phải tự nói tra ra gì; trang
        # HTML thì tiêu đề thẻ đã ghi "— không có trong dữ liệu", không lặp lại.
        lines.append(f"CAS {cas}: không có trong dữ liệu NĐ 24 (Phụ lục I-IV).")
        lines.append("")
        lines.append(textwrap.fill(NOTE_GAP, width=78))
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
    for annex in annexes_to_explain(seen_annex):
        lines.append(f"== Yêu cầu nhập khẩu (Phụ lục {annex}) ==")
        for bullet in IMPORT_RULES[annex]:
            lines.append(textwrap.fill(bullet, width=78, initial_indent="  - ", subsequent_indent="    "))
        lines.append("")
    return "\n".join(lines)
