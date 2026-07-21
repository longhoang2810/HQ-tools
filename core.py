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
# Mục Phụ lục III chỉ có tên, ô mã CAS ghi '---' (extract.py tách sang file riêng).
PL3_NO_CAS = json.loads((Path(__file__).parent / "data" / "nd24_pl3_no_cas.json").read_text(encoding="utf-8"))
# Chất nằm dưới dòng "Ngoại trừ:" của Phụ lục III — nghị định loại trừ khỏi mục đó
# (nguyên văn Công ước CWC). extract.py KHÔNG đưa vào DATA; giữ ở đây để trả lời
# được câu "sao mã này in trong bảng Phụ lục III mà tool bảo không phải PL III".
PL3_EXCLUDED = json.loads((Path(__file__).parent / "data" / "nd24_pl3_ngoai_tru.json").read_text(encoding="utf-8"))
# re.ASCII: \b của Python mặc định là unicode nên "ấ67-56-1" KHÔNG match (coi "ấ"
# là word char), trong khi \b của JS (build_html.py) là ASCII nên match — CLI từng
# sót CAS dính chữ có dấu mà trang HTML lại thấy. ASCII làm hai bên hành xử y hệt.
CAS_RE = re.compile(r"\b\d{2,7}-\d{2}-\d\b", re.ASCII)

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
    "III": [
        "PHẢI CÓ: Giấy phép xuất khẩu, nhập khẩu hóa chất cần kiểm soát đặc biệt — đây là điều kiện thông quan (Điều 14.2).",
        # Nguồn CV 2595/HC-QLHC KHÔNG có trong repo (như PENALTY_WARNING) -> đối
        # chiếu bản gốc công văn trước khi sửa câu này.
        "Chấp nhận Giấy phép dạng file PDF có chữ ký số của Bộ Công Thương để thông quan — không bắt buộc bản giấy (Công văn 2595/HC-QLHC ngày 31/12/2025 của Cục Hóa chất).",
        "Đã được cấp Giấy phép nhập khẩu thì MIỄN khai báo hóa chất (Điều 6.7.a).",
        "Các trường hợp được miễn Giấy phép XNK quy định tại Điều 21 NĐ 26/2026/NĐ-CP.",
        "Nhập khẩu để sản xuất sản phẩm khác: lập tài khoản và công bố mục đích sử dụng trên Cơ sở dữ liệu chuyên ngành KHI nhập khẩu (Điều 14.3) không phải điều kiện thông quan.",
        "Đưa vào SỬ DỤNG lần đầu, hoặc đổi mục đích đã công bố: phải công bố LOẠI HÓA CHẤT VÀ MỤC ĐÍCH SỬ DỤNG (rộng hơn công bố mục đích lúc nhập khẩu ở trên) TRƯỚC 30 NGÀY — mốc này gắn với khâu SỬ DỤNG, không phải khâu nhập khẩu (Điều 15.1).",
        "Xuất khẩu tiền chất công nghiệp: cần thêm văn bản chấp thuận của Bộ Công an (Điều 14.6.d).",
    ],
}

IMPORT_ANNEXES = ("I", "III")

# Ẩn khối phụ lục nào khi phụ lục khác đã có mặt. Điều 6.7.a: hóa chất KSĐB đã
# được cấp Giấy phép nhập khẩu thì MIỄN khai báo -> với chất Phụ lục III, khối
# Phụ lục I (vốn chỉ nói về khai báo) là thừa và gây hiểu nhầm "phải khai báo".
# Nhúng sang JS (build_html.py) để CLI và HTML dùng CHUNG một quy tắc.
SUPPRESS_ANNEX = {"III": ["I"]}


def annexes_to_explain(present):
    """Các phụ lục cần in phần 'Yêu cầu nhập khẩu', theo thứ tự, đã bỏ khối bị ẩn."""
    hidden = {h for a in present for h in SUPPRESS_ANNEX.get(a, [])}
    return [a for a in IMPORT_ANNEXES if a in present and a not in hidden]

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
}

# Phụ lục làm verdict "xanh" thành "xanh nhưng còn nghĩa vụ khác" — để không bị
# đọc thành "không phải làm gì". Chỉ dùng để CHỌN CHỮ VERDICT; nghĩa vụ cụ thể do
# khối IMPORT_RULES của chính phụ lục đó nói, không tóm tắt lại lần nữa ở cuối.
OTHER_OBLIGATION_ANNEXES = ("II",)

