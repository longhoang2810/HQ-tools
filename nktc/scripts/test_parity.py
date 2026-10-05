#!/usr/bin/env python3
import base64
import json
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
import xml.etree.ElementTree as ET
import zipfile
from html import escape
from pathlib import Path

from openpyxl import Workbook, load_workbook


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "nktc_process.py"
TEMPLATE = ROOT / "NKTC-xu-ly-excel.template.html"
BUNDLE = ROOT / "NKTC-xu-ly-excel.html"
EXCELJS = ROOT / "assets" / "exceljs.min.js"
REGIONS = ROOT / "regions.txt"
CVNK_TEMPLATE = ROOT / "assets" / "CVNK_Gui_thue_template.docx"
NODE = shutil.which("node")

sys.path.insert(0, str(ROOT / "scripts"))
from nktc_process import to_float


HEADERS = [
    "So_to_khai",
    "Ma_LH",
    "Ma_DN_XNK",
    "Ten_DN_XNK",
    "Ma_dia_chi_DN_XNK",
    "So_quan_ly_cua_noi_bo_doanh_nghiep",
    "Tong_tri_gia_tinh_thue",
]

AMOUNT_CASES = [
    ("1,234.56", 1234.56),
    ("12.345,67", 12345.67),
    ("1.234.567,89", 1234567.89),
    ("1,234", 1234.0),
    ("1.234", 1.234),
    ("  9,999,999.99  ", 9999999.99),
    (1234.5, 1234.5),
    (0, 0.0),
    ("", 0.0),
    (None, 0.0),
    ("   ", 0.0),
    ("12 345", 0.0),
    ("#N/A", 0.0),
    ("abc", 0.0),
    ("1234 USD", 0.0),
]

UNPARSEABLE_VALUES = ["12 345", "#N/A", "abc", "1234 USD"]

STRICT_GRAMMAR_REJECTED = [
    "0x10",
    "1_000",
    "Infinity",
    "NaN",
    "abc",
    "12 345",
    "٣",
    "１２３４",
]


NODE_HARNESS = r"""
const fs = require('fs');
const vm = require('vm');
const request = JSON.parse(fs.readFileSync(0, 'utf8'));
global.ExcelJS = require(request.exceljs);

const elements = new Map();
function element(id) {
  if (!elements.has(id)) {
    elements.set(id, {
      id,
      value: '',
      files: [],
      className: '',
      textContent: '',
      disabled: false,
      addEventListener() {},
      click() {},
    });
  }
  return elements.get(id);
}
global.document = {
  getElementById: element,
  createElement() { return {href: '', download: '', click() {}}; },
};
global.window = global;
global.confirm = () => true;
global.__lastBlob = null;
global.URL = {createObjectURL: b => { global.__lastBlob = b; return 'blob:test'; }, revokeObjectURL() {}};
global.setTimeout = fn => { fn(); return 0; };

element('regions').value = request.regions || 'Test\tHa Noi';
element('month').value = '06';
element('year').value = '2026';
element('tbMonth').value = '07';
element('tbYear').value = '2026';
element('outName').value = 'out.xlsx';
if (request.source) {
  element('source').files = [{
    arrayBuffer: async () => fs.promises.readFile(request.source),
  }];
}

const template = fs.readFileSync(request.template, 'utf8');
const match = template.match(/<script>\s*(\(\(\) => \{[\s\S]*?\}\)\(\);)\s*<\/script>\s*<\/body>/);
if (!match) throw new Error('Could not extract inline NKTC application JS');
const app = match[1].replace(
  /\}\)\(\);\s*$/,
  "globalThis.__NKTC_TEST__={num,extractRows,chooseRegion,buildRegionSheet,run,runSplit,sourceColumns,cvnkGenerate,setLastRun:g=>{lastRun={groups:g};},getUnparseableAmounts:()=>unparseableAmounts,getBlankAmounts:()=>blankAmounts};})();"
);
vm.runInThisContext(app, {filename: request.template});
const api = global.__NKTC_TEST__;

(async () => {
  if (request.action === 'amounts') {
    process.stdout.write(JSON.stringify(request.values.map(value => api.num(value))));
    return;
  }
  if (request.action === 'amounts_with_count') {
    const values = request.values.map(value => api.num(value));
    process.stdout.write(JSON.stringify({values, unparseableAmounts: api.getUnparseableAmounts(), blankAmounts: api.getBlankAmounts()}));
    return;
  }
  if (request.action === 'columns') {
    const source = new ExcelJS.Workbook();
    await source.xlsx.load(fs.readFileSync(request.source));
    try { process.stdout.write(JSON.stringify(api.sourceColumns(source.worksheets[0]))); }
    catch (e) { process.stdout.write(JSON.stringify({error: e.message})); }
    return;
  }
  if (request.action === 'cvnk') {
    for (const k of ['month','year','tbMonth','tbYear']) element(k).value = request[k];
    api.setLastRun(request.groups);
    try { await api.cvnkGenerate(); }
    catch (e) { process.stdout.write(JSON.stringify({error: e.message})); return; }
    const buf = Buffer.from(await global.__lastBlob.arrayBuffer());
    fs.writeFileSync(request.output, buf);
    process.stdout.write(JSON.stringify({ok: true, bytes: buf.length}));
    return;
  }
  if (request.action === 'status') {
    // Same contract as the real click handler: a thrown error becomes an error status.
    try { await api.run(); }
    catch (e) { process.stdout.write(JSON.stringify({kind: 'error', text: e.message, downloaded: global.__lastBlob !== null})); return; }
    if (request.output) fs.writeFileSync(request.output, Buffer.from(await global.__lastBlob.arrayBuffer()));
    const status = element('status');
    process.stdout.write(JSON.stringify({kind: status.className, text: status.textContent, downloaded: global.__lastBlob !== null}));
    return;
  }
  if (request.action === 'split') {
    await api.runSplit();
    fs.writeFileSync(request.output, Buffer.from(await global.__lastBlob.arrayBuffer()));
    const status = element('status');
    process.stdout.write(JSON.stringify({kind: status.className, text: status.textContent}));
    return;
  }
  if (request.action === 'build') {
    const source = new ExcelJS.Workbook();
    await source.xlsx.load(fs.readFileSync(request.source));
    const rows = api.extractRows(source.worksheets[0]);
    const region = {name: 'Test', terms: ['ha noi']};
    const records = rows.filter(row => api.chooseRegion(row.A, [region]) === region.name);
    const output = new ExcelJS.Workbook();
    const count = api.buildRegionSheet(output, region.name, records);
    const data = await output.xlsx.writeBuffer();
    fs.writeFileSync(request.output, Buffer.from(data));
    process.stdout.write(JSON.stringify(count));
    return;
  }
  throw new Error(`Unknown action: ${request.action}`);
})().catch(error => {
  console.error(error && error.stack ? error.stack : error);
  process.exitCode = 1;
});
"""


