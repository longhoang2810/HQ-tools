# HS Local Corpus Session Notes

## Local corpus readiness

`~/Desktop/HS` was set up with:

- `source/Hs.rar` — original archive.
- `source/BT2026.xlsx` — Vietnam tariff workbook.
- `extracted/` — extracted chapter `.doc` files.
- `index/docs_text/` — converted chapter text files.
- `index/bt2026_rows.csv` — searchable BT2026 rows.
- `build_index.py` and `hs_search.py` — local rebuild/search helpers.

The current text index converted 96 chapter files without extract errors or replacement-character corruption. It is suitable for search and reasoning, but it is not a perfect legal-format copy: old `.doc` conversion can lose tables, pagination, hyperlinks, and some formatting. For high-stakes quotations, cross-check the original `.doc` or official source.

## Output preference learned

For HS classification answers, do not enumerate internal tool calls or the workflow performed. Give the classification result, concise reasoning, important evidence, competing codes, and missing facts only.

## Classification patterns from this session

### Organic thinner/diluent mixtures

A product identified in MSDS as a diluent/thinner containing hydrocarbons C9 aromatics and n-butyl acetate was classified to `3814.00.00`, because heading 38.14 names organic composite solvents and thinners. Do not classify as the individual component code, such as n-butyl acetate, when the imported good is a prepared solvent mixture.

### MBS impact modifier polymers

An LG Chem EM500/MBS product described as `2-Propenoic acid, 2-methyl-methylester, polymer with 1,3-butadiene and ethenylbenzene`, >98% polymer, white powder, used as an impact modifier for plastics, was treated as a primary-form polymer under Chapter 39. A conservative 8-digit result was `3903.90.99` unless technical data supports the more specific impact-resistant styrenic polymer line `3903.90.91` by Izod impact criteria.
