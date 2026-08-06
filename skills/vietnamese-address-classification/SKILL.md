---
name: vietnamese-address-classification
description: "Use when grouping Vietnamese records by province/city."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vietnamese, address, geography, spreadsheet, classification]
---

# Vietnamese Address Classification

## Use when

Classifying rows, records, or spreadsheet data into Vietnamese province/city groups from unstructured address text, especially when outputs require one group per location.

## Source of truth

Store reviewed locations in a plain UTF-8 text configuration. Do not hardcode location lists in application logic.

Recommended shape:

```text
sheet_name<TAB>keyword 1 | keyword 2 | keyword 3
HCM<TAB>Ho Chi Minh | Thanh pho Ho Chi Minh | TP.HCM | TPHCM
```

- Ignore blank lines and `#` comments.
- Use a stable, valid output identifier (`sheet_name`) separate from readable aliases.
- Validate unique identifiers; Excel sheet IDs must be at most 31 characters and exclude `[]:*?/\\`.
- Include historical province names when incoming data predates administrative mergers, but map them to current intended group.

## Matching rules

1. Normalize case and Vietnamese accents before matching (`đ` → `d`).
2. Use specific aliases: full locality names, `tinh <name>`, `thanh pho <name>`, or known unambiguous forms.
3. Never use generic abbreviations or short tokens such as `hp`, `q1`, or `p1`.
4. Do not create groups automatically from raw address fragments. Street names, wards, industrial parks, and abbreviations produce false regions.
5. If multiple reviewed locality names match, select match whose occurrence is furthest right in address. Vietnamese addresses commonly state province/city last, while street names may contain another locality name.
6. Assign every row once only: selected group or `unmatched`. Never duplicate row across multiple sheets.
7. Keep `unmatched` visible and include original address plus reason. Do not silently discard records.

## Regression checks

Maintain small runnable test covering:

- Current and historical aliases map to intended group.
- `TP.HCM` and accent variants match Hồ Chí Minh City.
- Street named `Điện Biên Phủ` or `Đà Nẵng` inside Hải Phòng still maps Hải Phòng.
- One input row appears in exactly one output group.
- Sum of all grouped rows plus `unmatched` equals input rows.

## Verification on a real export

1. Print input row count, each group count, unmatched count, and coverage.
2. Assert `grouped_rows + unmatched_rows == input_rows`; coverage must not exceed 100%.
3. Inspect representative rows from groups with new aliases and from `unmatched`.
4. If output uses Excel sheets, verify sheet names and counts after reopening workbook.

## References

- `references/regions-txt-and-priority.md` — config format and priority rationale.
