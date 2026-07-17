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
from pathlib import Path

import core

DATA_JSON = json.dumps(core.DATA, ensure_ascii=False)
IMPORT_RULES_JSON = json.dumps(core.IMPORT_RULES, ensure_ascii=False)
IMPORT_ANNEXES_JSON = json.dumps(core.IMPORT_ANNEXES, ensure_ascii=False)
ANNEX_ORDER_JSON = json.dumps(core.ANNEX_ORDER, ensure_ascii=False)
OTHER_OBLIGATION_ANNEXES_JSON = json.dumps(core.OTHER_OBLIGATION_ANNEXES, ensure_ascii=False)
VERDICT_JSON = json.dumps(core.VERDICT, ensure_ascii=False)
SUPPRESS_ANNEX_JSON = json.dumps(core.SUPPRESS_ANNEX, ensure_ascii=False)
ANNEX_DISPLAY_ORDER_JSON = json.dumps(core.ANNEX_DISPLAY_ORDER, ensure_ascii=False)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def exemptions_html():
    parts = ['<h2>Các trường hợp được miễn trừ</h2>', '<p class="cite">Nghị định 26/2026/NĐ-CP</p>']
    for group in core.EXEMPTIONS:
        parts.append(f'<h3>{esc(group["title"])} ({esc(group["cite"])})</h3>')
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
  <p>Theo Phụ lục I–IV, Nghị định 24/2026/NĐ-CP &amp; yêu cầu nhập khẩu, Nghị định 26/2026/NĐ-CP</p>
  <p class="author">Tác giả: Nguyễn Hoàng Long - HQ KCX&amp;KCN</p>
</header>

<div class="card instructions">
  <div class="icon">ℹ️</div>
  <div>
    <h2>Hướng dẫn sử dụng</h2>
    <ol>
      <li>Copy nguyên mô tả hàng hóa của doanh nghiệp — không cần tách tay từng mã CAS.</li>
      <li>Dán vào ô bên dưới rồi bấm <b>Tra cứu</b>. Công cụ tự tìm mọi mã CAS xuất hiện trong đoạn văn. Nếu khai báo không có mã CAS, gõ tên hóa chất (tiếng Việt hoặc tiếng Anh, không cần gõ dấu) để tìm theo tên.</li>
      <li>Công cụ không tự tính % hàm lượng — hóa chất Phụ lục III luôn báo "__VERDICT_PL3__"; đối chiếu ngưỡng miễn trừ nồng độ ở mục "Các trường hợp được miễn trừ" bên dưới bằng tài liệu khai báo gốc.</li>
    </ol>
  </div>
</div>

<div class="card" id="input-card">
  <div class="input-row">
    <textarea id="input" placeholder="Ví dụ: Hỗn hợp dung môi công nghiệp gồm Metanol CAS 67-56-1, Acetaldehyde (75-07-0), mã CAS 103-79-7 (P2P)... — hoặc gõ tên chất: metanol"></textarea>
    <button id="run-btn" onclick="run()">🔍 Tra cứu</button>
  </div>
  <div class="toolbar">
    <button class="mini" onclick="randomExample()">🎲 Ví dụ ngẫu nhiên</button>
    <button class="mini" onclick="randomNameExample()">🔤 Ví dụ tra theo tên</button>
    <button class="mini" onclick="clearAll()">✕ Xóa</button>
    <span class="hint">Mẹo: nhấn <b>Ctrl+Enter</b> (⌘+Enter trên Mac) để tra cứu nhanh</span>
  </div>
</div>

<div id="results"></div>

<div class="card exempt">
  __EXEMPTIONS_HTML__
</div>

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

const CAS_RE = /\\b\\d{2,7}-\\d{2}-\\d\\b/g;

function rowsFor(cas) {
  return DATA.filter(r => r.cas === cas);
}

function highestAnnex(cas) {
  const present = new Set(rowsFor(cas).map(r => r.annex));
  for (const a of ANNEX_ORDER) if (present.has(a)) return a;
  return null;
}

