# Tra cứu CAS – Nghị định 24/2026/NĐ-CP & 26/2026/NĐ-CP

Nhập mã CAS (hoặc dán nguyên mô tả hàng hóa của doanh nghiệp), cho biết
hóa chất thuộc Phụ lục nào (I–IV) của NĐ 24/2026/NĐ-CP và yêu cầu thủ tục
khi nhập khẩu theo NĐ 26/2026/NĐ-CP.

## Cách dễ nhất: mở `Tra-cuu-hoa-chat-ND24.html` bằng trình duyệt

Không cần cài Python, không cần terminal. Double-click file
[`Tra-cuu-hoa-chat-ND24.html`](<Tra-cuu-hoa-chat-ND24.html>) (hoặc mở bằng trình duyệt bất kỳ, kể cả không
có mạng — dữ liệu đã nhúng sẵn trong file). Dán mô tả DN vào ô, bấm
**Tra cứu**, đọc bảng kết quả (dòng đỏ = bắt buộc xin Giấy phép).

Cuối trang có **toàn văn cả hai nghị định** (NĐ 24 gồm đủ Phụ lục I–IV, NĐ 26 đủ
31 Điều), mở bằng link "📖 Đọc toàn văn" ở đầu trang. Nhúng thẳng vào file HTML —
không cần kèm file `.docx`, vì trang hay được gửi lẻ một file. Mỗi Điều/Phụ lục
có mục lục riêng để nhảy tới. Mọi dẫn chiếu trên trang đều là **link bấm được**:
cột "Phụ lục" của từng dòng kết quả → đúng Phụ lục trong NĐ 24; số mục ở cờ đỏ
họ chất và ở khối "Vùng mù" → Phụ lục III; dẫn chiếu ở mục "Các trường hợp được
miễn trừ" (Điều 6, 10, 21) → đúng Điều của NĐ 26.

Trang này cũng có mục **"Quy định & các trường hợp miễn trừ"** cố định ở cuối,
tách làm **hai mục lớn** vì đây là hai nghĩa vụ khác nhau hay bị lẫn:
**A. Khai báo hóa chất nhập khẩu** (quy định Điều 6 → miễn trừ Điều 6.7) và
**B. Giấy phép xuất khẩu, nhập khẩu** (quy định Điều 14.2 → miễn trừ Điều 21).
Mục B **chỉ nói chuyện khâu XNK**; giấy của khâu khác gom vào mục **"Quy định
khác"** (dropdown, gấp sẵn) ở cuối: Giấy chứng nhận Phụ lục II (Điều 8, 9, 10.2
+ miễn khi tự dùng Điều 10.3) và miễn trừ khâu sản xuất, tồn trữ (Điều 21.4,
21.5). Tách quy định với miễn trừ của cùng một loại giấy ra hai chỗ thì đọc mục
miễn trừ mà không thấy nghĩa vụ gốc. Ngay trên nó là khối cảnh báo **"Vùng mù: mục Phụ lục
III không có mã CAS"** — xem Giới hạn đã biết.

Góc phải dưới có hai nút nổi: **✕ Thu gọn toàn văn** (hiện khi đang mở toàn văn
— cuộn ngược mấy nghìn dòng tìm lại thẻ đóng là không khả thi) và **↑ Lên đầu
trang**.

Trang có **hai chế độ tra**, tự chọn bằng nút trên ô nhập:

| Chế độ | Làm gì | Dùng khi |
|---|---|---|
| **Tìm theo mã CAS** (mặc định) | Tự tìm mọi mã CAS trong đoạn văn | DN có khai mã CAS — chính xác nhất |
| **Tìm theo tên chất** | Dò tên hóa chất nằm trong đoạn ("Hỗn hợp dung môi gồm Metanol, Toluene" → ra cả hai); gõ một phần tên ("amino") thì liệt kê các chất mang tên đó. Tiếng Việt hoặc Anh, không cần gõ dấu, tối đa 30 kết quả | DN không khai mã CAS — chỉ là **gợi ý**, xem Giới hạn |

Mỗi chế độ chỉ làm đúng việc của nó, nhưng **luôn nhắc chế độ kia** khi đoạn có
dữ liệu cho nó: tra theo mã CAS mà đoạn còn tên hóa chất không kèm mã thì trang
báo "còn nhắc tới N tên hóa chất... chuyển sang Tìm theo tên chất"; ngược lại
tra theo tên mà đoạn có mã CAS thì trang báo đang bỏ qua chúng. Nhờ vậy mô tả
trộn (vài chất khai mã, vài chất chỉ ghi tên) không bị bỏ sót im lặng, mà cũng
không kéo cái khớp thừa của dò tên vào kết luận của mọi lô hàng.

