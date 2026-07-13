"""Smallest possible regression check: known CAS -> known annex(es), and
that scanning a pasted DN description pulls every CAS out of free text."""
from core import DATA, annexes_for, cas_status, extract_cas, highest_annex


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


if __name__ == "__main__":
    test_known_chemicals()
    test_highest_annex_prioritizes_permit_over_declaration()
    test_extract_cas_from_free_text()
    test_cas_status_annex_iii_always_needs_permit()
    test_cas_status_non_annex_iii_ok()
    print("ok")
