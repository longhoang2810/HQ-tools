"""Smallest possible regression check: known CAS -> known annex(es), and
that scanning a pasted DN description pulls every CAS out of free text."""
from core import (
    DATA,
    EXEMPTIONS,
    IMPORT_RULES,
    OBLIGATIONS,
    OLD_BANG,
    OLD_HAN_CHE,
    OLD_TIEN_CHAT,
    SHORT_FLAG,
    annexes_for,
    cas_status,
    extract_cas,
    format_report,
    highest_annex,
    transitional_flag_short,
    transitional_status,
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
    badge, text, note = cas_status("67-56-1")
    assert badge == "warn" and text == "Cần Giấy phép" and note is None


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
    assert badge == "ok" and text == "Không cần Giấy phép" and note is None


def test_annex_iv_multiple_thresholds_flagged():
    # 624-83-9 co 2 nguong PL IV khac nhau (150 / 5.000) -> phai canh bao,
    # khong duoc gop lai thanh mot; OBLIGATIONS phai co du II/IV.
    assert set(OBLIGATIONS) == {"II", "IV"}
    rep = format_report("624-83-9")
    assert "150" in rep and "5.000" in rep and "nhiều ngưỡng tồn trữ" in rep


def test_nq19_thresholds_and_devolution():
    # NQ 19 noi nguong: khoan 1 & 2 -> <= ; khoan 3 (hoa chat cam) GIU <0,1%.
    kho = {g["cite"]: g["items"] for g in EXEMPTIONS}
    k123 = next(items for cite, items in kho.items() if "khoản 1-3" in cite)
    assert "≤ 1%" in k123[0]                      # khoan 1: SX-KD
    assert "≤ 1%" in k123[1] and "≤ 5%" in k123[1]  # khoan 2: XNK
    assert "< 0,1%" in k123[2]                     # khoan 3: cam giu nguyen
    # NQ 19 them khoan 7/8/9.
    all_items = " ".join(i for g in EXEMPTIONS for i in g["items"])
    assert "Khoản 7" in all_items and "≤ 1mg" in all_items
    assert "Khoản 8" in all_items and "tại chỗ" in all_items
    assert "Khoản 9" in all_items and "31/12/2026" in all_items
    # Phan cap: Nhom 1 & hoa chat cam -> UBND cap tinh; Nhom 2 -> Bo Cong Thuong.
    r3 = IMPORT_RULES["III"]
    assert "≤1%" in r3 and "NQ 19" in r3
    assert "UBND cấp tỉnh" in r3 and "Nhóm 1" in r3 and "Nhóm 2" in r3
    assert "UBND cấp tỉnh" in SHORT_FLAG["III"] and "Nhóm 2" in SHORT_FLAG["III"]


def test_decree_cas_errata_corrected():
    # 2 mã CAS ghi sai trong NĐ 24 đã sửa về số CAS quốc tế (ERRATA trong
    # extract.py): số sai không còn tra ra, số đúng tra ra đúng phụ lục.
    assert annexes_for("10037-74-3") == set() and annexes_for("10137-74-3") == {"II"}  # Canxi clorat
    assert annexes_for("7746-08-4") == set() and annexes_for("7446-08-4") == {"II"}    # Selen dioxit


def test_short_flag_surfaces_dieu10_for_pl2():
    # SHORT_FLAG (trước là dead code) giờ được đưa lên bảng tóm tắt — cờ PL II
    # phải nhắc nghĩa vụ công bố / Giấy chứng nhận theo Điều 10.
    assert "Điều 10" in SHORT_FLAG["II"] and "công bố" in SHORT_FLAG["II"]


def test_pl3_transitional_exemption_documented():
    # Điều 30.4/30.5 (miễn xuất trình Giấy phép tới 31/12/2026) phải có trong
    # quy tắc PL III để verdict "Cần Giấy phép" không bị hiểu là tuyệt đối.
    assert "30.4" in IMPORT_RULES["III"] and "31/12/2026" in IMPORT_RULES["III"]


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


def test_transitional_old_chemical_is_definitive():
    # P2P là tiền chất công nghiệp cũ (NĐ113) -> khẳng định 'cũ', KHÔNG được miễn.
    st = transitional_status("103-79-7")
    assert st is not None and st[0] == "cu"
    assert "tiền chất công nghiệp" in st[1] and "KHÔNG thuộc diện miễn" in st[1]
    assert "103-79-7" in OLD_TIEN_CHAT


def test_nd82_nd33_resolve_previously_unknown_to_old():
    # Điểm cốt lõi của 'bổ sung': các chất trước đây 'chưa rõ' (chỉ có NĐ113) giờ
    # tra được là 'cũ' nhờ NĐ 82 (hạn chế SX-KD) và NĐ 33 (hóa chất Bảng).
    st_bang = transitional_status("111-48-8")           # Thiodiglycol -> Bảng 2 (NĐ33)
    assert st_bang is not None and st_bang[0] == "cu"
    assert "hóa chất Bảng" in st_bang[1]
    assert "111-48-8" in OLD_BANG

    st_hc = transitional_status("1163-19-5")             # DBDE -> hạn chế SX-KD (NĐ82 PL II)
    assert st_hc is not None and st_hc[0] == "cu"
    assert "hạn chế SX-KD" in st_hc[1]
    assert "1163-19-5" in OLD_HAN_CHE

    # NĐ 82 Điều 1.19 bổ sung tiền chất công nghiệp nhóm 1 (STT 830-835).
    assert "137-43-9" in OLD_TIEN_CHAT
    # Chất 'SX-KD có điều kiện' (STT 820-829) và POP 'khai báo' KHÔNG được coi là cũ
    # theo Điều 30.4 nếu không đồng thời thuộc 3 danh mục -> 7664-41-7 (amoniac) vắng.
    assert "7664-41-7" not in (OLD_TIEN_CHAT | OLD_HAN_CHE | OLD_BANG)


def test_transitional_non_pl3_returns_none():
    # Chỉ hóa chất Phụ lục III mới có trạng thái chuyển tiếp Điều 30.4.
    assert transitional_status("106-99-0") is None      # PL I/II/IV
    assert transitional_flag_short("106-99-0") is None


def test_transitional_failsafe_never_asserts_new_without_caveat():
    # THUỘC TÍNH AN TOÀN: mọi hóa chất PL III chỉ rơi vào 'cu' hoặc 'moi'. Với 'moi'
    # (đã đối chiếu đủ 3 danh mục), công cụ chỉ nói MIỄN XUẤT TRÌNH (không phải miễn
    # Giấy phép) và luôn kèm cảnh báo Bảng 1/2 định nghĩa theo HỌ chất -> không miễn
    # nhầm chất thuộc một họ CWC chưa liệt kê CAS rời.
    pl3 = {r["cas"] for r in DATA if r["annex"] == "III"}
    for cas in pl3:
        st = transitional_status(cas)
        assert st is not None and st[0] in ("cu", "moi")
        if st[0] == "moi":
            assert "miễn XUẤT TRÌNH" in st[1] or "miễn xuất trình" in st[1]
            assert "HỌ" in st[1] or "họ CWC" in st[1]     # cảnh báo định nghĩa theo họ
            assert "chưa có trong công cụ" not in st[1]   # NĐ82/NĐ33 đã tích hợp
        # không câu chữ nào được khẳng định chắc chắn 'được miễn' mà bỏ điều kiện
        assert "chắc chắn được miễn" not in st[1]


if __name__ == "__main__":
    test_known_chemicals()
    test_highest_annex_prioritizes_permit_over_declaration()
    test_extract_cas_from_free_text()
    test_cas_status_annex_iii_always_needs_permit()
    test_cas_status_non_annex_iii_flags_other_obligations()
    test_cas_status_plain_green_when_no_other_obligation()
    test_annex_iv_multiple_thresholds_flagged()
    test_nq19_thresholds_and_devolution()
    test_decree_cas_errata_corrected()
    test_short_flag_surfaces_dieu10_for_pl2()
    test_pl3_transitional_exemption_documented()
    test_exemptions_cover_dieu_21_4_and_product_declaration()
    test_congbo_is_not_a_customs_gate_pl2()
    test_pl3_splits_import_congbo_from_use_deadline()
    test_data_regenerated_from_official_nd24()
    test_transitional_old_chemical_is_definitive()
    test_nd82_nd33_resolve_previously_unknown_to_old()
    test_transitional_non_pl3_returns_none()
    test_transitional_failsafe_never_asserts_new_without_caveat()
    print("ok")
