---
name: scanned-vn-table-ocr-repair
description: "Repair Excel/JSON extracted from scanned Vietnamese customs QĐ appendix PDFs: Apple Vision OCR, STT→page map, JSON then openpyxl patch, strict multi-token garble verify. Use when phụ lục tables have broken VN text, wrong QĐ numbers, STT gaps, or name/risk swaps."
---

# Scanned VN customs table OCR repair

## When
Excel/JSON from scanned QĐ/phụ lục PDF is broken after vision extract (Codex or other). Symptoms: mojibake VN, wrong Quyết định numbers, STT gaps, column bleed, name/risk swapped.

## User prefs
- Report **result + paths + leftover gaps** only. No OCR/transcript dump unless asked.
- After a Codex status check, continue repair if user said Yes/continue.
- Codex status itself: result + reason only (see `codex-runtime-status`).

## Workflow
1. Backup xlsx.
2. Locate `final_data/appendix_*.json`, outputs xlsx, source PDF, `vision_batches`, row `source_batches`.
3. Map STT→PDF page from `source_batches` filenames (`appendix_II_PPP-QQQ`) first.
4. OCR on macOS: **Apple Vision** (`/tmp/vnocr` Swift+Vision) preferred over Tesseract `vie`.
   - `pdftoppm -png -r 180..220 -f N -l N`
   - Column crops: name ~7–42% W, risk ~48–84% W
   - Hard rows: horizontal ink bands → crop row containing STT → re-OCR
5. Patch **JSON first**, then openpyxl match STT on col A (int; strip trailing `.`).
6. Verify **strict multi-token garble count = 0**. Do not invent STTs missing from the scan.

## Strict garble (must be 0)
`dé sé|tén hang|cé ma|sé dé|kh6|xae|hudéng|duge|tdm|ran tahina|chat dé|hgp cd|sé Théng|bé Kem|gitip|nuéc rira|Thanh nhya|gitt chép|ligu nhya|�|[KHÔNG RÕ]|Chénh léch|hOn gdm|M2a!|Khai sal`

False positives alone — ignore: bare `mat` in *mờ/màu*, bare `dé` inside longer words, `cé` in *thực*, correct *hóa* with diacritics.

Safe bulk undiacritic: `Mat hang`→`Mặt hàng`, `de nham lan`→`dễ nhầm lẫn`, `phan loai`→`phân loại`, `thue suat`→`thuế suất`, `khai bao`→`khai báo`, `doanh nghiep`→`doanh nghiệp`, `nhua`→`nhựa`, `thué`→`thuế`, `chénh léch`→`chênh lệch`, `duge`→`được`, `hudéng`→`hưởng`.

## Name/risk swap
If name cell is a full risk sentence and risk is short/garbage → rebuild from row-band OCR.

## QĐ 1092 anchors (reference case)
- Job: `~/Documents/Codex/2026-07-20/new-chat/`
- II miss STT in source: **253, 460** (do not invent)
- III QĐ: STT7 `2822/QĐ-BCT 24/10/2024`; STT8 `3765/QĐ-BCT 26/12/2025`; STT20 `1400/QĐ-BCT 12/6/2026`
- II page anchors: STT~10–18 p12; ~19–26 p13; ~113–121 p25; ~248–252 p43; ~698 p105
- Approx: `page ≈ round(10.16 + 0.131*stt)` then refine via source_batches

## Prefer Apple Vision on macOS
- For Vietnamese body text, Apple Vision OCR beats Tesseract. Render PDF pages (`pdftoppm`), crop name/risk/HS/QĐ columns, then row bands for leftover STTs.
- Strict garble only (multi-token garbage, `�`). Do not flag bare `mat`/`dé`/`héa` inside valid words.
- Overlaps `scanned-table-excel-repair` (umbrella for full xlsx repair+verify). Prefer that skill for end-to-end QĐ appendix workbooks.

## Pitfalls
- Headroom/Telegram crush long stdout → write `/tmp`, chunk ≤350 chars.
- Column-only OCR mixes rows; use STT-anchored row bands for remaining severe lines.
- Related older skill: `scanned-table-excel-repair` (same class; prefer this workflow when both apply).

## Refs
- `references/qd1092-session-notes.md`