# Nghĩa vụ Phụ lục II không phải Giấy phép XNK. Hiển thị một lần ở cuối mục
# miễn trừ thay vì lặp lại trong chi tiết từng CAS. In THƯỜNG TRỰC như mục miễn
# trừ (tham khảo chung, không phải kết luận cho lô hàng) — tiêu đề phải tự nói
# rõ phạm vi để không bị đọc thành "lô này cũng phải có Giấy chứng nhận".
OTHER_OBLIGATIONS_TITLE = "Nghĩa vụ và miễn Giấy chứng nhận — chỉ áp dụng cho hóa chất Phụ lục II"
OTHER_OBLIGATIONS = [
    "Nhập khẩu để KINH DOANH: phải có Giấy chứng nhận đủ điều kiện sản xuất, kinh doanh hóa chất có điều kiện (Điều 8, 9, 10.2).",
    "MIỄN Giấy chứng nhận khi nhập khẩu để TỰ DÙNG (không kinh doanh): chỉ công bố mục đích sử dụng trên Cơ sở dữ liệu chuyên ngành hóa chất (Điều 10.3). Công bố KHÔNG phải điều kiện thông quan và không có thời hạn cứng — doanh nghiệp chủ động chọn thời điểm công bố.",
]

# Nghĩa vụ khai báo là nghĩa vụ CHUNG cho hóa chất chương 28/29, không riêng phụ
# lục nào -> đứng thành mục "A. Khai báo hóa chất nhập khẩu", KHÔNG lặp lại
# trong khối Phụ lục II ở cuối. lookup.py (tra 1 CAS, không có mục A đứng cạnh)
# vẫn in kèm — xem format_lookup.
# Điều 21.4 (san chiết nội bộ) và 21.5 (tồn trữ) miễn giấy của khâu SẢN XUẤT và
# TỒN TRỮ — không đụng tới Giấy phép XNK, nên không nằm ở mục B (chỉ nói về giấy
# phép xuất khẩu, nhập khẩu) mà xuống cuối cùng khối nghĩa vụ khác. KHÔNG gộp vào
# OTHER_OBLIGATIONS: khối đó là nghĩa vụ riêng của Phụ lục II và được lookup.py
# in kèm cho từng CAS, hai khoản này thì áp dụng chung.
OTHER_EXEMPTIONS_TITLE = "Miễn trừ khác — khâu sản xuất, tồn trữ (Điều 21, khoản 4 & 5)"
OTHER_EXEMPTIONS = [
    "(Điều 21.4) San chiết, pha chế hóa chất nhằm phục vụ TRỰC TIẾP cho hoạt động sản xuất nội bộ của chính tổ chức, cá nhân thực hiện việc san chiết, pha chế: miễn cấp Giấy chứng nhận / Giấy phép SẢN XUẤT. (Khoản 4 chỉ miễn giấy khâu sản xuất — không nói tới kinh doanh, khác khoản 1.)",
    "(Điều 21.5) Tổ chức cho thuê đất KHÔNG kèm cơ sở vật chất để tồn trữ hóa chất; hoặc dịch vụ tồn trữ hóa chất có điều kiện / kiểm soát đặc biệt hàm lượng ≤ 1%: miễn Giấy chứng nhận đủ điều kiện hoạt động dịch vụ tồn trữ. (NQ 19 nới từ <0,1%.)",
]

