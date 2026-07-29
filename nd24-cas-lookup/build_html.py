#!/usr/bin/env python3
"""Sinh Tra-cuu-hoa-chat-ND24.html — trang tra cứu offline, không cần terminal/Python để dùng.
Nhúng luôn data/nd24_chemicals.json + toàn bộ quy tắc từ core.py vào file
HTML nên chỉ cần double-click mở bằng trình duyệt là chạy được, kể cả
không có mạng.

Lấy quy tắc (VERDICT, EXEMPTIONS...) trực tiếp từ core.py (json.dumps)
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
OTHER_OBLIGATION_ANNEXES_JSON = json.dumps(core.OTHER_OBLIGATION_ANNEXES, ensure_ascii=False)
VERDICT_JSON = json.dumps(core.VERDICT, ensure_ascii=False)
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
    # Thu gọn được, nhưng TIÊU ĐỀ ĐỎ luôn hiện trong <summary>: khối này dài
    # (13 mục) mà lại nằm giữa kết quả và mục miễn trừ; gấp phần danh sách lại
    # thì vẫn không giấu mất lời cảnh báo.
    parts = [
        f'<details class="fold"><summary><h2>⚠ {esc(core.PL3_NO_CAS_TITLE)}</h2></summary>',
        f'<p class="lead">{esc(core.PL3_NO_CAS_LEAD)}</p>',
        '<p class="cite"><a href="#nd24-pl-iii">Mở nguyên văn Phụ lục III của NĐ 24</a>'
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
    parts.append("</details>")
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
            f"<summary>Toàn văn {esc(title)}</summary>"
            f'<div class="doc-body"><nav class="doc-toc">{links}</nav>{body}</div>'
            "</details>"
        )
    return "\n".join(parts)


def exemptions_html():
    parts = ['<h2>Quy định &amp; các trường hợp miễn trừ</h2>', '<p class="cite">Nghị định 26/2026/NĐ-CP</p>']
    for sect in core.EXEMPT_SECTIONS:
        parts.append(f'<h3 class="sect">{esc(sect["title"])}</h3>')
        parts.append('<p class="lead">Quy định</p>')
        parts.append("<ul>" + "".join(f"<li>{esc(item)}</li>" for item in sect["rule"]) + "</ul>")
        parts.append('<p class="lead">Trường hợp miễn trừ</p>')
        for group in core.EXEMPTIONS:
            if group["section"] != sect["key"]:
                continue
            parts.append(f'<h4>{esc(group["title"])} ({cite_link(group["cite"])})</h4>')
            if "lead" in group:
                parts.append(f'<p class="sub-lead">{esc(group["lead"])}</p>')
            parts.append("<ul>" + "".join(f"<li>{esc(item)}</li>" for item in group["items"]) + "</ul>")
    parts.append(f'<div class="warn-note">{esc(core.PENALTY_WARNING)}</div>')
    # Giấy của khâu KHÔNG phải xuất nhập khẩu — gộp một mục "Quy định khác", gấp
    # sẵn: cán bộ đứng ở khâu thông quan không cần tới, nhưng vẫn phải tra được.
    parts.append(
        f'<details class="fold"><summary><h2>{esc(core.OTHER_SECTION_TITLE)}</h2></summary>'
    )
    for title, items in (
        (core.OTHER_OBLIGATIONS_TITLE, core.OTHER_OBLIGATIONS),
        (core.OTHER_EXEMPTIONS_TITLE, core.OTHER_EXEMPTIONS),
    ):
        parts.append(f'<h3 class="sect">{esc(title)}</h3>')
        parts.append("<ul>" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>")
    parts.append("</details>")
    return "\n  ".join(parts)


HTML = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tra cứu hóa chất – NĐ 24 &amp; 26/2026/NĐ-CP</title>
<style>
  /* ===== Hệ màu công vụ: một màu chủ đạo xanh mực (navy) cho giao diện;
     đỏ/vàng/xanh lá CHỈ dành cho kết luận (verdict), không dùng trang trí. ===== */
  :root {
    --navy: #123a63; --navy-deep: #0c2743; --navy-tint: #eef2f8;
    --ink: #16212e; --muted: #566270; --faint: #8a95a3;
    --line: #dce2ea; --line-strong: #c3ccd7;
    --bg: #eceff4; --paper: #ffffff;

    --red: #9c261a; --red-bg: #fbeae7; --red-line: #e8b4ab;
    --green: #1d7442; --green-bg: #e7f3eb; --green-line: #afd7bc;
    --amber: #856310; --amber-bg: #faf1d7; --amber-line: #e3cc8b;

    --r-card: 10px; --r-ctrl: 7px; --r-tag: 6px;
    --shadow: 0 1px 2px rgba(16,32,54,.05), 0 8px 24px -14px rgba(16,32,54,.2);
    --focus: 0 0 0 3px rgba(18,58,99,.22);
  }
  * { box-sizing: border-box; }
  html { -webkit-text-size-adjust: 100%; }
  body {
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    max-width: 900px; margin: 0 auto; padding: 44px 24px 104px;
    color: var(--ink); background: var(--bg); line-height: 1.6; font-size: 16px;
    -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
  }
  ::selection { background: #cadcef; }
  a { color: var(--navy); }
  :focus-visible { outline: 2px solid var(--navy); outline-offset: 2px; }

  /* ---- Masthead công vụ: canh trái, dấu gạch navy như văn bản chính thống ---- */
  header { margin-bottom: 28px; padding-bottom: 22px; border-bottom: 1px solid var(--line); }
  header::before { content: ""; display: block; width: 42px; height: 4px; border-radius: 2px; background: var(--navy); margin-bottom: 18px; }
  h1 { font-size: 2rem; line-height: 1.1; margin: 0 0 6px; letter-spacing: -0.022em; font-weight: 800; }
  header .sub { margin: 0; color: var(--muted); font-size: 1rem; font-variant-numeric: tabular-nums; }
  header .author { margin: 14px 0 0; font-size: 0.82rem; font-weight: 600; color: var(--navy-deep); }
  header .docs { margin: 5px 0 0; font-size: 0.82rem; color: var(--muted); }
  header .docs a { color: var(--navy); text-decoration: none; border-bottom: 1px solid rgba(18,58,99,.32); padding-bottom: 1px; }
  header .docs a:hover { border-bottom-color: var(--navy); }

  /* ---- Panel ---- */
  .card { background: var(--paper); border: 1px solid var(--line); border-radius: var(--r-card); padding: 22px 24px; margin-bottom: 20px; box-shadow: var(--shadow); }

  .instructions h2 { margin: 0 0 10px; font-size: 1.02rem; font-weight: 700; }
  .instructions ol { margin: 0; padding-left: 22px; }
  .instructions li { margin-bottom: 6px; text-align: justify; }
  .instructions ul { margin: 6px 0 2px; padding-left: 20px; }
  .instructions b { color: var(--ink); }

  /* ---- Ô nhập ---- */
  .modes { display: inline-flex; gap: 4px; padding: 4px; background: var(--navy-tint); border: 1px solid var(--line); border-radius: var(--r-ctrl); margin-bottom: 14px; max-width: 100%; }
  .mode-btn { cursor: pointer; font-size: 0.92rem; font-weight: 600; padding: 8px 18px; border-radius: 5px; border: 1px solid transparent; background: transparent; color: var(--muted); transition: color .15s, background .15s, box-shadow .15s; }
  .mode-btn:hover { color: var(--navy); }
  .mode-btn:active { transform: translateY(1px); }
  .mode-btn.active { background: var(--paper); border-color: var(--line); color: var(--navy-deep); box-shadow: 0 1px 2px rgba(16,32,54,.09); }

  .input-row { display: flex; gap: 14px; align-items: stretch; }
  textarea { flex: 1; min-height: 128px; font-size: 1rem; padding: 14px 16px; border: 1px solid var(--line-strong); border-radius: var(--r-ctrl); resize: vertical; font-family: inherit; line-height: 1.55; color: var(--ink); background: #fff; }
  textarea::placeholder { color: var(--faint); }
  textarea:focus { outline: none; border-color: var(--navy); box-shadow: var(--focus); }
  button#run-btn { flex: 0 0 auto; align-self: stretch; min-width: 150px; font-size: 1rem; font-weight: 700; cursor: pointer; background: var(--navy); color: #fff; border: 1px solid var(--navy); border-radius: var(--r-ctrl); padding: 12px 24px; transition: background .15s, transform .05s; }
  button#run-btn:hover { background: var(--navy-deep); }
  button#run-btn:active { transform: translateY(1px); }
  .toolbar { display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap; align-items: center; }
  .toolbar .hint { color: var(--faint); font-size: 0.82rem; margin-left: auto; }
  .toolbar kbd { font: inherit; font-size: 0.78rem; font-weight: 700; background: var(--navy-tint); border: 1px solid var(--line-strong); border-bottom-width: 2px; border-radius: 4px; padding: 1px 6px; color: var(--navy-deep); }
  button.mini { font-size: 0.86rem; cursor: pointer; background: #fff; color: var(--navy-deep); border: 1px solid var(--line-strong); border-radius: var(--r-ctrl); padding: 7px 14px; font-weight: 600; transition: background .15s, border-color .15s, transform .05s; }
  button.mini:hover { border-color: var(--navy); background: var(--navy-tint); }
  button.mini:active { transform: translateY(1px); }

  /* Nhãn ẩn cho screen-reader: ô nhập phải có <label> thật, không mượn placeholder. */
  .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }
  @media (max-width: 560px) {
    body { padding: 30px 16px 92px; }
    h1 { font-size: 1.58rem; }
    .input-row { flex-direction: column; }
    button#run-btn { padding: 13px; }
    .toolbar .hint { display: none; }
  }

  /* ---- Kết quả ---- */
  #results > .card { animation: rise .3s cubic-bezier(.16,1,.3,1) both; }
  @keyframes rise { from { opacity: 0; transform: translateY(6px); } }
  @media (prefers-reduced-motion: reduce) { #results > .card { animation: none; } }

  #count { margin: 0; font-weight: 700; font-size: 1.05rem; color: var(--ink); }
  .stats { display: flex; gap: 8px; flex-wrap: wrap; margin: 14px 0 2px; }
  .chip { display: inline-flex; align-items: center; padding: 5px 12px; border-radius: var(--r-tag); font-size: 0.84rem; font-weight: 700; border: 1px solid transparent; }
  .chip.warn { background: var(--red-bg); border-color: var(--red-line); color: var(--red); }
  .chip.ok { background: var(--green-bg); border-color: var(--green-line); color: var(--green); }
  .chip.unknown { background: var(--amber-bg); border-color: var(--amber-line); color: var(--amber); }

  /* overflow:auto + max-height -> tờ khai dài cuộn trong khung riêng, và thead
     dính đỉnh khung để cán bộ luôn thấy tên cột khi soi 50 dòng. */
  .table-wrap { overflow: auto; max-height: 78vh; margin: 16px -4px 0; padding: 0 4px; }
  table { border-collapse: collapse; width: 100%; min-width: 620px; }
  th, td { padding: 12px 12px; text-align: left; vertical-align: top; font-size: 0.93rem; border-bottom: 1px solid var(--line); }
  thead th { position: sticky; top: 0; z-index: 1; background: var(--paper); color: var(--muted); font-weight: 700; font-size: 0.72rem; text-transform: uppercase; letter-spacing: .07em; border-bottom: 1.5px solid var(--line-strong); box-shadow: 0 1px 0 var(--line-strong); }
  tbody tr:last-child td { border-bottom: none; }
  /* Nham theo class chu KHONG theo :first-child/:nth-child — dong hang co nhieu
     ma CAS bi tach thanh nhieu <tr>, o STT/Mo ta dung rowspan nen tu hang thu 2
     tro di first-child lai la o ma CAS. */
  th:first-child, td.stt { width: 1%; white-space: nowrap; text-align: right; color: var(--muted); font-variant-numeric: tabular-nums; }
  td.mota { min-width: 190px; }
  td:last-child { min-width: 230px; }
  tr.warn td { background: var(--red-bg); }
  tr.ok td { background: var(--green-bg); }
  tr.unknown td { background: var(--amber-bg); }
  tr.warn td.stt { box-shadow: inset 3px 0 0 var(--red); }
  tr.ok td.stt { box-shadow: inset 3px 0 0 var(--green); }
  tr.unknown td.stt { box-shadow: inset 3px 0 0 var(--amber); }
  /* Tren dien thoai bang (min-width 620px) phai cuon ngang moi doc duoc cot Ket
     luan, luc do cot ma CAS troi han khoi man hinh -> khong biet ket luan nao la
     cua ma nao. Ghim cot ma: left:0 chi bat khi o sap troi qua mep trai, con o
     man hinh rong thi van nam dung cho cu. Nen o duc (hex, khong alpha) nen cot
     Mo ta cuon xuong duoi khong loi qua. */
  th.match, td.match { position: sticky; left: 0; z-index: 1; box-shadow: 6px 0 7px -6px rgba(16,32,54,.3); }
  thead th.match { z-index: 2; }
  .match-inline { display: none; }
  /* Man hep: bang 4 cot khong vua dien thoai. Do o 375px, luc moi mo bang chi
     thay 25% cot Ket luan (34/137px) — dung cot chu cai dung — phai cuon ngang
     107px moi doc duoc thu quan trong nhat. Ghim cot ma chi cuu duoc "ma nao ung
     voi ket luan nao", khong cuu duoc chuyen do. Nen duoi 700px bo han cot ma
     rieng va in ma ngay dau o Ket luan: con 3 cot, bang co vua khung (min-width
     0 -> het cuon ngang), ma van dinh lien ket luan. */
  @media (max-width: 700px) {
    table { min-width: 0; }
    /* Chia lai cho hep: Ket luan la thu can doc nen uu tien be ngang cho no,
       Mo ta chi de doi chieu (van con nguyen trong o nhap). */
    th, td { padding: 11px 8px; }
    td.mota { min-width: 0; }
    td:last-child { min-width: 0; width: 52%; }
    th.match, td.match { display: none; }
    .match-inline { display: block; margin-bottom: 5px; }
  }
  .cas { font-weight: 700; font-variant-numeric: tabular-nums; white-space: nowrap; color: var(--navy-deep); }
  .pill { display: inline-block; margin: 1px 0; padding: 4px 11px; border-radius: var(--r-tag); font-size: 0.8rem; font-weight: 700; line-height: 1.35; }
  .pill.warn { background: var(--red); color: #fff; }
  .pill.ok { background: var(--green); color: #fff; }
  .pill.unknown { background: var(--amber); color: #fff; }

  .exempt h2 { font-size: 1.18rem; margin: 0 0 6px; letter-spacing: -0.01em; }
  .exempt h3 { font-size: 0.96rem; margin: 18px 0 6px; color: var(--navy-deep); }
  .exempt ul { margin: 6px 0 0; padding-left: 22px; }
  .exempt li { margin-bottom: 6px; text-align: justify; }
  .exempt .lead, .exempt .warn-note { text-align: justify; }
  .exempt .warn-note { background: var(--red-bg); border: 1px solid var(--red-line); border-radius: var(--r-ctrl); padding: 12px 16px; margin-top: 16px; color: var(--red); font-size: 0.93rem; }
  .exempt .warn-note + details.fold { margin-top: 22px; padding-top: 18px; border-top: 1px solid var(--line-strong); }
  .exempt .cite { color: var(--muted); font-size: 0.84rem; }
  .exempt .lead { font-weight: 600; margin: 8px 0 4px; }
  /* Hai mục lớn (khai báo / giấy phép) phải tách hẳn nhau: đọc nhầm mục là áp
     nhầm ngưỡng miễn trừ của giấy phép sang khai báo. */
  .exempt h3.sect { font-size: 1.06rem; color: var(--ink); margin: 26px 0 8px; padding-top: 16px; border-top: 1px solid var(--line-strong); }
  .exempt h3.sect + .lead, .exempt ul + .lead { color: var(--navy); text-transform: uppercase; font-size: 0.75rem; letter-spacing: .07em; font-weight: 700; margin-top: 14px; }
  .exempt h4 { font-size: 0.93rem; margin: 14px 0 4px; color: var(--navy-deep); }
  .exempt .sub-lead { font-weight: 600; margin: 4px 0; text-align: justify; }

  /* Ghi chú "Ngoại trừ": thông tin, không phải cảnh báo -> nền xanh nhạt trung
     tính, để không tranh chỗ với cờ đỏ họ chất vốn mới là thứ cần chú ý. */
  .excl-note { margin-top: 10px; background: var(--navy-tint); border: 1px solid var(--line); border-radius: var(--r-tag); padding: 9px 12px; color: var(--muted); font-size: 0.79rem; text-align: left; font-weight: 400; }
  .excl-note b, .excl-note strong { color: var(--navy-deep); }

  /* Cờ họ chất: nằm trong ô trạng thái, phải "cãi lại" được pill xanh ngay
     cạnh nó nên dùng nền/viền đỏ, không phải chữ xám mờ. */
  .fam-hint { margin-top: 8px; background: var(--red-bg); border: 1px solid var(--red-line); border-radius: var(--r-tag); padding: 9px 12px; color: var(--red); font-size: 0.81rem; font-weight: 600; text-align: left; }
  .fam-hint ul { margin: 4px 0 0; padding-left: 18px; font-weight: 400; }
  .fam-hint .cite { color: var(--red); opacity: .82; font-size: 0.76rem; }
  /* Link sang toàn văn nằm trong khối đã có màu riêng -> giữ nguyên màu chữ của
     khối, chỉ gạch chân, để không phá tương phản cảnh báo. */
  .fam-hint a, .blind-spot a, td a { color: inherit; text-decoration: underline; text-underline-offset: 2px; }

  /* Cảnh báo vùng mù: nền đỏ đậm hơn để không bị đọc lướt như chú thích thường —
     đây là chỗ trang có thể im lặng bỏ sót chất cần Giấy phép. */
  .blind-spot { border-color: var(--red-line); background: linear-gradient(var(--paper), var(--paper)) padding-box, var(--paper); }
  .blind-spot h2 { color: var(--red); }
  .blind-spot .lead { font-weight: 400; background: var(--red-bg); border: 1px solid var(--red-line); border-radius: var(--r-ctrl); padding: 12px 16px; margin: 8px 0 4px; }
  .blind-spot li { font-size: 0.9rem; }
  details.fold > summary { cursor: pointer; list-style: none; display: flex; align-items: baseline; gap: 10px; }
  details.fold > summary::-webkit-details-marker { display: none; }
  details.fold > summary::before { content: "\\203A"; font-size: 1.3em; line-height: 1; color: var(--red); transition: transform .15s; }
  details.fold[open] > summary::before { transform: rotate(90deg); }
  details.fold > summary h2 { display: inline; }

  /* Toàn văn hai nghị định — nhúng thẳng vào trang để không phải mở file .docx
     rời (trang vẫn là 1 file chạy offline). Đóng sẵn, mở khi cần đọc. */
  details.doc { background: var(--paper); border: 1px solid var(--line); border-radius: var(--r-card); margin-bottom: 20px; box-shadow: var(--shadow); }
  details.doc > summary { cursor: pointer; padding: 18px 24px; font-weight: 700; color: var(--navy-deep); list-style: none; display: flex; align-items: center; gap: 10px; }
  details.doc > summary::-webkit-details-marker { display: none; }
  details.doc > summary::before { content: "\\203A"; font-size: 1.3em; color: var(--navy); transition: transform .15s; }
  details.doc[open] > summary::before { transform: rotate(90deg); }
  details.doc .doc-body { padding: 4px 24px 22px; border-top: 1px solid var(--line); }
  details.doc .doc-toc { font-size: 0.8rem; color: var(--muted); margin: 16px 0 20px; line-height: 2; }
  details.doc .doc-toc a { color: var(--navy); text-decoration: none; }
  details.doc .doc-toc a:hover { text-decoration: underline; }
  details.doc h3 { font-size: 1rem; color: var(--navy-deep); margin: 22px 0 6px; scroll-margin-top: 12px; }
  details.doc h4 { font-size: 0.9rem; margin: 14px 0 6px; }
  details.doc p { font-size: 0.9rem; text-align: justify; margin: 6px 0; }
  details.doc td, details.doc th { font-size: 0.82rem; padding: 6px 9px; text-transform: none; }
  details.doc :target { background: #fdf1c7; box-shadow: 0 0 0 4px #fdf1c7; border-radius: 2px; }

  /* Nút nổi góc phải: toàn văn dài mấy nghìn dòng, cuộn ngược lên tìm lại thẻ
     <summary> để đóng là không khả thi. */
  .fab { position: fixed; right: 18px; bottom: 18px; display: flex; flex-direction: column; gap: 8px; align-items: flex-end; z-index: 20; }
  .fab button { cursor: pointer; font-size: 0.84rem; font-weight: 600; padding: 10px 15px; border-radius: var(--r-ctrl); border: 1px solid var(--line-strong); background: var(--paper); color: var(--navy-deep); box-shadow: 0 6px 18px -6px rgba(16,32,54,.35); transition: background .15s, border-color .15s; }
  .fab button:hover { border-color: var(--navy); background: var(--navy-tint); }
  .fab button[hidden] { display: none; }

  .note { color: var(--muted); font-size: 0.88rem; text-align: justify; }
  footer { text-align: center; color: var(--faint); font-size: 0.82rem; margin-top: 40px; padding-top: 22px; border-top: 1px solid var(--line); }

  @media print {
    body { background: #fff; padding: 0; max-width: none; color: #000; }
    .instructions, #input-card, footer, .fab, header::before { display: none; }
    .card, details.doc { box-shadow: none; border-color: #999; break-inside: avoid; }
    header { border-color: #000; }
    .table-wrap { max-height: none; overflow: visible; }
    thead th, th.match, td.match { position: static; box-shadow: none; }
    tr.warn td.stt, tr.ok td.stt, tr.unknown td.stt { box-shadow: none; }
    .pill { border: 1px solid #666; color: #000 !important; background: #fff !important; }
  }
</style>
</head>
<body>

<header>
  <h1>Tra cứu hóa chất</h1>
  <p class="sub">Nghị định 24/2026/NĐ-CP · Nghị định 26/2026/NĐ-CP</p>
  <p class="author">Tác giả: Nguyễn Hoàng Long - HQ KCX&amp;KCN</p>
  <p class="docs">Toàn văn: <a href="#doc-nd24">NĐ 24/2026/NĐ-CP</a> · <a href="#doc-nd26">NĐ 26/2026/NĐ-CP</a></p>
</header>

<div class="card instructions">
  <h2>Hướng dẫn sử dụng</h2>
  <ol>
    <li>Copy nguyên mô tả hàng hóa — <b>mỗi dòng một dòng hàng</b> (dán thẳng từ Excel được), hoặc một đoạn. Không cần tách tay từng mã CAS.</li>
    <li>Dán vào ô bên dưới rồi bấm <b>Tra cứu</b>. Kết quả là bảng theo từng dòng hàng, hai chế độ tra:
      <ul>
        <li><b>Tìm theo mã CAS</b> (mặc định): mỗi dòng tra theo mọi mã CAS xuất hiện trong dòng đó. Chính xác nhất.</li>
        <li><b>Tìm theo tên chất</b>: mỗi dòng dò tên hóa chất có trong mô tả. Dùng khi không khai mã CAS — kết quả chỉ là gợi ý, xem cảnh báo trong bảng.</li>
      </ul>
    </li>
    <li>Kiểm tra các trường hợp miễn trừ Khai báo hóa chất và miễn trừ Giấy phép xuất khẩu, nhập khẩu ở bên dưới.</li>
  </ol>
</div>

<div class="card" id="input-card">
  <div class="modes" role="group" aria-label="Chế độ tra cứu">
    <button class="mode-btn active" id="mode-cas" aria-pressed="true" onclick="setMode('cas')">Tìm theo mã CAS</button>
    <button class="mode-btn" id="mode-name" aria-pressed="false" onclick="setMode('name')">Tìm theo tên chất</button>
  </div>
  <label for="input" class="sr-only">Mô tả hàng hóa cần tra cứu</label>
  <div class="input-row">
    <textarea id="input" placeholder="Dán mô tả hàng hóa — mỗi dòng một dòng hàng (copy từ Excel được), hoặc một đoạn. Ví dụ:&#10;1&#9;Dung môi công nghiệp CAS 67-56-1&#10;2&#9;Keo dán, thùng 20kg&#10;3&#9;Hỗn hợp 107-13-1 và 103-79-7"></textarea>
    <button id="run-btn" onclick="run()">Tra cứu</button>
  </div>
  <div class="toolbar">
    <button class="mini" onclick="randomExampleForMode()">Ví dụ ngẫu nhiên</button>
    <button class="mini" onclick="clearAll()">Xóa</button>
    <span class="hint">Mẹo: <kbd>Ctrl</kbd>+<kbd>Enter</kbd> (<kbd>⌘</kbd>+<kbd>Enter</kbd> trên Mac) để tra nhanh</span>
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

<div class="fab">
  <button id="fab-collapse" onclick="collapseDocs()" hidden>Thu gọn toàn văn</button>
  <button id="fab-top" onclick="goTop()" hidden>↑ Lên đầu trang</button>
</div>

<footer>Bản tóm tắt để tra cứu nhanh — luôn đối chiếu điều luật gốc trước khi ra quyết định thông quan.</footer>

<script>
const DATA = __DATA_JSON__;
const OTHER_OBLIGATION_ANNEXES = __OTHER_OBLIGATION_ANNEXES_JSON__;
const VERDICT = __VERDICT_JSON__;
const PL3_NO_CAS = __PL3_NO_CAS_JSON__;
const PL3_FAMILY_HINTS = __PL3_FAMILY_HINTS_JSON__;
const PL3_HINT_PREFIX = __PL3_HINT_PREFIX_JSON__;
const PL3_EXCLUDED = __PL3_EXCLUDED_JSON__;
const PL3_EXCLUDED_NOTE = __PL3_EXCLUDED_NOTE_JSON__;

// Doi xung voi CAS_RE trong core.py — lookbehind thay \\b dau ma de bat "CAS78-93-3"
// viet dinh lien. Lookbehind la ES2018, trang nay da dung matchAll (ES2020) roi.
const CAS_RE = /(?<!\\d)\\d{2,7}-\\d{2}-\\d\\b/g;

function rowsFor(cas) {
  return DATA.filter(r => r.cas === cas);
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
  // toLowerCase TRUOC roi moi đ->d: chu "Đ" hoa (U+0110) khong khop /đ/ thuong,
  // neu doi truoc thi no thoat, toLowerCase thanh "đ", roi normWords xoa "đ" (ngoai
  // [a-z]) -> "Đồng" ra "ong", khop nham "Ống nhua". Ha bac xuong truoc la sach.
  return s.normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").toLowerCase().replace(/đ/g, "d");
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
      // chat tuong ung", "... and its salts") va ngoac O CUOI ten ("Selen (dạng
      // bột)"): DN khai ten thuong mai, khong ai khai kem duoi cua nghi dinh.
      // BAT BUOC, khong phai tien nghi: thieu no thi "N,N-dimetyl amino etanol"
      // (108-01-0, PL II) khong khop ten day du roi tut xuong khop chu "etanol"
      // nam trong doan -> bao ra Etanol (64-17-5, PL I). Sai chat, va giau mat
      // nghia vu Giay chung nhan SX-KD cua chat that.
      // CHI bo ngoac O CUOI: "Đồng (I) clorua" co ngoac GIUA ten, bo di con moi
      // "Đồng" -> khop nham "đóng/đông/dòng/động" (deu chuan hoa ra "dong"). Giu
      // nguyen "(I) clorua" -> alias "dong i clorua", khong dinh tu thuong.
      const head = name.replace(/ (?:và|and) .*$/i, "").replace(/\\s*\\([^)]*\\)\\s*$/, "").trim();
      for (const alias of [name, head]) {
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

// Goc muoi/oxit: ten nguyen to don ("Natri") dung NGAY TRUOC mot trong cac tu nay
// la HOP CHAT ("natri clorua" = muoi an), khong phai nguyen to Natri (7440-23-5).
// ponytail: danh sach goc muoi thong dung, khong phu het; hop chat CO trong du
// lieu van khop nguyen ten (dai hon) truoc nen khong bi anh huong.
const ANION_SUFFIX = new Set(["clorua","oxit","dioxit","trioxit","peroxit","hydroxit",
  "hidroxit","sulfat","sunfat","sulfit","sunfit","cacbonat","carbonat","bicacbonat",
  "bicarbonat","hydrocacbonat","nitrat","nitrit","photphat","phosphat","phosphit",
  "silicat","borat","cromat","dicromat","permanganat","xyanua","xianua","sunfua",
  "sulfua","bromua","iotua","iodua","florua","clorat","peclorat","hypoclorit","axetat",
  "acetat","oxalat","stearat","benzoat","citrat","lactat","gluconat","thiosunfat"]);

// Ten hoa chat XUAT HIEN trong doan van, theo thu tu gap (doi xung extractCas).
function scanNames(text) {
  let hay = normWords(text);
  const hits = [];
  for (const { n, cas } of NAME_INDEX) {
    const i = hay.indexOf(" " + n + " ");
    if (i === -1) continue;
    // Ten mot tu ma tu ke sau la goc muoi -> la hop chat, khong bao nguyen to.
    if (!n.includes(" ")) {
      const rest = hay.slice(i + n.length + 2);
      const sp = rest.indexOf(" ");
      if (ANION_SUFFIX.has(sp === -1 ? rest : rest.slice(0, sp))) continue;
    }
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

// Hai che do TUONG MINH thay vi tu doan: can bo chon tra theo gi. Truoc day dò
// ten chi chay khi doan KHONG co ma CAS nao -> mo ta tron (vai chat khai ma, vai
// chat chi ghi ten) thi cac chat ghi ten bi bo qua IM LANG. Nay chon che do nao
// ra dung thu do, va che do con lai duoc nhac den khi doan co du lieu cho no.
let MODE = "cas";
const MODES = ["cas", "name"];
const MODE_PLACEHOLDER = {
  cas: "Dán mô tả hàng hóa — MỖI DÒNG LÀ MỘT DÒNG HÀNG (copy thẳng từ Excel được), hoặc một đoạn. Tra theo MÃ CAS. Ví dụ:\\n1\\tDung môi công nghiệp CAS 67-56-1\\n2\\tKeo dán, thùng 20kg\\n3\\tHỗn hợp 107-13-1 và 103-79-7",
  name: "Dán mô tả hàng hóa — MỖI DÒNG LÀ MỘT DÒNG HÀNG. Tra theo TÊN chất (khi doanh nghiệp không khai mã CAS). Ví dụ:\\n1\\tHỗn hợp dung môi gồm Metanol và Toluene\\n2\\tKeo dán công nghiệp",
};

function setMode(mode) {
  MODE = mode;
  for (const m of MODES) {
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

// ===== Moi DONG VAT LY = mot dong hang cua to khai. Ca hai che do (theo ma CAS
// va theo ten) deu doc theo dong nay; khac nhau o CHO LAY GI DE TRA moi dong:
// mode "cas" tra ma CAS trich trong dong, mode "name" tra ten chat do trong mo ta.
// Khong them quy tac phap ly nao: verdict luon di qua casStatus() nhu cu.
function parseLines(text) {
  const out = [];
  for (const raw of text.split("\\n")) {
    const line = raw.replace(/\\s+$/, "");
    if (!line.trim()) continue;
    // STT: "1<tab>", "1. " hoac "1) " dau dong. Sau dau "." / ")" bat buoc co
    // khoang trang de khong cat nham ten hoa chat kieu "2.4-D", "1.1.1-...".
    const m = line.match(/^\\s*(\\d{1,4})(?:[.)]\\s+|\\t\\s*)/);
    out.push({
      stt: m ? Number(m[1]) : null,
      mota: (m ? line.slice(m[0].length) : line).replace(/\\t/g, " ").trim(),
      cas: extractCas(line),
    });
  }
  return out;
}

// Dong khong tra duoc gi KHONG duoc ra xanh: ca to khai 50 dong se xanh het trong
// khi chua tra duoc gi. Trang thai rieng, mau vang, chu theo tung truc.
const NO_CAS_STATUS = { badge: "unknown", text: "Không thấy mã CAS — tự kiểm tra" };
const NO_NAME_STATUS = { badge: "unknown", text: "Không khớp tên trong dữ liệu — tự kiểm tra" };
// Nang nhat truoc: PL III > CAS la (chua ket luan duoc) > khong can giay phep.
const LINE_BADGE_ORDER = ["warn", "unknown", "ok"];
// Mode ten co the khop thua khi mo ta 1 tu ("axit") -> chan dong khong lan man.
const LINE_MATCH_CAP = 15;

function heaviestStatus(casList, emptyStatus) {
  if (!casList.length) return emptyStatus;
  const all = casList.map(casStatus);
  for (const b of LINE_BADGE_ORDER) {
    const hit = all.find(s => s.badge === b);
    if (hit) return hit;
  }
  return all[0];
}

// Chat lay ra de tra moi dong, theo truc dang chon.
function lineMatches(entry, byName) {
  const all = byName ? searchByName(entry.mota) : entry.cas;
  return all.slice(0, LINE_MATCH_CAP);
}

// Mode CAS: ten chat doc duoc trong dong nhung KHONG kem ma CAS -> co vang, KHONG
// doi verdict cua dong (dò ten khop thua duoc, xem gioi han o README).
function lineNameHint(entry) {
  const named = scanNames(entry.mota).filter(cas => !entry.cas.includes(cas));
  if (!named.length) return "";
  const names = [...new Set(named.map(cas => rowsFor(cas)[0].name_vn))].slice(0, 5);
  return `<div class="fam-hint">⚠ Mô tả có nhắc tên hóa chất trong dữ liệu nhưng KHÔNG kèm mã CAS: ${esc(names.join(", "))}. Kết luận trên chỉ tính theo mã CAS — chuyển sang <b>Tìm theo tên chất</b> để tra riêng.</div>`;
}

// Mode ten: dong co ma CAS thi che do nay bo qua (tra theo ten) -> nhac chuyen mode.
function lineCasHint(entry) {
  if (!entry.cas.length) return "";
  return `<div class="fam-hint">⚠ Dòng có mã CAS (${esc(entry.cas.join(", "))}) — chế độ tra theo tên bỏ qua. Chuyển sang <b>Tìm theo mã CAS</b> để tra theo mã.</div>`;
}

function runLines(text, resultsEl, mode) {
  const byName = mode === "name";
  const lines = parseLines(text);
  if (!lines.length) {
    resultsEl.innerHTML = `<div class="card"><p class="note">Chưa có dòng hàng nào. Dán mô tả hàng hóa vào ô trên — mỗi dòng một dòng hàng.</p></div>`;
    return;
  }
  const emptyStatus = byName ? NO_NAME_STATUS : NO_CAS_STATUS;
  const per = lines.map(l => {
    const matches = lineMatches(l, byName);
    return { l, matches, status: heaviestStatus(matches, emptyStatus) };
  });
  const counts = { warn: 0, unknown: 0, ok: 0 };
  per.forEach(p => counts[p.status.badge]++);
  const noMatch = per.filter(p => !p.matches.length).length;

  let stats = '<div class="stats">';
  if (counts.warn) stats += `<span class="chip warn">⚠ ${counts.warn}/${lines.length} dòng hàng cần Giấy phép XNK</span>`;
  if (noMatch) stats += `<span class="chip unknown">? ${noMatch} dòng ${byName ? "không khớp tên nào" : "không thấy mã CAS"}</span>`;
  // Mode CAS con case ma CAS ngoai du lieu (khac han dong khong co ma); mode ten
  // thi ten khop luon nam trong du lieu nen unknownIn = 0. Tach chip cho tong = so dong.
  const unknownIn = counts.unknown - noMatch;
  if (unknownIn) stats += `<span class="chip unknown">? ${unknownIn} dòng có mã CAS ngoài dữ liệu</span>`;
  if (counts.ok) stats += `<span class="chip ok">✓ ${counts.ok} dòng không cần Giấy phép XNK</span>`;
  stats += "</div>";

  // Dan tu Excel, o mo ta dai co the bi xuong dong -> vo dong hang. Khong sua ho
  // duoc (khong biet dong nao la phan tiep), nhung STT dut quang thi bao de tu soi.
  let sttNote = "";
  const stts = lines.map(l => l.stt).filter(v => v !== null);
  if (stts.length >= 2 && stts.length < lines.length) {
    sttNote = `<p class="note">⚠ ${lines.length - stts.length}/${lines.length} dòng không bắt được STT — nếu dán từ Excel, ô mô tả dài có thể đã bị xuống dòng và tách thành nhiều dòng hàng. Kiểm tra lại trước khi dùng kết quả.</p>`;
  } else if (stts.length && stts.some((v, i) => i && v !== stts[i - 1] + 1)) {
    sttNote = `<p class="note">⚠ STT không liên tục — có thể mô tả bị xuống dòng hoặc thiếu dòng hàng. Kiểm tra lại trước khi dùng kết quả.</p>`;
  }

  // Tra theo ten khop thua/thieu -> canh bao thang, khong de doc bang thanh "ca lo
  // chi co bay nhieu chat"; dong "khong khop ten" KHONG dong nghia khong can giay.
  const nameNote = byName
    ? `<p class="note"><b>Chỉ là gợi ý theo tên — không thay cho mã CAS.</b> Cột "Chất khớp tên" chỉ dò tên có trong dữ liệu NĐ 24 nằm trong mô tả; chất mang tên khác hoặc ngoài Phụ lục I–IV sẽ KHÔNG hiện, nên dòng "không khớp tên" <b>không</b> có nghĩa là hàng không cần giấy phép. Tên ghép cũng có thể khớp thừa (mô tả "natri clorua" khớp ra "Natri"). Luôn đối chiếu mã CAS trên tài liệu khai báo gốc.</p>`
    : "";

  const matchHead = byName ? "Chất khớp tên" : "Mã CAS";
  let table = `<div class="card">
    <p id="count">Đọc được ${lines.length} dòng hàng</p>
    ${nameNote}
    ${sttNote}
    ${stats}
    <div class="table-wrap"><table><thead><tr><th>STT</th><th>Mô tả</th><th class="match">${matchHead}</th><th>Kết luận</th></tr></thead><tbody>`;
  per.forEach((p, i) => {
    const { l, matches, status } = p;
    const short = l.mota.length > 90 ? l.mota.slice(0, 90) + "…" : l.mota;
    // Moi ma CAS mot <tr> rieng, STT/Mo ta rowspan -> ma va ket luan cua no LUON
    // cung hang ngang. Truoc day noi bang <br>: khoi ghi chu (excl-note/fam-hint)
    // trong o ket luan day cac pill sau xuong, tu ma thu 2 la lech han khoi ma.
    const sub = matches.length
      ? matches.map(c => {
          const s = casStatus(c);
          const label = byName ? esc((rowsFor(c)[0] || {}).name_vn || c) : esc(c);
          // Ban thu hai cua nhan, an tren desktop, hien khi man hep an cot rieng.
          return {
            match: label,
            concl: `<span class="match-inline${byName ? "" : " cas"}">${label}</span>`
              + `<span class="pill ${s.badge}">${esc(s.text)}</span>${hintHtml(c)}`,
          };
        })
      : [{ match: "—", concl: `<span class="pill ${status.badge}">${esc(status.text)}</span>` }];
    // Ghi chu cap dong hang (khong thuoc ma nao) -> gan o hang cuoi cua nhom.
    sub[sub.length - 1].concl += byName ? lineCasHint(l) : lineNameHint(l);
    sub.forEach((s, j) => {
      table += `<tr class="${status.badge}">`
        + (j === 0
            ? `<td class="stt" rowspan="${sub.length}">${l.stt === null ? i + 1 : l.stt}</td>`
              + `<td class="mota" rowspan="${sub.length}" title="${esc(l.mota)}">${esc(short)}</td>`
            : "")
        + `<td class="match${byName ? "" : " cas"}">${s.match}</td>`
        + `<td>${s.concl}</td></tr>`;
    });
  });
  table += "</tbody></table></div>";

  resultsEl.innerHTML = table;
  resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

function run() {
  const text = document.getElementById("input").value;
  const resultsEl = document.getElementById("results");
  runLines(text, resultsEl, MODE);
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
  if (MODE === "name") randomNameExample();
  else randomExample();
}

// Vi du: moi chat mot dong hang, CONG THEM mot dong hang khong tra duoc gi -> lan
// bam nao cung thay ca ca "khong thay/khop" (mau vang), vi do moi la ca de bi doc
// nham thanh "khong can giay phep".
const LINE_EXAMPLE_GOODS = [
  "Keo dán công nghiệp, thùng 20kg",
  "Bao bì nhựa PE dạng cuộn",
  "Băng keo dán thùng carton",
  "Găng tay bảo hộ lao động",
];
const MIX_PREFIX = ["Hỗn hợp dung môi gồm", "Nguyên liệu sản xuất gồm",
  "Chế phẩm công nghiệp chứa", "Hỗn hợp gồm"];

// Gom danh sach chat thanh 2-3 DONG HANG, moi dong nhieu chat nhu mo ta that,
// cong them mot dong hang thuong (khong tra ra gi -> luon co ca mau vang) -> ~3-4 dong.
function mixExample(items) {
  const nLines = items.length >= 6 ? 3 : 2;
  const buckets = Array.from({ length: nLines }, () => []);
  shuffle(items).forEach((it, i) => buckets[i % nLines].push(it));
  const lines = buckets.filter(b => b.length).map(g => `${pick(MIX_PREFIX)} ${g.join(", ")}`);
  lines.push(pick(LINE_EXAMPLE_GOODS));
  document.getElementById("input").value = shuffle(lines)
    .map((mota, i) => `${i + 1}\\t${mota}`).join("\\n");
  run();
}

// Mode CAS: moi dong gop nhieu chat KEM ma CAS.
function randomExample() {
  const { rows, known } = exampleRows();
  const items = rows.map(r => `${r.name_vn} (CAS ${r.cas})`);
  const outside = OUTSIDE_DATA.filter(([, cas]) => !known.has(cas));
  if (outside.length) { const [n, c] = pick(outside); items.push(`${n} (CAS ${c})`); }
  mixExample(items);
}

// Mode ten: moi dong gop nhieu chat mo ta bang TEN (khong kem ma CAS).
// extractCas de chac ten khong tu chua chuoi dang CAS (se roi sang truc CAS).
function randomNameExample() {
  const names = exampleRows().rows.map(r => r.name_vn).filter(n => !extractCas(n).length);
  mixExample(names);
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

// Nut noi: thu gon toan van + len dau trang.
const docsEls = [...document.querySelectorAll("details.doc")];
function syncFab() {
  const openDoc = docsEls.some(d => d.open);
  document.getElementById("fab-collapse").hidden = !openDoc;
  document.getElementById("fab-top").hidden = scrollY < 400;
}
// Phai la ham dat ten, KHONG goi thang scrollTo() trong inline handler: trong
// handler, scope chain co ca chinh cai nut -> `scrollTo` an vao
// Element.prototype.scrollTo, cuon cai nut (khong cuon duoc) thay vi cuon trang.
function goTop() {
  window.scrollTo({ top: 0 });
}
function collapseDocs() {
  docsEls.forEach(d => d.open = false);
  // Sau khi dong, vi tri cuon dang o giua vung vua bi xoa -> dua ve dau khoi
  // toan van thay vi de nguoi doc roi vao footer khong biet minh o dau.
  docsEls[0].scrollIntoView({ block: "start" });
  syncFab();
}
docsEls.forEach(d => d.addEventListener("toggle", syncFab));
addEventListener("scroll", syncFab, { passive: true });
syncFab();
</script>
</body>
</html>
"""

