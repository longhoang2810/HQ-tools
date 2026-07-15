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
Phụ lục I–IV của **bản chính thức NĐ 24/2026/NĐ-CP** (`nd24.md`, các Phụ lục ở
dạng bảng markdown, 1360 dòng CAS). Để tạo lại:

```
python3 extract.py            # đọc nd24.md -> data/nd24_chemicals.json
```

> Trước đây dữ liệu lấy từ `nd24.txt` (bản `textutil` một-ô-mỗi-dòng, parse theo
> số dòng cứng). Đã thay bằng `nd24.md` chính thức: parser bám cấu trúc bảng nên
> ổn định hơn, và sửa được vài lỗi phân loại của bản cũ (POP về đúng PL III thay
> vì PL IV; PL I không còn bị rớt chất).

**Trạng thái chuyển tiếp Điều 30.4/30.5** — với hóa chất Phụ lục III, công cụ
đối chiếu **NĐ 113/2017/NĐ-CP** (`nd113.md`) để cho biết chất đó là **"cũ"** (đã
có trong danh mục tiền chất công nghiệp / hạn chế SX-KD của NĐ 113 → KHÔNG được
miễn Giấy phép) hay **"chưa rõ"** (không có trong NĐ 113 → *có thể* là chất mới
được miễn tới 31/12/2026, nhưng phải đối chiếu thêm **NĐ 82/2022** và **Danh mục
hóa chất Bảng NĐ 33/2024** — hai văn bản này chưa có trong công cụ). Công cụ
**không bao giờ** tự kết luận "được miễn"; tập cũ trích từ `extract_nd113.py`:

```
python3 extract_nd113.py      # đọc nd113.md -> data/nd113_old_cas.json
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
- Trạng thái chuyển tiếp (Điều 30.4/30.5) chỉ đối chiếu được với **NĐ 113/2017**;
  **chưa** có **NĐ 82/2022** và **Danh mục hóa chất Bảng NĐ 33/2024**. Vì vậy
  công cụ chỉ khẳng định chắc "cũ", còn "chưa rõ" nghĩa là *phải tự đối chiếu
  thêm* — không đồng nghĩa với "được miễn". (Thiết kế fail-safe: thà báo cần
  Giấy phép còn hơn miễn nhầm.)
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
