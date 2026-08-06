---
name: scanned-table-excel-repair
description: "Repair tables extracted from scanned Vietnamese PDFs into Excel."
---

# Scanned table Excel repair (VN customs / QĐ)

## When
Excel phụ lục from scanned PDF (Vision/OCR) has wrong cells, STT gaps, HS format bugs, decision-number typos, column bleed, or soft-wrap chaos.

## General OCR-to-workbook workflow
1. Back up the workbook and identify source PDF plus any row/source-page metadata.
2. Build an STT/row-to-page map from extraction batches before claiming a missing row is absent from the source.
3. For image-only Vietnamese tables on macOS, render disputed pages at roughly 180–220 DPI and prefer Apple Vision OCR. Crop relevant columns, then use STT-anchored row bands if column OCR mixes rows.
4. Repair structured JSON first when present, then patch matching Excel rows by normalized STT (integer with trailing punctuation stripped).
5. Preserve multi-token HS/QĐ/risk cells, ignore headings as data rows, and resolve suspected column swaps from the same row-band evidence.
6. Reopen and gate: STT/duplicate checks, strict garble markers, required marker cells, source-backed gaps, and visual review of each failed claim.
7. Keep uncertain/unmatched records visible; never invent source rows.

## Reference case: QĐ 1092 default paths
- Workbook: `/Users/cheese/Documents/Codex/2026-07-20/new-chat/outputs/QD_1092_Phu_luc_I_II_III.xlsx`
- PDF: Google Drive `QĐ 1092 ban hành danh mục hàng hóa rủi ro..._0001.pdf`
- Page images: `work/review_pages/`, `~/.gemini/antigravity/scratch/page_300-*.png`

## Expected structure
| Sheet | Data STT | Notes |
|-------|----------|-------|
| Phụ lục I | 1–27 | Col A section title is NOT STT |
| Phụ lục II | 1–806 | **253** = source PDF gap (252→254). **460** = Excel omit only — PDF p72 HAS row; add if missing |
| Phụ lục III | 1–20 | Section headers chống BPG / chống trợ cấp |

## Workflow
1. Backup `*.xlsx.bak_before_*` before any write.
2. Structural openpyxl: sheet names, STT ranges, missing/dup (filter section headers in col A), marker `�`/`[KHÔNG RÕ]`, HS as text not scientific.
3. Map disputed STT → page image before patch. **Never call missing STT “gap nguồn” without vision.**
4. Patch cells via openpyxl (or JSON→openpyxl). Keep multi-token cells; never collapse HS lists to empty.
5. Soft-wrap legibility pass: join mid-sentence `\n` / mid-word breaks; keep HS/MFN one-per-line; multi-`Quyết định số` → one line each; `wrap_text=True` + freeze `A2` + width ~12–42.
6. Gate checklist = **contains**, not exact full-cell equality.
7. Spot-check with vision on every FAIL claim and every “source gap” claim.
8. Upload: if gws token missing, `cp` into `GoogleDrive-*/My Drive/` (Desktop sync).

## Open FAIL (fix next)
1. Insert PL II STT **460** from PDF p72 (vít/bu lông… HS DN `98181310/98181390`, risk `73181510/73181590/73182400`, MFN B02).
2. PL III STT **10** H: `2806` → **`2866`**.

## Residual notes
- PL III STT7 E/F may mirror PDF column swap.
- Gate 10 PL III: PASS under contains after wrap fix.
- AGY free-form full audit: not default — see `agy-cli-print-mode`.

## References
- `references/qd1092-final-gate-verify.md` — 10 PL III gate cells
- `references/agy-full-verify-findings.md` — AGY_VERIFY=FAIL details
- `references/qd1092-appendix-repair.md` — appendix path notes