def source_row(name, code, amount=100, declaration=100000001, address="Ha Noi"):
    return [
        declaration,
        "E21",
        code,
        name,
        address,
        f"12345678XK{declaration}",
        amount,
    ]


def write_source(path, rows, code_format=None, headers=None):
    wb = Workbook()
    ws = wb.active
    ws.append(HEADERS if headers is None else headers)
    for row in rows:
        ws.append(row)
    if code_format:
        ws["C2"].number_format = code_format
    wb.save(path)


def inject_cached_formula_results(path, cached_results):
    namespace = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    ET.register_namespace("", namespace)
    patched = path.with_name(f"{path.stem}-patched.xlsx")
    with zipfile.ZipFile(path, "r") as source_zip, zipfile.ZipFile(patched, "w") as target_zip:
        for info in source_zip.infolist():
            data = source_zip.read(info.filename)
            if info.filename == "xl/worksheets/sheet1.xml":
                root = ET.fromstring(data)
                for coordinate, (value, value_type) in cached_results.items():
                    cell = root.find(f".//{{{namespace}}}c[@r='{coordinate}']")
                    if cell is None:
                        raise AssertionError(f"Missing formula cell {coordinate}")
                    if value_type:
                        cell.set("t", value_type)
                    else:
                        cell.attrib.pop("t", None)
                    cached = cell.find(f"{{{namespace}}}v")
                    if cached is None:
                        cached = ET.SubElement(cell, f"{{{namespace}}}v")
                    cached.text = str(value)
                data = ET.tostring(root, encoding="utf-8", xml_declaration=False)
            target_zip.writestr(info, data)
    shutil.move(patched, path)


def delete_cached_formula_results(path, coordinates):
    namespace = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    ET.register_namespace("", namespace)
    patched = path.with_name(f"{path.stem}-patched.xlsx")
    with zipfile.ZipFile(path, "r") as source_zip, zipfile.ZipFile(patched, "w") as target_zip:
        for info in source_zip.infolist():
            data = source_zip.read(info.filename)
            if info.filename == "xl/worksheets/sheet1.xml":
                root = ET.fromstring(data)
                for coordinate in coordinates:
                    cell = root.find(f".//{{{namespace}}}c[@r='{coordinate}']")
                    if cell is None:
                        raise AssertionError(f"Missing formula cell {coordinate}")
                    cached = cell.find(f"{{{namespace}}}v")
                    if cached is not None:
                        cell.remove(cached)
                data = ET.tostring(root, encoding="utf-8", xml_declaration=False)
            target_zip.writestr(info, data)
    shutil.move(patched, path)


def write_regions(path):
    path.write_text("Test\tHa Noi\n", encoding="utf-8")


def run_python(source, output, regions):
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(source),
            "-o",
            str(output),
            "--regions",
            str(regions),
            "--month",
            "06",
            "--year",
            "2026",
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def region_snapshot(path):
    ws = load_workbook(path, data_only=True)["Test"]
    rows = []
    for row in range(5, ws.max_row + 1):
        rows.append(tuple(
            "" if ws.cell(row, col).value is None else ws.cell(row, col).value
            for col in range(1, 9)
        ))
    return rows, {str(rng) for rng in ws.merged_cells.ranges}


@unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
def run_js(temp_dir, request):
    harness = Path(temp_dir) / "nktc_js_harness.js"
    harness.write_text(textwrap.dedent(NODE_HARNESS), encoding="utf-8")
    payload = {
        "template": str(TEMPLATE),
        "exceljs": str(EXCELJS),
        **request,
    }
    result = subprocess.run(
        [NODE, str(harness)],
        input=json.dumps(payload, ensure_ascii=False),
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


@unittest.skipUnless(NODE, "node is required for browser-JS tests")
class CvnkLetterTest(unittest.TestCase):
    """Công văn (.docx) gửi cơ quan thuế — trước đây KHÔNG có test nào.

    Hai thứ được chốt ở đây: ngày tháng lấy SỐNG từ form (snapshot của lần Xuất
    Excel từng làm công văn một đằng, file Excel một nẻo, im lặng), và ô tháng/năm
    hỏng thì TỪ CHỐI hẳn thay vì đẻ ra "ngày 01/NaN/2024" trên văn bản đã gửi đi.
    """

    GROUPS = {"Hn": [{"A": "Ha Noi"}]}

    def _gen(self, tmp, **over):
        # Chạy trên BUNDLE, không phải template: mẫu .docx chỉ được nhúng base64
        # lúc build, trong template nó vẫn là chuỗi __CVNK_TEMPLATE_B64__ nên atob
        # ném "Invalid character". Bundle cũng đúng là thứ cán bộ mở.
        req = {"action": "cvnk", "template": str(BUNDLE),
               "month": "09", "year": "2026", "tbMonth": "10",
               "tbYear": "2026", "groups": self.GROUPS,
               "output": str(Path(tmp) / "cv.docx")}
        req.update(over)
        return run_js(tmp, req), Path(tmp) / "cv.docx"

    def _doc_text(self, path):
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8")
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", xml))

    def test_dates_come_from_the_form_at_click_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            got, out = self._gen(tmp)
            self.assertTrue(got.get("ok"), got)
            text = self._doc_text(out)
        self.assertIn("01/09/2026", text)          # FROM_DATE
        self.assertIn("30/09/2026", text)          # TO_DATE — tháng 9 có 30 ngày
        self.assertIn("tháng 10 năm 2026", text)   # DOC_MONTH/DOC_YEAR
        self.assertNotIn("{{", text)               # không còn placeholder nào

    def test_generated_docx_is_a_valid_readable_zip(self):
        with tempfile.TemporaryDirectory() as tmp:
            got, out = self._gen(tmp)
            self.assertTrue(got.get("ok"), got)
            with zipfile.ZipFile(out) as z:
                self.assertIsNone(z.testzip(), "CRC hỏng trong .docx sinh ra")
                ET.fromstring(z.read("word/document.xml"))

    def test_unbuilt_template_says_so_instead_of_atob_invalid_character(self):
        # Mở .template.html (chưa build) thì CVNK_TEMPLATE_B64 vẫn là chuỗi đánh
        # dấu -> atob ném "Invalid character", người dùng không hiểu gì. Phải nói
        # thẳng là chưa build và chỉ ra file/lệnh đúng.
        with tempfile.TemporaryDirectory() as tmp:
            got, out = self._gen(tmp, template=str(TEMPLATE))
        self.assertIn("error", got)
        self.assertNotIn("Invalid character", got["error"])
        self.assertIn("build_html.py", got["error"])
        self.assertFalse(out.exists())

    def test_bad_month_or_year_is_refused_not_guessed(self):
        # parseInt() nuốt rác: "ab"->NaN, "2x"->2, "13" lọt. Cả ba phải bị CHẶN.
        cases = [
            ({"month": "ab"}, "Tháng báo cáo"),
            ({"month": "13"}, "Tháng báo cáo"),
            ({"month": "2x"}, "Tháng báo cáo"),
            ({"month": ""}, "Tháng báo cáo"),
            ({"tbMonth": "&"}, "Tháng thông báo"),
            ({"year": "20x6"}, "Năm báo cáo"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for over, field in cases:
                with self.subTest(**over):
                    got, out = self._gen(tmp, **over)
                    self.assertIn("error", got, f"{over} phải bị từ chối")
                    self.assertIn(field, got["error"])
                    self.assertFalse(out.exists(), "không được ghi file khi input hỏng")


class HeaderDetectionParityTest(unittest.TestCase):
    """Cột nguồn chỉ được tìm theo TÊN header, ở CẢ HAI bản; không đủ 7 cột thì DỪNG.

    Ca hỏng thật (tái hiện 2026-07-28): file có dòng banner phía trên header và cột
    trị giá dời P->Q. Bản cũ không thấy header ở dòng 1 nên rơi về layout cố định
    A/B/H/I/J/K/P -> "Coverage 100%", banner xanh, tiền sai hoàn toàn. File xuất
    thật T6/2026 cũng đã lệch layout cũ (mã DN ở I, trị giá ở Q), nên mọi kiểu
    "đoán cột" đều là sai tiền im lặng.
    """

    SHIFTED = ["NEW", *HEADERS]
    RENAMED = ["NEW", *(h if h != "Ma_dia_chi_DN_XNK" else "Dia_chi_DN_XNK" for h in HEADERS)]
    BANNER = ["DANH SÁCH TỜ KHAI TẠI CHỖ THÁNG 6/2026"]

    def _ws(self, *rows):
        wb = Workbook()
        ws = wb.active
        for row in rows:
            ws.append(row)
        return ws

    def _source(self, tmp, *rows):
        path = Path(tmp) / "source.xlsx"
        wb = Workbook()
        for row in rows:
            wb.active.append(row)
        wb.save(path)
        return path

    def test_python_partial_headers_stop_and_name_the_missing_column(self):
        from nktc_process import SourceLayoutError, detect_src
        with self.assertRaises(SourceLayoutError) as ctx:
            detect_src(self._ws(self.RENAMED))
        self.assertIn("ma_dia_chi_dn_xnk", str(ctx.exception))

    def test_python_no_headers_stop(self):
        from nktc_process import SourceLayoutError, detect_src
        with self.assertRaises(SourceLayoutError):
            detect_src(self._ws(["x"] * 16))

    def test_python_full_headers_detected_after_banner(self):
        from nktc_process import detect_src
        cols, header_row = detect_src(self._ws(self.BANNER, ["", ""], self.SHIFTED))
        self.assertEqual(header_row, 3)
        self.assertEqual(cols["Tong_tri_gia"], self.SHIFTED.index("Tong_tri_gia_tinh_thue") + 1)

    def test_python_explicit_header_rows_must_match_exactly(self):
        from nktc_process import SourceLayoutError, detect_src
        ws = self._ws(self.BANNER, self.SHIFTED)
        self.assertEqual(detect_src(ws, 2)[1], 2)
        with self.assertRaises(SourceLayoutError):
            detect_src(ws, 1)

    def test_python_cli_refuses_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = self._source(tmp, self.RENAMED, ["", *source_row("Co", "1")])
            output = tmp_path / "out.xlsx"
            regions = tmp_path / "regions.txt"
            write_regions(regions)
            with self.assertRaises(subprocess.CalledProcessError) as ctx:
                run_python(source, output, regions)
            self.assertEqual(ctx.exception.returncode, 2)
            self.assertIn("ma_dia_chi_dn_xnk", ctx.exception.stderr)
            self.assertFalse(output.exists())

    def test_python_cli_refuses_zero_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            row = source_row("Co", "1")
            row[1] = "A11"
            source = self._source(tmp, HEADERS, row)
            output = tmp_path / "out.xlsx"
            regions = tmp_path / "regions.txt"
            write_regions(regions)
            with self.assertRaises(subprocess.CalledProcessError) as ctx:
                run_python(source, output, regions)
            self.assertEqual(ctx.exception.returncode, 2)
            self.assertFalse(output.exists())

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_javascript_partial_headers_stop_and_name_the_missing_column(self):
        with tempfile.TemporaryDirectory() as tmp:
            got = run_js(tmp, {"action": "columns",
                               "source": str(self._source(tmp, self.RENAMED))})
        self.assertIn("ma_dia_chi_dn_xnk", got["error"])

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_javascript_no_headers_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            got = run_js(tmp, {"action": "columns",
                               "source": str(self._source(tmp, ["x"] * 16))})
        self.assertIn("error", got)

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_javascript_full_headers_detected_after_banner(self):
        with tempfile.TemporaryDirectory() as tmp:
            got = run_js(tmp, {"action": "columns",
                               "source": str(self._source(tmp, self.BANNER, ["", ""], self.SHIFTED))})
        self.assertEqual(got["headerRow"], 3)
        self.assertEqual(got["cols"]["Tong_tri_gia"], self.SHIFTED.index("Tong_tri_gia_tinh_thue") + 1)

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_javascript_bad_header_or_zero_rows_shows_error_and_downloads_nothing(self):
        row = source_row("Co", "1")
        row[1] = "A11"
        for rows in ([self.RENAMED, ["", *source_row("Co", "1")]], [HEADERS, row]):
            with tempfile.TemporaryDirectory() as tmp:
                got = run_js(tmp, {"action": "status",
                                   "source": str(self._source(tmp, *rows))})
            self.assertEqual(got["kind"], "error")
            self.assertIn("Không xuất file", got["text"])
            self.assertFalse(got["downloaded"])

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_banner_and_shifted_amount_column_give_the_right_money_in_both(self):
        """Đúng ca tái hiện cũ: banner + mọi cột dời phải một ô (trị giá P->Q)."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = self._source(
                tmp, self.BANNER, self.SHIFTED,
                ["x", *source_row("Co A", "0001", amount=1234.5)],
                ["x", *source_row("Co B", "0002", amount=99, declaration=100000002)],
            )
            python_output, js_output, _ = WorkbookParityTest.run_both_from_source(None, tmp_path, source)
            python_rows, _ = region_snapshot(python_output)
            js_rows, _ = region_snapshot(js_output)
        self.assertEqual([r[5] for r in python_rows], [1234.5, 99])
        self.assertEqual(js_rows, python_rows)


class AmountParsingParityTest(unittest.TestCase):
    def test_python_amount_behaviour_table(self):
        for value, expected in AMOUNT_CASES:
            with self.subTest(value=value):
                self.assertEqual(to_float(value), expected)

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_javascript_amount_behaviour_table(self):
        with tempfile.TemporaryDirectory() as tmp:
            actual = run_js(tmp, {"action": "amounts", "values": [v for v, _ in AMOUNT_CASES]})
        self.assertEqual(actual, [expected for _, expected in AMOUNT_CASES])

    def test_python_counts_blank_amounts_separately_from_unparseable(self):
        # Ô trống KHÔNG gộp vào "không đọc được": file nguồn hỏng và DN không khai
        # là hai chuyện khác nhau, tuy cùng ghi 0.00. Đếm riêng, báo riêng.
        values = [0, "", None, "   ", *UNPARSEABLE_VALUES]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source, output = tmp_path / "source.xlsx", tmp_path / "python.xlsx"
            regions = tmp_path / "regions.txt"
            write_source(
                source,
                [source_row(f"Company {i}", str(i), value, 100000000 + i)
                 for i, value in enumerate(values, start=1)],
            )
            write_regions(regions)
            result = run_python(source, output, regions)
        self.assertIn(
            "CẢNH BÁO: 3 dòng có Trị giá ĐỂ TRỐNG, đã ghi 0.00 - kiểm tra lại file nguồn.",
            result.stdout,
        )

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_javascript_blank_amount_count_matches_python(self):
        values = [0, "", None, "   ", *UNPARSEABLE_VALUES]
        with tempfile.TemporaryDirectory() as tmp:
            actual = run_js(tmp, {"action": "amounts_with_count", "values": values})
        self.assertEqual(actual["blankAmounts"], 3)
        self.assertEqual(actual["unparseableAmounts"], len(UNPARSEABLE_VALUES))

    def test_python_warning_counts_only_nonblank_unparseable_amounts(self):
        values = [0, "", None, "   ", *UNPARSEABLE_VALUES]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.xlsx"
            output = tmp_path / "python.xlsx"
            regions = tmp_path / "regions.txt"
            write_source(
                source,
                [source_row(f"Company {i}", str(i), value, 100000000 + i)
                 for i, value in enumerate(values, start=1)],
            )
            write_regions(regions)
            result = run_python(source, output, regions)
        self.assertIn(
            "CẢNH BÁO: 4 dòng có Trị giá không đọc được, đã ghi 0.00 - kiểm tra lại file nguồn.",
            result.stdout,
        )

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_javascript_warning_counts_only_nonblank_unparseable_amounts(self):
        values = [0, "", None, "   ", *UNPARSEABLE_VALUES]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.xlsx"
            write_source(
                source,
                [source_row(f"Company {i}", str(i), value, 100000000 + i)
                 for i, value in enumerate(values, start=1)],
            )
            status = run_js(
                tmp,
                {
                    "action": "status",
                    "source": str(source),
                    "regions": "Test\tHa Noi",
                },
            )
        self.assertEqual(status["kind"], "error")
        self.assertIn("4 dòng", status["text"])

    def test_python_strict_amount_grammar_and_count(self):
        stats = {}
        actual = [to_float(value, stats) for value in STRICT_GRAMMAR_REJECTED]
        self.assertEqual(actual, [0.0] * len(STRICT_GRAMMAR_REJECTED))
        self.assertEqual(stats.get("unparseable_amounts"), len(STRICT_GRAMMAR_REJECTED))
        for value, expected in AMOUNT_CASES[:7]:
            with self.subTest(value=value):
                self.assertEqual(to_float(value), expected)

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_javascript_strict_amount_grammar_and_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            actual = run_js(
                tmp,
                {"action": "amounts_with_count", "values": STRICT_GRAMMAR_REJECTED},
            )
            accepted = run_js(
                tmp,
                {"action": "amounts", "values": [value for value, _ in AMOUNT_CASES[:7]]},
            )
        self.assertEqual(actual["values"], [0.0] * len(STRICT_GRAMMAR_REJECTED))
        self.assertEqual(actual["unparseableAmounts"], len(STRICT_GRAMMAR_REJECTED))
        self.assertEqual(accepted, [expected for _, expected in AMOUNT_CASES[:7]])

    def test_python_boolean_amount_is_unparseable_and_counted(self):
        stats = {}
        self.assertEqual(to_float(True, stats), 0.0)
        self.assertEqual(stats.get("unparseable_amounts"), 1)

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_javascript_boolean_amount_is_unparseable_and_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            actual = run_js(
                tmp,
                {"action": "amounts_with_count", "values": [True]},
            )
        self.assertEqual(actual, {"values": [0.0], "unparseableAmounts": 1, "blankAmounts": 0})


class WorkbookParityTest(unittest.TestCase):
    def run_both_from_source(self, tmp_path, source):
        python_output = tmp_path / "python.xlsx"
        js_output = tmp_path / "javascript.xlsx"
        regions = tmp_path / "regions.txt"
        write_regions(regions)
        run_python(source, python_output, regions)
        js_count = run_js(
            tmp_path,
            {
                "action": "build",
                "source": str(source),
                "output": str(js_output),
            },
        )
        return python_output, js_output, js_count

    def run_both(self, tmp_path, rows, code_format=None):
        source = tmp_path / "source.xlsx"
        write_source(source, rows, code_format=code_format)
        return self.run_both_from_source(tmp_path, source)

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_default_source_sheet_is_first_even_when_another_sheet_is_active(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.xlsx"
            wb = Workbook()
            first = wb.active
            first.title = "First"
            first.append(HEADERS)
            first.append(source_row("First Sheet Company", "0001", declaration=100000001))
            active = wb.create_sheet("Active")
            active.append(HEADERS)
            active.append(source_row("Active Sheet Company", "0002", declaration=200000001))
            wb.active = 1
            wb.save(source)

            python_output, js_output, _ = self.run_both_from_source(tmp_path, source)
            python_rows, _ = region_snapshot(python_output)
            js_rows, _ = region_snapshot(js_output)

        self.assertEqual(python_rows, js_rows)
        self.assertEqual(python_rows[0][1], "First Sheet Company")

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_zero_padded_company_code_is_preserved_in_both(self):
        with tempfile.TemporaryDirectory() as tmp:
            python_output, js_output, _ = self.run_both(
                Path(tmp),
                [source_row("Company", 123456)],
                code_format="0000000000",
            )
            for output in (python_output, js_output):
                with self.subTest(output=output.name):
                    rows, _ = region_snapshot(output)
                    self.assertEqual(rows[0][2], "0000123456")

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_formula_codes_and_amounts_match_without_merging_companies(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.xlsx"
            write_source(
                source,
                [
                    source_row("Company A", "=17+17", "=2+2", 100000001),
                    source_row("Company B", "=6+6", "=1+2", 100000002),
                ],
            )
            inject_cached_formula_results(
                source,
                {
                    "C2": (34, None),
                    "G2": (4, None),
                    "C3": (12, None),
                    "G3": (3, None),
                },
            )
            python_output, js_output, js_count = self.run_both_from_source(tmp_path, source)
            python_rows, _ = region_snapshot(python_output)
            js_rows, _ = region_snapshot(js_output)
        self.assertEqual(js_count["companies"], 2)
        self.assertEqual([row[2] for row in python_rows], ["34", "12"])
        self.assertEqual([row[5] for row in python_rows], [4, 3])
        self.assertEqual(js_rows, python_rows)

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_formulas_without_cached_results_keep_distinct_companies(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.xlsx"
            write_source(
                source,
                [
                    source_row("Company A", "=17+17", "=2+2", 100000001),
                    source_row("Company B", "=6+6", "=1+2", 100000002),
                ],
            )
            delete_cached_formula_results(source, {"C2", "G2", "C3", "G3"})
            python_output, js_output, js_count = self.run_both_from_source(tmp_path, source)
            python_rows, _ = region_snapshot(python_output)
            js_rows, _ = region_snapshot(js_output)
        self.assertEqual(js_count["companies"], 2)
        self.assertEqual([row[2] for row in python_rows], ["", ""])
        self.assertEqual([row[5] for row in python_rows], [0, 0])
        self.assertEqual([row[1] for row in python_rows], ["Company A", "Company B"])
        self.assertEqual(js_rows, python_rows)

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_formula_error_and_plain_error_cells_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.xlsx"
            wb = Workbook()
            ws = wb.active
            ws.append(HEADERS)
            ws.append(source_row("Company A", "=NA()", declaration=100000001))
            ws.append(source_row("Company B", "#DIV/0!", declaration=100000002))
            ws["C3"].data_type = "e"
            wb.save(source)
            inject_cached_formula_results(source, {"C2": ("#N/A", "e")})
            python_output, js_output, js_count = self.run_both_from_source(tmp_path, source)
            python_rows, _ = region_snapshot(python_output)
            js_rows, _ = region_snapshot(js_output)
        self.assertEqual(js_count["companies"], 2)
        self.assertEqual([row[2] for row in python_rows], ["#N/A", "#DIV/0!"])
        self.assertEqual(js_rows, python_rows)

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_negative_zero_padded_company_code_matches_python_zfill(self):
        with tempfile.TemporaryDirectory() as tmp:
            python_output, js_output, _ = self.run_both(
                Path(tmp),
                [source_row("Company", -12)],
                code_format="0000",
            )
            for output in (python_output, js_output):
                with self.subTest(output=output.name):
                    rows, _ = region_snapshot(output)
                    self.assertEqual(rows[0][2], "-012")

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_same_code_nonadjacent_names_form_one_merged_company(self):
        rows = [
            source_row("CONG TY A", "0001", declaration=100000001),
            source_row("Cong ty A", "0001", declaration=100000002),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            python_output, js_output, js_count = self.run_both(Path(tmp), rows)
            self.assertEqual(js_count["companies"], 1)
            for output in (python_output, js_output):
                with self.subTest(output=output.name):
                    snapshot, merges = region_snapshot(output)
                    self.assertEqual([row[0] for row in snapshot], [1, ""])
                    self.assertEqual(snapshot[0][1], "CONG TY A")
                    self.assertEqual(snapshot[0][2], "0001")
                    self.assertTrue({"A5:A6", "B5:B6", "C5:C6"}.issubset(merges))
            summary = load_workbook(python_output, data_only=True)["summary"]
            self.assertEqual(summary["D8"].value, 1)

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_same_code_rows_are_bucketed_when_not_adjacent_after_sort(self):
        rows = [
            source_row("Zulu Company", "0001", declaration=100000001),
            source_row("Middle Company", "0002", declaration=100000002),
            source_row("Alpha Company", "0001", declaration=100000003),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            python_output, js_output, js_count = self.run_both(Path(tmp), rows)
            self.assertEqual(js_count["companies"], 2)
            for output in (python_output, js_output):
                with self.subTest(output=output.name):
                    snapshot, merges = region_snapshot(output)
                    self.assertEqual([row[0] for row in snapshot], [1, "", 2])
                    self.assertEqual([row[1] for row in snapshot], ["Alpha Company", "", "Middle Company"])
                    self.assertTrue({"A5:A6", "B5:B6", "C5:C6"}.issubset(merges))

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_blank_codes_are_separate_unmerged_companies(self):
        rows = [
            source_row("Company A", "", declaration=100000001),
            source_row("Company B", "   ", declaration=100000002),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            python_output, js_output, js_count = self.run_both(Path(tmp), rows)
            self.assertEqual(js_count["companies"], 2)
            for output in (python_output, js_output):
                with self.subTest(output=output.name):
                    snapshot, merges = region_snapshot(output)
                    self.assertEqual([row[0] for row in snapshot], [1, 2])
                    self.assertNotIn("A5:A6", merges)
                    self.assertNotIn("B5:B6", merges)
                    self.assertNotIn("C5:C6", merges)

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_vietnamese_name_order_and_stt_match_python(self):
        names = [
            "Âu Lạc",
            "Zeta",
            "ÁNH DƯƠNG",
            "Đại Phát",
            "an Binh",
            "Ô Môn",
            "bao Long",
        ]
        rows = [
            source_row(name, f"{index:04d}", declaration=100000000 + index)
            for index, name in enumerate(names, start=1)
        ]
        with tempfile.TemporaryDirectory() as tmp:
            python_output, js_output, _ = self.run_both(Path(tmp), rows)
            python_rows, _ = region_snapshot(python_output)
            js_rows, _ = region_snapshot(js_output)
        expected_names = sorted(names, key=str.lower)
        self.assertEqual([row[1] for row in python_rows], expected_names)
        self.assertEqual(
            [(row[0], row[1]) for row in js_rows],
            [(row[0], row[1]) for row in python_rows],
        )

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_company_name_whitespace_matches_order_stt_and_bucket_display_name(self):
        rows = [
            source_row("Zulu Company  ", "0001", declaration=100000001),
            source_row("Beta Company", "0002", declaration=100000002),
            source_row("  Zulu Company", "0001", declaration=100000003),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            python_output, js_output, js_count = self.run_both(Path(tmp), rows)
            python_rows, _ = region_snapshot(python_output)
            js_rows, _ = region_snapshot(js_output)
        self.assertEqual(js_count["companies"], 2)
        self.assertEqual([row[0] for row in python_rows], [1, 2, ""])
        self.assertEqual(
            [row[1] for row in python_rows],
            ["Beta Company", "Zulu Company  ", ""],
        )
        self.assertEqual(js_rows, python_rows)

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_header_whitespace_runs_select_amount_column_in_both(self):
        headers = list(HEADERS)
        headers[-1] = "Tong  tri gia  tinh thue"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.xlsx"
            wb = Workbook()
            ws = wb.active
            ws.append(headers)
            ws.append(source_row("Company", "0001", amount=321.5))
            wb.save(source)
            python_output, js_output, _ = self.run_both_from_source(tmp_path, source)
            python_rows, _ = region_snapshot(python_output)
            js_rows, _ = region_snapshot(js_output)
        self.assertEqual(python_rows[0][5], 321.5)
        self.assertEqual(js_rows, python_rows)

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_boolean_company_code_is_lowercase_text_in_both(self):
        with tempfile.TemporaryDirectory() as tmp:
            python_output, js_output, _ = self.run_both(
                Path(tmp),
                [source_row("Company", True)],
            )
            python_rows, _ = region_snapshot(python_output)
            js_rows, _ = region_snapshot(js_output)
        self.assertEqual(python_rows[0][2], "true")
        self.assertEqual(js_rows, python_rows)


    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_so_quan_ly_is_trimmed_before_cutting_8_chars_in_both(self):
        padded = source_row("Padded", "0001")
        padded[5] = "  12345678XK100000001  "
        short = source_row("Short", "0002", declaration=100000002)
        short[5] = "   12345678   "  # 8 chars after trim -> nothing left -> dropped
        with tempfile.TemporaryDirectory() as tmp:
            python_output, js_output, _ = self.run_both(Path(tmp), [padded, short])
            python_rows, _ = region_snapshot(python_output)
            js_rows, _ = region_snapshot(js_output)
        self.assertEqual([r[4] for r in python_rows], ["XK100000001"])
        self.assertEqual(js_rows, python_rows)

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_unmatched_sheet_groups_and_merges_by_company_in_both(self):
        rows = [
            source_row("Beta", "0002", declaration=100000003, address="Ca Mau"),
            source_row("Alpha", "0001", declaration=100000001, address="Ca Mau"),
            source_row("Alpha", "0001", declaration=100000002, address="Ca Mau"),
            source_row("Gamma", "", declaration=100000004, address="Ca Mau"),
            source_row("Gamma", "", declaration=100000005, address="Ca Mau"),
            source_row("Matched", "0009", declaration=100000006),
        ]

        def snapshot(path):
            ws = load_workbook(path, data_only=True)["unmatched"]
            cells = [tuple("" if ws.cell(r, c).value is None else ws.cell(r, c).value
                           for c in range(1, 11)) for r in range(5, ws.max_row + 1)]
            return cells, {str(rng) for rng in ws.merged_cells.ranges}

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.xlsx"
            write_source(source, rows)
            python_output = tmp_path / "python.xlsx"
            regions = tmp_path / "regions.txt"
            write_regions(regions)
            run_python(source, python_output, regions)
            js_output = tmp_path / "javascript.xlsx"
            run_js(tmp_path, {"action": "status", "source": str(source),
                              "output": str(js_output), "regions": "Test\tHa Noi"})
            python_cells, python_merges = snapshot(python_output)
            js_cells, js_merges = snapshot(js_output)
        # Alpha (2 rows, merged) = STT 1, Beta = 2, each blank-code Gamma row is its own STT.
        self.assertEqual([r[0] for r in python_cells], [1, "", 2, 3, 4])
        self.assertIn("A5:A6", python_merges)
        self.assertEqual(js_cells, python_cells)
        self.assertEqual(js_merges, python_merges)


class SplitExportTest(unittest.TestCase):
    """Nut "Xuat tach moi tinh 1 file": ZIP mo duoc, moi vung co du lieu 1 file,
    vung rong bi bo, noi dung sheet vung trung du lieu voi ban CLI."""

    @unittest.skipUnless(NODE, "node is required for browser-JS parity tests")
    def test_zip_has_one_file_per_nonempty_region_matching_python(self):
        rows = [
            source_row("CONG TY A", "0001", declaration=100000001),
            source_row("CONG TY A", "0001", declaration=100000002),
            source_row("CONG TY B", "0002", declaration=100000003, address="Da Nang"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            source = tmp_path / "source.xlsx"
            write_source(source, rows)
            regions_text = "Test\tHa Noi\nRỗng\tCa Mau"
            regions = tmp_path / "regions.txt"
            regions.write_text(regions_text, encoding="utf-8")
            python_output = tmp_path / "python.xlsx"
            run_python(source, python_output, regions)
            zip_path = tmp_path / "split.zip"
            status = run_js(tmp_path, {"action": "split", "source": str(source),
                                       "output": str(zip_path), "regions": regions_text})
            self.assertEqual(status["kind"], "ok", status["text"])
            self.assertIn("Rỗng", status["text"])
            with zipfile.ZipFile(zip_path) as zf:
                self.assertIsNone(zf.testzip())
                self.assertEqual(zf.namelist(), ["Test.xlsx", "unmatched.xlsx"])
                self.assertTrue(all(info.flag_bits & 0x800 for info in zf.infolist()))
                zf.extractall(tmp_path / "out")
            self.assertEqual(region_snapshot(tmp_path / "out" / "Test.xlsx"), region_snapshot(python_output))
            unmatched = load_workbook(tmp_path / "out" / "unmatched.xlsx", data_only=True)["unmatched"]
            self.assertEqual(unmatched["B5"].value, "CONG TY B")
            self.assertIsNone(unmatched["B6"].value)


class BundleSyncTest(unittest.TestCase):
    def test_shipped_html_matches_template_and_vendored_inputs(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(template.count("__REGIONS__"), 1)
        self.assertEqual(template.count("/* EXCELJS_BUNDLE */"), 1)
        self.assertEqual(template.count("__CVNK_TEMPLATE_B64__"), 1)
        expected = (
            template
            .replace("__REGIONS__", escape(REGIONS.read_text(encoding="utf-8")))
            .replace("/* EXCELJS_BUNDLE */", EXCELJS.read_text(encoding="utf-8"))
            .replace("__CVNK_TEMPLATE_B64__", base64.b64encode(CVNK_TEMPLATE.read_bytes()).decode("ascii"))
        )
        self.assertEqual(BUNDLE.read_text(encoding="utf-8"), expected)


if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    )
    if result.wasSuccessful():
        print("PASS_MARKER: parity")
    raise SystemExit(0 if result.wasSuccessful() else 1)
