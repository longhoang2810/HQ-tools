---
name: hs
description: "Classify goods to Vietnam 8-digit HS/AHTN codes using the local ~/Desktop/HS corpus and BT2026 tariff index."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [HS-Code, Vietnam, Customs, AHTN, BT2026]
---

# HS

Use this skill when the user asks to "áp mã", "tra mã HS", "HS", or classify described goods for Vietnam customs/tariff purposes.

## Local Corpus

Primary local workspace:

- `~/Desktop/HS/source/BT2026.xlsx` — Vietnam tariff workbook copied from Downloads.
- `~/Desktop/HS/docx/` — converted `.docx` chapter documents for source lookup/checking.
- `~/Desktop/HS/index/docs_text/` — text index converted from chapter documents for fast search.
- `~/Desktop/HS/index/bt2026_rows.csv` — searchable BT2026 rows with 8-digit codes.
- `~/Desktop/HS/build_index.py` — rebuilds the local index.
- `~/Desktop/HS/hs_search.py` — local keyword search over chapter notes and BT2026.
If setting up or refreshing the corpus, preserve source workbooks under `source/`, converted `.docx` chapter files under `docx/`, and searchable `.txt`/`.csv`/`.jsonl` artifacts under `index`/.

If files change, rebuild before classifying:

```bash
cd ~/Desktop/HS
python3 build_index.py
```

## Required Intake

Ask only for facts that affect classification. Prefer concise Vietnamese questions. Typical missing fields:

- Tên hàng, công dụng chính, ngành sử dụng.
- Vật liệu/thành phần, tỷ lệ, dạng hàng khi nhập.
- Nguyên lý hoạt động, nguồn điện/nhiên liệu, công suất/kích thước nếu là máy/thiết bị.
- Hàng nguyên chiếc, bộ phận, phụ kiện, vật tư tiêu hao, bộ/kit hay chưa hoàn chỉnh.
- Catalog/spec/model/photo nếu người dùng có.

## Search Workflow

1. If the user provides PDF/DOCX/XLSX/MSDS files, import/convert them with MarkItDown when available, preserving key sections such as product identification, composition, physical state, intended use, transport, and regulatory data.
2. Identify likely chapters/headings from product facts, not from product name alone.
3. Run broad local searches with Vietnamese and English keywords:

```bash
cd ~/Desktop/HS
python3 hs_search.py "<tu khoa hang hoa>" --limit 10
```

3. Use `~/Desktop/HS/index/docs_text/chapter_XX.txt` for fast discovery, then check the corresponding `.docx` file in `~/Desktop/HS/docx/` when citing or resolving close calls.
4. Search `BT2026` for candidate headings/subheadings and official Vietnamese descriptions. For Excel tariff schedules, preserve code display format while normalizing code values for lookup; keep official description, unit, tax/duty fields, sheet name, row number, and chapter/heading context for citation when available.
5. Use 8-digit codes where `BT2026.xlsx` contains a matching tariff line; otherwise give the justified 6-digit parent and say what facts or tariff wording are missing for 8-digit certainty.
6. Compare competing headings and reject alternatives explicitly when they are plausible.
7. If needed, inspect the workbook `~/Desktop/HS/source/BT2026.xlsx` for context.

## Analysis Workflow

Use a Perplexity-style evidence loop so the answer is evidence-backed, source-aware, and not keyword-driven:

