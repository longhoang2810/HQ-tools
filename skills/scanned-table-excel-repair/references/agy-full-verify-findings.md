# AGY full-verify findings (QĐ 1092, 2026-07-21)

## Command pattern that worked
```bash
# flags BEFORE -p; no --mode; no --dangerously-skip-permissions; isolate WS
agy --print-timeout=45m0s --add-dir=/tmp/qd1092_agy_iso \
  --model='Gemini 3.5 Flash (High)' -p "$PROMPT"
```

Report path: `.../new-chat/outputs/AGY_FULL_VERIFY_REPORT.md`

## Verdict
**AGY_VERIFY=FAIL** (Hermes re-checked claims)

### Real defects
| Issue | Evidence |
|-------|----------|
| PL II missing STT **460** | PDF `page_300-072.png` has full row; Excel 459→461 |
| PL III STT **10** H typo | Excel `2806/QĐ-BCT`; PDF p131 `2866/QĐ-BCT` |

### Not defects / override
| Claim | Why override |
|-------|----------------|
| Gate 7D FAIL | Contains-check PASS (full origin string longer) |
| Gate 8F FAIL | Contains-check PASS (long risk-name sentence) |
| Missing 253 | Source gap PDF 252→254 — leave empty |

### PL II STT 460 row (from vision p72)
- Tên: Vít, bu lông, đai ốc, vít đầu vuông… vòng đệm…
- HS DN: 98181310, 98181390
- HS rủi ro: 73181510, 73181590, 73182400
- Rủi ro: Khai báo sai mục đích sử dụng để hưởng thuế suất thấp của nhóm 9818
- MFN: B02

## Fix order for PASS
1. Insert PL II STT 460 from PDF p72
2. Replace STT10 H token `2806` → `2866` (keep other QĐs in same cell)
3. Re-run structural + gate contains checks