DECLARATION_RULE = (
    "Khai báo hóa chất nhập khẩu qua Cổng một cửa quốc gia (Điều 6) — nghĩa vụ "
    "chung cho hóa chất thuộc chương 28, 29, không riêng Phụ lục II; phải có "
    "phản hồi khai báo mới được thông quan (Điều 6.3.c)."
)

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
        "section": "khaibao",
        "title": "Miễn khai báo hóa chất nhập khẩu",
        "cite": "Điều 6, khoản 7",
        "items": [
            "Hóa chất cần kiểm soát đặc biệt / hóa chất cấm đã được cấp Giấy phép nhập khẩu (khỏi khai báo riêng, vì đã qua thủ tục cấp phép).",
            "Nhập khẩu dưới 10 kg hóa chất thuộc chương 28, 29 Danh mục HS.",
            "Nhập khẩu dưới 1 kg hóa chất mới để thử nghiệm, đánh giá đặc tính hóa lý.",
            "Hỗn hợp chất không thuộc chương 28/29 nhưng có chứa hóa chất thuộc chương 28/29.",
        ],
    },
    # Miễn Giấy chứng nhận của Phụ lục II (Điều 10.3) KHÔNG nằm ở đây: nó dính
    # liền với nghĩa vụ Giấy chứng nhận, nên ở chung khối OTHER_OBLIGATIONS cuối
    # trang — tách ra hai chỗ thì đọc mục miễn trừ mà không thấy quy định gốc.
    {
        "section": "giayphep",
        "title": "1. Miễn theo ngưỡng nồng độ — theo TỪNG loại giấy / hoạt động",
        "cite": "Điều 21, khoản 1-3 (ngưỡng khoản 1/2 cập nhật theo NQ 19/2026/NQ-CP)",
        "items": [
            "Khoản 1 — MIỄN CẤP Giấy chứng nhận / Giấy phép SẢN XUẤT, KINH DOANH: hóa chất có điều kiện và hóa chất cần kiểm soát đặc biệt có hàm lượng ≤ 1% khối lượng hỗn hợp chất. (NQ 19 nới từ <0,1%.)",
            "Khoản 2 — MIỄN CẤP Giấy phép XUẤT KHẨU, NHẬP KHẨU: hóa chất cần kiểm soát đặc biệt Nhóm 1 có hàm lượng ≤ 1%, hoặc Nhóm 2 có hàm lượng ≤ 5% khối lượng hỗn hợp chất. (NQ 19 đổi biên < thành ≤.)",
            "Khoản 3 — MIỄN CẤP Giấy phép SẢN XUẤT, NHẬP KHẨU hóa chất cấm có nồng độ < 0,1% khối lượng hỗn hợp chất. (NQ 19 GIỮ NGUYÊN ngưỡng gốc NĐ 26.)",
        ],
    },
    {
        "section": "giayphep",
        "title": "2. Miễn khi hóa chất nằm trong sản phẩm hoàn chỉnh",
        "cite": "Điều 21, khoản 6",
        "lead": (
            "MIỄN CẤP Giấy chứng nhận sản xuất, kinh doanh (với hóa chất có "
            "điều kiện) và Giấy phép sản xuất, kinh doanh, xuất khẩu, nhập "
            "khẩu (với hóa chất cần kiểm soát đặc biệt), khi hóa chất đó "
            "được chứa (không tách riêng) trong các sản phẩm sau:"
        ),
        "items": [
            "Dược phẩm, chế phẩm diệt khuẩn/côn trùng, thực phẩm, mỹ phẩm.",
            "Thức ăn chăn nuôi/thủy sản, thuốc thú y, thuốc BVTV, phân bón hữu cơ/sinh học/khoáng; sản phẩm bảo quản, chế biến nông sản, lâm sản, hải sản và thực phẩm.",
            "Chất phóng xạ, vật liệu xây dựng, sơn, mực in.",
            "Sản phẩm gia dụng: keo dán, chất tẩy rửa, hóa mỹ phẩm.",
            "Xăng, dầu, condensate, naphta dùng chế biến xăng dầu.",
            "Pin, ắc quy, thiết bị y tế, thiết bị thí nghiệm.",
            "Lưu ý: được miễn giấy phép hóa chất KHÔNG miễn mọi nghĩa vụ — tổ chức, cá nhân nhập khẩu sản phẩm chứa hóa chất nguy hiểm vẫn phải công bố thông tin hàm lượng hóa chất nguy hiểm trước khi lưu thông (NĐ 26, Điều 28, 29).",
        ],
    },
    {
        "section": "giayphep",
        "title": "3. Miễn Giấy phép XNK bổ sung (NQ 19 thêm mới)",
        "cite": "Điều 21, khoản 7-8 (NQ 19/2026/NQ-CP bổ sung, NĐ 26 gốc chỉ tới khoản 6)",
        "items": [
            "Khoản 7 — MIỄN CẤP Giấy phép XUẤT KHẨU, NHẬP KHẨU hóa chất cần kiểm soát đặc biệt dùng trong lĩnh vực thí nghiệm, khối lượng ≤ 1mg/lần nhập khẩu.",
            "Khoản 8 — MIỄN CẤP Giấy phép XUẤT KHẨU, NHẬP KHẨU hóa chất cần kiểm soát đặc biệt với xuất khẩu, nhập khẩu tại chỗ; và mua bán hóa chất giữa doanh nghiệp trong khu hải quan riêng với doanh nghiệp nội địa.",
        ],
    },
]

