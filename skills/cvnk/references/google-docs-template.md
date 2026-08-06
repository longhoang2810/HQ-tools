# CVNK Google Docs Template

Use when the user wants the CVNK/Gửi thuế workflow to run inside Google Docs rather than by editing DOCX XML.

## Template placeholders

Create the template from the standard CVNK DOCX by replacing real dates with:

- `{{DOC_MONTH}}` — current month, two digits.
- `{{DOC_YEAR}}` — current year.
- `{{FROM_DATE}}` — first day of previous calendar month, `dd/mm/yyyy`.
- `{{TO_DATE}}` — last day of previous calendar month, `dd/mm/yyyy`.

In the document text:

```text
Phường Ngô Quyền, ngày     tháng {{DOC_MONTH}} năm {{DOC_YEAR}}
```

```text
từ ngày {{FROM_DATE}} đến ngày {{TO_DATE}}
```

For this user, the generated DOCX template was placed at:

```text
/Users/cheese/Google Drive/My Drive/Hải quan/CVNK_Gui_thue_template.docx
```

The user should open it in Drive with **Open with → Google Docs**, then save/use that Google Doc as the template.

## Apps Script menu

Paste this into **Extensions → Apps Script** on the Google Doc template, save, then reload the document.

```javascript
function onOpen() {
  DocumentApp.getUi()
    .createMenu('CVNK')
    .addItem('Cập nhật ngày tháng', 'updateCVNKDates')
    .addToUi();
}

function updateCVNKDates() {
  const doc = DocumentApp.getActiveDocument();
  const body = doc.getBody();

  const today = new Date();

  const currentMonth = String(today.getMonth() + 1).padStart(2, '0');
  const currentYear = String(today.getFullYear());

  const firstDayPrevMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
  const lastDayPrevMonth = new Date(today.getFullYear(), today.getMonth(), 0);

  const fromDate = formatDateVN(firstDayPrevMonth);
  const toDate = formatDateVN(lastDayPrevMonth);

  const replacements = {
    '\\{\\{DOC_MONTH\\}\\}': currentMonth,
    '\\{\\{DOC_YEAR\\}\\}': currentYear,
    '\\{\\{FROM_DATE\\}\\}': fromDate,
    '\\{\\{TO_DATE\\}\\}': toDate,
  };

  for (const [pattern, value] of Object.entries(replacements)) {
    body.replaceText(pattern, value);
  }

  doc.saveAndClose();

  DocumentApp.getUi().alert(
    `Đã cập nhật CVNK:\n` +
    `- Tháng/năm văn bản: ${currentMonth}/${currentYear}\n` +
    `- Kỳ báo cáo: ${fromDate} đến ${toDate}`
  );
}

function formatDateVN(date) {
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
}
```

## Pitfalls

- Copy the Google Doc template for the month before running the menu, because the script replaces placeholders with real dates.
- Prefer placeholders over regex matching real dates in Google Docs. `replaceText` on fixed placeholders is much safer for formatting.
- Do not do repeated Google Docs → DOCX → XML edit → upload loops for this workflow; use the Google Doc template and Apps Script menu when the user wants to work in Docs.