1. **Question decomposition** — split the classification problem into decisive sub-questions: objective nature of the good, principal function/use, material or composition, operating principle, import condition, part/accessory status, and whether a legal note creates an exclusion or inclusion.
2. **Fact lock** — restate only decisive facts before searching. Separate confirmed facts from assumptions and unknown facts. Mark unknowns that could change chapter/heading/subheading.
3. **Candidate map** — list 2-4 plausible sections/chapters/headings from function, material, and use. Include at least one competing heading when a reasonable alternative exists.
4. **Evidence gathering** — search local chapter notes/text and `BT2026` with both Vietnamese and English keywords. For important claims, prefer primary sources: Section Notes, Chapter Notes, heading text, subheading notes, BT2026 wording, catalog/MSDS/TDS, and official customs classification notices.
5. **Source cross-check** — verify important claims against at least two independent evidence types when possible, such as product technical document + legal note, or BT2026 line + chapter explanatory text/ruling. If only one source supports a claim, say so in the uncertainty/confidence note.
6. **Legal filters** — apply relevant Section Notes, Chapter Notes, heading/subheading notes, and exclusions before relying on commercial names or keyword hits. Notes override product labels and search matches.
7. **Customs rulings check** — look for Vietnamese customs classification rulings or official classification/result notices for the same or closely comparable goods. Use them to calibrate the analysis, but do not let an old or factually different ruling override GIR, legal notes, or current BT2026 wording.
8. **Heading decision** — justify the 4-digit heading using GIR 1 whenever possible. If GIR 2, 3, 5, or 6 matters, name the rule and explain why.
9. **Subheading decision** — choose the 6-digit subheading under GIR 6, then map to the Vietnam/AHTN 8-digit line from `BT2026.xlsx` only if the tariff wording supports that specificity.
10. **Self-challenge** — before finalizing, test the conclusion: What evidence contradicts it? Which assumption could be wrong? Is another heading more specific? Is the conclusion stronger than the evidence allows?
11. **Alternative rejection** — explicitly reject plausible competing headings/subheadings with the fact, legal note, or BT2026 wording that disqualifies each one.
12. **Confidence check** — state confidence and the exact missing facts that would change the result; do not ask for facts that would not affect classification.

## Reasoning Standard

Classify in this order:

1. Determine the good's objective characteristics at import.
2. Apply GIR/GRI and relevant Section/Chapter Notes.
3. Select the 4-digit heading.
4. Select 6-digit HS subheading under GIR 6.
5. Select Vietnam/AHTN 8-digit code from `BT2026.xlsx` if evidence supports it.
6. State confidence and missing facts that could change the result.

## GIR 6 / Subheading Rule

Apply GIR 6 explicitly whenever moving from the 4-digit heading to the 6-digit HS subheading and then to Vietnam/AHTN 8-digit lines:

- First lock the correct 4-digit heading using GIR 1-5 and legal notes; do not use an 8-digit tariff line to pull the good into a different heading.
- Compare only subheadings at the same level within the selected heading; do not compare subheadings across different headings or hierarchy levels.
- Treat subheading texts and Subheading Notes as legally controlling at the subheading level, with Section/Chapter Notes applied mutatis mutandis unless context requires otherwise.
- If a 1-dash subheading is selected, compare the relevant 2-dash subheadings only within that 1-dash branch.
- Map to an 8-digit AHTN/BT2026 line only when the official Vietnamese wording fits the chosen 6-digit subheading and the product facts support that extra specificity.
- If the 8-digit wording is unclear or facts are missing, give the supported 6-digit parent and state what fact or BT2026 wording prevents an 8-digit conclusion.

## Output Format

Answer in Vietnamese unless the user asks otherwise. The user prefers results, reasoning, and only necessary evidence; do not list internal tool calls or step-by-step actions taken.

- `Mã đề xuất`: 8-digit code formatted as `xxxx.xx.xx` if available.
- `Tên hàng`: concise commercial/technical name from MSDS/catalog/invoice.
- `Mô tả BT2026`: official wording from `BT2026` where found.
- `Cơ sở phân loại`: concise chain of reasoning from decisive facts -> legal notes/GIR -> heading/subheading -> 8-digit BT2026 line.
- `Bằng chứng chính`: 2-5 decisive source-backed points; cite local paths/source documents next to important claims where useful.
- `Nguồn đã tra`: cite only important local paths or source documents, not the process used to inspect them.
- `Mã cạnh tranh`: nearby competing codes if meaningful, with one-line rejection reason for each plausible alternative.
- `Giả định/điểm chưa chắc`: assumptions or weak evidence that affect confidence.
- `Cần bổ sung`: only ask for facts needed to improve confidence or choose between plausible codes.
- `Mức tin cậy`: high/medium/low with one sentence explaining the main uncertainty and whether evidence was cross-checked.

## References

- `references/session-notes.md` — local corpus readiness notes, user output preference, and classification patterns from prior HS/MSDS work.

## Cautions

- Do not invent 8-digit detail. If BT2026 has no clear 8-digit match, give the supported 6-digit parent and explain.
- Do not rely only on keyword matches; legal notes control classification.
- For Chapter 39 copolymers, apply Chapter 39 Subheading Note 1 and Chapter Note 4 carefully: named monomers in the same heading may be considered together, but do not treat the order of monomers in a chemical name as conclusive proof of weight ratio. If monomer ratios are confidential or missing, present plausible classification scenarios and request TDS/COA/manufacturer declaration before finalizing.
- Treat the result as a reasoned recommendation, not binding customs/legal advice.
