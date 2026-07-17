# Tra cứu CAS – Nghị định 24/2026/NĐ-CP & 26/2026/NĐ-CP

Nhập mã CAS (hoặc dán nguyên mô tả hàng hóa của doanh nghiệp), cho biết
hóa chất thuộc Phụ lục nào (I–IV) của NĐ 24/2026/NĐ-CP và yêu cầu thủ tục
khi nhập khẩu theo NĐ 26/2026/NĐ-CP.

## Cách dễ nhất: mở `Tra-cuu-hoa-chat-ND24.html` bằng trình duyệt

Không cần cài Python, không cần terminal. Double-click file
[`Tra-cuu-hoa-chat-ND24.html`](<Tra-cuu-hoa-chat-ND24.html>) (hoặc mở bằng trình duyệt bất kỳ, kể cả không
có mạng — dữ liệu đã nhúng sẵn trong file). Dán mô tả DN vào ô, bấm
**Tra cứu**, đọc bảng kết quả (dòng đỏ = bắt buộc xin Giấy phép).

Trang này cũng có mục **"Các trường hợp được miễn trừ"** cố định ở cuối
(NĐ 26 Điều 6.7, Điều 10.3, Điều 21).

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

Phần **yêu cầu nhập khẩu / miễn trừ** (`IMPORT_RULES`, `EXEMPTIONS` trong
`core.py`) là bản tóm tắt từ **NĐ 26/2026/NĐ-CP** (ngưỡng miễn trừ cập nhật theo
**NQ 19/2026/NQ-CP**) — toàn văn để đối chiếu nằm ở `nd26.txt` trong repo. Sửa
tóm tắt trong `core.py` xong chạy lại `python3 build_html.py` để cập nhật trang
HTML.

`PENALTY_WARNING` (chế tài khi không xuất trình được giấy phép lúc đăng ký tờ
khai — Điều 19 **NĐ 169/2026/NĐ-CP**) là ngoại lệ: **không có văn bản nguồn trong
repo** để đối chiếu như `nd24.md`/`nd26.txt`. Đối chiếu bản gốc trước khi sửa câu này.

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

- Không có danh mục "Hóa chất Bảng 1" (Công ước vũ khí hóa học) hay "hóa
  chất cấm" (Mục 4 NĐ 26) — hai văn bản nguồn không liệt kê CAS cụ thể cho
  nhóm này trong Phụ lục III (chỉ có Bảng 2, Bảng 3). CAS không tra ra chỉ
  báo **"Không rõ"** — tool không nhắc gì thêm; "không có trong dữ liệu"
  không đồng nghĩa "không cần giấy".
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
  ở `và`/`and`/`(`). Không có nó thì "N,N-dimetyl amino etanol" (108-01-0, PL III,
  **cần** Giấy phép) tụt xuống khớp chữ "etanol" → báo ra Etanol (64-17-5, PL I,
  *không cần*): sai chất, sai về phía nguy hiểm. `test_do_ten_hoa_chat_trong_mo_ta_khong_co_ma_cas`
  chốt ca này.
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
