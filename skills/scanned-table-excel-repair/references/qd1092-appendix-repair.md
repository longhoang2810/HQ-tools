# QĐ 1092 appendix repair notes

## Source
PDF scan: Google Drive  
`QĐ 1092 ban hành danh mục hàng hóa rủi ro về phân loại và áp dụng mức thuế_0001.pdf`

## Expected structure
| Sheet | Data STT | Notes |
|-------|----------|-------|
| Phụ lục I | 1–27 | Col A section title `1. Hàng hóa…` is NOT STT |
| Phụ lục II | 1–806 | **253** = source PDF gap only. **460** = must exist (PDF p72); Excel omit = bug |
| Phụ lục III | 1–20 | Section headers: chống bán phá giá / chống trợ cấp |

## Deliverable
`/Users/cheese/Documents/Codex/2026-07-20/new-chat/outputs/QD_1092_Phu_luc_I_II_III.xlsx`

Backup often: `*.xlsx.bak_before_fix`, `*.bak_before_wrapfix_*`

## Repair rules
- Prefer Apple Vision OCR > Tesseract vie for VN.
- Map STT→page via batches / `work/review_pages` / `scratch/page_300-*.png` before patch.
- Patch structured JSON then openpyxl.
- Multi-token cells: never collapse to 0.
- HS columns: store as text; keep leading zeros and dotted forms (`7208.38.00`).
- False STT dups: filter section numbers in col A before gap analysis.
- **Before labeling missing STT “gap nguồn”**: open PDF page image. 460 on p72 is real.
- Soft-wrap legibility pass after extract:
  - join mid-sentence `\n` / mid-word breaks
  - keep one HS or MFN code per line; multi-`Quyết định số` → one decision per line
  - `Alignment(wrap_text=True, vertical='top')`, freeze `A2`, column width ~12–42
- Upload: if `gws`/token missing, `cp` into `GoogleDrive-*/My Drive/` (Desktop sync). Do not block on API auth.

## Open FAIL to fix next
1. Add PL II STT **460** from PDF p72 (vít/bu lông… HS DN `98181310/98181390`, risk `73181510/73181590/73182400`, MFN B02).
2. PL III STT **10** H: `2806` → **`2866`**.

## Residual / final gate
See `qd1092-final-gate-verify.md` (10 PL III cells).  
See `agy-full-verify-findings.md` (AGY session + vision confirms).
