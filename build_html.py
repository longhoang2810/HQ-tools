#!/usr/bin/env python3
"""Sinh Tra-cuu-hoa-chat-ND24.html — trang tra cứu offline, không cần terminal/Python để dùng.
Nhúng luôn data/nd24_chemicals.json + toàn bộ quy tắc từ core.py vào file
HTML nên chỉ cần double-click mở bằng trình duyệt là chạy được, kể cả
không có mạng.

Lấy IMPORT_RULES/EXEMPTIONS trực tiếp từ core.py (json.dumps)
thay vì gõ tay lại trong JS — tránh HTML và CLI lệch nội dung với nhau
(đây chính là nguyên nhân Điều 21 bị thiếu ở bản trước).

Chạy lại file này mỗi khi data/nd24_chemicals.json hoặc core.py thay đổi:
    python3 build_html.py
"""
import json
import re
from pathlib import Path

import core

HERE = Path(__file__).parent

DATA_JSON = json.dumps(core.DATA, ensure_ascii=False)
IMPORT_RULES_JSON = json.dumps(core.IMPORT_RULES, ensure_ascii=False)
IMPORT_ANNEXES_JSON = json.dumps(core.IMPORT_ANNEXES, ensure_ascii=False)
ANNEX_ORDER_JSON = json.dumps(core.ANNEX_ORDER, ensure_ascii=False)
OTHER_OBLIGATION_ANNEXES_JSON = json.dumps(core.OTHER_OBLIGATION_ANNEXES, ensure_ascii=False)
VERDICT_JSON = json.dumps(core.VERDICT, ensure_ascii=False)
SUPPRESS_ANNEX_JSON = json.dumps(core.SUPPRESS_ANNEX, ensure_ascii=False)
ANNEX_DISPLAY_ORDER_JSON = json.dumps(core.ANNEX_DISPLAY_ORDER, ensure_ascii=False)
PL3_NO_CAS_JSON = json.dumps(core.PL3_NO_CAS, ensure_ascii=False)
PL3_FAMILY_HINTS_JSON = json.dumps(core.PL3_FAMILY_HINTS, ensure_ascii=False)
PL3_HINT_PREFIX_JSON = json.dumps(core.PL3_HINT_PREFIX, ensure_ascii=False)
PL3_EXCLUDED_JSON = json.dumps(core.PL3_EXCLUDED, ensure_ascii=False)
PL3_EXCLUDED_NOTE_JSON = json.dumps(core.PL3_EXCLUDED_NOTE, ensure_ascii=False)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pl3_no_cas_html():
    """Khối cảnh báo các mục Phụ lục III ghi theo họ chất, không có mã CAS.
    Lấy từ core (data/nd24_pl3_no_cas.json do extract.py sinh từ nd24.md) —
    không gõ tay danh sách trong HTML, y như mục miễn trừ."""
    parts = [
        f'<h2>⚠ {esc(core.PL3_NO_CAS_TITLE)}</h2>',
        f'<p class="lead">{esc(core.PL3_NO_CAS_LEAD)}</p>',
        '<p class="cite">📖 <a href="#nd24-pl-iii">Mở nguyên văn Phụ lục III của NĐ 24</a>'
        " để đối chiếu mô tả từng mục.</p>",
    ]
    for group in sorted({e["category"] for e in core.PL3_NO_CAS}):
        parts.append(f"<h3>{esc(group)}</h3>")
        items = "".join(
            f'<li><b><a href="#nd24-pl-iii">{esc(e["stt"])}</a></b> {esc(e["ten"])}</li>'
            for e in core.PL3_NO_CAS
            if e["category"] == group
        )
        parts.append(f"<ul>{items}</ul>")
    return "\n  ".join(parts)


DIEU_RE = re.compile(r"^Điều\s+(\d+)\.")


def cite_link(cite, doc="nd26"):
    """'Điều 21, khoản 4 & 5' -> link tới Điều 21 trong khối toàn văn.
    Chỉ dùng cho EXEMPTIONS (toàn bộ dẫn chiếu NĐ 26); PENALTY_WARNING dẫn NĐ 169
    không có toàn văn trong repo nên KHÔNG đi qua hàm này."""
    m = re.match(r"Điều\s+(\d+)", cite)
    if not m:
        return esc(cite)
    return f'<a href="#{doc}-dieu-{m.group(1)}">{esc(m.group(0))}</a>{esc(cite[m.end():])}'


def _heading(text, doc, toc, level="h3"):
    """Heading của văn bản luật; dòng 'Điều N.'/'PHỤ LỤC' được gắn id để link tới."""
    key = None
    m = DIEU_RE.match(text)
    if m:
        key = f"{doc}-dieu-{m.group(1)}"
    elif text.upper().startswith("PHỤ LỤC"):
        # id thuần ASCII: location.hash bị percent-encode, querySelector("#nd24-ph%E1...")
        # sẽ không khớp id có dấu -> link Phụ lục im lặng không nhảy.
        key = f"{doc}-pl-{text.split()[-1].lower()}"
    if not key:
        return f"<{level}>{esc(text)}</{level}>"
    toc.append((key, text))
    return f'<{level} id="{key}">{esc(text)}</{level}>'


def _cell(text):
    # nd24.md dùng <br> trong ô bảng -> giữ lại sau khi escape.
    return esc(text).replace("&lt;br&gt;", "<br>")


def _table_html(rows, header_idx):
    out = ['<div class="table-wrap"><table>']
    for i, row in enumerate(rows):
        tag = "th" if i == header_idx else "td"
        cells = "".join(f"<{tag}>{_cell(c)}</{tag}>" for c in row)
        out.append(f"<tr>{cells}</tr>")
    out.append("</table></div>")
    return "".join(out)


def nd24_doc_html(toc):
    """nd24.md (markdown: heading '#' + bảng '|') -> HTML."""
    out, rows, header_idx = [], [], -1

    def flush():
        nonlocal rows, header_idx
        if rows:
            out.append(_table_html(rows, header_idx))
        rows, header_idx = [], -1

    for raw in HERE.joinpath("nd24.md").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(c and set(c) <= set("-: ") for c in cells):
                header_idx = len(rows) - 1  # dòng phân cách -> dòng ngay trên là header
            else:
                rows.append(cells)
            continue
        flush()
        if not line:
            continue
        if line.startswith("#"):
            out.append(_heading(line.lstrip("# ").strip(), "nd24", toc))
        else:
            out.append(f"<p>{esc(line)}</p>")
    flush()
    return "\n".join(out)


