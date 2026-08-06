# Regions TXT and locality priority

## Configuration format

```text
# comment
sheet_name<TAB>alias 1 | alias 2 | alias 3
hp<HARD_TAB>Hai Phong | Thanh pho Hai Phong | Hai Duong
```

Use a literal tab between output ID and aliases. This keeps future province/city additions as data edits, not code edits.

## Aliases after administrative merger

Keep previous provincial names in aliases when source exports still use old addresses. Map aliases to one current output sheet. Example: a current provincial sheet may include constituent former provinces.

## Why rightmost locality wins

Address text often holds street/road first, then ward/district, then province/city. Locality names appear in streets too:

```text
Duong Dien Bien Phu, Thanh pho Hai Phong
So 437 Duong Da Nang, Thanh pho Hai Phong
```

Substring matching alone marks both provinces. Use each matching alias's last occurrence; select alias occurring furthest right. If no unique latest match exists, place row in `unmatched` for review.

## Required invariant

```text
grouped rows + unmatched rows = filtered input rows
```

Anything above 100% coverage means duplicated classification. Anything below 100% without unmatched means dropped rows.
