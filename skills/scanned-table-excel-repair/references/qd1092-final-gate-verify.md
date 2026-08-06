# QĐ 1092 — final residual gate (PL III)

## Deliverable (Codex vision extract)
`/Users/cheese/Documents/Codex/2026-07-20/new-chat/outputs/QD_1092_Phu_luc_I_II_III.xlsx`

Sheets: `Phụ lục I` | `Phụ lục II` | `Phụ lục III`.

PDF source (Drive):
`.../My Drive/QĐ 1092 ban hành danh mục hàng hóa rủi ro về phân loại và áp dụng mức thuế_0001.pdf`

## Known structure
| Sheet | Data STT | Source gaps |
|-------|----------|-------------|
| I | 1–27 | none |
| II | 1–806 (805 rows) | **253, 460** (scan source; not extract bugs) |
| III | 1–20 | none; section headers for chống BPG / chống trợ cấp |

## Final 10-cell gate (Codex → Grok)
When session idle on “chờ Grok xác nhận 10 ô”, check only:

1. III STT **5 B** — exactly codes: `72163311`, `72163319`, `72163390`, `72287010`, `72287090`
2. III STT **5 F** — contains `sai bản chất hàng hóa`
3. III STT **6 C** — contains `một dạng thù hình` and `thiết kế`
4. III STT **7 D** — contains `nước Đại Hàn Dân quốc`
5. III STT **7 G** — starts with / contains `Kiểm tra tên hàng khai báo để tránh doanh nghiệp khai sai`
6. III STT **8 E** — ends with / contains `72269210`, `72269290`
7. III STT **8 F** — contains `sai bản chất hàng hóa`
8. III STT **8 G** — contains `3390/QĐ-BCT`
9. III STT **18 B** — contains `7208.38.00`, `7211.14.19`, `7211.90.12`, `7211.90.19`
10. III STT **20 F** — starts with `Kính màu hấp thụ nhiệt/ kính nổi có màu`

Also confirm STT20 H has `1400/QĐ-BCT` when spot-checking.

## Page image hints
- `work/review_pages/pliii-*.png`, `hi_pliii_*.png`
- `work/fix_pages/p123.png`… (rotated pages for early III rows)
- `outputs/_verify_pdf_pages/rot/p123_r90.png` etc.

## Report
Write `outputs/GROK_FINAL10_PASS.md` (or FAIL with STT/col/excel/pdf page). Result + reason only.