def nd26_doc_html(toc):
    """nd26.txt (mỗi đoạn một dòng) -> HTML."""
    out = []
    for raw in HERE.joinpath("nd26.txt").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if re.match(r"^(Chương|Mục|Điều)\s", line):
            out.append(_heading(line, "nd26", toc))
        elif line == line.upper() and len(line) > 3:
            out.append(f"<h4>{esc(line)}</h4>")
        else:
            out.append(f"<p>{esc(line)}</p>")
    return "\n".join(out)


def full_text_html():
    """Hai khối toàn văn NĐ 24 & NĐ 26, dựng từ nd24.md/nd26.txt trong repo —
    không gõ tay, không cần file .docx đi kèm (trang vẫn là 1 file chạy offline)."""
    parts = []
    for doc, title, body_fn in (
        ("nd24", "Nghị định 24/2026/NĐ-CP — các danh mục hóa chất (Phụ lục I–IV)", nd24_doc_html),
        ("nd26", "Nghị định 26/2026/NĐ-CP — quản lý hoạt động hóa chất", nd26_doc_html),
    ):
        toc = []
        body = body_fn(toc)
        links = " · ".join(
            f'<a href="#{key}">{esc(text.split(".")[0] if text.startswith("Điều") else text)}</a>'
            for key, text in toc
        )
        parts.append(
            f'<details class="doc" id="doc-{doc}">'
            f"<summary>📖 Toàn văn {esc(title)}</summary>"
            f'<div class="doc-body"><nav class="doc-toc">{links}</nav>{body}</div>'
            "</details>"
        )
    return "\n".join(parts)


def exemptions_html():
    parts = ['<h2>Các trường hợp được miễn trừ</h2>', '<p class="cite">Nghị định 26/2026/NĐ-CP</p>']
    for group in core.EXEMPTIONS:
        parts.append(f'<h3>{esc(group["title"])} ({cite_link(group["cite"])})</h3>')
        if "lead" in group:
            parts.append(f'<p class="lead">{esc(group["lead"])}</p>')
        parts.append("<ul>" + "".join(f"<li>{esc(item)}</li>" for item in group["items"]) + "</ul>")
    parts.append(f'<div class="warn-note">{esc(core.PENALTY_WARNING)}</div>')
    parts.append(f'<h2>{esc(core.OTHER_OBLIGATIONS_TITLE)}</h2>')
    parts.append("<ul>" + "".join(f"<li>{esc(item)}</li>" for item in core.OTHER_OBLIGATIONS) + "</ul>")
    return "\n  ".join(parts)