# Hai nghĩa vụ khác nhau, hay bị lẫn: KHAI BÁO (mọi hóa chất chương 28/29) và
# GIẤY PHÉP/GIẤY CHỨNG NHẬN (theo phụ lục). Mỗi mục nói QUY ĐỊNH trước rồi mới
# tới MIỄN TRỪ của chính nó — đọc "miễn trừ" mà không biết đang miễn cái gì thì
# dễ áp nhầm ngưỡng của giấy phép sang khai báo và ngược lại.
# Phần "quy định" TRỎ VỀ IMPORT_RULES/OTHER_OBLIGATIONS, không chép lại chữ:
# chép lại là hai nguồn phải đồng bộ tay. test_hai_muc_quy_dinh_mien_tru_dung_dieu
# chốt đúng điều luật nếu ai đó xếp lại thứ tự các danh sách kia.
EXEMPT_SECTIONS = [
    {
        "key": "khaibao",
        "title": "A. Khai báo hóa chất nhập khẩu",
        "rule": [DECLARATION_RULE],
    },
    {
        "key": "giayphep",
        "title": "B. Giấy phép xuất khẩu, nhập khẩu",
        "rule": [IMPORT_RULES["III"][0], IMPORT_RULES["III"][1]],
    },
]

# Chế tài khi không xuất trình được giấy phép lúc đăng ký tờ khai — vế còn lại
# của câu hỏi "cần giấy gì": không có giấy thì hậu quả là gì.
# Nguồn NĐ 169/2026 KHÔNG có trong repo (khác nd24.md/nd26.txt) -> không tự sửa
# câu này; đối chiếu Điều 19 bản gốc trước khi đổi.
PENALTY_WARNING = (
    "Lưu ý: Doanh nghiệp tại thời điểm đăng ký tờ khai hải quan không xuất trình "
    "giấy phép xuất khẩu, nhập khẩu sẽ bị xử phạt theo Điều 19 Nghị định "
    "169/2026/NĐ-CP ngày 15/5/2026 của Chính phủ quy định xử phạt vi phạm hành "
    "chính trong lĩnh vực hải quan."
)

# Cảnh báo vùng mù: các mục trên là HỌ chất, nghị định không cho mã CAS nào nên
# tra theo mã KHÔNG BAO GIỜ ra chúng. Nguy hiểm thật, không phải giả định: Asen
# trioxit (1327-53-3) chỉ được nghị định ghi mã ở Phụ lục IV, nên tool kết luận
# "{VERDICT[none]}" trong khi mục 37 "Asen và các hợp chất của asen" của Phụ lục
# III phủ nó. Tool KHÔNG tự suy ra chất nào thuộc họ nào (phải hiểu hóa học: hợp
# chất nào là hợp chất của asen, Cr nào là Cr6+) -> in nguyên danh sách để cán bộ
# tự đối chiếu, thay vì đoán rồi báo sai.
PL3_NO_CAS_TITLE = "Vùng mù: mục Phụ lục III không có mã CAS — tra theo mã sẽ KHÔNG ra"
PL3_NO_CAS_LEAD = (
    "Nghị định 24/2026/NĐ-CP xếp các mục dưới đây vào Phụ lục III (hóa chất cần kiểm soát "
    "đặc biệt) nhưng ghi theo HỌ CHẤT, không có mã CAS."
)
# Chất bị ghi "Ngoại trừ" (Fonofos, DMAE, DEAE): mã CAS của chúng CÓ in trong
# bảng Phụ lục III nên ai tra bản gốc cũng thấy — phải nói rõ vì sao kết luận lại
# không phải PL III, không thì trông như tool sót.
PL3_EXCLUDED_NOTE = (
    'ⓘ Nghị định 24 có in mã này trong bảng Phụ lục III, nhưng ở dòng "Ngoại trừ" của mục '
    "{stt} — tức nghị định LOẠI TRỪ nó khỏi mục đó, không phải xếp nó vào Bảng 2. "
    "Kết luận trên đã tính đúng."
)


def pl3_excluded(cas):
    """Bản ghi 'Ngoại trừ' của Phụ lục III cho CAS này (thường 0 hoặc 1)."""
    return [e for e in PL3_EXCLUDED if e["cas"] == cas]


