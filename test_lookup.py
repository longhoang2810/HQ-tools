"""Smallest possible regression check: known CAS -> known annex(es), and
that scanning a pasted DN description pulls every CAS out of free text."""
from pathlib import Path

from core import (
    DATA,
    EXEMPTIONS,
    EXEMPTIONS_WARNING,
    IMPORT_RULES,
    OBLIGATIONS,
    SHORT_FLAG,
    VERDICT,
    annexes_for,
    cas_status,
    extract_cas,
    format_report,
    highest_annex,
)


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
    badge, text, note = cas_status("67-56-1")
    assert badge == "warn" and text == "Cần Giấy phép XNK hóa chất KSĐB" and note is None


def test_cas_status_non_annex_iii_flags_other_obligations():
    # 106-99-0 = PL I/II/IV, khong PL III -> xanh nhung phai neu nghia vu PL II/IV
    # de "khong can Giay phep" khong bi doc thanh "khong phai lam gi".
    badge, text, note = cas_status("106-99-0")
    assert badge == "ok"
    assert text == "Không cần Giấy phép XNK — có nghĩa vụ khác"
    assert note and "Phụ lục II" in note and "Phụ lục IV" in note


def test_cas_status_plain_green_when_no_other_obligation():
    # Chat chi thuoc PL I (khong PL II/III/IV) -> xanh thuan, note None.
    plain = next((r["cas"] for r in DATA if annexes_for(r["cas"]) == {"I"}), None)
    assert plain is not None
    badge, text, note = cas_status(plain)
    assert badge == "ok" and text == "Không cần Giấy phép XNK" and note is None


def test_annex_iv_multiple_thresholds_flagged():
    # 624-83-9 co 2 nguong PL IV khac nhau (150 / 5.000) -> phai canh bao,
    # khong duoc gop lai thanh mot; OBLIGATIONS phai co du II/IV.
    assert set(OBLIGATIONS) == {"II", "IV"}
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
    r3 = IMPORT_RULES["III"]
    assert "≤1%" in r3 and "NQ 19" in r3


def test_moi_verdict_goi_dung_ten_giay():
    # Nguyen tac: cong cu tra loi "chat nay CAN GIAY GI" -> moi cho hien thi phai
    # goi dung ten giay, khong dung chu "Giay phep" trong nghia.
    assert "Giấy phép xuất khẩu, nhập khẩu hóa chất cần kiểm soát đặc biệt" in SHORT_FLAG["III"]
    assert "Giấy chứng nhận đủ điều kiện SX-KD hóa chất có điều kiện" in SHORT_FLAG["II"]
    assert "Không cần giấy phép nào" in SHORT_FLAG["I"]      # PL I khong co giay phep
    assert "Không liên quan Giấy phép XNK" in SHORT_FLAG["IV"]
    # PL III phai neu ro GP XNK khac GP san xuat, kinh doanh KSDB.
    assert "Giấy phép sản xuất, kinh doanh hóa chất KSĐB" in IMPORT_RULES["III"]


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
        [IMPORT_RULES[a] for a in "I II III IV".split()]
        + [SHORT_FLAG[a] for a in "I II III IV".split()]
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


def test_short_flag_surfaces_dieu10_for_pl2():
    # SHORT_FLAG (trước là dead code) giờ được đưa lên bảng tóm tắt — cờ PL II
    # phải nhắc nghĩa vụ công bố / Giấy chứng nhận theo Điều 10.
    assert "Điều 10" in SHORT_FLAG["II"] and "công bố" in SHORT_FLAG["II"]


def test_exemptions_cover_dieu_21_4_and_product_declaration():
    cites = " | ".join(g["cite"] for g in EXEMPTIONS)
    assert "khoản 4" in cites  # san chiết, pha chế nội bộ (Điều 21.4)
    all_items = " ".join(i for g in EXEMPTIONS for i in g["items"])
    assert "Điều 28, 29" in all_items  # nghĩa vụ công bố hàm lượng trong sản phẩm


def test_congbo_is_not_a_customs_gate_pl2():
    # Điều 10.3: công bố mục đích sử dụng KHÔNG phải điều kiện thông quan và
    # doanh nghiệp chủ động thời điểm; điều kiện thông quan là khai báo NK
    # (Điều 6). Cả IMPORT_RULES lẫn SHORT_FLAG phải nói rõ sự phân biệt này.
    rule = IMPORT_RULES["II"]
    assert "Điều 6" in rule and "trước khi thông quan" in rule
    assert "không phải cửa" in rule or "KHÔNG đặt việc công bố làm điều kiện thông quan" in rule
    assert "CHỦ ĐỘNG" in SHORT_FLAG["II"] and "Điều 6" in SHORT_FLAG["II"]


def test_pl3_splits_import_congbo_from_use_deadline():
    # Không được gộp Điều 14.3 (công bố KHI nhập khẩu, không thời hạn cứng)
    # với Điều 15.1 (công bố TRƯỚC 30 NGÀY khi đưa vào sử dụng lần đầu).
    rule = IMPORT_RULES["III"]
    assert "Điều 14.3" in rule and "Điều 15.1" in rule
    # Mốc 30 ngày phải gắn với khâu sử dụng, không gắn với khâu nhập khẩu.
    assert "30 NGÀY" in rule and "SỬ DỤNG" in rule
    # Điều 14.3 phải được nêu là KHÔNG phải điều kiện thông quan.
    assert "KHÔNG phải điều kiện thông quan" in rule


def test_data_regenerated_from_official_nd24():
    # Bản chính thức NĐ24 (markdown) đầy đủ hơn bản textutil cũ: POP nằm ở PL III
    # (không phải PL IV), PL I không bị rớt chất, và errata CAS vẫn được áp dụng.
    assert len(DATA) > 1300
    assert annexes_for("126-72-7") == {"III"}   # Tris(2,3-dibromopropyl)phosphate (POP) -> III
    assert "I" in annexes_for("108-88-3")        # Toluene có trong PL I (bản cũ bị rớt)
    assert annexes_for("10137-74-3") == {"II"} and annexes_for("10037-74-3") == set()  # errata giữ nguyên


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
    test_khong_con_noi_dung_ho_so_trinh_tu_thu_tuc()
    test_decree_cas_errata_corrected()
    test_short_flag_surfaces_dieu10_for_pl2()
    test_exemptions_cover_dieu_21_4_and_product_declaration()
    test_congbo_is_not_a_customs_gate_pl2()
    test_pl3_splits_import_congbo_from_use_deadline()
    test_data_regenerated_from_official_nd24()
    print("ok")
