---
name: cvnk
description: "Use when updating the customs tax notification Word document (công văn nhập khẩu tại chỗ / gửi thuế). Fills the 'Phường ..., ngày ... tháng ... năm ...' line with blank day and current month/year, and fills the reporting period 'từ ngày ... đến ngày ...' with the first/last day of the previous calendar month, preserving .docx structure to avoid Word unreadable-content warnings."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [word, docx, customs, tax, vietnamese, cvnk]
    related_skills: [nktc, ocr-and-documents]
---

# CVNK – Update Word Tax Notification Dates

## When to Use

Use this skill when the user points to a Word document such as `Gửi thuế.docx`, `file gửi thuế.docx`, or a customs/tax notification letter and asks to update:

- The line beginning with `Phường ... ngày ... tháng ... năm ...`
- The paragraph containing `từ ngày ... đến ngày ...`

This workflow is for monthly customs/tax notification documents. It preserves the original Word package and edits only `word/document.xml` text nodes, because rebuilding XML with generic XML serializers can make Microsoft Word show `Word found unreadable content`.

## Date Rules

- `Phường ..., ngày ... tháng ... năm ...`:
  - Leave the day blank.
  - Fill current month and current year.
  - Example for 2026-06-01: `Phường Ngô Quyền, ngày     tháng 06 năm 2026`
- Reporting period paragraph:
  - Fill the previous calendar month.
  - Use the correct last day of that month (`28/29/30/31` as appropriate).
  - Example for 2026-06-01: `từ ngày 01/05/2026 đến ngày 31/05/2026`

## Google Docs Template Workflow

When the user wants to work in Google Docs instead of DOCX XML:

1. Create a clean `.docx` template from the standard CVNK file by replacing real dates with placeholders while preserving existing `w:t` nodes and paragraph/run structure:
   - Date line: `ngày     tháng {{DOC_MONTH}} năm {{DOC_YEAR}}`
   - Period line: `từ ngày {{FROM_DATE}} đến ngày {{TO_DATE}}`
2. Upload/copy the template to the user's Drive Hải quan folder, currently visible via Google Drive Desktop as:
   - `/Users/cheese/Google Drive/My Drive/Hải quan/CVNK_Gui_thue_template.docx`
3. Tell the user to open the DOCX in Drive with **Open with → Google Docs** and save it as a Google Doc template.
4. Attach an Apps Script menu to the Google Doc template, then reload the document. See `references/google-docs-template.md` for the ready-to-paste Apps Script.
5. Use this when the user wants a reusable Google Docs workflow. It avoids export/edit/re-upload loops and lets the user copy the template each month, then run **CVNK → Cập nhật ngày tháng**. Remind them to copy the template before running the script because placeholders are replaced with real dates.

## DOCX XML Workflow

1. Locate the source file, usually on Desktop:

```bash
python3 - <<'PY'
import glob, os
for p in glob.glob(os.path.expanduser('~/Desktop/*.docx')):
    if not os.path.basename(p).startswith('~$'):
        print(p)
PY
```

2. Before editing, create a backup if one does not already exist. For Desktop `Gửi thuế.docx`, use:

```text
/Users/cheese/Desktop/Gửi thuế.backup.docx
```

3. Edit the `.docx` as a zip file and modify only `word/document.xml` with string/regex replacement. Do **not** parse and reserialize the whole XML using `xml.etree.ElementTree` or similar, because that may alter namespace prefixes/markup and cause Word unreadable-content warnings.

Use this script pattern, adjusting `src`/`orig` if the filename differs:

