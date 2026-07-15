"""Smallest possible regression check: known CAS -> known annex(es), and
that scanning a pasted DN description pulls every CAS out of free text."""
from core import (
    DATA,
    EXEMPTIONS,
    IMPORT_RULES,
    ND113_OLD,
    ND113_TIEN_CHAT,
    SHORT_FLAG,
    annexes_for,
    cas_status,
    extract_cas,
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


def test_cas_status_non_annex_iii_ok():
    badge, text, note = cas_status("106-99-0")  # PL I/II/IV, khong co PL III
    assert badge == "ok" and text == "Không cần Giấy phép"


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
    assert "NĐ 113/2017" in st[1] and "KHÔNG thuộc diện miễn" in st[1]
    assert "103-79-7" in ND113_TIEN_CHAT


def test_transitional_non_pl3_returns_none():
    # Chỉ hóa chất Phụ lục III mới có trạng thái chuyển tiếp Điều 30.4.
    assert transitional_status("106-99-0") is None      # PL I/II/IV
    assert transitional_flag_short("106-99-0") is None


def test_transitional_failsafe_never_asserts_new_without_caveat():
    # THUỘC TÍNH AN TOÀN: với MỌI hóa chất PL III không có trong NĐ113, công cụ
    # KHÔNG được tự kết luận 'mới/được miễn' — luôn phải kèm cảnh báo đối chiếu
    # NĐ 82/2022 và Danh mục Bảng NĐ 33/2024. Đây là điểm dễ sai gây miễn nhầm.
    pl3 = {r["cas"] for r in DATA if r["annex"] == "III"}
    for cas in pl3:
        st = transitional_status(cas)
        assert st is not None and st[0] in ("cu", "chua_xac_dinh")
        if st[0] == "chua_xac_dinh":
            assert "NĐ 82/2022" in st[1] and "NĐ 33/2024" in st[1]
            assert "phải đối chiếu" in st[1].lower() or "PHẢI đối chiếu" in st[1]
        # không câu chữ nào được khẳng định chắc chắn 'được miễn' mà bỏ điều kiện
        assert "chắc chắn được miễn" not in st[1]


if __name__ == "__main__":
    test_known_chemicals()
    test_highest_annex_prioritizes_permit_over_declaration()
    test_extract_cas_from_free_text()
    test_cas_status_annex_iii_always_needs_permit()
    test_cas_status_non_annex_iii_ok()
    test_decree_cas_errata_corrected()
    test_short_flag_surfaces_dieu10_for_pl2()
    test_pl3_transitional_exemption_documented()
    test_exemptions_cover_dieu_21_4_and_product_declaration()
    test_congbo_is_not_a_customs_gate_pl2()
    test_pl3_splits_import_congbo_from_use_deadline()
    test_data_regenerated_from_official_nd24()
    test_transitional_old_chemical_is_definitive()
    test_transitional_non_pl3_returns_none()
    test_transitional_failsafe_never_asserts_new_without_caveat()
    print("ok")
