"""Smallest possible regression check: known CAS -> known annex(es), and
that scanning a pasted DN description pulls every CAS out of free text."""
import re
from pathlib import Path

import core

from core import (
    DATA,
    EXEMPTIONS,
    EXEMPTIONS_WARNING,
    IMPORT_RULES,
    OTHER_OBLIGATION_ANNEXES,
    VERDICT,
    annexes_for,
    cas_status,
    extract_cas,
    format_report,
    highest_annex,
)


def norm_rules():
    """IMPORT_RULES là chuỗi nhiều dòng -> cụm từ hay bị NGẮT QUA DÒNG, khiến
    `assert "x y" in rule` đỏ oan (đã dính 3 lần trong lúc refactor). Chuẩn hóa
    khoảng trắng + hạ chữ thường rồi mới so."""
    return {k: re.sub(r"\s+", " ", " ".join(v)).lower() for k, v in IMPORT_RULES.items()}


def test_known_chemicals():
    assert annexes_for("106-99-0") == {"I", "II", "IV"}          # 1,3-Butadiene
    assert annexes_for("103-79-7") == {"III"}                     # Phenylacetone (P2P), tien chat
    assert annexes_for("78-53-5") == {"III"}                      # Amiton, Bang 2
    assert annexes_for("355-46-4") == {"III"}                     # PFHxS, Rotterdam/Stockholm
    assert annexes_for("000-00-0") == set()                       # not present
    assert len(DATA) > 1000


def test_highest_annex_prioritizes_permit_over_declaration():
    # Methanol la ca PL I lan PL III (Bang 2) -> phai uu tien canh bao PL III.
    assert highest_annex("67-56-1") == "III"


def test_extract_cas_from_free_text():
    text = "Hỗn hợp gồm Metanol CAS 67-56-1, Acetaldehyde (75-07-0) và mã CAS 103-79-7 (P2P)."
    assert extract_cas(text) == ["67-56-1", "75-07-0", "103-79-7"]


def test_cas_status_annex_iii_always_needs_permit():
    # Khong tu nhan dien % nua -> hoa chat PL III luon bao can giay phep,
    # du thuc te co the duoc mien theo nong do (can doi chieu thu cong).
    # Verdict phai goi DUNG TEN giay, khong noi "Giay phep" trong nghia.
    assert cas_status("67-56-1") == ("warn", "Cần Giấy phép XNK hóa chất KSĐB")


def test_cas_status_non_annex_iii_flags_other_obligations():
    # 106-99-0 = PL I/II/IV, khong PL III -> xanh nhung verdict phai noi con
    # nghia vu khac, de "khong can Giay phep" khong bi doc thanh "khong phai lam gi".
    # Nghia vu CU THE do khoi IMPORT_RULES cua PL II/IV noi -> khong tom tat lai.
    assert cas_status("106-99-0") == ("ok", "Không cần Giấy phép XNK — có nghĩa vụ khác")
    assert set(OTHER_OBLIGATION_ANNEXES) == {"II", "IV"}


def test_cas_status_plain_green_when_no_other_obligation():
    # Chat chi thuoc PL I (khong PL II/III/IV) -> xanh thuan.
    plain = next((r["cas"] for r in DATA if annexes_for(r["cas"]) == {"I"}), None)
    assert plain is not None
    assert cas_status(plain) == ("ok", "Không cần Giấy phép XNK")


def test_annex_iv_multiple_thresholds_flagged():
    # 624-83-9 co 2 nguong PL IV khac nhau (150 / 5.000) -> phai canh bao,
    # khong duoc gop lai thanh mot.
    rep = format_report("624-83-9")
    assert "150" in rep and "5.000" in rep and "nhiều ngưỡng tồn trữ" in rep


def test_nq19_thresholds_kept():
    # NQ 19 noi nguong: khoan 1 & 2 -> <= ; khoan 3 (hoa chat cam) GIU <0,1%.
    # NQ 19 KHONG them/bot chat nao, nhung DOI nguong -> anh huong "can giay hay
    # khong" nen phai giu. Phan phan cap cua NQ 19 la thu tuc -> da bo.
    kho = {g["cite"]: g["items"] for g in EXEMPTIONS}
    k123 = next(items for cite, items in kho.items() if "khoản 1-3" in cite)
    assert "≤ 1%" in k123[0]                       # khoan 1: SX-KD
    assert "≤ 1%" in k123[1] and "≤ 5%" in k123[1]  # khoan 2: XNK
    assert "< 0,1%" in k123[2]                     # khoan 3: cam giu nguyen
    # NQ 19 them khoan 7/8 (deu la MIEN CAP Giay phep XNK -> thuoc "can giay gi").
    all_items = " ".join(i for g in EXEMPTIONS for i in g["items"])
    assert "Khoản 7" in all_items and "≤ 1mg" in all_items
    assert "Khoản 8" in all_items and "tại chỗ" in all_items
    # Nguong cu the KHONG con nhac lai trong IMPORT_RULES (da co muc mien tru).
    assert "≤1%" not in " ".join(IMPORT_RULES["III"])


