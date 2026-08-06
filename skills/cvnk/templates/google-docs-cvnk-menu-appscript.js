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