Tiện ích trên trang: nút **Ví dụ ngẫu nhiên** tạo mẫu **theo đúng chế độ đang
chọn** và **phủ đủ mọi trường hợp** chế độ đó có thể ra — bản mã CAS gồm chất PL
III cần Giấy phép, chất vừa PL I vừa PL III (khối khai báo PL I bị ẩn theo Điều
6.7.a), chất PL II còn nghĩa vụ khác, chất PL I chỉ khai báo, chất PL IV không
phát sinh, và một mã CAS ngoài dữ liệu ra "Không rõ"; bản theo tên là mô tả chỉ
ghi tên chất, không có case "Không rõ" (xem Giới hạn). Ngoài ra: nút **Xóa**, phím
tắt **Ctrl+Enter**, tự tra ngay khi dán, và chip thống kê số chất cần Giấy phép. Ghi kèm `% hàm lượng`
trên cùng dòng với mã CAS để tự so ngưỡng miễn trừ Điều 21.

Nếu sửa `data/nd24_chemicals.json` hoặc `core.py` (quy tắc/miễn trừ), chạy
lại `python3 build_html.py` để cập nhật `Tra-cuu-hoa-chat-ND24.html` — file này sinh cả
phần miễn trừ lẫn dữ liệu từ `core.py`, không gõ tay riêng trong HTML,
tránh lệch nội dung giữa CLI và trang web.

## Dùng CLI cho công chức hải quan — dán cả mô tả DN

`scan.py` tự tách hết mã CAS ra khỏi một đoạn mô tả (thường DN khai một
hỗn hợp gồm nhiều chất), không cần tách tay từng mã:

```
python3 scan.py
# rồi dán nguyên mô tả DN vào, ví dụ:
# "Hỗn hợp dung môi công nghiệp gồm Metanol CAS 67-56-1, Acetaldehyde (75-07-0)..."
# xong bấm Ctrl+D
```

hoặc trỏ thẳng vào file mô tả: `python3 scan.py mota.txt`.

In ra bảng tóm tắt (CAS nào cần Giấy phép, CAS nào chỉ cần khai báo) rồi
tới chi tiết từng CAS.

## Tra 1 mã CAS

```
python3 lookup.py 107-13-1
```

## Dữ liệu

`data/nd24_chemicals.json` được sinh từ `extract.py`, parse trực tiếp
Phụ lục I–IV của **bản chính thức NĐ 24/2026/NĐ-CP** (`nd24.md`, các Phụ lục ở
dạng bảng markdown, 1360 dòng CAS). Để tạo lại:

```
python3 extract.py            # đọc nd24.md -> data/nd24_chemicals.json
```

> Trước đây dữ liệu lấy từ `nd24.txt` (bản `textutil` một-ô-mỗi-dòng, parse theo
> số dòng cứng). Đã thay bằng `nd24.md` chính thức: parser bám cấu trúc bảng nên
> ổn định hơn, và sửa được vài lỗi phân loại của bản cũ (POP về đúng PL III thay
> vì PL IV; PL I không còn bị rớt chất).

**Đã đối chiếu `nd24.md` với bản gốc `24_2026_ND-CP_682556.docx`** (17/7/2026):
mã CAS duy nhất **1257 = 1257**, không sót cũng không thừa mã nào; cấu trúc khối
`Ngoại trừ` của Phụ lục III cũng khớp. Hai mục ghi cụt (45 "Biphenyl (PCB)", 81
"Polychlorinated") là **văn bản gốc ghi vậy**, không phải lỗi chuyển đổi.

Phần **yêu cầu nhập khẩu / miễn trừ** (`IMPORT_RULES`, `EXEMPTIONS` trong
`core.py`) là bản tóm tắt từ **NĐ 26/2026/NĐ-CP** (ngưỡng miễn trừ cập nhật theo
**NQ 19/2026/NQ-CP**) — toàn văn để đối chiếu nằm ở `nd26.txt` trong repo (**đã
đối chiếu với bản gốc `26_2026_ND-CP_682552.docx`**: đủ 31/31 Điều, chỉ khác cách
xuống dòng ở khối "Nơi nhận"/quốc hiệu). Bản gốc `.docx` của cả hai nghị định
nay nằm luôn trong repo để đối chiếu lại về sau. Sửa
tóm tắt trong `core.py` xong chạy lại `python3 build_html.py` để cập nhật trang
HTML.