HTML = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tra cứu hóa chất – NĐ 24 &amp; 26/2026/NĐ-CP</title>
<style>
  :root {
    --blue: #1a5fb4; --blue-dark: #123f7a;
    --ink: #1c2530; --muted: #5b6673; --line: #dfe4ea;
    --bg: #f4f6f9; --card: #ffffff;
    --red-bg: #fdecea; --red-line: #f3b9b2; --red-ink: #9a2f21;
    --green-bg: #eaf6ec; --green-line: #b9dcc0;
    --amber-bg: #fff8e6; --amber-line: #f0d488;
  }
  * { box-sizing: border-box; }
  body { font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif; max-width: 880px; margin: 0 auto; padding: 32px 20px 60px; color: var(--ink); background: var(--bg); line-height: 1.5; }
  header { text-align: center; margin-bottom: 26px; padding-top: 18px; position: relative; }
  header::before { content: ""; position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 64px; height: 4px; border-radius: 2px; background: linear-gradient(90deg, var(--blue), #2f7d3c); }
  h1 { font-size: 1.9rem; margin: 0 0 6px; letter-spacing: -0.01em; }
  header p { color: var(--muted); margin: 0; font-size: 1rem; }
  header .author { margin-top: 8px; font-size: 0.85rem; font-weight: 600; color: var(--blue-dark); }

  .card { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 20px 22px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(20,30,50,0.05); }

  .instructions { display: flex; gap: 12px; align-items: flex-start; }
  .instructions .icon { font-size: 1.4rem; line-height: 1; }
  .instructions ol { margin: 8px 0 0; padding-left: 20px; }
  .instructions li { margin-bottom: 4px; text-align: justify; }
  .instructions h2 { margin: 0; font-size: 1.05rem; }

  .modes { display: flex; gap: 8px; margin-bottom: 12px; }
  .mode-btn { cursor: pointer; font-size: 0.92rem; font-weight: 600; padding: 7px 16px; border-radius: 8px; border: 1px solid var(--line); background: #fff; color: var(--muted); }
  .mode-btn:hover { border-color: var(--blue); }
  .mode-btn.active { background: var(--blue); border-color: var(--blue); color: #fff; }

  .input-row { display: flex; gap: 12px; align-items: stretch; }
  textarea { flex: 1; min-height: 110px; font-size: 1rem; padding: 12px 14px; border: 1px solid var(--line); border-radius: 8px; resize: vertical; font-family: inherit; }
  textarea:focus { outline: 2px solid var(--blue); outline-offset: 1px; }
  button#run-btn { flex: 0 0 auto; align-self: stretch; min-width: 130px; font-size: 1.05rem; font-weight: 600; cursor: pointer; background: var(--blue); color: #fff; border: none; border-radius: 8px; padding: 10px 20px; transition: background .15s; }
  button#run-btn:hover { background: var(--blue-dark); }
  .toolbar { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; align-items: center; }
  .toolbar .hint { color: var(--muted); font-size: 0.82rem; margin-left: auto; }
  button.mini { font-size: 0.86rem; cursor: pointer; background: #fff; color: var(--blue-dark); border: 1px solid var(--line); border-radius: 7px; padding: 5px 12px; font-weight: 600; }
  button.mini:hover { border-color: var(--blue); background: #f2f6fc; }
  @media (max-width: 560px) { .input-row { flex-direction: column; } button#run-btn { padding: 12px; } .toolbar .hint { display: none; } }

  #count { margin: 0 0 10px; font-weight: 600; color: var(--ink); }
  .stats { display: flex; gap: 8px; flex-wrap: wrap; margin: 0 0 12px; }
  .chip { display: inline-block; padding: 4px 12px; border-radius: 99px; font-size: 0.86rem; font-weight: 700; border: 1px solid transparent; }
  .chip.warn { background: var(--red-bg); border-color: var(--red-line); color: var(--red-ink); }
  .chip.ok { background: var(--green-bg); border-color: var(--green-line); color: #24632f; }
  .chip.unknown { background: var(--amber-bg); border-color: var(--amber-line); color: #7a600e; }

  .table-wrap { overflow-x: auto; }
  table { border-collapse: collapse; width: 100%; }
  th, td { padding: 9px 10px; text-align: left; vertical-align: top; font-size: 0.93rem; border-bottom: 1px solid var(--line); }
  th { color: var(--muted); font-weight: 600; font-size: 0.82rem; text-transform: uppercase; letter-spacing: .03em; }
  tr.warn td { background: var(--red-bg); }
  tr.ok td { background: var(--green-bg); }
  tr.unknown td { background: var(--amber-bg); }
  .cas { font-weight: 700; font-variant-numeric: tabular-nums; white-space: nowrap; }
  .pill { display: inline-block; padding: 2px 9px; border-radius: 99px; font-size: 0.78rem; font-weight: 700; white-space: nowrap; }
  .pill.warn { background: var(--red-ink); color: #fff; }
  .pill.ok { background: #2f7d3c; color: #fff; }
  .pill.unknown { background: #9a7a12; color: #fff; }

  details.detail { border: 1px solid var(--line); border-radius: 8px; margin-top: 10px; background: #fbfcfd; overflow: hidden; }
  details.detail[open] { border-color: #c9d3de; }
  details.detail summary { cursor: pointer; padding: 10px 14px; font-weight: 600; list-style: none; display: flex; align-items: center; gap: 8px; }
  details.detail summary::-webkit-details-marker { display: none; }
  details.detail summary::before { content: "▸"; color: var(--muted); transition: transform .12s; }
  details.detail[open] summary::before { transform: rotate(90deg); }
  details.detail .body { padding: 2px 16px 16px; font-size: 0.93rem; color: #333; border-top: 1px solid var(--line); margin-top: 4px; padding-top: 12px; text-align: justify; }
  details.detail .cats { white-space: pre-wrap; color: var(--muted); font-size: 0.9rem; }
  details.detail h4 { margin: 14px 0 6px; font-size: 0.9rem; color: var(--blue-dark); }
  details.detail ul.rules { margin: 0; padding-left: 20px; }
  details.detail ul.rules li { margin-bottom: 5px; text-align: left; }

  .exempt h2 { font-size: 1.1rem; margin: 0 0 4px; }
  .exempt h3 { font-size: 0.95rem; margin: 16px 0 6px; color: var(--blue-dark); }
  .exempt ul { margin: 4px 0 0; padding-left: 20px; }
  .exempt li { margin-bottom: 4px; text-align: justify; }
  .exempt .lead, .exempt .warn-note { text-align: justify; }
  .exempt .warn-note { background: var(--red-bg); border: 1px solid var(--red-line); border-radius: 8px; padding: 10px 14px; margin-top: 14px; color: var(--red-ink); font-size: 0.93rem; }
  .exempt .cite { color: var(--muted); font-size: 0.85rem; }
  .exempt .lead { font-weight: 600; margin: 6px 0 4px; }

  /* Ghi chú "Ngoại trừ": thông tin, không phải cảnh báo -> xám trung tính, để
     không tranh chỗ với cờ đỏ họ chất vốn mới là thứ cần chú ý. */
  .excl-note { margin-top: 8px; background: #f2f6fc; border: 1px solid var(--line); border-left: 3px solid var(--blue); border-radius: 6px; padding: 7px 10px; color: var(--muted); font-size: 0.78rem; text-align: left; font-weight: 400; }

  /* Cờ họ chất: nằm trong ô trạng thái, phải "cãi lại" được pill xanh ngay
     cạnh nó nên dùng nền/viền đỏ, không phải chữ xám mờ. */
  .fam-hint { margin-top: 8px; background: var(--red-bg); border: 1px solid var(--red-line); border-left: 3px solid var(--red-ink); border-radius: 6px; padding: 7px 10px; color: var(--red-ink); font-size: 0.8rem; font-weight: 600; text-align: left; }
  .fam-hint ul { margin: 4px 0 0; padding-left: 18px; font-weight: 400; }
  .fam-hint .cite { color: var(--red-ink); opacity: .8; font-size: 0.76rem; }
  /* Link sang toàn văn nằm trong khối đã có màu riêng -> giữ nguyên màu chữ của
     khối, chỉ gạch chân, để không phá tương phản cảnh báo. */
  .fam-hint a, .blind-spot a, td a { color: inherit; text-decoration: underline; text-underline-offset: 2px; }

  /* Cảnh báo vùng mù: viền đỏ để không bị đọc lướt như chú thích thường —
     đây là chỗ trang có thể im lặng bỏ sót chất cần Giấy phép. */
  .blind-spot { border-color: var(--red-line); border-left: 4px solid var(--red-ink); }
  .blind-spot h2 { color: var(--red-ink); }
  .blind-spot .lead { font-weight: 400; background: var(--red-bg); border-radius: 8px; padding: 10px 14px; margin: 8px 0 4px; }
  .blind-spot li { font-size: 0.9rem; }

  /* Toàn văn hai nghị định — nhúng thẳng vào trang để không phải mở file .docx
     rời (trang vẫn là 1 file chạy offline). Đóng sẵn, mở khi cần đọc. */
  header .docs { margin-top: 10px; font-size: 0.85rem; }
  header .docs a { color: var(--blue-dark); text-decoration: none; border-bottom: 1px dashed var(--blue); }
  details.doc { background: var(--card); border: 1px solid var(--line); border-radius: 12px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(20,30,50,0.05); }
  details.doc > summary { cursor: pointer; padding: 16px 22px; font-weight: 600; }
  details.doc .doc-body { padding: 0 22px 20px; border-top: 1px solid var(--line); }
  details.doc .doc-toc { font-size: 0.8rem; color: var(--muted); margin: 14px 0 18px; line-height: 2; }
  details.doc .doc-toc a { color: var(--blue-dark); text-decoration: none; }
  details.doc .doc-toc a:hover { text-decoration: underline; }
  details.doc h3 { font-size: 1rem; color: var(--blue-dark); margin: 20px 0 6px; scroll-margin-top: 12px; }
  details.doc h4 { font-size: 0.9rem; margin: 14px 0 6px; }
  details.doc p { font-size: 0.9rem; text-align: justify; margin: 6px 0; }
  details.doc td, details.doc th { font-size: 0.82rem; padding: 5px 8px; text-transform: none; }
  details.doc :target { background: #fff6d6; }

  .note { color: var(--muted); font-size: 0.88rem; text-align: justify; }
  footer { text-align: center; color: var(--muted); font-size: 0.82rem; margin-top: 30px; }

  @media print {
    body { background: #fff; padding: 0; max-width: none; }
    .instructions, #input-card, footer, header::before { display: none; }
    .card { box-shadow: none; border-color: #bbb; break-inside: avoid; }
    details.detail { break-inside: avoid; }
    .pill { border: 1px solid #888; color: #000 !important; background: #fff !important; }
  }
</style>
</head>
<body>

<header>
  <h1>Tra cứu hóa chất</h1>
  <p>Nghị định 24/2026/NĐ-CP &amp; Nghị định 26/2026/NĐ-CP</p>
  <p class="author">Tác giả: Nguyễn Hoàng Long - HQ KCX&amp;KCN</p>
  <p class="docs">📖 Đọc toàn văn: <a href="#doc-nd24">NĐ 24/2026/NĐ-CP</a> · <a href="#doc-nd26">NĐ 26/2026/NĐ-CP</a></p>
</header>

<div class="card instructions">
  <div class="icon">ℹ️</div>
  <div>
    <h2>Hướng dẫn sử dụng</h2>
    <ol>
      <li>Copy nguyên mô tả hàng hóa của doanh nghiệp — không cần tách tay từng mã CAS.</li>
      <li>Dán vào ô bên dưới rồi bấm <b>Tra cứu</b>. Hai chế độ tra:
        <ul>
          <li><b>Tìm theo mã CAS</b> (mặc định): tự tìm mọi mã CAS xuất hiện trong đoạn văn. Chính xác nhất — dùng khi doanh nghiệp có khai mã CAS.</li>
          <li><b>Tìm theo tên chất</b>: dò tên hóa chất có trong đoạn (tiếng Việt hoặc tiếng Anh, không cần gõ dấu), hoặc gõ một phần tên để liệt kê các chất mang tên đó. Dùng khi doanh nghiệp không khai mã CAS — kết quả chỉ là gợi ý, xem cảnh báo trong bảng.</li>
        </ul>
      </li>
      <li>Công cụ không tự tính % hàm lượng — hóa chất Phụ lục III luôn báo "__VERDICT_PL3__"; đối chiếu ngưỡng miễn trừ nồng độ ở mục "Các trường hợp được miễn trừ" bên dưới bằng tài liệu khai báo gốc.</li>
    </ol>
  </div>
</div>

<div class="card" id="input-card">
  <div class="modes">
    <button class="mode-btn active" id="mode-cas" aria-pressed="true" onclick="setMode('cas')">🔢 Tìm theo mã CAS</button>
    <button class="mode-btn" id="mode-name" aria-pressed="false" onclick="setMode('name')">🔤 Tìm theo tên chất</button>
  </div>
  <div class="input-row">
    <textarea id="input" placeholder="Ví dụ: Hỗn hợp dung môi công nghiệp gồm Metanol CAS 67-56-1, Acetaldehyde (75-07-0), mã CAS 103-79-7 (P2P)..."></textarea>
    <button id="run-btn" onclick="run()">🔍 Tra cứu</button>
  </div>
  <div class="toolbar">
    <button class="mini" onclick="randomExampleForMode()">🎲 Ví dụ ngẫu nhiên</button>
    <button class="mini" onclick="clearAll()">✕ Xóa</button>
    <span class="hint">Mẹo: nhấn <b>Ctrl+Enter</b> (⌘+Enter trên Mac) để tra cứu nhanh</span>
  </div>
</div>

<div id="results"></div>

<div class="card exempt blind-spot">
  __PL3_NO_CAS_HTML__
</div>

<div class="card exempt">
  __EXEMPTIONS_HTML__
</div>

__FULL_TEXT_HTML__

<footer>Bản tóm tắt để tra cứu nhanh — luôn đối chiếu điều luật gốc trước khi ra quyết định thông quan.</footer>

<script>
const DATA = __DATA_JSON__;
const IMPORT_RULES = __IMPORT_RULES_JSON__;
const IMPORT_ANNEXES = __IMPORT_ANNEXES_JSON__;
const OTHER_OBLIGATION_ANNEXES = __OTHER_OBLIGATION_ANNEXES_JSON__;
const VERDICT = __VERDICT_JSON__;
const SUPPRESS_ANNEX = __SUPPRESS_ANNEX_JSON__;
const ANNEX_DISPLAY_ORDER = __ANNEX_DISPLAY_ORDER_JSON__;

const ANNEX_ORDER = __ANNEX_ORDER_JSON__;
const PL3_NO_CAS = __PL3_NO_CAS_JSON__;
const PL3_FAMILY_HINTS = __PL3_FAMILY_HINTS_JSON__;
const PL3_HINT_PREFIX = __PL3_HINT_PREFIX_JSON__;
const PL3_EXCLUDED = __PL3_EXCLUDED_JSON__;
const PL3_EXCLUDED_NOTE = __PL3_EXCLUDED_NOTE_JSON__;

const CAS_RE = /\\b\\d{2,7}-\\d{2}-\\d\\b/g;

function rowsFor(cas) {
  return DATA.filter(r => r.cas === cas);
}

function highestAnnex(cas) {
  const present = new Set(rowsFor(cas).map(r => r.annex));
  for (const a of ANNEX_ORDER) if (present.has(a)) return a;
  return null;
}

// Nhan phu luc la LINK sang nguyen van phu luc do trong khoi toan van cuoi
// trang — can bo doc dong ket qua xong muon xem chinh chu nghi dinh thi bam
// ngay tai cho, khong phai cuon di tim.
function annexLink(a) {
  return `<a href="#nd24-pl-${esc(a).toLowerCase()}" title="Mở nguyên văn Phụ lục ${esc(a)} của NĐ 24">PL ${esc(a)}</a>`;
}

function annexLabels(cas) {
  const present = new Set(rowsFor(cas).map(r => r.annex));
  return ANNEX_DISPLAY_ORDER.filter(a => present.has(a)).map(annexLink).join(", ") || "—";
}

// Doi xung voi extract_cas() trong core.py.
function extractCas(text) {
  const seen = new Set(), out = [];
  for (const m of text.matchAll(CAS_RE)) {
    if (!seen.has(m[0])) { seen.add(m[0]); out.push(m[0]); }
  }
  return out;
}

function normName(s) {
  return s.normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").replace(/đ/g, "d").toLowerCase();
}

// Bo het dau cau ve khoang trang -> so khop theo TU, khong theo ky tu: "N,N-dimetyl"
// va "N,N dimetyl" cung dang; va " etanol " khong an vao "metanol".
function normWords(s) {
  return " " + normName(s).replace(/[^a-z0-9]+/g, " ").trim() + " ";
}

// Chi so ten -> CAS de do ten hoa chat NAM TRONG doan mo ta (DN thuong khai
// "Hon hop dung moi gom Metanol, Toluen" khong kem ma CAS). Cum DAI NHAT truoc:
// gap "natri clorua" thi an luon "natri" nam trong no, khong bao ca hai chat.
const NAME_INDEX = (() => {
  // Gom theo TEN: mot ten co the mang nhieu ma CAS (cung ten goi, khac so dang
  // ky; hoac cung chat ghi khac chinh ta giua cac phu luc). Khop trung ten thi
  // bao HET cac ma do — bao mot ma la giau mat cac ma con lai khoi can bo.
  const byName = new Map();
  for (const r of DATA) {
    for (const name of [r.name_vn, r.name_en]) {
      // Index them PHAN DAU ten, bo duoi qualifier ("... và các muối proton hóa
      // chat tuong ung", "... and its salts") va phan trong ngoac ("Selen (dạng
      // bột)"): DN khai ten thuong mai, khong ai khai kem duoi cua nghi dinh.
      // BAT BUOC, khong phai tien nghi: thieu no thi "N,N-dimetyl amino etanol"
      // (108-01-0, PL II) khong khop ten day du roi tut xuong khop chu "etanol"
      // nam trong doan -> bao ra Etanol (64-17-5, PL I). Sai chat, va giau mat
      // nghia vu Giay chung nhan SX-KD cua chat that.
      for (const alias of [name, name.split(/ và | and | \\(/i)[0]]) {
        const n = normWords(alias).trim();
        // >=3 ky tu: ten ngan nhat trong du lieu la "clo"/"flo"/"oxy"; nguong nay
        // khong bo sot ten nao ma chan manh vun 1-2 ky tu khop lung tung.
        if (n.length < 3) continue;
        if (!byName.has(n)) byName.set(n, new Set());
        byName.get(n).add(r.cas);
      }
    }
  }
  return [...byName.entries()]
    .map(([n, cas]) => ({ n, cas: [...cas] }))
    .sort((a, b) => b.n.length - a.n.length);
})();

// Ten hoa chat XUAT HIEN trong doan van, theo thu tu gap (doi xung extractCas).
function scanNames(text) {
  let hay = normWords(text);
  const hits = [];
  for (const { n, cas } of NAME_INDEX) {
    const i = hay.indexOf(" " + n + " ");
    if (i === -1) continue;
    for (const c of cas) hits.push([i, c]);
    // Che cum vua khop (giu nguyen do dai de vi tri cac cum khac khong lech).
    hay = hay.slice(0, i) + " " + "\\u0000".repeat(n.length) + " " + hay.slice(i + n.length + 2);
  }
  hits.sort((a, b) => a[0] - b[0]);
  return [...new Set(hits.map(([, cas]) => cas))];
}

// Go mot phan ten: moi tu cua truy van phai xuat hien trong name_vn hoac name_en.
// Uu tien khop nguyen ten > dau ten > chua trong ten.
function partialNameMatches(text) {
  const q = normName(text.trim());
  if (q.length < 2) return [];
  const tokens = q.split(/\\s+/);
  const scored = [];
  for (const r of DATA) {
    const vn = normName(r.name_vn), en = normName(r.name_en);
    if (!tokens.every(t => vn.includes(t) || en.includes(t))) continue;
    const score = (vn === q || en === q) ? 0 : (vn.startsWith(q) || en.startsWith(q)) ? 1 : 2;
    scored.push([score, r.cas]);
  }
  scored.sort((a, b) => a[0] - b[0]);
  return [...new Set(scored.map(([, cas]) => cas))];
}

// Tra theo ten khi doan nhap khong co ma CAS nao. Hai kieu khop bo tuc nhau, KHONG
// thay the nhau: mo ta DN ("Hon hop gom Metanol, Toluen") chi scanNames bat duoc
// (partial doi MOI tu cua ca cau nam trong mot ten -> khong bao gio khop); con go
// mot phan ten ("amino") thi chi partial bat duoc. Cum do duoc trong doan van len truoc.
const NAME_LIMIT = 30;
function searchByName(text) {
  const out = scanNames(text);
  const seen = new Set(out);
  for (const cas of partialNameMatches(text)) if (!seen.has(cas)) { seen.add(cas); out.push(cas); }
  return out;
}

// Doi xung voi cas_status() trong core.py — khong tu nhan dien % ham
// luong (khai bao tu do de ghi lon xon, doan nham % de ket luan mien tru
// sai): hoa chat Phu luc III luon bao "Can Giay phep".
function casStatus(cas) {
  const rows = rowsFor(cas);
  if (!rows.length) return { badge: "unknown", text: VERDICT.unknown };
  const present = new Set(rows.map(r => r.annex));
  if (present.has("III")) return { badge: "warn", text: VERDICT.pl3 };
  // Khong thuoc PL III: khong can Giay phep XNK nhung con nghia vu PL II ->
  // verdict phai noi "con nghia vu khac"; PL IV khong thuoc khau XNK.
  if (OTHER_OBLIGATION_ANNEXES.some(a => present.has(a))) {
    return { badge: "ok", text: VERDICT.other_obligation };
  }
  return { badge: "ok", text: VERDICT.none };
}

function esc(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Doi xung voi pl3_family_hints() trong core.py — du lieu (PL3_NO_CAS,
// PL3_FAMILY_HINTS) nhung tu core, khong go tay. test_co_ho_chat_html_khop_core
// chay ca hai ban tren TOAN BO du lieu roi so, de hai noi khong the lech nhau.
function pl3FamilyHints(cas) {
  const rows = rowsFor(cas);
  if (!rows.length || new Set(rows.map(r => r.annex)).has("III")) return [];
  const name = `${rows[0].name_vn} ${rows[0].name_en}`.toLowerCase();
  return PL3_NO_CAS.filter(e => (PL3_FAMILY_HINTS[e.stt] || []).some(k => name.includes(k)));
}

function hintHtml(cas) {
  let out = "";
  // Doi xung voi pl3_excluded() trong core.py.
  for (const e of PL3_EXCLUDED.filter(x => x.cas === cas)) {
    out += `<div class="excl-note">${esc(PL3_EXCLUDED_NOTE.replace("{stt}", e.ngoai_tru_khoi.replace(/\\.$/, "")))}</div>`;
  }
  const hints = pl3FamilyHints(cas);
  if (hints.length) {
    const items = hints.map(e => `<li><b><a href="#nd24-pl-iii" title="Mở nguyên văn Phụ lục III của NĐ 24">${esc(e.stt)}</a></b> ${esc(e.ten)} <span class="cite">(${esc(e.category)})</span></li>`).join("");
    out += `<div class="fam-hint"><b>${esc(PL3_HINT_PREFIX)}</b><ul>${items}</ul></div>`;
  }
  return out;
}

// Chi goi cho CAS CO trong du lieu — CAS khong co thi khong dung the chi tiet.
function detailFor(cas) {
  const rows = rowsFor(cas);
  let out = "";
  const seenAnnex = new Set();
  // IMPORT_ANNEXES nhúng từ core.py — trước đây JS hard-code ["I","II","III"]
  // nên chất chỉ thuộc PL II hiện category trong HTML còn CLI lại nói
  // "Không phát sinh yêu cầu nhập khẩu riêng" (hai nơi hai kiểu).
  const importRows = rows.filter(r => IMPORT_ANNEXES.includes(r.annex));
  for (const r of importRows) {
    out += `- ${r.category}\\n`;
    seenAnnex.add(r.annex);
  }
  if (!importRows.length) return `<div class="cats">Không phát sinh yêu cầu nhập khẩu riêng.</div>`;
  let html = `<div class="cats">${esc(out.trim())}</div>`;
  // Cùng quy tắc ẩn khối với core.annexes_to_explain (SUPPRESS_ANNEX nhúng từ core.py).
  const hidden = new Set();
  for (const a of seenAnnex) for (const h of (SUPPRESS_ANNEX[a] || [])) hidden.add(h);
  for (const annex of Object.keys(IMPORT_RULES)) {
    if (!seenAnnex.has(annex) || hidden.has(annex)) continue;
    const items = IMPORT_RULES[annex].map(b => `<li>${esc(b)}</li>`).join("");
    html += `<h4>Yêu cầu nhập khẩu (Phụ lục ${annex})</h4><ul class="rules">${items}</ul>`;
  }
  return html;
}

// Hai che do TUONG MINH thay vi tu doan: can bo chon tra theo gi. Truoc day dò
// ten chi chay khi doan KHONG co ma CAS nao -> mo ta tron (vai chat khai ma, vai
// chat chi ghi ten) thi cac chat ghi ten bi bo qua IM LANG. Nay chon che do nao
// ra dung thu do, va che do con lai duoc nhac den khi doan co du lieu cho no.
let MODE = "cas";
const MODE_PLACEHOLDER = {
  cas: "Ví dụ: Hỗn hợp dung môi công nghiệp gồm Metanol CAS 67-56-1, Acetaldehyde (75-07-0), mã CAS 103-79-7 (P2P)...",
  name: "Ví dụ: Hỗn hợp dung môi công nghiệp gồm Metanol, Toluene và Axeton — hoặc gõ một phần tên: amino",
};

function setMode(mode) {
  MODE = mode;
  for (const m of ["cas", "name"]) {
    const btn = document.getElementById("mode-" + m);
    btn.classList.toggle("active", m === mode);
    btn.setAttribute("aria-pressed", String(m === mode));
  }
  const input = document.getElementById("input");
  input.placeholder = MODE_PLACEHOLDER[mode];
  // Doi che do ma van con ket qua cu tren man hinh = doc nham ket qua che do kia.
  if (input.value.trim()) run(); else document.getElementById("results").innerHTML = "";
  input.focus();
}

function run() {
  const text = document.getElementById("input").value;
  const resultsEl = document.getElementById("results");
  const casInText = extractCas(text);
  let entries, heading, hint = "", nameNote = "";

  if (MODE === "cas") {
    if (casInText.length === 0) {
      resultsEl.innerHTML = `<div class="card"><p class="note">Không tìm thấy mã CAS nào (định dạng NNN-NN-N) trong đoạn đã nhập. Kiểm tra lại mô tả, dán trực tiếp mã CAS (ví dụ: 107-13-1), hoặc chuyển sang <b>Tìm theo tên chất</b> nếu doanh nghiệp không khai mã CAS.</p></div>`;
      return;
    }
    entries = casInText;
    heading = `Tìm thấy ${entries.length} mã CAS`;
    // Che do nay KHONG tu dò ten (bao thua ten se lam ban ket luan cua MOI lo
    // hang), nhung im lang bo qua chat chi ghi ten thi can bo tuong bang da liet
    // ke het -> khong dua vao bang, chi nhac co cai o day de tu quyet.
    const namedOnly = scanNames(text).filter(cas => !entries.includes(cas));
    if (namedOnly.length) {
      const names = [...new Set(namedOnly.map(cas => rowsFor(cas)[0].name_vn))];
      hint = `<p class="note">⚠ Đoạn này còn nhắc tới ${names.length} tên hóa chất có trong dữ liệu nhưng <b>không kèm mã CAS</b>: ${esc(names.slice(0, 5).join(", "))}${names.length > 5 ? "…" : ""}. Chế độ này không tra chúng — chuyển sang <b>Tìm theo tên chất</b> để xem.</p>`;
    }
  } else {
    const byName = searchByName(text);
    if (byName.length === 0) {
      resultsEl.innerHTML = `<div class="card"><p class="note">Không có tên hóa chất nào trong dữ liệu NĐ 24 khớp với đoạn đã nhập. Kiểm tra lại chính tả, gõ một phần tên (ví dụ: metanol), hoặc chuyển sang <b>Tìm theo mã CAS</b> nếu doanh nghiệp có khai mã CAS.</p></div>`;
      return;
    }
    entries = byName.slice(0, NAME_LIMIT);
    heading = `Tìm theo tên được ${byName.length} chất khớp`
      + (byName.length > NAME_LIMIT ? `, hiển thị ${NAME_LIMIT} chất khớp nhất` : "");
    // Tra theo ten KHONG co case "Khong ro" nhu che do CAS: ten khong khop thi
    // khong hien dong nao. Bang doc thanh "ca lo chi co bay nhieu chat" duoc ->
    // phai noi thang gioi han nay ngay trong ket qua.
    nameNote = `<p class="note"><b>Chỉ là gợi ý theo tên — không thay cho mã CAS.</b> Bảng dưới chỉ liệt kê tên khớp với dữ liệu NĐ 24; chất mang tên khác hoặc không có trong Phụ lục I–IV sẽ KHÔNG hiện dòng nào (khác tra theo mã CAS — mã lạ vẫn báo "${esc(VERDICT.unknown)}"), nên bảng này không chứng minh lô hàng chỉ có bấy nhiêu chất. Tên ghép cũng có thể khớp thừa (mô tả "natri clorua" khớp ra chất "Natri"). Luôn đối chiếu mã CAS trên tài liệu khai báo gốc.</p>`;
    if (casInText.length) {
      hint = `<p class="note">⚠ Đoạn này có ${casInText.length} mã CAS — chế độ <b>Tìm theo tên chất</b> bỏ qua chúng. Chuyển sang <b>Tìm theo mã CAS</b> để tra theo mã.</p>`;
    }
  }

  const counts = { warn: 0, ok: 0, unknown: 0 };
  const statuses = entries.map(cas => {
    const s = casStatus(cas);
    counts[s.badge]++;
    return s;
  });

  let stats = '<div class="stats">';
  if (counts.warn) stats += `<span class="chip warn">⚠ ${counts.warn} chất cần Giấy phép</span>`;
  if (counts.ok) stats += `<span class="chip ok">✓ ${counts.ok} chất không cần Giấy phép XNK</span>`;
  if (counts.unknown) stats += `<span class="chip unknown">? ${counts.unknown} chất không có trong dữ liệu</span>`;
  // Chip rieng cho chat bi gan co: khong co no thi dong tom tat van dem chung vao
  // "chat khong can Giay phep" — canh bao nam trong bang ma tom tat lai noi nguoc.
  const flagged = entries.filter(cas => pl3FamilyHints(cas).length).length;
  if (flagged) stats += `<span class="chip warn">⚠ ${flagged} chất cần đối chiếu họ chất Phụ lục III</span>`;
  stats += "</div>";

  let table = `<div class="card">
    <p id="count">${heading}</p>
    ${hint}
    ${nameNote}
    ${stats}
    <div class="table-wrap"><table><tr><th>CAS</th><th>Tên chất</th><th>Phụ lục</th><th>Trạng thái</th></tr>`;
  entries.forEach((cas, i) => {
    const rows = rowsFor(cas);
    const name = rows.length ? rows[0].name_vn : "(không có trong dữ liệu)";
    const { badge, text: statusText } = statuses[i];
    // Co ho chat nam NGAY TRONG o trang thai, duoi pill: de o khoi canh bao cuoi
    // trang thi can bo doc xong dong xanh la di, khong cuon xuong.
    table += `<tr class="${badge}"><td class="cas">${esc(cas)}</td><td>${esc(name)}</td><td>${annexLabels(cas)}</td><td><span class="pill ${badge}">${esc(statusText)}</span>${hintHtml(cas)}</td></tr>`;
  });
  table += "</table></div>";

  let details = "";
  entries.forEach((cas, i) => {
    const rows = rowsFor(cas);
    // CAS khong co trong du lieu: khong co gi de noi ngoai dieu bang da noi
    // -> khong dung the chi tiet (bam ra rong thi con te hon la khong co).
    if (!rows.length) return;
    const annex = highestAnnex(cas);
    const { badge } = statuses[i];
    const title = `${cas} — ${rows[0].name_vn} (${rows[0].name_en})`;
    // Chi mo san chi tiet chat can chu y (do/vang); chat on thi thu gon.
    const open = badge === "ok" ? "" : " open";
    details += `<details class="detail"${open}><summary><span class="pill ${badge}">PL ${annex}</span> ${esc(title)}</summary><div class="body">${detailFor(cas)}</div></details>`;
  });

  resultsEl.innerHTML = table + details;
  resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

function clearAll() {
  document.getElementById("input").value = "";
  document.getElementById("results").innerHTML = "";
  document.getElementById("input").focus();
}

// Moi lan bam phai ra DU cac ket luan trang co the hien, khong pho mac may rui:
// boc 4 chat bat ky nhu truoc thi phan lon lan bam khong co chat Phu luc III nao
// (~250/1214 ma CAS) -> khong thay dong do, tuong trang chi biet bao "khong can".
// Moi bucket = mot nhanh hien thi khac nhau, khong phai chi khac verdict.
const EXAMPLE_BUCKETS = [
  a => a.has("III") && a.has("I"),                   // can Giay phep; khoi khai bao PL I bi an (Dieu 6.7.a)
  a => a.has("III") && !a.has("I"),                  // can Giay phep, chi khoi PL III
  a => a.has("II") && !a.has("I") && !a.has("III"),  // khong can Giay phep XNK — con nghia vu khac
  a => a.has("I") && !a.has("II") && !a.has("III"),  // khong can Giay phep XNK — chi khai bao
  a => a.size === 1 && a.has("IV"),                  // khong phat sinh yeu cau nhap khau rieng
];

// CAS that nhung ngoai Phu luc I-IV -> vi du luon co mot dong "Khong ro". Loc lai
// luc chay phong khi ban ND sau dua chat nao do vao Phu luc.
const OUTSIDE_DATA = [["Nước cất", "7732-18-5"], ["Natri clorua (muối ăn)", "7647-14-5"], ["Glycerin", "56-81-5"]];

function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

// Moi bucket mot chat, dung chung cho ca hai nut vi du.
function exampleRows() {
  const byCas = new Map();
  DATA.forEach(row => {
    if (!byCas.has(row.cas)) byCas.set(row.cas, { row, annexes: new Set() });
    byCas.get(row.cas).annexes.add(row.annex);
  });
  const entries = [...byCas.values()];
  const rows = [];
  for (const match of EXAMPLE_BUCKETS) {
    const pool = entries.filter(e => match(e.annexes));
    // Ten ngan doc giong khai bao that hon (nhieu ten_vn la ca cum ngoac dai
    // dong); van lay ten dai neu bucket khong con chat nao khac.
    const short = pool.filter(e => e.row.name_vn.length <= 30);
    if (pool.length) rows.push(pick(short.length ? short : pool).row);
  }
  return { rows, known: byCas };
}

function randomExampleForMode() {
  if (MODE === "cas") randomExample(); else randomNameExample();
}

function randomExample() {
  const { rows, known } = exampleRows();
  const items = rows.map(r => [r.name_vn, r.cas]);
  const outside = OUTSIDE_DATA.filter(([, cas]) => !known.has(cas));
  if (outside.length) items.push(pick(outside));
  // Xao tron de mo ta doc nhu khai bao that, khong phai danh sach xep theo phu luc.
  document.getElementById("input").value = "Hỗn hợp mẫu gồm: " +
    shuffle(items).map(([name, cas]) => `${name} (CAS ${cas})`).join(", ") + ".";
  run();
}

// Vi du mo ta DN KHONG kem ma CAS nao — nhanh do ten trong doan van. Khong co
// case "Khong ro" o day: chat ngoai du lieu thi khong co ten de do ra.
// extractCas de chac khong ten nao tu no chua chuoi dang CAS (se roi nhanh CAS).
function randomNameExample() {
  const names = shuffle(exampleRows().rows.map(r => r.name_vn).filter(n => !extractCas(n).length));
  document.getElementById("input").value = "Hỗn hợp mẫu gồm: " +
    names.slice(0, -1).join(", ") + " và " + names[names.length - 1] + " (doanh nghiệp không khai mã CAS).";
  run();
}

const inputEl = document.getElementById("input");
inputEl.addEventListener("keydown", e => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); run(); }
});
// Tu tra cuu ngay khi dan mo ta vao o (setTimeout de gia tri kip cap nhat).
inputEl.addEventListener("paste", () => setTimeout(run, 0));

// Link toi mot Dieu nam trong khoi toan van (dang <details> dong san) thi phai
// mo khoi ra roi moi cuon toi, khong trinh duyet nao cuon vao noi dung an duoc.
function openHash() {
  if (!location.hash) return;
  const el = document.querySelector(location.hash);
  if (!el) return;
  const d = el.tagName === "DETAILS" ? el : el.closest("details");
  if (d) d.open = true;
  el.scrollIntoView({ block: "start" });
}
addEventListener("hashchange", openHash);
openHash();
</script>
</body>
</html>
"""

out = (
    HTML.replace("__PL3_NO_CAS_HTML__", pl3_no_cas_html())
    .replace("__EXEMPTIONS_HTML__", exemptions_html())
    .replace("__FULL_TEXT_HTML__", full_text_html())
    .replace("__DATA_JSON__", DATA_JSON)
    .replace("__IMPORT_RULES_JSON__", IMPORT_RULES_JSON)
    .replace("__IMPORT_ANNEXES_JSON__", IMPORT_ANNEXES_JSON)
    .replace("__ANNEX_ORDER_JSON__", ANNEX_ORDER_JSON)
    .replace("__OTHER_OBLIGATION_ANNEXES_JSON__", OTHER_OBLIGATION_ANNEXES_JSON)
    .replace("__VERDICT_JSON__", VERDICT_JSON)
    .replace("__SUPPRESS_ANNEX_JSON__", SUPPRESS_ANNEX_JSON)
    .replace("__ANNEX_DISPLAY_ORDER_JSON__", ANNEX_DISPLAY_ORDER_JSON)
    .replace("__PL3_NO_CAS_JSON__", PL3_NO_CAS_JSON)
    .replace("__PL3_FAMILY_HINTS_JSON__", PL3_FAMILY_HINTS_JSON)
    .replace("__PL3_HINT_PREFIX_JSON__", PL3_HINT_PREFIX_JSON)
    .replace("__PL3_EXCLUDED_JSON__", PL3_EXCLUDED_JSON)
    .replace("__PL3_EXCLUDED_NOTE_JSON__", PL3_EXCLUDED_NOTE_JSON)
    .replace("__VERDICT_PL3__", core.VERDICT["pl3"])
)
Path(__file__).parent.joinpath("Tra-cuu-hoa-chat-ND24.html").write_text(out, encoding="utf-8")
print("Tra-cuu-hoa-chat-ND24.html written —", len(out), "bytes")