function annexLabels(cas) {
  const present = new Set(rowsFor(cas).map(r => r.annex));
  return ANNEX_DISPLAY_ORDER.filter(a => present.has(a)).map(a => `PL ${a}`).join(", ") || "—";
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

// Tra theo ten khi doan nhap khong co ma CAS nao: moi tu cua truy van phai
// xuat hien trong name_vn hoac name_en (bo dau, khong phan biet hoa/thuong).
// Uu tien khop nguyen ten > dau ten > chua trong ten.
const NAME_LIMIT = 30;
function searchByName(text) {
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
  const seen = new Set(), out = [];
  for (const [, cas] of scored) if (!seen.has(cas)) { seen.add(cas); out.push(cas); }
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

function run() {
  const text = document.getElementById("input").value;
  const resultsEl = document.getElementById("results");
  let entries = extractCas(text);
  let heading = `Tìm thấy ${entries.length} mã CAS`;

  if (entries.length === 0) {
    // Khong co ma CAS -> thu tra theo ten hoa chat.
    const byName = searchByName(text);
    if (byName.length === 0) {
      resultsEl.innerHTML = `<div class="card"><p class="note">Không tìm thấy mã CAS nào (định dạng NNN-NN-N) và cũng không có tên hóa chất nào khớp với đoạn đã nhập. Kiểm tra lại mô tả, dán trực tiếp mã CAS (ví dụ: 107-13-1), hoặc gõ tên chất (ví dụ: metanol).</p></div>`;
      return;
    }
    entries = byName.slice(0, NAME_LIMIT);
    heading = `Không có mã CAS trong đoạn đã nhập — tìm theo tên được ${byName.length} chất khớp`
      + (byName.length > NAME_LIMIT ? `, hiển thị ${NAME_LIMIT} chất khớp nhất` : "");
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
  stats += "</div>";

  let table = `<div class="card">
    <p id="count">${heading}</p>
    ${stats}
    <div class="table-wrap"><table><tr><th>CAS</th><th>Tên chất</th><th>Phụ lục</th><th>Trạng thái</th></tr>`;
  entries.forEach((cas, i) => {
    const rows = rowsFor(cas);
    const name = rows.length ? rows[0].name_vn : "(không có trong dữ liệu)";
    const { badge, text: statusText } = statuses[i];
    table += `<tr class="${badge}"><td class="cas">${esc(cas)}</td><td>${esc(name)}</td><td>${esc(annexLabels(cas))}</td><td><span class="pill ${badge}">${esc(statusText)}</span></td></tr>`;
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

function randomExample() {
  const byCas = new Map();
  DATA.forEach(row => {
    if (!byCas.has(row.cas)) byCas.set(row.cas, { row, annexes: new Set() });
    byCas.get(row.cas).annexes.add(row.annex);
  });
  const entries = [...byCas.values()];
  const items = [];
  for (const match of EXAMPLE_BUCKETS) {
    const pool = entries.filter(e => match(e.annexes));
    if (pool.length) {
      const { row } = pick(pool);
      items.push([row.name_vn, row.cas]);
    }
  }
  const outside = OUTSIDE_DATA.filter(([, cas]) => !byCas.has(cas));
  if (outside.length) items.push(pick(outside));
  // Xao tron de mo ta doc nhu khai bao that, khong phai danh sach xep theo phu luc.
  document.getElementById("input").value = "Hỗn hợp mẫu gồm: " +
    shuffle(items).map(([name, cas]) => `${name} (CAS ${cas})`).join(", ") + ".";
  run();
}

// Nhanh tra theo ten can o nhap KHONG co ma CAS nao -> phai la vi du rieng.
// extractCas de loai ten tu no da chua chuoi dang CAS (se roi vao nhanh CAS).
function randomNameExample() {
  const row = pick(DATA.filter(r => extractCas(r.name_vn).length === 0));
  document.getElementById("input").value = row.name_vn;
  run();
}

const inputEl = document.getElementById("input");
inputEl.addEventListener("keydown", e => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); run(); }
});
// Tu tra cuu ngay khi dan mo ta vao o (setTimeout de gia tri kip cap nhat).
inputEl.addEventListener("paste", () => setTimeout(run, 0));
</script>
</body>
</html>
"""

out = (
    HTML.replace("__EXEMPTIONS_HTML__", exemptions_html())
    .replace("__DATA_JSON__", DATA_JSON)
    .replace("__IMPORT_RULES_JSON__", IMPORT_RULES_JSON)
    .replace("__IMPORT_ANNEXES_JSON__", IMPORT_ANNEXES_JSON)
    .replace("__ANNEX_ORDER_JSON__", ANNEX_ORDER_JSON)
    .replace("__OTHER_OBLIGATION_ANNEXES_JSON__", OTHER_OBLIGATION_ANNEXES_JSON)
    .replace("__VERDICT_JSON__", VERDICT_JSON)
    .replace("__SUPPRESS_ANNEX_JSON__", SUPPRESS_ANNEX_JSON)
    .replace("__ANNEX_DISPLAY_ORDER_JSON__", ANNEX_DISPLAY_ORDER_JSON)
    .replace("__VERDICT_PL3__", core.VERDICT["pl3"])
)
Path(__file__).parent.joinpath("Tra-cuu-hoa-chat-ND24.html").write_text(out, encoding="utf-8")
print("Tra-cuu-hoa-chat-ND24.html written —", len(out), "bytes")
