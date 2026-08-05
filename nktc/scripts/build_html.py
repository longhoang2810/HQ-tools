#!/usr/bin/env python3
"""Build the standalone NKTC HTML application from its template and assets."""
import base64
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
template = (ROOT / "NKTC-xu-ly-excel.template.html").read_text(encoding="utf-8")
regions = (ROOT / "regions.txt").read_text(encoding="utf-8")
exceljs = (ROOT / "assets" / "exceljs.min.js").read_text(encoding="utf-8")
cvnk_template_b64 = base64.b64encode((ROOT / "assets" / "CVNK_Gui_thue_template.docx").read_bytes()).decode("ascii")

markers = {
    "__REGIONS__": 1,
    "/* EXCELJS_BUNDLE */": 1,
    "__CVNK_TEMPLATE_B64__": 1,
}
for marker, expected in markers.items():
    if template.count(marker) != expected:
        raise SystemExit(f"Template marker missing or duplicated: {marker}")

output = (template
    .replace("__REGIONS__", escape(regions))
    .replace("/* EXCELJS_BUNDLE */", exceljs)
    .replace("__CVNK_TEMPLATE_B64__", cvnk_template_b64))
path = ROOT / "NKTC-xu-ly-excel.html"
path.write_text(output, encoding="utf-8")
print(f"{path}: {path.stat().st_size} bytes")
