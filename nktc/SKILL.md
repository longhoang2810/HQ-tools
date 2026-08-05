---
name: nktc
description: "Use when processing an NKTC customs-declaration Excel export (nhập khẩu tại chỗ). Filters Ma_LH in {E21, G13}, remaps columns, and builds one formatted .xlsx per configured province/city from regions.txt with accent-insensitive address matching, grouped/merged company rows, Vietnamese header, Times New Roman formatting and borders."
version: 2.5.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [excel, openpyxl, vietnamese, customs, nktc, hai-phong, reporting, docx, cvnk]
    related_skills: [powerpoint, cvnk]
---

# NKTC – Excel Customs Declaration Processor

## Overview

Processes an NKTC (nhập khẩu tại chỗ / on-the-spot import) customs-declaration
Excel export in two steps and produces **one formatted workbook** with `summary`,
one sheet per configured province/city, and `unmatched` for rows not matching a
configured location. `regions.txt` is the current 9-sheet operating list:
hp, Hn, PT, HY, BN, TH, TQ, QT, NB. `regions-34-backup.txt` retains the full
34-unit configuration for a later approved expansion. Legacy mode
`--separate-files` still writes
one .xlsx per configured group. All logic is in `scripts/nktc_process.py` (uses
`openpyxl`).
The source file is a wide export where the meaningful columns historically sat
at fixed positions A, B, H, I, J, K, P. The script now first tries to detect the
source columns from the header row (`So_to_khai`, `Ma_LH`, `Ma_DN_XNK`,
`Ten_DN_XNK`, `Ma_dia_chi_DN_XNK`, `So_quan_ly_cua_noi_bo_doanh_nghiep`,
`Tong_tri_gia_tinh_thue`) and falls back to the legacy fixed positions only when
headers are missing. This prevents shifted monthly exports from silently using
the company-name column as the address column.

## When to Use

- User attaches/points to an NKTC Excel export and asks for the province lists
- Any "lọc E21/G13 → tạo các file theo tỉnh" / "danh sách doanh nghiệp nhập
  khẩu tại chỗ" request
- If the user sends an NKTC file and says "Try again" / "làm lại" / "chạy lại",
  run the standard workflow directly; do not ask what to do with the file.
- Recurring monthly customs report with the same column layout

Don't use for: arbitrary Excel reshaping unrelated to this fixed column layout.

## Source Column Layout (1-based, fixed positions)

| Col | Field                              | Used as |
|-----|------------------------------------|---------|
| A   | So_to_khai                         | → D     |
| B   | Ma_LH (filter ∈ {E21, G13})        | filter  |
| H   | Ma_DN_XNK                          | → C     |
| I   | Ten_DN_XNK (sort A→Z)              | → B     |
| J   | Ma_dia_chi_DN_XNK                  | → A     |
| K   | So_quan_ly_cua_noi_bo_doanh_nghiep | → E (strip first 8 chars) |
| P   | Tong_tri_gia_tinh_thue             | → F     |

## What the Script Does

**Step 1 – filter & normalize**
1. Keep rows where col B (Ma_LH) is in `{E21, G13}` (override with `--ma-lh`,
   comma-separated). This is the standard filter condition for NKTC exports.
2. Exclude any row where output E would be blank after stripping the first 8
   characters from source column K / detected `So_quan_ly_cua_noi_bo_doanh_nghiep`.
3. Sort by col I (Ten_DN_XNK) A→Z.
4. Remap to A=J, B=I, C=H, D=A, E=K(−8 chars), F=P.
   Optionally dump this intermediate table with `--step1-out step1.xlsx`.

**Step 2 – build one workbook with configured province/city sheets + `unmatched`**
For each region below, keep Step-1 rows whose col A (address) matches the
region's terms, then write a sheet named by region stem into the output workbook.
Rows that passed the E21/G13 filter but do not match any configured location term set go into the `unmatched` sheet with source address and reason. A `summary` sheet is written first with Step-1 rows, region rows, unmatched rows, coverage, and per-sheet counts.
Address
matching is **accent-insensitive**: terms are stored unaccented, the address
is de-accented before comparison (đ/Đ → d), so both "Hà Nội" and "Ha Noi"
match. If an address contains multiple place names (such as a street named
Điện Biên Phủ in Hải Phòng), the matching locality furthest right wins; each
row is assigned to exactly one sheet.