def test_moi_verdict_goi_dung_ten_giay():
    # Nguyen tac: cong cu tra loi "chat nay CAN GIAY GI" -> moi cho hien thi phai
    # goi dung ten giay, khong dung chu "Giay phep" trong nghia. Bang tom tat chi
    # con pill (khong con SHORT_FLAG) -> ten giay duoc khoa o VERDICT va IMPORT_RULES.
    assert VERDICT["pl3"] == "Cần Giấy phép XNK hóa chất KSĐB"
    assert VERDICT["none"] == "Không cần Giấy phép XNK"
    r = norm_rules()
    assert "giấy phép xuất khẩu, nhập khẩu hóa chất cần kiểm soát đặc biệt" in r["III"]
    assert "giấy chứng nhận đủ điều kiện sản xuất, kinh doanh hóa chất có điều kiện" in r["II"]
    assert "kế hoạch phòng ngừa, ứng phó sự cố hóa chất" in r["IV"]
    # PL III phai neu ro GP XNK khac GP san xuat, kinh doanh KSDB.
    assert "giấy phép sản xuất, kinh doanh hóa chất ksđb" in r["III"]


def test_html_khong_lech_khoi_core():
    # build_html.py dựng lại logic hiển thị bằng JS -> ĐÃ TỪNG LỆCH THẬT: JS
    # hard-code "Cần Giấy phép" trong khi core.py đã đổi thành "Cần Giấy phép XNK
    # hóa chất KSĐB" => trang HTML (thứ cán bộ thực sự mở) mất phần "giấy gì",
    # còn CLI thì đúng. Test Python thuần không bắt được vì nó chỉ soi core.py.
    # Chốt: mọi chữ verdict phải đến TỪ core.VERDICT, không viết tay trong JS.
    src = Path(__file__).with_name("build_html.py").read_text(encoding="utf-8")
    for key, text in VERDICT.items():
        assert text not in src, f"verdict '{key}' viết tay trong build_html.py, phải lấy từ core.VERDICT"
    # Kể cả TRÍCH DẪN verdict trong chữ tĩnh của trang cũng phải qua placeholder —
    # nếu không nó sẽ mốc lại y như lần "Cần Giấy phép" cũ nằm ở dòng trợ giúp.
    assert "Cần Giấy phép" not in src, "chữ verdict viết tay trong build_html.py — dùng __VERDICT_PL3__"
    assert "__VERDICT_JSON__" in src and "VERDICT.pl3" in src
    # ...và artifact đã commit phải khớp core.py (chạy lại build_html.py nếu đỏ).
    html = Path(__file__).with_name("Tra cứu hóa chất NĐ24.html")
    if html.exists():
        page = html.read_text(encoding="utf-8")
        assert VERDICT["pl3"] in page, "HTML đã commit cũ hơn core.py — chạy python3 build_html.py"


def test_khong_con_noi_dung_ho_so_trinh_tu_thu_tuc():
    # PHAM VI: trang tra cuu "can giay gi" -> khong chua ho so/trinh tu/thu tuc cap,
    # tham quyen cap (phan cap NQ 19), hay khoi chuyen tiep Dieu 30.4 (mien XUAT
    # TRINH ho so GP SX-KD). Chan viec chung quay lai.
    blob = " ".join(
        [" ".join(IMPORT_RULES[a]) for a in "I II III IV".split()]
        + [i for g in EXEMPTIONS for i in g["items"]]
        + [g["cite"] for g in EXEMPTIONS]
        + [EXEMPTIONS_WARNING]
    )
    for banned in (
        "UBND cấp tỉnh",        # tham quyen cap (phan cap NQ 19)
        "Bộ Công Thương",       # tham quyen cap
        "gia hạn 1 lần",        # thu tuc
        "Điều 30.4",            # khoi chuyen tiep
        "Khoản 9",              # mien XUAT TRINH ho so
        "xuất trình hồ sơ",     # ho so
        "NĐ 113/2017",          # danh muc cu -> chi phuc vu khoi chuyen tiep
        "NĐ 82/2022",
        "NĐ 33/2024",
    ):
        assert banned not in blob, f"nội dung ngoài phạm vi quay lại: {banned}"