# ponytail: nhận diện họ chất bằng TỪ KHÓA TRONG TÊN — heuristic, không phải hóa
# học thật. Trần của nó: chỉ bắt được chất mang tên nguyên tố; SÓT tên không mang
# (Calomel = Hg2Cl2 không có chữ "thủy ngân"), và không phân biệt được Cr3+ với
# Cr6+ nếu tên không nói. Nâng cấp khi cần chắc hơn: đối chiếu cột "Công thức hóa
# học" của nd24.md (extract.py chưa lấy cột này).
# Chỉ để GỢI Ý đối chiếu, KHÔNG đổi verdict: đoán sai theo hướng nào cũng hại —
# báo thừa thì cán bộ mất công, báo thiếu thì lọt hàng cần giấy phép.
# Giữ dấu tiếng Việt khi so: bỏ dấu thì "chì" thành "chi", khớp lung tung.
PL3_HINT_PREFIX = (
    "⚠ TÊN CHẤT NÀY GỢI Ý CÓ THỂ THUỘC MỘT MỤC PHỤ LỤC III GHI THEO HỌ CHẤT — "
    "kết luận trên dựa vào mã CAS nên KHÔNG tính mục đó. Tự đối chiếu:"
)
PL3_FAMILY_HINTS = {
    "37.": ["asen", "arsenic"],
    "38.": ["cromat", "chromate", "cr6", "crom (vi)", "chromium (vi)"],
    "39.": ["thủy ngân", "mercury"],
    "40.": ["xyanua", "cyanide"],
    "41.": ["chì", "lead"],
}


def pl3_family_hints(cas):
    """Mục Phụ lục III (họ chất, không có mã CAS) mà TÊN của CAS này gợi ý là có
    thể thuộc về. Trả [] nếu chất đã là Phụ lục III — verdict đã báo cần Giấy
    phép rồi, nhắc thêm chỉ làm nhiễu."""
    rows = rows_for(cas)
    if not rows or "III" in annexes_for(cas):
        return []
    name = f"{rows[0]['name_vn']} {rows[0]['name_en']}".lower()
    return [
        e
        for e in PL3_NO_CAS
        if any(k in name for k in PL3_FAMILY_HINTS.get(e["stt"], []))
    ]


def format_pl3_no_cas(width=78):
    lines = [PL3_NO_CAS_TITLE.upper(), ""]
    lines.append(textwrap.fill(PL3_NO_CAS_LEAD, width=width))
    lines.append("")
    for group in sorted({e["category"] for e in PL3_NO_CAS}):
        lines.append(f"  {group}")
        for e in PL3_NO_CAS:
            if e["category"] == group:
                lines.append(
                    textwrap.fill(
                        f"{e['stt']} {e['ten']}",
                        width=width,
                        initial_indent="    - ",
                        subsequent_indent="      ",
                    )
                )
        lines.append("")
    return "\n".join(lines)


ANNEX_ORDER = ["III", "II", "I", "IV"]  # ưu tiên hiển thị mức kiểm soát cao nhất trước
ANNEX_DISPLAY_ORDER = ["I", "II", "III", "IV"]


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


def annex_labels(cas):
    """Liệt kê đầy đủ phụ lục của CAS theo thứ tự I-IV để hiển thị trong bảng."""
    present = annexes_for(cas)
    return ", ".join(f"PL {a}" for a in ANNEX_DISPLAY_ORDER if a in present) or "—"


def highest_annex(cas):
    """Phụ lục có mức kiểm soát cao nhất mà CAS này thuộc về (III > II > I > IV)."""
    present = annexes_for(cas)
    for a in ANNEX_ORDER:
        if a in present:
            return a
    return None


def cas_status(cas):
    """Trạng thái hiển thị cho 1 CAS. Trả (badge, text) — badge in
    {"ok","warn","unknown"}.

    ponytail: không tự nhận diện % hàm lượng từ mô tả (khai báo tự do dễ bị
    ghi sai định dạng/lộn xộn, đoán nhầm % có thể dẫn tới kết luận miễn
    trừ sai) — hóa chất Phụ lục III luôn báo "Cần Giấy phép"; cán bộ tự đối
    chiếu ngưỡng miễn trừ nồng độ ở Điều 21 (xem EXEMPTIONS/format_exemptions)
    bằng tài liệu khai báo gốc.
    """
    rows = rows_for(cas)
    if not rows:
        return ("unknown", VERDICT["unknown"])
    present = annexes_for(cas)
    if "III" in present:
        return ("warn", VERDICT["pl3"])
    # Không thuộc PL III: không cần Giấy phép XNK, nhưng còn nghĩa vụ Phụ lục II
    # (Giấy chứng nhận/công bố) -> verdict phải nói "còn nghĩa vụ khác".
    if any(a in present for a in OTHER_OBLIGATION_ANNEXES):
        return ("ok", VERDICT["other_obligation"])
    return ("ok", VERDICT["none"])


