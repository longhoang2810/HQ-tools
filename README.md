# Tra cứu CAS – Nghị định 24/2026/NĐ-CP & 26/2026/NĐ-CP

Nhập mã CAS (hoặc dán nguyên mô tả hàng hóa của doanh nghiệp), cho biết
hóa chất thuộc Phụ lục nào (I–IV) của NĐ 24/2026/NĐ-CP và yêu cầu thủ tục
khi nhập khẩu theo NĐ 26/2026/NĐ-CP.

## Cách dễ nhất: mở `Tra cứu hóa chất NĐ24.html` bằng trình duyệt

Không cần cài Python, không cần terminal. Double-click file
[`Tra cứu hóa chất NĐ24.html`](<Tra cứu hóa chất NĐ24.html>) (hoặc mở bằng trình duyệt bất kỳ, kể cả không
có mạng — dữ liệu đã nhúng sẵn trong file). Dán mô tả DN vào ô, bấm
**Tra cứu**, đọc bảng kết quả (dòng đỏ = bắt buộc xin Giấy phép).

Trang này cũng có mục **"Các trường hợp được miễn trừ"** cố định ở cuối
(NĐ 26 Điều 6.7, Điều 10.3, Điều 21).

Tiện ích trên trang: nút **Xóa**, phím tắt **Ctrl+Enter**, tự tra ngay khi
dán, và chip thống kê số chất cần Giấy phép. Ghi kèm `% hàm lượng`
trên cùng dòng với mã CAS để tự so ngưỡng miễn trừ Điều 21.

Nếu sửa `data/nd24_chemicals.json` hoặc `core.py` (quy tắc/miễn trừ), chạy
lại `python3 build_html.py` để cập nhật `Tra cứu hóa chất NĐ24.html` — file này sinh cả
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
Phụ lục I–IV của NĐ 24/2026/NĐ-CP (1331 dòng CAS). Để tạo lại từ file gốc:

```
textutil -convert txt -output nd24.txt "24_2026_ND-CP_....docx"
python3 extract.py nd24.txt
```

Phần **yêu cầu nhập khẩu / miễn trừ** (`IMPORT_RULES`, `EXEMPTIONS`,
`SHORT_FLAG` trong `core.py`) là bản tóm tắt thủ tục từ **NĐ 26/2026/NĐ-CP** —
toàn văn để đối chiếu nằm ở `nd26.txt` trong repo. Sửa tóm tắt trong `core.py`
xong chạy lại `python3 build_html.py` để cập nhật trang HTML.

## Giới hạn đã biết

- Không có danh mục "Hóa chất Bảng 1" (Công ước vũ khí hóa học) hay "hóa
  chất cấm" (Mục 4 NĐ 26) — hai văn bản nguồn không liệt kê CAS cụ thể cho
  nhóm này trong Phụ lục III (chỉ có Bảng 2, Bảng 3). Tool sẽ tự nhắc điều
  này khi không tìm thấy CAS.
- Yêu cầu nhập khẩu trong `lookup.py` là bản tóm tắt điều luật, không thay
  thế văn bản gốc — luôn đối chiếu Điều được dẫn chiếu trước khi làm hồ sơ.
- Phụ lục II mục 2 (hỗn hợp chất) và Phụ lục III mục II (hỗn hợp chất kiểm
  soát đặc biệt) là quy tắc theo ngưỡng hàm lượng %, không tra theo CAS —
  không nằm trong phạm vi tool này.

## Kiểm tra

```
python3 test_lookup.py
```

Skipped: chưa có OCR ảnh scan — nếu công chức cần dán ảnh chụp hồ sơ thay
vì text, thêm bước OCR trước khi đưa vào `scan.py`/`Tra cứu hóa chất NĐ24.html`.

---

Tác giả: **Nguyễn Hoàng Long** - HQ KCX&KCN