def test_decree_cas_errata_corrected():
    # 2 mã CAS ghi sai trong NĐ 24 đã sửa về số CAS quốc tế (ERRATA trong
    # extract.py): số sai không còn tra ra, số đúng tra ra đúng phụ lục.
    assert annexes_for("10037-74-3") == set() and annexes_for("10137-74-3") == {"II"}  # Canxi clorat
    assert annexes_for("7746-08-4") == set() and annexes_for("7446-08-4") == {"II"}    # Selen dioxit


def test_exemptions_cover_dieu_21_4_and_product_declaration():
    cites = " | ".join(g["cite"] for g in EXEMPTIONS)
    assert "khoản 4" in cites  # san chiết, pha chế nội bộ (Điều 21.4)
    all_items = " ".join(i for g in EXEMPTIONS for i in g["items"])
    assert "Điều 28, 29" in all_items  # nghĩa vụ công bố hàm lượng trong sản phẩm


def test_congbo_is_not_a_customs_gate_pl2():
    # Điều 10.3: công bố mục đích sử dụng KHÔNG phải điều kiện thông quan và
    # doanh nghiệp CHỦ ĐỘNG thời điểm; điều kiện thông quan là khai báo NK
    # (Điều 6). Bảng tóm tắt nay chỉ có pill -> IMPORT_RULES["II"] (hiện ngay dưới
    # bảng) là nơi DUY NHẤT nói sự phân biệt này, nên phải nói đủ.
    rule = norm_rules()["II"]
    # cửa thông quan = khai báo (Điều 6), KHÔNG phải công bố
    assert "điều kiện thông quan là khai báo hóa chất nhập khẩu" in rule
    assert "điều 6" in rule
    assert "công bố không phải điều kiện thông quan" in rule
    assert "chủ động chọn thời điểm công bố" in rule
    assert "điều 10.3" in rule
    # ...và phải gọi đúng tên giấy cho khâu kinh doanh (Điều 10.2).
    assert "giấy chứng nhận đủ điều kiện" in rule and "10.2" in rule


def test_pl3_splits_import_congbo_from_use_deadline():
    # Không được gộp Điều 14.3 (công bố KHI nhập khẩu, không thời hạn cứng)
    # với Điều 15.1 (công bố TRƯỚC 30 NGÀY khi đưa vào sử dụng lần đầu).
    # Hai ý phải nằm ở HAI gạch đầu dòng riêng, không dính vào nhau.
    b14 = next(b for b in IMPORT_RULES["III"] if "Điều 14.3" in b)
    b15 = next(b for b in IMPORT_RULES["III"] if "Điều 15.1" in b)
    assert b14 is not b15
    # Điều 14.3: gắn khâu NHẬP KHẨU, không thời hạn cứng, không phải cửa thông quan.
    assert "KHI nhập khẩu" in b14 and "không có thời hạn cứng" in b14
    assert "không phải điều kiện thông quan" in b14
    # Điều 15.1: mốc 30 NGÀY là mốc cứng, gắn khâu SỬ DỤNG.
    assert "TRƯỚC 30 NGÀY" in b15 and "SỬ DỤNG" in b15
    assert "không phải khâu nhập khẩu" in b15


def test_data_regenerated_from_official_nd24():
    # Bản chính thức NĐ24 (markdown) đầy đủ hơn bản textutil cũ: POP nằm ở PL III
    # (không phải PL IV), PL I không bị rớt chất, và errata CAS vẫn được áp dụng.
    assert len(DATA) > 1300
    assert annexes_for("126-72-7") == {"III"}   # Tris(2,3-dibromopropyl)phosphate (POP) -> III
    assert "I" in annexes_for("108-88-3")        # Toluene có trong PL I (bản cũ bị rớt)
    assert annexes_for("10137-74-3") == {"II"} and annexes_for("10037-74-3") == set()  # errata giữ nguyên


def test_pl3_an_khoi_pl1_vi_da_mien_khai_bao():
    # Điều 6.7.a (nd26.txt:118): "Nhập khẩu hóa chất cần kiểm soát đặc biệt khi đã
    # được cơ quan có thẩm quyền cấp Giấy phép nhập khẩu" -> MIỄN khai báo. Khối
    # Phụ lục I chỉ nói về khai báo, nên với chất PL III nó vừa thừa vừa gây hiểu
    # nhầm "vẫn phải khai báo". 9 chất vừa PL I vừa PL III (Metanol, Toluene...).
    assert core.annexes_to_explain({"I", "III"}) == ["III"]
    assert core.annexes_to_explain({"I", "III", "IV"}) == ["III", "IV"]
    assert core.annexes_to_explain({"I"}) == ["I"]          # không có III thì vẫn hiện
    assert core.annexes_to_explain({"II", "III"}) == ["II", "III"]  # PL II giữ (giấy khác)
    rep = format_report("67-56-1")                          # Metanol = PL I + III + IV
    assert "Yêu cầu nhập khẩu (Phụ lục I)" not in rep
    assert "Yêu cầu nhập khẩu (Phụ lục III)" in rep
    assert "MIỄN khai báo hóa chất (Điều 6.7.a)" in " ".join(IMPORT_RULES["III"])