| Sheet/file | Address contains (any of)        |
|-----------|----------------------------------|
| `hp`      | hai ph, hai phong, hp, hai duong |
| `Hn.xlsx` | ha noi                           |
| `PT.xlsx` | phu tho, vinh phuc               |
| `HY.xlsx` | hung yen                         |
| `BN.xlsx` | bac ninh, bac giang              |
| `TH.xlsx` | thanh hoa                        |
| `TQ.xlsx` | tuyen quang                      |
| `QT.xlsx` | quang tri                        |
| `NB.xlsx` | nam dinh, ninh binh              |
| `HCM.xlsx` | ho chi minh, tp hcm, tphcm       |

Terms are stored unaccented because matching strips accents first, so accented
forms are covered automatically: `hải phòng` → `hai phong`, `hà nội` →
`ha noi`, `phú thọ` → `phu tho`, `vĩnh phúc` → `vinh phuc`, `hưng yên` →
`hung yen`, `bắc ninh`/`bắc giang` → `bac ninh`/`bac giang`, `thanh hoá` →
`thanh hoa`, `tuyên quang` → `tuyen quang`, `quảng trị` → `quang tri`,
`nam định`/`ninh bình` → `nam dinh`/`ninh binh`.

### Add or change a province/city

Edit `regions.txt`; no Python change needed. One active line uses:

```text
sheet_name<TAB>address keyword | address keyword
HCM<TAB>Ho Chi Minh | Thanh pho Ho Chi Minh | TP.HCM | TPHCM
```

Blank lines and lines beginning with `#` are ignored. Sheet names must be unique,
valid Excel names, and at most 31 characters. Keywords are case/accent-insensitive.
Use `--regions /path/to/regions.txt` to run a different reviewed location list.

Each file uses the same layout and formatting:
- Output columns: `A=STT | B=Tên DN XNK | C=Mã DN XNK | D=Số tờ khai |
  E=Tờ khai XK | F=Trị giá tính thuế (USD) | G=Thuế NK | H=Ghi chú`.
- E = source K with first 8 chars stripped; G = 0 everywhere; H (`Ghi chú`) has the region/file title (`hp`, `Hn`, etc.) on the first data row only and is blank on the remaining rows.
- Group rows with same B+C (Tên DN + Mã DN): **merge cells in A, B, C**;
  keep each row's own D and E. STT is numbered per company group. (Because
  E21 and G13 declarations for the same company group together, a company can
  span several D/E rows under one merged STT.)
