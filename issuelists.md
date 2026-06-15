# Danh sách Vấn đề & Nguyên tắc Code (Issue Lists)

Tài liệu này ghi chú lại các lỗi hoặc quyết định kỹ thuật đã gặp phải trong quá trình refactor để phòng tránh cho các Phase tiếp theo.

## 1. Quyết định Về Lỗi Import Namespace (Gặp ở Phase 1 & 2)
- **Vấn đề**: Việc dùng `from logic import ...` hay `from refactor.logic import ...` liên tục gây lỗi tùy thuộc vào việc người dùng chạy file test từ thư mục nào (từ thư mục gốc của project hay từ bên trong thư mục `refactor/`).
- **Giải pháp dứt điểm (Cho tất cả các phase sau)**:
  1. **Luôn dùng Absolute Import**: Bắt đầu bằng tên package `refactor`. (Ví dụ: `from refactor.config import ...`, `from refactor.logic import ...`).
  2. **Cách chạy App**: Bắt buộc người dùng phải đứng ở thư mục gốc của dự án (`classvision-student-recognition_v1`) và chạy lệnh `python -m refactor.main` hoặc chạy các script test từ thư mục gốc. Không được `cd refactor` rồi chạy trực tiếp.
  - Áp dụng nguyên tắc này cho Phase 3 (UI Components) và Phase 4 (Pages) để code hoàn toàn đồng nhất.

## 2. Lỗi Gán thuộc tính động (Dynamic Attribute Assignment) trên QWidget (Phase 4)
- **Vấn đề**: Việc viết `page.btn_start = btn_start` trên một instance của `QWidget` sẽ bị VS Code (Pylance) báo lỗi đỏ vì `QWidget` không có sẵn thuộc tính `btn_start`.
- **Giải pháp dứt điểm (Cho Phase 5)**:
  - Khi một hàm cần trả về nhiều widget con để tương tác, **tuyệt đối không gán thuộc tính động**.
  - Thay vào đó, trả về một **Dictionary**.
  - Ví dụ: `return {"page": page, "btn_start": btn_start}`. Sau đó ở file `main.py` ta sẽ truy cập bằng `ui["btn_start"]`.