`PENALTY_WARNING` (chế tài) dẫn hai văn bản:

- Mốc *"phải có giấy phép TẠI THỜI ĐIỂM đăng ký tờ khai"* là **Điều 18 khoản 1
  điểm m Thông tư 38/2015/TT-BTC** (đã sửa đổi). Nguồn đối chiếu là bản hợp nhất
  38-39-121 trong Obsidian của tác giả, **không có trong repo**. Cả 3 thông tư
  KHÔNG quy định mức phạt nào (0 lần cụm "phạt tiền") — chúng đặt nghĩa vụ và
  điều kiện, chế tài nằm ở nghị định xử phạt. Điều 28 cho phép hải quan tra giấy
  phép trên Cổng một cửa nên DN không bắt buộc nộp bản giấy: vì vậy câu này nói
  *"không có giấy phép"*, KHÔNG phải "không xuất trình".
- Mức phạt là **Điều 19 NĐ 169/2026/NĐ-CP**, bản gốc `169_2026_ND-CP_679683.docx`
  có trong repo — số hiệu, ngày 15/5/2026 và tên nghị định khớp; hiệu lực
  01/7/2026, thay NĐ 128/2020. Lưu ý khi sửa câu này:
Điều 19 **khoản 4** phạt hành vi *"phải có ... giấy phép nhưng KHÔNG CÓ giấy
phép"*, còn khoản 5 phạt gấp 2 nếu quá 30 ngày kể từ ngày hàng về đến cửa khẩu
mới nộp hồ sơ hải quan; khoản 7 giới hạn "giấy phép nêu tại Điều này" là giấy
phép theo **Luật Quản lý ngoại thương** (NĐ 26 có căn cứ luật này).

Còn một câu **không có văn bản nguồn trong repo** — đối chiếu bản gốc trước khi
sửa: dòng "chấp nhận Giấy phép bản PDF có chữ ký số của Bộ Công Thương để thông
quan" trong `IMPORT_RULES["III"]` (**CV 2595/HC-QLHC** ngày 31/12/2025 của Cục
Hóa chất).

## Phạm vi: "chất này cần GIẤY GÌ"

Công cụ chỉ trả lời **hóa chất cần giấy gì**, nên luôn gọi đúng tên từng loại giấy:

| Giấy | Cho hoạt động | Gặp ở |
|---|---|---|
| Giấy phép xuất khẩu, nhập khẩu hóa chất KSĐB | xuất/nhập khẩu | Phụ lục III |
| Giấy chứng nhận đủ điều kiện SX-KD hóa chất có điều kiện | sản xuất, kinh doanh | Phụ lục II |
| Giấy phép sản xuất, kinh doanh hóa chất KSĐB | sản xuất, kinh doanh | Phụ lục III |
| Giấy chứng nhận đủ điều kiện hoạt động tồn trữ | tồn trữ (dịch vụ) | Điều 21.5 |

**KHÔNG** đưa vào: hồ sơ gồm những gì, trình tự, thủ tục cấp, thẩm quyền cấp (phân
cấp NQ 19), và khối chuyển tiếp Điều 30.4/30.5/30.6 — Điều 30.4 chỉ *miễn xuất
trình hồ sơ* **Giấy phép SX-KD**, không đụng tới Giấy phép XNK, nên không đổi câu
trả lời "cần giấy gì". Đó là việc của cơ quan cấp phép, không phải của trang tra cứu.
`test_khong_con_noi_dung_ho_so_trinh_tu_thu_tuc` chặn các nội dung này quay lại.

## Giới hạn đã biết