def format_exemptions():
    lines = ["QUY ĐỊNH & CÁC TRƯỜNG HỢP MIỄN TRỪ (NĐ 26/2026/NĐ-CP)", ""]
    for sect in EXEMPT_SECTIONS:
        lines.extend([sect["title"].upper(), "", "  Quy định:"])
        lines.extend(f"  - {item}" for item in sect["rule"])
        lines.extend(["", "  Trường hợp miễn trừ:"])
        for group in EXEMPTIONS:
            if group["section"] != sect["key"]:
                continue
            lines.append(f"  {group['title']} ({group['cite']})")
            if "lead" in group:
                lines.append(f"    {group['lead']}")
            lines.extend(f"    - {item}" for item in group["items"])
            lines.append("")
    lines.append(textwrap.fill(PENALTY_WARNING, width=78))
    lines.extend(["", OTHER_OBLIGATIONS_TITLE.upper(), ""])
    lines.extend(f"  - {item}" for item in OTHER_OBLIGATIONS)
    lines.extend(["", OTHER_EXEMPTIONS_TITLE.upper(), ""])
    lines.extend(f"  - {item}" for item in OTHER_EXEMPTIONS)
    return "\n".join(lines)


def format_report(cas):
    rows = rows_for(cas)
    lines = []
    if not rows:
        # CLI in báo cáo đứng một mình (lookup.py) nên phải tự nói tra ra gì; trang
        # HTML thì bảng đã ghi "Không rõ" nên bỏ hẳn thẻ chi tiết, không in dòng này.
        out = f"CAS {cas}: không có trong dữ liệu NĐ 24 (Phụ lục I-IV)."
        # ...trừ chất bị ghi "Ngoại trừ" (Fonofos): mã CÓ in trong bảng Phụ lục III
        # nên "không có trong dữ liệu" nghe như tool sót. Nói rõ lý do.
        for e in pl3_excluded(cas):
            out += "\n\n" + textwrap.fill(PL3_EXCLUDED_NOTE.format(stt=e["ngoai_tru_khoi"].rstrip(".")), width=78)
        return out
    lines.append(f"CAS {cas}: {rows[0]['name_vn']} ({rows[0]['name_en']})")
    lines.append("")
    for e in pl3_excluded(cas):
        lines.append(textwrap.fill(PL3_EXCLUDED_NOTE.format(stt=e["ngoai_tru_khoi"].rstrip(".")), width=78))
        lines.append("")
    for hint in pl3_family_hints(cas):
        lines.append(
            textwrap.fill(
                f"{PL3_HINT_PREFIX} {hint['stt']} {hint['ten']} ({hint['category']})",
                width=78,
                subsequent_indent="  ",
            )
        )
        lines.append("")
    seen_annex = set()
    import_rows = [r for r in rows if r["annex"] in IMPORT_ANNEXES]
    for r in import_rows:
        lines.append(f"- {r['category']}")
        seen_annex.add(r["annex"])
    if not import_rows:
        lines.append("Không phát sinh yêu cầu nhập khẩu riêng.")
        return "\n".join(lines)
    lines.append("")
    for annex in annexes_to_explain(seen_annex):
        lines.append(f"== Yêu cầu nhập khẩu (Phụ lục {annex}) ==")
        for bullet in IMPORT_RULES[annex]:
            lines.append(textwrap.fill(bullet, width=78, initial_indent="  - ", subsequent_indent="    "))
        lines.append("")
    return "\n".join(lines)


def format_lookup(cas):
    """Báo cáo cho lookup.py (tra 1 CAS đứng một mình). Khác scan.py — vốn đã có
    bảng verdict + mục 'NGHĨA VỤ KHÁC' cuối kết quả — lookup.py chỉ in mỗi báo
    cáo này, nên chất Phụ lục II phải tự nói nghĩa vụ của nó, không thì người
    tra đọc 'Không phát sinh yêu cầu nhập khẩu riêng' thành 'không phải làm gì'."""
    parts = [format_report(cas)]
    if "II" in annexes_for(cas):
        parts.append("== Nghĩa vụ khác (Phụ lục II) ==")
        parts.extend(
            textwrap.fill(o, width=78, initial_indent="  - ", subsequent_indent="    ")
            # + DECLARATION_RULE: lookup.py không có mục "A. Khai báo" đứng cạnh
            # như trang HTML/scan.py, bỏ hẳn là mất luôn cửa thông quan thật sự.
            for o in [*OTHER_OBLIGATIONS, DECLARATION_RULE]
        )
    return "\n".join(parts)