- Header rows 1–4:
  - Row 1: `DANH SÁCH DOANH NGHIỆP LÀM THỦ TỤC NHẬP KHẨU TẠI CHỖ THÁNG MM/YYYY`
    where **MM = previous month**, **YYYY = current year** (auto-filled from
    today's date when `--month/--year` are omitted).
  - Row 2: `(Kèm theo Thông báo số NUM/TB-XNKTC(GC) ngày DD tháng MM năm YYYY)`
    where the Thông báo **MM = current month**, **YYYY = current year**
    (auto-filled when `--tb-month/--tb-year` are omitted).
  - Rows 1–2 merged A:H, bold, size 14, centered.
  - Row 3 blank. Row 4 column names, bold, centered.
- Formatting: Times New Roman everywhere; data size 11; cols B & C vertical
  top; all-borders on the data region; col D (`Số tờ khai`) number format `0`
  with enough width to avoid scientific notation; col F number format `#,##0.00`.

## References

- `references/export-import.md` — portable archive/export workflow for copying this skill to another Hermes agent or profile, plus Drive upload/auth notes.

## Usage

### HTML offline, không cần Python

`NKTC-xu-ly-excel.html` là ứng dụng độc lập: mở trực tiếp bằng Chrome, Edge,
Safari hoặc Firefox, chọn `.xlsx`, chỉnh vùng trong ô cấu hình rồi tải workbook
kết quả. Toàn bộ dữ liệu xử lý ngay trên trình duyệt, không có upload/server.

File này đã nhúng ExcelJS nên có dung lượng khoảng 1 MB. Mặc định HTML hiển thị
9 vùng vận hành. Khi cần 34 vùng, tải `regions-34-backup.txt` qua nút **Nhập
TXT**; danh sách 34 không tự bật. Khi sửa `regions.txt` hoặc giao diện, dựng lại bằng:

```bash
python3 scripts/build_html.py
```

Nguồn HTML gồm `NKTC-xu-ly-excel.template.html`, `assets/exceljs.min.js`,
`regions.txt`, và `regions-34-backup.txt`. Không sửa trực tiếp bundle HTML trừ
tình huống khẩn cấp; sửa template/TXT rồi build để các thay đổi có thể tái tạo.

HTML hỗ trợ tải lên/tải xuống `regions.txt`, khôi phục mặc định 34 vùng, và giữ
quy tắc phân vùng như CLI: địa danh khớp ở cuối địa chỉ được ưu tiên, một dòng
chỉ vào một sheet.

### Tạo công văn (nút "Tạo công văn")

Sau khi bấm **Xuất Excel NKTC**, nút **Tạo công văn** tạo file `.docx` "Thông báo
V/v làm thủ tục xuất khẩu, nhập khẩu tại chỗ" (mẫu gửi thuế 9 tỉnh/thành) từ cùng
dữ liệu vừa xử lý — không chạy lại file nguồn, không cần bấm Xuất Excel lại nếu
chỉ muốn tạo lại công văn với dữ liệu cũ.

- Chỉ tạo thư cho vùng **có ít nhất 1 dòng khớp** tháng đó; vùng không có dữ liệu
  bị bỏ qua, không tạo thư trống.
- Chỉ hoạt động với đúng 9 khoá vùng cố định trong mẫu công văn: `hp, Hn, PT, HY,
  BN, TH, TQ, QT, NB`. Nếu đổi `regions.txt` sang cấu hình 34 tỉnh/thành hoặc đổi
  tên sheet, công văn sẽ không có thư cho vùng đã đổi tên (không báo lỗi, chỉ
  im lặng bỏ qua vùng đó — kiểm tra số thư trong thông báo "Đã tạo công văn: X/9
  vùng" sau khi bấm).
- Ngày ký (`ngày ___ tháng MM năm YYYY`) lấy từ ô **Tháng thông báo/Năm thông báo**,
  luôn để trống ngày (điền tay khi có số công văn chính thức). Kỳ báo cáo (`từ
  ngày...đến ngày...`) lấy từ ô **Tháng báo cáo/Năm báo cáo** (không phải ngày
  hệ thống) — cho phép tạo công văn cho tháng cũ nếu cần.
- Mẫu gốc có placeholder ở `assets/CVNK_Gui_thue_template.docx` (`{{DOC_MONTH}}`,
  `{{DOC_YEAR}}`, `{{FROM_DATE}}`, `{{TO_DATE}}`), vendor tương tự exceljs — sửa
  mẫu này rồi build lại, không sửa tay `NKTC-xu-ly-excel.html`.
- **Ba đường kẻ ngang thể thức (dưới tên cơ quan, dưới tiêu ngữ, dưới trích yếu)
  là `w:pBdr` bottom của một đoạn rỗng cỡ chữ 1pt đặt ngay sau dòng chữ**, không
  phải shape. Bản mẫu cũ vẽ chúng bằng 36 `straightConnector1` neo toạ độ tuyệt
  đối (`positionH relativeFrom="column"`) — đổi khổ giấy/lề/bề rộng bảng là lệch
  ngay, đã bỏ hết. Nếu sửa lại bề rộng cột header thì phải chỉnh `w:ind` của ba
  đoạn kẻ đó cho khớp, nếu không đường kẻ sẽ không còn cân giữa dòng chữ.
- **Bảng header chia cứng 4100/5255 twip, `tblCellMar` = 0.** Quốc hiệu 12pt đậm
  rộng 5006tw; để lề trong ô mặc định (108tw/bên) hoặc thu ô phải xuống dưới
  5222tw là "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" xuống dòng.
- Cắt/ghép docx bằng cắt chuỗi trực tiếp trên `word/document.xml` (không dùng
  serializer XML tổng quát, giống lý do cvnk tránh serializer để không bị Word
  báo "unreadable content"), nén/giải nén bằng `CompressionStream`/
  `DecompressionStream('deflate-raw')` có sẵn trong trình duyệt — không thêm thư
  viện zip/docx nào. Cần Chrome/Edge/Firefox bản mới; nếu trình duyệt không hỗ
  trợ, nút báo lỗi rõ ràng, Excel vẫn xuất bình thường.
- **Mỗi thư cắt từ `<w:tbl>` header tới `<w:tbl>` footer của chính nó, KHÔNG lấy
  phần trước header.** Vùng giữa 2 thư trong mẫu không bao giờ được đọc.
  Mẫu cũ nhét 6-7 đoạn `<w:p>` rỗng vào đó (tác giả chèn tay để đẩy thư sau sang
  trang mới khi in liên tục); các đoạn này không có `<w:spacing>` riêng nên ăn
  theo `docDefaults`, cộng dồn thành ~3in khoảng trắng đầu trang khi ghép với
  ngắt trang thật do code tự chèn — và co lại mất tác dụng ngay khi siết
  `docDefaults`. **Nay đã thay bằng đúng 1 `<w:br w:type="page"/>` mỗi chỗ nối**
  (8 cái), nên mở mẫu trực tiếp cũng ra 1 trang/thư. Đừng nhét lại đoạn rỗng.
- **Thứ tự 9 lá thư trong mẫu KHÁC thứ tự trong `regions.txt`**: mẫu là Hà Nội,
  Hải Phòng, Phú Thọ, Hưng Yên, Bắc Ninh, Thanh Hóa, Tuyên Quang, Quảng Trị, Ninh
  Bình (Hà Nội đứng trước Hải Phòng); `regions.txt` là hp, Hn, PT... (Hải Phòng
  trước Hà Nội). Mapping đúng nằm ở hằng số `CVNK_LETTER_KEYS` trong
  `NKTC-xu-ly-excel.template.html` — đã xác minh bằng cách đếm vị trí bảng thật
  trong file mẫu, đừng suy luận lại từ thứ tự `regions.txt`.

### CLI

```bash
# Default: -o is one OUTPUT .xlsx workbook containing configured region sheets
python3 scripts/nktc_process.py INPUT.xlsx -o OUT.xlsx \
    --month 05 --year 2026 \
    --tb-no 123 --tb-day 29 --tb-month 5 --tb-year 2026

# Legacy: write 9 separate files into OUTDIR
python3 scripts/nktc_process.py INPUT.xlsx -o OUTDIR --separate-files \
    --month 05 --year 2026

# Use a separate reviewed province/city configuration
python3 scripts/nktc_process.py INPUT.xlsx -o OUT.xlsx --regions ./regions.txt

# Chỉ khi nghiệp vụ cần mở rộng đủ 34 vùng
python3 scripts/nktc_process.py INPUT.xlsx -o OUT.xlsx --regions ./regions-34-backup.txt
```

When the user attaches an NKTC source file and says "Try again", "làm lại", or otherwise asks to repeat the standard processing without extra details, run the standard workflow directly instead of asking what to do:

```bash
python3 /Users/cheese/.hermes/skills/productivity/nktc/scripts/nktc_process.py \
    INPUT.xlsx \
    -o /Users/cheese/.hermes/cache/documents/nktc_output_T5_2026 \
    --month 05 --year 2026
```

For future files, infer the report month/year from the filename when it contains patterns like `T5.2026`, `T05.2026`, `tháng 5 2026`, or `05-2026`; otherwise use the script defaults unless the user specifies month/year. Name the output folder descriptively, e.g. `nktc_output_T5_2026`, and report the full folder path plus the 9 generated files and row/company counts.

Common flags:
- `--sheet NAME`     pick a specific source sheet (default: active sheet)
- `--ma-lh E21,G13`  comma-separated loại hình filter values (default E21,G13)
- `--header-rows 1`  number of header rows in the source before data starts
- `--regions FILE`   UTF-8 `sheet<TAB>keyword | keyword` location config
- `--step1-out step1.xlsx`  also save the intermediate Step-1 table
- `-o OUTDIR`        output directory for configured region files (default: `.`,
  created if missing)
- `--month/--year`   fill the title `THÁNG MM/YYYY`. **Default: previous
  month + current year**, auto-filled from today's date.
- `--tb-no/--tb-day/--tb-month/--tb-year`  fill the Thông báo subtitle.
  `--tb-month/--tb-year` **default to the current month + current year**.

If the user doesn't give month/year values, the script auto-fills them from
today's date (title = previous month / current year; subtitle = current month
/ current year). Only `--tb-no` and `--tb-day` are left blank when omitted, so
the user can fill those by hand.

## Adapting to a Real File

The script detects the source layout from the header row by default and only
falls back to legacy fixed positions (A,B,H,I,J,K,P) when recognizable headers
are absent. Before trusting a surprising result, still do a quick header sanity
check: locate columns named like `Ma_LH`, `Ma_DN_XNK`, `Ten_DN_XNK`,
`Ma_dia_chi_DN_XNK`, `So_quan_ly_cua_noi_bo_doanh_nghiep`, and
`Tong_tri_gia_tinh_thue`. Monthly T exports can shift meaningful fields one or
more columns to the right (for example, T5.xlsx had `Ma_dia_chi_DN_XNK` at K,
not J). If a real export has **extra header rows** (title banners above the
column names), pass `--header-rows N` so detection and filtering start from the
right header/data boundary.

When a province count is unexpectedly zero, diagnose against the detected
address column before changing region terms. For example, Thanh Hóa rows may be
missed if the script reads the company-name column as the address column; the
fix is header-based column detection, not adding more `thanh hoa` spellings.

## Common Pitfalls

1. **Reading by header name.** The script reads by column index on purpose;
   don't "fix" it to match header strings — real exports have inconsistent
   header wording.
2. **Wrong header-rows count.** If the source has a multi-row banner, the
   first real data rows get treated as headers (or junk rows leak in). Verify
   with `--step1-out` and inspect the row count.
3. **Stripping fewer/more than 8 chars on col E.** The spec is exactly 8 — if
   the internal management number prefix length changes, update `strip8`.
4. **Grouping key.** Rows group by B+C (name AND code). Two branches with the
   same name but different Mã DN stay separate — that's intended. E21 and G13
   declarations for the same B+C group under one STT, so a company may show
   several D/E rows.
5. **Trị giá as text.** Source values may be stored as strings with commas;
   `to_float` strips commas. If totals look wrong, check the raw cell type.
6. **Mã DN XNK leading zeroes.** Keep company codes as text. The script uses
   `cell_to_text()` and preserves zero-padded numeric display formats such as
   `0000000000`; do not coerce output column C back to numeric.
7. **Location config.** Edit `regions.txt`, not Python, to add a reviewed
   province/city. Keep terms specific enough to identify the locality; do not
   use generic abbreviations such as `hp` or `q1`. A malformed config stops
   before reading the Excel source and reports its exact line.
8. **In `--separate-files` mode, `-o` is a directory, not a filename.** Step 2 writes configured files (`hp.xlsx`,
   `Hn.xlsx`, …) into the `-o` directory. Passing `-o hp.xlsx` would create a
   directory literally named `hp.xlsx`. Use `-o OUTDIR` (or omit for cwd).
9. **A row can land in more than one sheet/file.** If an address contains terms for
   two regions (rare), it's written to both. Region terms are mutually
   exclusive in practice, but there's no dedupe across files.


## Verification Checklist

- [ ] Step-1 row count matches expected number of E21 + G13 declarations after excluding rows whose fixed column L has blank rightmost 8 trimmed characters
- [ ] Workbook contains `summary`, every sheet named in `regions.txt`, and `unmatched`; total data rows across non-summary sheets equals Step-1 row count
- [ ] Each file's merged ranges include A1:H1, A2:H2, and one A/B/C merge per
      multi-declaration company
- [ ] STT increments per company group, not per row
- [ ] Col E values are source K minus the first 8 chars
- [ ] Col G all 0, col H all blank
- [ ] A1/A2 Times New Roman, size 14, bold, centered; col F = `#,##0.00`
- [ ] Cols B & C vertical alignment = top; thin border on every data cell
- [ ] Accented and unaccented addresses both land in the right file