out = (
    HTML.replace("__PL3_NO_CAS_HTML__", pl3_no_cas_html())
    .replace("__EXEMPTIONS_HTML__", exemptions_html())
    .replace("__FULL_TEXT_HTML__", full_text_html())
    .replace("__DATA_JSON__", DATA_JSON)
    .replace("__OTHER_OBLIGATION_ANNEXES_JSON__", OTHER_OBLIGATION_ANNEXES_JSON)
    .replace("__VERDICT_JSON__", VERDICT_JSON)
    .replace("__PL3_NO_CAS_JSON__", PL3_NO_CAS_JSON)
    .replace("__PL3_FAMILY_HINTS_JSON__", PL3_FAMILY_HINTS_JSON)
    .replace("__PL3_HINT_PREFIX_JSON__", PL3_HINT_PREFIX_JSON)
    .replace("__PL3_EXCLUDED_JSON__", PL3_EXCLUDED_JSON)
    .replace("__PL3_EXCLUDED_NOTE_JSON__", PL3_EXCLUDED_NOTE_JSON)
    .replace("__VERDICT_PL3__", core.VERDICT["pl3"])
)
Path(__file__).parent.joinpath("Tra-cuu-hoa-chat-ND24.html").write_text(out, encoding="utf-8")
print("Tra-cuu-hoa-chat-ND24.html written —", len(out), "bytes")
