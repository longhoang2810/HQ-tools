#!/usr/bin/env python3
"""Build the standalone NKTC HTML application from its template and assets."""
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
template = (ROOT / "NKTC-xu-ly-excel.template.html").read_text(encoding="utf-8")
regions = (ROOT / "regions.txt").read_text(encoding="utf-8")
exceljs = (ROOT / "assets" / "exceljs.min.js").read_text(encoding="utf-8")

if template.count("__REGIONS__") != 1 or template.count("/* EXCELJS_BUNDLE */") != 1:
    raise SystemExit("Template markers missing or duplicated")

output = template.replace("__REGIONS__", escape(regions)).replace("/* EXCELJS_BUNDLE */", exceljs)
path = ROOT / "NKTC-xu-ly-excel.html"
path.write_text(output, encoding="utf-8")
print(f"{path}: {path.stat().st_size} bytes")