- **Vùng mù: 13 mục Phụ lục III ghi theo HỌ CHẤT, không có mã CAS** (ô CAS trong
  nd24.md để `---`) nên tra theo mã không bao giờ ra: 6 họ Bảng 2 dạng
  `N,N-Dialkyl…` (mục 26, 27, 28, 32, 33, 34); 5 họ nguyên tố — **37. Asen và các
  hợp chất của asen; 38. Các hợp chất của Cr⁶⁺; 39. Thủy ngân và các hợp chất;
  40. Các hợp chất xyanua; 41. Chì và các hợp chất**; và 2 mục **chính nghị định
  ghi cụt** (45 "Biphenyl (PCB)", 81 "Polychlorinated" — đã đối chiếu bản gốc
  `24_2026_ND-CP_682556.docx`, không phải lỗi chuyển đổi của nd24.md).

  Hậu quả đo được, **không phải giả định**: Asen trioxit (1327-53-3) chỉ được nghị
  định ghi mã ở Phụ lục IV nên công cụ kết luận **"Không cần Giấy phép XNK"**,
  trong khi mục 37 phủ nó. 7 chất trong dữ liệu dính kiểu này (3 hợp chất asen, 2
  hợp chất chì, 2 cromat); chất không có trong dữ liệu (natri xyanua, thủy ngân
  clorua…) thì ra "Không rõ".

  Xử lý hai tầng, **không tầng nào đổi verdict** (verdict vẫn thuần theo mã CAS):
  1. `extract.py` tách các mục này sang `data/nd24_pl3_no_cas.json`, in nguyên văn
     thành **khối cảnh báo riêng** dưới kết quả (và cuối `scan.py`).
  2. **Cờ ngay trong dòng kết quả** (`PL3_FAMILY_HINTS`): tên chất chứa `asen`,
     `cromat`, `thủy ngân`, `xyanua`, `chì`… thì dòng đó hiện cờ đỏ "tên chất này
     gợi ý có thể thuộc mục … — tự đối chiếu", kèm một chip riêng trong thống kê.
     Cần tầng này vì khối cảnh báo cuối trang không cứu được ca xanh: cán bộ đọc
     dòng xanh là xong, không cuộn xuống. Hiện bắt đúng 7 chất, không báo thừa chất
     nào trên cả 1360 dòng.

  Cờ là **heuristic theo tên, không phải hóa học** — trần của nó: sót chất mang tên
  không có tên nguyên tố (Calomel = Hg₂Cl₂), và không phân biệt Cr³⁺ với Cr⁶⁺ nếu
  tên không nói. Nâng cấp khi cần chắc hơn: đối chiếu cột "Công thức hóa học" của
  nd24.md (`extract.py` chưa lấy cột này). Công cụ **không tự kết luận** chất nào
  thuộc họ nào — đoán sai theo hướng nào cũng hại.
  `test_pl3_khong_ma_cas_khong_bi_bo_im_lang` và `test_co_ho_chat_bat_dung_ca_xanh_nguy_hiem`
  chốt việc này; `test_co_ho_chat_html_khop_core` chạy cả bản JS lẫn bản Python trên
  toàn bộ dữ liệu rồi so, để trang HTML và CLI không thể lệch nhau.
- Không có danh mục "Hóa chất Bảng 1" (Công ước vũ khí hóa học) hay "hóa
  chất cấm" (Mục 4 NĐ 26). NĐ 24 Phụ lục III mục B chỉ có **Bảng 2 và Bảng 3** —
  không một chất Bảng 1 nào, và có dòng ghi rõ *"except for those listed in
  Schedule 1"*. Lưu ý: NĐ 26 lại dẫn chiếu "Hóa chất Bảng 1 **thuộc Phụ lục III**
  của NĐ 24" (Điều 8.5) — thứ không tồn tại trong NĐ 24. Danh mục Bảng 1 nằm ở
  **NĐ 33/2024/NĐ-CP** (Công ước CWC; NĐ 26 Điều 31 chỉ bãi bỏ Điều 10–20 của nó,
  Phụ lục vẫn còn hiệu lực), nhưng ở đó Bảng 1 cũng ghi theo họ chất — mã CAS chỉ
  có ở các dòng "Ví dụ" (Sarin 107-44-8, Soman 96-64-0, Tabun 77-81-6, VX
  50782-69-9). Hiện tra 4 mã đó ra **"Không rõ"**. Chưa đưa vào: mâu thuẫn giữa
  hai nghị định cần người có thẩm quyền xác định trước.
