# Kế hoạch Refactor Thủ Công (Mức Đồ án Sinh viên)

Tài liệu này chia quá trình refactor ứng dụng thành các giai đoạn (phase) nhỏ. Cấu trúc được làm phẳng và đơn giản hóa (không chia quá nhiều class, không chia tầng phức tạp như enterprise), ưu tiên code thủ công để dễ kiểm soát.

**⚠️ QUY TẮC BẮT BUỘC (TEST SAU MỖI PHASE):**
Sau khi hoàn thành bất kỳ Phase nào, bắt buộc phải tự động chạy lệnh `python [tên_file].py` (ví dụ `python ui_components.py`) ngay trong thư mục `refactor/` để đảm bảo file vừa tạo không bị lỗi import hay syntax error. Nếu file in ra dòng chữ "Test file ... OK!" thì mới được coi là hoàn thành Phase.

---

## 🎯 Phase 1: Tạo các file cơ sở (Config & Logic)
**Mục tiêu:** Gom toàn bộ thiết lập và logic xử lý (đọc ghi CSV, điểm danh, AI) vào 2 file gốc cơ bản. Tránh tạo quá nhiều service rườm rà.

- [x] Dọn dẹp sạch thư mục `refactor/`.
- [x] Tạo `refactor/config.py`: Copy và hardcode trực tiếp các thông số cài đặt từ file cũ sang, loại bỏ module runtime_config phức tạp.
- [x] Tạo `refactor/logic.py`: Viết các hàm (function) cơ bản thay vì dùng class phức tạp để: đọc danh sách sinh viên từ CSV, lưu file điểm danh, khởi tạo model AI InsightFace.

**✅ Definition of Done (DoD):** Có 2 file `config.py` và `logic.py` hoàn chỉnh, không báo lỗi cú pháp.
**🔍 Verification:** Chạy `python -c "import refactor.config; import refactor.logic"`. Nếu không có lỗi `ModuleNotFoundError` hay lỗi cú pháp là đạt.
**🌟 Kết quả mong đợi:** Phần core logic gọn nhẹ, sẵn sàng gọi từ UI mà không cần qua nhiều bước trung gian.

---

## 🚀 Phase 2: Xử lý Đa luồng (Workers)
**Mục tiêu:** Gom các tác vụ chạy ngầm (Camera và AI) vào 1 file duy nhất để giữ UI luôn mượt.

- [x] Tạo file `refactor/workers.py`.
- [x] Chuyển logic của `camera_worker.py` và `recognition_worker.py` cũ vào chung file này. Tối giản hóa các tín hiệu (signals) truyền tải, chỉ giữ lại những gì thật sự cần cho UI.

**✅ Definition of Done (DoD):** File `workers.py` chứa đầy đủ mã nguồn cho luồng Camera và luồng Nhận diện khuôn mặt.
**🔍 Verification:** Đọc code thấy rõ 2 luồng QThread, không có lỗi import dư thừa.
**🌟 Kết quả mong đợi:** 1 file quản lý toàn bộ các tác vụ nặng, dễ bảo trì.

---

## 🎨 Phase 3: Giao diện dùng chung (UI Components)
**Mục tiêu:** Gom các tiện ích giao diện (fonts, icons, themes, widgets) vào 1 chỗ.

- [x] Tạo `refactor/ui_components.py`.
- [x] Chép code định dạng giao diện (Theme, Icon) và các khối widget (như KpiCard, Bảng điểm danh) vào file này. Cập nhật lại các đường dẫn file ảnh.

**✅ Definition of Done (DoD):** 1 file duy nhất `ui_components.py` chứa mọi thành phần dùng chung.
**🔍 Verification:** Chạy test script nhỏ import các component này lên màn hình để đảm bảo không bị lỗi resource.
**🌟 Kết quả mong đợi:** Dễ dàng gọi các nút bấm, bảng biểu ra dùng ở Phase sau mà code không bị lặp lại.

---

## ✂️ Phase 4: Tách các trang Giao diện (UI Pages)
**Mục tiêu:** Chia nhỏ file `main_window.py` (hơn 1400 dòng) hiện tại bằng cách đưa logic mỗi trang ra file riêng.

- [x] Tạo `refactor/ui_pages.py` (hoặc có thể chia nhẹ thành 2 file `page_realtime.py`, `page_image.py` nếu dài).
- [x] Code lại giao diện của các trang: Điểm danh trực tiếp, Điểm danh ảnh, Quản lý sinh viên... Thành các hàm dựng UI đơn giản.

**✅ Definition of Done (DoD):** Có các class/hàm xây dựng giao diện rõ ràng cho từng trang độc lập, không còn nằm chung 1 file khổng lồ.
**🔍 Verification:** Kiểm tra mã nguồn thấy sự tách biệt logic rõ ràng, mỗi trang là một module tự quản lý nút bấm của nó.
**🌟 Kết quả mong đợi:** Logic giao diện rành mạch, dễ thêm/bớt tính năng.

---

## 🏗️ Phase 5: Khung Cửa Sổ Chính & Entry Point
**Mục tiêu:** Lắp ráp Sidebar và các trang lại với nhau để chạy ứng dụng.

- [x] Viết `refactor/main_window.py`: File này chỉ còn lại code vẽ Sidebar và chuyển tab qua lại bằng `QStackedWidget`.
- [x] Tạo `refactor/main.py`: Entry point ngắn gọn chứa hàm `if __name__ == '__main__':` khởi động ứng dụng.

**✅ Definition of Done (DoD):** Ứng dụng chạy lên được, `main_window.py` siêu ngắn gọn chỉ điều hướng trang.
**🔍 Verification:** User xem file `main_window.py` mới, sẽ thấy số lượng dòng code giảm đáng kể (chỉ chứa setup Sidebar và chuyển trang).
**🌟 Kết quả mong đợi:** Ứng dụng đã được kết nối hoàn chỉnh.

---

## ✅ Phase 6: Kiểm thử toàn hệ thống
**Mục tiêu:** Xác minh phần mềm bản refactor hoạt động đúng chức năng của bản gốc.

- [ ] Chạy lệnh `python refactor/main.py`.
- [ ] Thử bật Camera điểm danh và tắt đi.
- [ ] Thử tính năng điểm danh bằng ảnh.

**✅ Definition of Done (DoD):** App không bị crash, chuyển trang mượt mà. Chức năng nhận diện sinh viên, lưu file CSV chạy đúng.
**🔍 Verification:** User trực tiếp thao tác.
**🌟 Kết quả mong đợi:** 100% hoàn thành refactor sang kiến trúc đơn giản cho sinh viên mà không phá vỡ UI/UX gốc.
