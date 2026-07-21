"""Smallest possible regression check: known CAS -> known annex(es), and
that scanning a pasted DN description pulls every CAS out of free text."""
import json
import re
import shutil
import subprocess
from pathlib import Path

import core

from core import (
    DATA,
    EXEMPTIONS,
    PENALTY_WARNING,
    IMPORT_RULES,
    OTHER_OBLIGATIONS,
    OTHER_OBLIGATION_ANNEXES,
    VERDICT,
    annexes_for,
    annex_labels,
    cas_status,
    extract_cas,
    format_report,
    rows_for,
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
    assert annex_labels("67-56-1") == "PL I, PL III, PL IV"


def test_extract_cas_from_free_text():
    text = "Hỗn hợp gồm Metanol CAS 67-56-1, Acetaldehyde (75-07-0) và mã CAS 103-79-7 (P2P)."
    assert extract_cas(text) == ["67-56-1", "75-07-0", "103-79-7"]


def test_extract_cas_ascii_boundary_nhu_js():
    # \b Python mặc định là unicode: "ấ67-56-1" KHÔNG match vì "ấ" là word char,
    # trong khi \b của JS là ASCII nên match -> CLI sót CAS mà HTML thấy.
    # re.ASCII bắt hai bên hành xử y hệt trên chữ có dấu.
    assert extract_cas("ấ67-56-1") == ["67-56-1"]
    # Chữ ASCII dính liền thì cả hai bên cùng KHÔNG match — giữ nguyên.
    assert extract_cas("a67-56-1") == []


def test_khong_con_ten_rong_trong_data():
    # nd24.md có dòng tiếp diễn chỉ chứa CAS (|  |  |  | 134237-51-7 |  |) — CAS
    # thứ 2+ của chất dòng trên. extract.py từng không kế thừa tên -> 6 mã CAS
    # tên rỗng, lookup in "CAS ...:  ()".
    assert all(r["name_vn"].strip() and r["name_en"].strip() for r in DATA)
    hbcd = next(r for r in DATA if r["cas"] == "134237-51-7")
    assert "Hexabrom" in hbcd["name_vn"]


def test_cas_status_annex_iii_always_needs_permit():
    # Khong tu nhan dien % nua -> hoa chat PL III luon bao can giay phep,
    # du thuc te co the duoc mien theo nong do (can doi chieu thu cong).
    # Verdict phai goi DUNG TEN giay, khong noi "Giay phep" trong nghia.
    assert cas_status("67-56-1") == ("warn", "Cần Giấy phép XNK hóa chất KSĐB")


def test_cas_status_non_annex_iii_flags_other_obligations():
    # 106-99-0 = PL I/II/IV, khong PL III -> PL II van tao nghia vu khac;
    # PL IV khong lien quan den verdict nhap khau.
    assert cas_status("106-99-0") == ("ok", "Không cần Giấy phép XNK — có nghĩa vụ khác")
    assert set(OTHER_OBLIGATION_ANNEXES) == {"II"}


def test_cas_status_plain_green_when_no_other_obligation():
    # Chat chi thuoc PL I (khong PL II/III/IV) -> xanh thuan.
    plain = next((r["cas"] for r in DATA if annexes_for(r["cas"]) == {"I"}), None)
    assert plain is not None
    assert cas_status(plain) == ("ok", "Không cần Giấy phép XNK")


def test_annex_iv_storage_omitted_from_import_report():
    # Nguong ton tru PL IV khong thuoc khau nhap khau va khong hien trong bao cao.
    rep = format_report("624-83-9")
    assert "tồn trữ" not in rep and "Phụ lục IV" not in rep


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
    other = re.sub(r"\s+", " ", " ".join(OTHER_OBLIGATIONS)).lower()
    assert "giấy chứng nhận đủ điều kiện sản xuất, kinh doanh hóa chất có điều kiện" in other
    assert "các trường hợp được miễn giấy phép xnk quy định tại điều 21" in r["III"]


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
    # Duyệt đúng các khóa thật của IMPORT_RULES; PL II đã chuyển xuống khối
    # "Nghĩa vụ khác", hard-code II ở đây sẽ gọi undefined.map và làm nút Tra cứu chết.
    assert "for (const annex of Object.keys(IMPORT_RULES))" in src
    # Bộ lọc dòng category cũng phải nhúng từ core — JS từng hard-code
    # ["I","II","III"] trong khi core.IMPORT_ANNEXES = ("I","III"), làm chất
    # chỉ thuộc PL II hiện khác nhau giữa HTML và CLI.
    assert "IMPORT_ANNEXES.includes(r.annex)" in src and "__IMPORT_ANNEXES_JSON__" in src
    assert '["I", "II", "III"]' not in src, "bộ lọc phụ lục viết tay trong JS — dùng __IMPORT_ANNEXES_JSON__"
    # Thứ tự ưu tiên phụ lục cũng nhúng từ core — JS từng hard-code bản riêng.
    assert "__ANNEX_ORDER_JSON__" in src
    assert '["III", "II", "I", "IV"]' not in src, "ANNEX_ORDER viết tay trong JS — dùng __ANNEX_ORDER_JSON__"
    # ...và artifact đã commit phải khớp core.py (chạy lại build_html.py nếu đỏ).
    html = Path(__file__).with_name("Tra-cuu-hoa-chat-ND24.html")
    if html.exists():
        page = html.read_text(encoding="utf-8")
        assert VERDICT["pl3"] in page, "HTML đã commit cũ hơn core.py — chạy python3 build_html.py"
        assert PENALTY_WARNING in page, "HTML cũ hơn core.py — chạy python3 build_html.py"
        assert core.OTHER_OBLIGATIONS_TITLE in page


def test_html_co_nut_vi_du_ngau_nhien():
    src = Path(__file__).with_name("build_html.py").read_text(encoding="utf-8")
    assert 'onclick="randomExampleForMode()"' in src  # ví dụ theo đúng chế độ đang chọn
    assert 'onclick="setMode(\'cas\')"' in src and 'onclick="setMode(\'name\')"' in src
    assert 'onclick="clearAll()"' in src
    assert 'const byCas = new Map()' in src
    assert 'shuffle(items).map(([name, cas]) => `${name} (CAS ${cas})`)' in src


def test_vi_du_ngau_nhien_van_con_case_khong_ro():
    # Ví dụ ngẫu nhiên chèn sẵn một CAS NGOÀI Phụ lục I-IV để luôn hiện đủ cả
    # verdict "Không rõ". Danh sách này viết tay trong JS -> nếu bản NĐ sau đưa
    # hết mấy chất đó vào Phụ lục, bộ lọc lúc chạy bỏ sạch và ví dụ MẤT case
    # "Không rõ" mà không ai hay. Đỏ = thêm một chất khác còn ngoài dữ liệu.
    src = Path(__file__).with_name("build_html.py").read_text(encoding="utf-8")
    m = re.search(r"const OUTSIDE_DATA = \[(.*?)\];", src)
    assert m, "không tìm thấy OUTSIDE_DATA trong build_html.py"
    cas_list = core.CAS_RE.findall(m.group(1))
    assert cas_list, "OUTSIDE_DATA không có mã CAS nào"
    in_data = {r["cas"] for r in DATA}
    assert any(c not in in_data for c in cas_list), (
        "mọi CAS trong OUTSIDE_DATA đều đã có trong dữ liệu — ví dụ ngẫu nhiên "
        "không còn chất nào ra 'Không rõ'"
    )


def _run_js(snippet):
    """Chạy JS của trang bằng node để test THẬT hàm dò tên, không chỉ soi chuỗi
    nguồn. Trang là file HTML tĩnh nên không có harness JS nào — node lấy nguyên
    khối <script> đã build, chỉ chặn mấy dòng DOM ở cuối bằng stub document."""
    node = shutil.which("node")
    if not node:
        return None  # máy không có node -> bỏ qua, phần còn lại vẫn chạy python thuần
    html = Path(__file__).with_name("Tra-cuu-hoa-chat-ND24.html")
    if not html.exists():
        return None
    script = re.search(r"<script>(.*)</script>", html.read_text(encoding="utf-8"), re.S).group(1)
    stub = (
        "const document = { getElementById: () => ({ addEventListener() {}, focus() {} }),"
        " querySelector: () => null, querySelectorAll: () => [] };\n"
        "const location = { hash: '' };\n"
        "function addEventListener() {}\n"
        "const scrollY = 0;\n"
    )
    proc = subprocess.run(
        [node, "-e", stub + script + "\n" + snippet],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, f"node lỗi: {proc.stderr[:600]}"
    return json.loads(proc.stdout)


def test_do_ten_hoa_chat_trong_mo_ta_khong_co_ma_cas():
    # Mô tả DN không kèm mã CAS: phải dò được TÊN nằm trong đoạn văn. Trước đây
    # chỉ khớp khi gõ trống đúng một tên chất -> nguyên đoạn mô tả ra "không tìm
    # thấy gì", đúng loại mô tả mà DN hay khai nhất.
    got = _run_js("""
      console.log(JSON.stringify({
        mota: scanNames("Hỗn hợp dung môi công nghiệp gồm Metanol, Toluene và nước cất."),
        // "etanol" KHÔNG được ăn vào "metanol" (khớp theo TỪ, không theo ký tự)
        chi_metanol: scanNames("Metanol"),
        // cụm DÀI NHẤT thắng: "natri hydroxit" (có trong dữ liệu) không được
        // báo kèm cả "Natri" (7440-23-5) nằm trong tên nó
        natri_hydroxit: scanNames("Dung dịch natri hydroxit 5%"),
        // đoạn không có hóa chất nào -> không bịa ra chất
        rong: scanNames("Hàng hóa đóng trong thùng carton, không nguy hiểm"),
        // dấu câu khác nhau vẫn cùng một tên; và DN khai tên KHÔNG kèm đuôi
        // qualifier của nghị định ("... và các muối proton hóa chất tương ứng")
        // vẫn phải ra ĐÚNG chất 108-01-0 (PL II — nghĩa vụ Giấy chứng nhận SX-KD),
        // tuyệt đối không tụt xuống khớp chữ "etanol" -> ra Etanol 64-17-5 (PL I):
        // sai chất, và giấu mất nghĩa vụ PL II của chất thật.
        dau_cau: scanNames("chứa N,N dimetyl amino etanol"),
      }));
    """)
    if got is None:
        return
    assert "67-56-1" in got["mota"] and "108-88-3" in got["mota"], f"sót tên trong mô tả: {got['mota']}"
    assert got["chi_metanol"] == ["67-56-1"], f"'etanol' ăn vào 'metanol': {got['chi_metanol']}"
    assert got["natri_hydroxit"] == ["1310-73-2"], f"không ưu tiên cụm dài nhất: {got['natri_hydroxit']}"
    assert got["rong"] == [], f"bịa ra chất từ đoạn không có hóa chất: {got['rong']}"
    assert got["dau_cau"] == ["108-01-0"], (
        f"tên khai thiếu đuôi qualifier ra sai chất: {got['dau_cau']} (64-17-5 = Etanol)"
    )


def test_che_do_cas_khong_de_ten_lot_vao_bang():
    # Ranh giới giữa hai chế độ. Dò tên có thể khớp thừa ("natri clorua" -> chất
    # "Natri"), nên chế độ CAS phải KHÔNG BAO GIỜ đưa chất khớp theo tên vào bảng
    # kết luận — nếu không, cái báo thừa đó lây sang mọi lô hàng có khai mã CAS.
    # Ngược lại, chất chỉ ghi tên cũng không được bỏ qua im lặng -> phải nhắc.
    got = _run_js("""
      const els = {};
      globalThis.__el = id => els[id] || (els[id] = { value: "", innerHTML: "", placeholder: "",
        classList: { toggle() {} }, setAttribute() {}, addEventListener() {}, focus() {}, scrollIntoView() {} });
      document.getElementById = globalThis.__el;
      __el("input").value = "Hỗn hợp gồm Metanol CAS 67-56-1 và Toluene";
      MODE = "cas"; run();
      const casMode = __el("results").innerHTML;
      MODE = "name"; run();
      const nameMode = __el("results").innerHTML;
      console.log(JSON.stringify({
        cas_co_metanol: casMode.includes("67-56-1"),
        cas_co_toluene: casMode.includes("108-88-3"),   // phải KHÔNG — tên không được vào bảng
        cas_nhac_ten: casMode.includes("Toluene"),      // nhưng phải được nhắc tới
        ten_co_toluene: nameMode.includes("108-88-3"),
        ten_nhac_ma_cas: nameMode.includes("mã CAS —"),
      }));
    """)
    if got is None:
        return
    assert got["cas_co_metanol"], "chế độ CAS sót mã CAS có trong đoạn"
    assert not got["cas_co_toluene"], "chế độ CAS để chất khớp theo TÊN lọt vào bảng kết luận"
    assert got["cas_nhac_ten"], "chế độ CAS bỏ qua im lặng chất chỉ ghi tên — phải nhắc"
    assert got["ten_co_toluene"], "chế độ tên không dò ra chất chỉ ghi tên"
    assert got["ten_nhac_ma_cas"], "chế độ tên bỏ qua mã CAS trong đoạn mà không nhắc"


def test_pl3_khong_ma_cas_khong_bi_bo_im_lang():
    # Phụ lục III có mục ghi theo HỌ chất, ô CAS để "---" -> extract.py bỏ khỏi
    # bảng tra (đúng, không có mã để tra), nhưng bỏ IM LẶNG thì công cụ giấu mất
    # vùng mù: Asen trioxit (1327-53-3) chỉ có mã ở PL IV nên ra "không cần Giấy
    # phép", trong khi mục 37 "Asen và các hợp chất của asen" của PL III phủ nó.
    stt = {e["stt"] for e in core.PL3_NO_CAS}
    assert {"37.", "38.", "39.", "40.", "41."} <= stt, f"thiếu họ nguyên tố: {sorted(stt)}"
    assert len(core.PL3_NO_CAS) >= 13
    assert all(e["ten"].strip() and e["category"] for e in core.PL3_NO_CAS)
    # Ca cụ thể đã đo được: đừng ai "sửa" nó thành xanh sạch mà không đọc mục 37.
    assert cas_status("1327-53-3")[1] == VERDICT["none"] and "III" not in annexes_for("1327-53-3")
    khoi = core.format_pl3_no_cas()
    assert "Asen và các hợp chất của asen" in khoi and "Các hợp chất xyanua" in khoi
    # Danh sách phải sinh từ nd24.md, không gõ tay trong HTML.
    src = Path(__file__).with_name("build_html.py").read_text(encoding="utf-8")
    assert "__PL3_NO_CAS_HTML__" in src and "core.PL3_NO_CAS" in src
    assert "Asen và các hợp chất" not in src, "danh sách gõ tay trong build_html.py — phải lấy từ core"
    html = Path(__file__).with_name("Tra-cuu-hoa-chat-ND24.html")
    if html.exists():
        assert "Asen và các hợp chất của asen" in html.read_text(encoding="utf-8"), (
            "HTML đã commit cũ hơn dữ liệu — chạy python3 build_html.py"
        )


def test_dong_ngoai_tru_pl3_khong_bi_doc_nguoc():
    # Phụ lục III có 2 dòng "Ngoại trừ:" — chất NGAY DƯỚI nó là chất bị LOẠI TRỪ
    # khỏi mục ngay trên, không phải chất thuộc mục (nguyên văn Công ước CWC:
    # Bảng 2 B.4 miễn trừ Fonofos, B.10 miễn trừ DMAE/DEAE). Parser từng đọc ngược
    # -> bắt doanh nghiệp xin Giấy phép XNK cho chất nghị định đã nói rõ là không phải.
    for cas in ("944-22-9", "108-01-0", "100-37-8"):
        assert "III" not in annexes_for(cas), f"{cas} bị xếp PL III — đọc ngược dòng Ngoại trừ"
        assert core.pl3_excluded(cas), f"{cas} phải nằm trong danh sách ngoại trừ để giải thích được"
    # Hai chất kia vẫn là PL II (mục 278/265) -> verdict phải nói còn nghĩa vụ khác.
    assert cas_status("108-01-0") == ("ok", VERDICT["other_obligation"])
    assert cas_status("100-37-8") == ("ok", VERDICT["other_obligation"])
    # Fonofos chỉ xuất hiện ở dòng ngoại trừ -> không thuộc phụ lục nào.
    assert annexes_for("944-22-9") == set()
    # ...nhưng mã CÓ in trong bảng PL III của nghị định, nên "không có trong dữ
    # liệu" phải kèm lý do, không thì trông như tool sót.
    rep = re.sub(r"\s+", " ", format_report("944-22-9"))
    assert "Ngoại trừ" in rep and "mục 26" in rep

    # KHÔNG được nuốt oan chất thuộc mục: 676-97-1 và 756-79-6 nằm dưới dòng
    # "Ví dụ:" của mục 26 (là VÍ DỤ CỦA mục, không phải ngoại trừ) -> vẫn PL III.
    for cas in ("676-97-1", "756-79-6"):
        assert annexes_for(cas) == {"III"}, f"{cas} là ví dụ của mục 26, không được bỏ"
    # ...và chất ngay sau khối ngoại trừ (mục 34, 35, 36) không bị dính theo.
    assert annexes_for("111-48-8") == {"III"} and annexes_for("464-07-3") == {"III"}
    assert len(core.PL3_EXCLUDED) == 3, core.PL3_EXCLUDED


def test_co_ho_chat_bat_dung_ca_xanh_nguy_hiem():
    # Khối cảnh báo cuối trang không cứu được ca này: cán bộ đọc dòng xanh "Không
    # cần Giấy phép XNK" là xong, không cuộn xuống. Nên chất có TÊN gợi ý thuộc họ
    # chất PL III phải được gắn cờ NGAY TRONG dòng kết quả.
    hints = core.pl3_family_hints("1327-53-3")          # Asen trioxit
    assert [h["stt"] for h in hints] == ["37."], hints
    assert core.pl3_family_hints("143-33-9") == []      # không có trong dữ liệu -> không có tên để đoán
    # Chất ĐÃ là PL III thì thôi, verdict đã đỏ — nhắc thêm chỉ làm nhiễu.
    assert core.pl3_family_hints("67-56-1") == []
    # Không được báo thừa: chạy trên toàn bộ dữ liệu, chỉ 7 chất đã đo được dính.
    flagged = {c for c in {r["cas"] for r in DATA} if core.pl3_family_hints(c)}
    assert flagged == {
        "1303-28-2", "1327-53-3", "7784-42-1",     # hợp chất asen -> mục 37
        "24613-89-6", "49663-84-5",                # cromat -> mục 38
        "13424-46-9", "63918-97-8",                # hợp chất chì -> mục 41
    }, sorted(flagged)
    # ...và tất cả đều đang XANH — đó chính là lý do phải gắn cờ.
    assert all(cas_status(c)[0] == "ok" for c in flagged)
    # format_report bẻ dòng bằng textwrap -> so trên bản đã chuẩn hóa khoảng
    # trắng, không thì đỏ oan vì cụm từ bị ngắt (xem norm_rules).
    rep = re.sub(r"\s+", " ", format_report("1327-53-3"))
    assert re.sub(r"\s+", " ", core.PL3_HINT_PREFIX) in rep
    assert "Asen và các hợp chất của asen" in rep


def test_co_ho_chat_html_khop_core():
    # JS dựng lại pl3_family_hints -> phải khớp core trên TOÀN BỘ dữ liệu, không
    # chỉ vài ca mẫu: lệch ở đây nghĩa là trang HTML và CLI kết luận khác nhau về
    # cùng một lô hàng. Chạy thẳng JS của trang bằng node rồi so.
    got = _run_js("""
      const out = [...new Set(DATA.map(r => r.cas))].filter(c => pl3FamilyHints(c).length)
        .map(c => [c, pl3FamilyHints(c).map(e => e.stt)]);
      console.log(JSON.stringify(Object.fromEntries(out)));
    """)
    if got is None:
        return
    mine = {
        c: [h["stt"] for h in core.pl3_family_hints(c)]
        for c in {r["cas"] for r in DATA}
        if core.pl3_family_hints(c)
    }
    assert got == mine, f"JS và core lệch nhau: chỉ JS {set(got) - set(mine)}, chỉ core {set(mine) - set(got)}"


def test_pl3_hoa_chat_khac_khong_bi_gan_nham_bang_2():
    # nd24.md: Nhóm 1 có tiêu đề "Hóa chất khác" (mục 37-41 + 113 chất có mã CAS)
    # nằm SAU khối B – Hóa chất Bảng 2. Parser không biết tiêu đề này thì cả 113
    # chất mang category của khối trước -> trang nói Benzen thuộc "Công ước Vũ khí
    # hóa học". Verdict vẫn đúng (đều PL III) nhưng CĂN CỨ hiện ra thì sai.
    def cat3(cas):
        return next(r["category"] for r in rows_for(cas) if r["annex"] == "III")

    assert "Hóa chất khác" in cat3("71-43-2")        # Benzen
    assert "Hóa chất khác" in cat3("625-45-6")       # Axit methoxy axetic
    assert "Bảng 2" not in cat3("71-43-2")
    # ...và chất Bảng 2 THẬT (mục 35, ngay trước tiêu đề đó) vẫn đúng là Bảng 2.
    assert "Bảng 2" in cat3("111-48-8")              # Thiodiglycol


def test_html_can_deu_chu_thich_va_luu_y():
    src = Path(__file__).with_name("build_html.py").read_text(encoding="utf-8")
    assert "details.detail .body" in src and "text-align: justify" in src
    assert ".exempt li" in src and ".exempt .warn-note" in src
    assert ".instructions li" in src and ".note" in src


def test_khong_con_noi_dung_ho_so_trinh_tu_thu_tuc():
    # PHAM VI: trang tra cuu "can giay gi" -> khong chua ho so/trinh tu/thu tuc cap,
    # tham quyen cap (phan cap NQ 19), hay khoi chuyen tiep Dieu 30.4 (mien XUAT
    # TRINH ho so GP SX-KD). Chan viec chung quay lai.
    blob = " ".join(
        [" ".join(IMPORT_RULES[a]) for a in "I III".split()]
        + [" ".join(OTHER_OBLIGATIONS)]
        + [i for g in EXEMPTIONS for i in g["items"]]
        + [g["cite"] for g in EXEMPTIONS]
        + [PENALTY_WARNING]
    )
    for banned in (
        "UBND cấp tỉnh",        # tham quyen cap (phan cap NQ 19)
        # Chan "ai CAP giay" chu khong chan moi lan nhac ten bo: CV 2595 cho phep
        # dung GP ban PDF ky so cua BCT de thong quan — day la viec cua khau
        # thong quan, dung pham vi, khong phai tham quyen cap phep.
        "Bộ Công Thương cấp",   # tham quyen cap
        "thẩm quyền cấp",       # tham quyen cap
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
    # Đ21.4 nguyên văn chỉ miễn "Giấy chứng nhận, Giấy phép SẢN XUẤT" — không có
    # "kinh doanh" (khác khoản 1). Từng viết rộng hơn luật.
    k4 = next(i for g in EXEMPTIONS for i in g["items"] if "Điều 21.4" in i)
    assert "Giấy phép SẢN XUẤT" in k4 and "Giấy phép sản xuất, kinh doanh" not in k4
    # Đ21.6.b có cả "sản phẩm bảo quản, chế biến nông sản..." — từng bị rớt khỏi
    # danh sách miễn trừ (sót một diện miễn = đòi giấy phép oan).
    assert "bảo quản, chế biến nông sản, lâm sản, hải sản" in all_items


def test_lookup_pl2_tu_noi_nghia_vu():
    # lookup.py chỉ in mỗi báo cáo (không có bảng verdict + mục 'NGHĨA VỤ KHÁC'
    # như scan.py) -> chất Phụ lục II phải tự nói nghĩa vụ, không thì
    # "Không phát sinh yêu cầu nhập khẩu riêng" bị đọc thành "không phải làm gì".
    rep = core.format_lookup("10137-74-3")  # Canxi clorat, chỉ PL II
    assert "Nghĩa vụ khác (Phụ lục II)" in rep
    assert "Giấy chứng nhận đủ điều kiện" in rep
    # Chất không thuộc PL II thì không kèm khối này.
    assert "Nghĩa vụ khác" not in core.format_lookup("103-79-7")  # chỉ PL III


def test_congbo_is_not_a_customs_gate_pl2():
    # Điều 10.3: công bố mục đích sử dụng KHÔNG phải điều kiện thông quan và
    # doanh nghiệp CHỦ ĐỘNG thời điểm; điều kiện thông quan là khai báo NK
    # (Điều 6). Nghĩa vụ Phụ lục II hiện ở khối "Nghĩa vụ khác" bên dưới mục miễn
    # trừ; câu khai báo tách sang DECLARATION_RULE (mục "A. Khai báo") vì là
    # nghĩa vụ chung, không riêng Phụ lục II.
    rule = re.sub(r"\s+", " ", " ".join(OTHER_OBLIGATIONS)).lower()
    decl = re.sub(r"\s+", " ", core.DECLARATION_RULE).lower()
    # cửa thông quan = khai báo (Điều 6), KHÔNG phải công bố
    assert "khai báo hóa chất nhập khẩu qua cổng một cửa" in decl
    assert "không riêng phụ lục ii" in decl
    assert "điều 6" in decl
    assert "phản hồi khai báo mới được thông quan" in decl
    assert "chương 28, 29" in decl
    # lookup.py tra 1 CAS không có mục A đứng cạnh -> vẫn phải in kèm câu này.
    assert "phản hồi khai báo mới được thông quan" in core.format_lookup("107-13-1")
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
    # Điều 14.3: gắn khâu NHẬP KHẨU và không phải cửa thông quan.
    assert "KHI nhập khẩu" in b14 and "không phải điều kiện thông quan" in b14
    # Điều 15.1: mốc 30 NGÀY là mốc cứng, gắn khâu SỬ DỤNG.
    assert "TRƯỚC 30 NGÀY" in b15 and "SỬ DỤNG" in b15
    assert "không phải khâu nhập khẩu" in b15
    # Nội dung công bố cũng khác nhau, không chỉ mốc thời gian: Điều 14.3 chỉ
    # công bố mục đích, Điều 15.1 công bố CẢ loại hóa chất lẫn mục đích (rộng hơn).
    assert "LOẠI HÓA CHẤT VÀ MỤC ĐÍCH SỬ DỤNG" in b15
    assert "LOẠI HÓA CHẤT" not in b14


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
    assert core.annexes_to_explain({"I", "III", "IV"}) == ["III"]
    assert core.annexes_to_explain({"I"}) == ["I"]          # không có III thì vẫn hiện
    assert core.annexes_to_explain({"II", "III"}) == ["III"]  # PL II ở khối Nghĩa vụ khác
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


def test_bang_scan_thang_cot_khi_co_cas_khong_tra_ra():
    # Hỗn hợp thật của DN hay lẫn 1 mã CAS không có trong dữ liệu. Bề rộng cột tên
    # từng chỉ đo các chất CÓ dữ liệu -> "(không có trong dữ liệu)" (24 ký tự) tràn
    # cột, đẩy lệch Phụ lục/Trạng thái của riêng dòng đó. Mọi dòng phải thẳng cột.
    import io
    import contextlib

    import scan

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        scan.print_summary(["108-88-3", "64-17-5", "75-09-2"])   # Toluene, Etanol, không có
    rows = [l for l in buf.getvalue().split("\n") if l and not l.startswith("-")][2:]
    assert len(rows) == 3
    moc = [r.index(annex_labels(cas)) for r, cas in zip(rows, ["108-88-3", "64-17-5", "75-09-2"])]
    assert len(set(moc)) == 1, f"cột Phụ lục lệch giữa các dòng: {moc}"


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


def test_hai_muc_quy_dinh_mien_tru_dung_dieu():
    # Phần "Quy định" của mỗi mục TRỎ VỀ IMPORT_RULES/OTHER_OBLIGATIONS theo chỉ
    # số -> ai xếp lại thứ tự hai danh sách kia là mục này im lặng dẫn nhầm điều
    # luật (miễn trừ khai báo áp sang giấy phép và ngược lại). Chốt theo Điều.
    sect = {s["key"]: s for s in core.EXEMPT_SECTIONS}
    kb = " ".join(sect["khaibao"]["rule"])
    gp = " ".join(sect["giayphep"]["rule"])
    assert "Điều 6" in kb and "khai báo" in kb.lower()
    assert "Giấy phép" not in kb, "mục khai báo không được nói về giấy phép"
    assert "Điều 14.2" in gp
    assert "chữ ký số" in gp and "2595/HC-QLHC" in gp, "thiếu CV 2595 (GP bản PDF ký số)"
    # Giấy chứng nhận của Phụ lục II (quy định Điều 8, 9, 10.2 + miễn Điều 10.3)
    # nằm TRỌN ở khối cuối, không xé đôi sang mục B.
    other = " ".join(OTHER_OBLIGATIONS)
    assert "Điều 8, 9, 10.2" in other and "Điều 10.3" in other
    assert "Điều 10.3" not in gp and "Điều 10.3" not in " ".join(
        i for g in EXEMPTIONS for i in g["items"]
    ), "miễn Giấy chứng nhận PL II bị lặp lại ngoài khối cuối"
    # Mọi nhóm miễn trừ phải nằm trong đúng một mục — thiếu section là rơi khỏi
    # cả hai mục, biến mất im lặng khỏi trang lẫn CLI.
    keys = {s["key"] for s in core.EXEMPT_SECTIONS}
    assert all(g.get("section") in keys for g in EXEMPTIONS)
    rep = core.format_exemptions()
    for g in EXEMPTIONS:
        assert g["title"] in rep
    assert rep.index("A. KHAI BÁO") < rep.index("B. GIẤY PHÉP") < rep.index("Miễn trừ khác")


def test_toan_van_hai_nghi_dinh_nhung_trong_trang():
    # Trang phải tự chứa toàn văn NĐ 24 + NĐ 26 (không đi kèm file .docx rời, vì
    # trang hay được gửi lẻ một file). Và mọi link "#..." phải có đích thật —
    # link chết thì cán bộ bấm vào không thấy gì mà cũng không báo lỗi.
    html = Path(__file__).with_name("Tra-cuu-hoa-chat-ND24.html").read_text(encoding="utf-8")
    ids = set(re.findall(r'id="(nd2[46]-[^"]+)"', html))
    hrefs = {h for h in re.findall(r'href="#(nd2[46]-[^"]+)"', html) if "${" not in h}
    assert not hrefs - ids, f"link tới mục không tồn tại: {hrefs - ids}"
    # Link dựng lúc chạy trong JS (annexLink) không soi tĩnh được -> chốt riêng:
    # mọi Phụ lục hiện trong cột "Phụ lục" phải có đích trong khối toàn văn.
    assert 'href="#nd24-pl-${esc(a).toLowerCase()}"' in html, "annexLink đổi dạng id"
    for a in core.ANNEX_DISPLAY_ORDER:
        assert f"nd24-pl-{a.lower()}" in ids, f"cột Phụ lục link tới PL {a} nhưng không có đích"
    assert all(i.isascii() for i in ids), "id có dấu -> location.hash percent-encode sẽ không khớp"
    assert len([i for i in ids if i.startswith("nd26-dieu-")]) == 31, "NĐ 26 có 31 Điều"
    assert len([i for i in ids if i.startswith("nd24-dieu-")]) == 5, "NĐ 24 có 5 Điều"
    assert {f"nd24-pl-{n}" for n in ("i", "ii", "iii", "iv")} <= ids, "thiếu Phụ lục NĐ 24"
    # Bảng Phụ lục là phần dài nhất, dễ rơi im lặng nếu parser bảng hỏng.
    assert "1327-53-3" in html and "Điều 31. Hiệu lực thi hành" in html
    # Dẫn chiếu trong mục miễn trừ phải là link tới Điều tương ứng của NĐ 26.
    assert '<a href="#nd26-dieu-21">Điều 21</a>' in html
    # ...nhưng KHÔNG được biến "Điều 19" của NĐ 169 (nghị định khác, không có
    # toàn văn trong repo) thành link trỏ nhầm sang Điều 19 của NĐ 26.
    assert core.PENALTY_WARNING.split("Điều 19")[0] + "Điều 19 Nghị định" in html


if __name__ == "__main__":
    # Máy không có pytest nên đây là runner thật. Duyệt tự động thay vì gọi tay
    # từng test — danh sách tay đã từng quên 2 test HTML, thành chữ chết.
    tests = [f for name, f in sorted(globals().items()) if name.startswith("test_")]
    for f in tests:
        f()
    print(f"ok ({len(tests)} tests)")