- **Dòng "Ngoại trừ" của Phụ lục III loại trừ chất, không thêm chất.** PL III có 2
  dòng `Ngoại trừ:` (mục 26 và 33) — chất ngay dưới là chất bị **loại khỏi** mục
  đó, đúng nguyên văn Công ước CWC (Bảng 2 B.4 miễn trừ Fonofos; B.10 miễn trừ
  DMAE/DEAE). Đọc ngược chiều là bắt DN xin Giấy phép cho chất nghị định đã nói rõ
  là không phải xin. 3 mã dính: **944-22-9** (Fonofos — chỉ có ở dòng này nên
  không thuộc phụ lục nào), **108-01-0** và **100-37-8** (vẫn là PL II theo mục
  278/265). Vì mã của chúng CÓ in trong bảng PL III, `data/nd24_pl3_ngoai_tru.json`
  giữ lại để trang/CLI nói rõ lý do thay vì im lặng.
  `test_dong_ngoai_tru_pl3_khong_bi_doc_nguoc` chốt cả hai chiều — không nuốt oan
  676-97-1/756-79-6 vốn nằm dưới dòng "Ví dụ:" của mục 26.
- CAS không tra ra chỉ báo **"Không rõ"** — tool không nhắc gì thêm; "không có
  trong dữ liệu" không đồng nghĩa "không cần giấy".
- Yêu cầu nhập khẩu trong `lookup.py` là bản tóm tắt điều luật, không thay
  thế văn bản gốc — luôn đối chiếu Điều được dẫn chiếu trước khi làm hồ sơ.
- **Tra theo tên (chỉ HTML) là gợi ý, không thay mã CAS.** Ba giới hạn, trang
  cũng tự cảnh báo ngay trong kết quả:
  1. **Không có case "Không rõ".** Tên không khớp dữ liệu thì không hiện dòng nào
     — mô tả "gồm Metanol, Toluene và Axeton" chỉ ra 2 chất vì Axeton không thuộc
     Phụ lục I–IV. Khác nhánh CAS: mã lạ vẫn hiện "Không rõ". Bảng tra theo tên
     **không** chứng minh lô hàng chỉ có bấy nhiêu chất.
  2. **Tên ghép khớp thừa.** Mô tả "natri clorua" (muối ăn, không thuộc NĐ 24) ra
     chất "Natri" — vì "natri clorua" không có trong dữ liệu để nuốt cụm ngắn hơn.
     Báo thừa và hiện rõ để cán bộ tự loại, đúng hướng fail-safe.
  3. **Hai chế độ không trộn kết quả.** Chế độ Tìm theo mã CAS không bao giờ đưa
     chất khớp theo tên vào bảng — nếu trộn, cái khớp thừa ở mục 2 sẽ lây sang
     mọi lô hàng có khai mã CAS. Đổi lại, mỗi chế độ phải **nhắc** chế độ kia khi
     đoạn có dữ liệu cho nó, để mô tả trộn không bị bỏ sót im lặng.
     `test_che_do_cas_khong_de_ten_lot_vao_bang` chốt cả hai vế này.

  Tên trong NĐ 24 hay kèm đuôi qualifier ("... **và các muối proton hóa chất
  tương ứng**") mà DN không bao giờ khai, nên chỉ số tên có thêm phần đầu tên (cắt
  ở `và`/`and`/`(`). Không có nó thì "N,N-dimetyl amino etanol" (108-01-0, PL II)
  tụt xuống khớp chữ "etanol" → báo ra Etanol (64-17-5, PL I): sai chất, và giấu
  mất nghĩa vụ Giấy chứng nhận SX-KD của chất thật.
  `test_do_ten_hoa_chat_trong_mo_ta_khong_co_ma_cas` chốt ca này.
- Không tự nhận diện `% hàm lượng` để kết luận miễn trừ: hóa chất Phụ lục III
  **luôn** báo "Cần Giấy phép XNK hóa chất KSĐB"; cán bộ tự đối chiếu ngưỡng Điều
  21 bằng tài liệu khai báo gốc. (Fail-safe: thà báo cần hơn miễn nhầm.)
- Phụ lục II mục 2 (hỗn hợp chất) và Phụ lục III mục II (hỗn hợp chất kiểm
  soát đặc biệt) là quy tắc theo ngưỡng hàm lượng %, không tra theo CAS —
  không nằm trong phạm vi tool này.

## Kiểm tra

```
python3 test_lookup.py
```

Skipped: chưa có OCR ảnh scan — nếu công chức cần dán ảnh chụp hồ sơ thay
vì text, thêm bước OCR trước khi đưa vào `scan.py`/`Tra-cuu-hoa-chat-ND24.html`.

---

Tác giả: **Nguyễn Hoàng Long** - HQ KCX&KCN