def test_import_rules_khong_be_dong_cung():
    # Trước đây IMPORT_RULES là chuỗi đã bẻ dòng + thụt lề -> HTML (pre-wrap) hiện
    # thụt lề giữa câu, xuống dòng loạn. Mỗi ý phải là MỘT dòng liền, để người
    # render tự ngắt theo bề rộng của họ.
    for annex, bullets in IMPORT_RULES.items():
        assert isinstance(bullets, list), f"PL {annex}: phải là list gạch đầu dòng"
        for b in bullets:
            assert "\n" not in b, f"PL {annex}: gạch đầu dòng còn bẻ dòng cứng: {b[:40]}"
            assert b == b.strip(), f"PL {annex}: gạch đầu dòng thừa khoảng trắng"


def test_khong_con_tong_ket_cuoi_chi_tiet():
    # Đoạn tổng kết cuối (p.obl) chép lại y nguyên nghĩa vụ mà khối IMPORT_RULES
    # của PL II/IV ngay trên đã nói -> hai nguồn phải đồng bộ tay, đúng cái bẫy
    # đã làm HTML lệch core.py một lần. Bỏ hẳn; verdict pill giữ vai trò cảnh báo.
    src = Path(__file__).with_name("build_html.py").read_text(encoding="utf-8")
    for dead in ("p.obl", "note_prefix", "OBLIGATIONS[", "detailFor(cas, note)"):
        assert dead not in src, f"tàn dư tổng kết cuối trong build_html.py: {dead}"
    assert "note_prefix" not in VERDICT and not hasattr(core, "OBLIGATIONS")
    # cas_status chỉ còn (badge, text) — không còn note để render.
    assert len(cas_status("106-99-0")) == 2


def test_unknown_khong_con_ghi_chu():
    # Chất không có trong dữ liệu: bảng đã nói đủ (cột Tên chất, pill trạng thái,
    # chip thống kê) -> trang KHÔNG dựng thẻ chi tiết, và không còn NOTE_GAP.
    src = Path(__file__).with_name("build_html.py").read_text(encoding="utf-8")
    assert "NOTE_GAP" not in src and not hasattr(core, "NOTE_GAP")
    assert "Không tìm thấy trong Phụ lục" not in src, "JS viết tay lại câu 'không tìm thấy'"
    assert "if (!rows.length) return;" in src, "CAS không có dữ liệu phải bỏ qua thẻ chi tiết"
    # CLI thì ngược lại: lookup.py in mỗi format_report, không có bảng đứng trước,
    # nên vẫn phải tự nói tra ra gì — bỏ nốt thì in ra chuỗi rỗng.
    assert format_report("000-00-0") == "CAS 000-00-0: không có trong dữ liệu NĐ 24 (Phụ lục I-IV)."


if __name__ == "__main__":
    test_known_chemicals()
    test_highest_annex_prioritizes_permit_over_declaration()
    test_extract_cas_from_free_text()
    test_cas_status_annex_iii_always_needs_permit()
    test_cas_status_non_annex_iii_flags_other_obligations()
    test_cas_status_plain_green_when_no_other_obligation()
    test_annex_iv_multiple_thresholds_flagged()
    test_nq19_thresholds_kept()
    test_moi_verdict_goi_dung_ten_giay()
    test_html_khong_lech_khoi_core()
    test_pl3_an_khoi_pl1_vi_da_mien_khai_bao()
    test_import_rules_khong_be_dong_cung()
    test_khong_con_tong_ket_cuoi_chi_tiet()
    test_unknown_khong_con_ghi_chu()
    test_khong_con_noi_dung_ho_so_trinh_tu_thu_tuc()
    test_decree_cas_errata_corrected()
    test_exemptions_cover_dieu_21_4_and_product_declaration()
    test_congbo_is_not_a_customs_gate_pl2()
    test_pl3_splits_import_congbo_from_use_deadline()
    test_data_regenerated_from_official_nd24()
    print("ok")
