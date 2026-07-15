"""Smallest possible regression check: known CAS -> known annex(es), and
that scanning a pasted DN description pulls every CAS out of free text."""
from core import DATA, EXEMPTIONS, IMPORT_RULES, SHORT_FLAG, annexes_for, cas_status, extract_cas, highest_annex


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
    print("ok")