```python
import zipfile, shutil, tempfile, os, re, datetime, calendar, html

src = '/Users/cheese/Desktop/Gửi thuế.docx'
orig = '/Users/cheese/Desktop/Gửi thuế.backup.docx'
if not os.path.exists(orig):
    shutil.copy2(src, orig)

# Use the original backup as the clean base when repairing a file that Word warns about.
base = orig if os.path.exists(orig) else src

today = datetime.date.today()
first_prev = (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)
last_prev = first_prev.replace(day=calendar.monthrange(first_prev.year, first_prev.month)[1])
phuong_date = f'ngày     tháng {today.month:02d} năm {today.year}'
period = f'từ ngày {first_prev.day:02d}/{first_prev.month:02d}/{first_prev.year} đến ngày {last_prev.day:02d}/{last_prev.month:02d}/{last_prev.year}'

wt_re = re.compile(r'(<w:t\\b[^>]*>)(.*?)(</w:t>)', re.S)
p_re = re.compile(r'<w:p\\b.*?</w:p>', re.S)

def visible_text(pxml):
    return ''.join(html.unescape(m.group(2)) for m in wt_re.finditer(pxml))

def xml_escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def replace_visible_preserve_runs(pxml, pattern, repl):
    """Replace visible text spanning w:t nodes while preserving paragraph/run structure."""
    matches = list(wt_re.finditer(pxml))
    if not matches:
        return pxml, 0
    texts = [html.unescape(m.group(2)) for m in matches]
    full = ''.join(texts)
    hit = pattern.search(full)
    if not hit:
        return pxml, 0
    start, end = hit.span()
    spans = []
    pos = 0
    for t in texts:
        spans.append((pos, pos + len(t)))
        pos += len(t)
    new_texts = texts[:]
    inserted = False
    for i, (a, b) in enumerate(spans):
        if b <= start or a >= end:
            continue
        local_start = max(start - a, 0)
        local_end = min(end - a, len(texts[i]))
        before = texts[i][:local_start]
        after = texts[i][local_end:]
        if not inserted:
            new_texts[i] = before + repl + after
            inserted = True
        else:
            new_texts[i] = before + after
    out = []
    last = 0
    for i, m in enumerate(matches):
        out.append(pxml[last:m.start()])
        open_tag = m.group(1)
        if ('xml:space=' not in open_tag) and (new_texts[i].startswith(' ') or new_texts[i].endswith(' ') or '  ' in new_texts[i]):
            open_tag = open_tag[:-1] + ' xml:space="preserve">'
        out.append(open_tag + xml_escape(new_texts[i]) + m.group(3))
        last = m.end()
    out.append(pxml[last:])
    return ''.join(out), 1

changed_date = 0
changed_period = 0
pat_date = re.compile(r'ngày\s*\d{0,2}\s*tháng\s*\d{1,2}\s*năm\s*\d{4}')
pat_period = re.compile(r'từ ngày\s*\d{1,2}/\d{1,2}/\d{4}\s*đến ngày\s*\d{1,2}/\d{1,2}/\d{4}')

def process_paragraph(m):
    global changed_date, changed_period
    pxml = m.group(0)
    txt = visible_text(pxml)
    out = pxml
    if 'Phường' in txt and 'ngày' in txt and 'tháng' in txt and 'năm' in txt:
        out, n = replace_visible_preserve_runs(out, pat_date, phuong_date)
        changed_date += n
    txt2 = visible_text(out)
    if 'từ ngày' in txt2 and 'đến ngày' in txt2:
        out, n = replace_visible_preserve_runs(out, pat_period, period)
        changed_period += n
    return out

with zipfile.ZipFile(base, 'r') as zin:
    xml = zin.read('word/document.xml').decode('utf-8')
    new_xml = p_re.sub(process_paragraph, xml)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
    tmp.close()
    with zipfile.ZipFile(tmp.name, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == 'word/document.xml':
                data = new_xml.encode('utf-8')
            zout.writestr(item, data)
shutil.move(tmp.name, src)
print('updated:', src)
print('backup:', orig)
print('phuong date replacements:', changed_date, '->', phuong_date)
print('period replacements:', changed_period, '->', period)
```

## Verification

After editing, validate the docx package and XML:

```bash
python3 - <<'PY'
import zipfile
from xml.parsers.expat import ParserCreate
p = '/Users/cheese/Desktop/Gửi thuế.docx'
with zipfile.ZipFile(p) as z:
    bad = z.testzip()
    print('zip test:', 'OK' if bad is None else bad)
    xml = z.read('word/document.xml')
ParserCreate().Parse(xml, True)
print('xml parse: OK')
PY
```

Optionally count the replacements:

```bash
python3 - <<'PY'
import zipfile, re, html
p = '/Users/cheese/Desktop/Gửi thuế.docx'
with zipfile.ZipFile(p) as z:
    text = html.unescape(re.sub(r'<[^>]+>', '', z.read('word/document.xml').decode('utf-8')))
print(text.count('ngày     tháng'))
print(text.count('từ ngày'))
PY
```

## Pitfalls

- Do not edit the temporary lock file beginning with `~$`.
- Do not use `xml.etree.ElementTree` to rewrite the whole document XML; it can alter prefixes/markup and trigger Word's unreadable-content warning.
- Do not collapse all paragraph text into the first `w:t` node. Replace only the matched visible date span across existing `w:t` nodes so paragraph/run structure, centering, and spacing such as the gap between `Mẫu số 01/...` and the next line stay unchanged.
- If Word reports unreadable content after a previous bad edit, rebuild from the clean `.backup.docx` and apply the safe string-based replacement.
- Preserve `xml:space="preserve"` or add it to the first replacement text node so the blank day spacing is retained.
- Always calculate the previous month using calendar logic, not hard-coded `30` days.
