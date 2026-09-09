# HQ-tools: ghi chú cho Claude

## Google Drive
- Công cụ Drive chỉ nhận nội dung inline (base64), không thay được nội dung file đã có, không upload từ đường dẫn.
- Sửa file trên máy, gửi vào chat bằng SendUserFile để duyệt, chỉ upload Drive một lần ở bản chốt.
- Thay bản cũ trên Drive: tạo file mới rồi trash_file bản cũ (link đổi), hoặc để người dùng tự "Quản lý phiên bản" nếu cần giữ link.
- Upload docx với disableConversionToGoogleType=true.

## Môi trường phiên web
- PDF: thiếu pdftoppm, dùng pymupdf render trang ra PNG.
- docx npm phải npm install; kiểm tra docx bằng python-docx, LibreOffice không chạy được.
- Proxy chặn các trang luật Việt Nam; sau lần WebFetch đầu thất bại, nhờ người dùng tải văn bản lên.
