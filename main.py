import os
import sys
import onnxruntime # Bắt buộc phải import ONNX Runtime ĐẦU TIÊN để tránh xung đột DLL với PyQt6 và OpenCV
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

from main_window import build_main_window
from workers import start_camera, stop_camera
from logic import recognize_faces_in_frame, get_all_classes
from ui_components import draw_boxes_on_image
from config import DEFAULT_TOTAL_STUDENTS

class _GuiInvoker(QObject):
    """Lớp ẩn nhỏ bé duy nhất để ép hàm chạy về luồng chính (Main Thread) an toàn"""
    invoke_signal = pyqtSignal(object)

_invoker = _GuiInvoker()
_invoker.invoke_signal.connect(lambda func: func())

def invoke_in_gui(func):
    """Ép một hàm chạy trên luồng chính (GUI thread) để an toàn vẽ giao diện."""
    try:
        _invoker.invoke_signal.emit(func)
    except RuntimeError:
        pass # Bỏ qua nếu app đã tắt và _invoker bị hủy

def setup_app_logic(ui: dict):
    """Gắn kết logic từ workers vào giao diện"""
    rt_ui = ui["realtime_ui"]
    
    def on_frame_ready(frame, ai_results, fps):
        # 1. Vẽ khung OpenCV lên ảnh NGAY TẠI LUỒNG NGẦM (Nhanh, không làm đơ GUI)
        qimg = draw_boxes_on_image(frame, ai_results)
        
        # 2. Chỉ đẩy tấm hình đã vẽ xong lên giao diện ở luồng chính
        def update_ui():
            from PyQt6.QtGui import QPixmap
            rt_ui["video_label"].setPixmap(QPixmap.fromImage(qimg))
            # Đếm số người có mặt (loại bỏ Unknown)
            present_count = sum(1 for d in ai_results if d.get("status") != "unknown")
            absent_count = max(0, DEFAULT_TOTAL_STUDENTS - present_count)
            
            # Cập nhật KPI Có Mặt (Thẻ thứ 2, index 1)
            rt_ui["kpi_cards"].itemAt(1).widget().layout().itemAt(1).layout().itemAt(1).widget().setText(str(present_count))
            # Cập nhật KPI Vắng Mặt (Thẻ thứ 3, index 2)
            rt_ui["kpi_cards"].itemAt(2).widget().layout().itemAt(1).layout().itemAt(1).widget().setText(str(absent_count))
            # Cập nhật KPI FPS (Thẻ thứ 4, index 3 - do đã xóa thẻ Đi Trễ)
            rt_ui["kpi_cards"].itemAt(3).widget().layout().itemAt(1).layout().itemAt(1).widget().setText(str(fps))
        
        invoke_in_gui(update_ui)

    def on_camera_error(err_msg):
        def update_err():
            rt_ui["video_label"].setText(err_msg)
        invoke_in_gui(update_err)

    # Gắn sự kiện cho nút bấm (thêm *args để tránh lỗi tham số checked của PyQt)
    rt_ui["btn_start_camera"].clicked.connect(
        lambda *args: start_camera(on_frame_ready, on_camera_error)
    )
    rt_ui["btn_stop_camera"].clicked.connect(stop_camera)
    
    # Đổ dữ liệu Lớp học thực tế từ Database vào ComboBox
    cb_class = rt_ui["cb_class"]
    cb_class.clear()
    cb_class.addItem("-- Chọn Lớp --")
    
    real_classes = get_all_classes()
    if real_classes:
        cb_class.addItems(real_classes)
    else:
        # Nếu chưa có lớp nào trong DB thì hiện thông báo
        cb_class.addItem("(Chưa có dữ liệu lớp)")

def setup_student_manage_logic(ui):
    from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox
    from ui_pages import StudentDialog
    from logic import get_students, add_student, update_student, delete_student
    
    st_ui = ui["student_ui"]
    table = st_ui["table"]
    
    def load_data():
        search_text = st_ui["txt_search"].text().strip()
        students = get_students(search_text)
        
        table.setRowCount(0)
        for row_idx, student in enumerate(students):
            table.insertRow(row_idx)
            # student tuple: (student_id, full_name, class_name)
            table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1))) # Cột STT
            table.setItem(row_idx, 1, QTableWidgetItem(student[0])) # MSSV
            table.setItem(row_idx, 2, QTableWidgetItem(student[1])) # Họ Tên
            table.setItem(row_idx, 3, QTableWidgetItem(student[2])) # Lớp
            
    def on_add():
        dialog = StudentDialog(ui["window"])
        if dialog.exec():
            mssv, name, class_name = dialog.get_data()
            if not mssv or not name:
                QMessageBox.warning(ui["window"], "Lỗi", "Vui lòng nhập đủ MSSV và Họ tên!")
                return
            success, msg = add_student(mssv, name, class_name)
            if success:
                load_data()
            else:
                QMessageBox.warning(ui["window"], "Lỗi", msg)
                
    def on_edit():
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(ui["window"], "Lỗi", "Vui lòng chọn một sinh viên để sửa!")
            return
            
        mssv = table.item(current_row, 1).text()
        name = table.item(current_row, 2).text()
        class_name = table.item(current_row, 3).text()
        
        dialog = StudentDialog(ui["window"], student_data=(mssv, name, class_name))
        if dialog.exec():
            _, new_name, new_class = dialog.get_data()
            success, msg = update_student(mssv, new_name, new_class)
            if success:
                load_data()
            else:
                QMessageBox.warning(ui["window"], "Lỗi", msg)
                
    def on_delete():
        current_row = table.currentRow()
        if current_row < 0:
            QMessageBox.warning(ui["window"], "Lỗi", "Vui lòng chọn một sinh viên để xóa!")
            return
            
        mssv = table.item(current_row, 1).text()
        name = table.item(current_row, 2).text()
        
        reply = QMessageBox.question(
            ui["window"], "Xác nhận xóa", 
            f"Bạn có chắc muốn xóa sinh viên {name} ({mssv})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, msg = delete_student(mssv)
            if success:
                load_data()
            else:
                QMessageBox.warning(ui["window"], "Lỗi", msg)
    
    # Kết nối Signal
    st_ui["btn_search"].clicked.connect(load_data)
    st_ui["txt_search"].returnPressed.connect(load_data)
    st_ui["btn_refresh"].clicked.connect(lambda: [st_ui["txt_search"].clear(), load_data()])
    st_ui["btn_add"].clicked.connect(on_add)
    st_ui["btn_edit"].clicked.connect(on_edit)
    st_ui["btn_delete"].clicked.connect(on_delete)
    
    # Tải dữ liệu lần đầu
    load_data()

def setup_image_attendance_logic(ui):
    from PyQt6.QtWidgets import QFileDialog, QTableWidgetItem, QMessageBox
    from PyQt6.QtGui import QPixmap
    import cv2
    from logic import recognize_faces_in_frame
    from ui_components import draw_boxes_on_image
    from config import DEFAULT_TOTAL_STUDENTS
    import datetime
    
    img_ui = ui["image_ui"]
    
    def on_upload_image():
        file_path, _ = QFileDialog.getOpenFileName(
            ui["window"], "Chọn ảnh điểm danh", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if not file_path:
            return
            
        img_ui["btn_upload"].setText("Đang xử lý AI...")
        # Ép UI cập nhật ngay lập tức
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
        
        # Đọc ảnh
        frame = cv2.imread(file_path)
        if frame is None:
            QMessageBox.warning(ui["window"], "Lỗi", "Không thể đọc file ảnh!")
            img_ui["btn_upload"].setText("Chọn ảnh tải lên...")
            return
            
        # Resize ảnh nếu quá lớn để không bị lag giao diện
        h, w = frame.shape[:2]
        if w > 1920:
            scale = 1920 / w
            frame = cv2.resize(frame, (1920, int(h * scale)))
            
        # Gọi AI (chạy thẳng luôn vì đây là ảnh tĩnh, không cần luồng ngầm)
        results = recognize_faces_in_frame(frame)
        
        # Vẽ boxes
        qimg = draw_boxes_on_image(frame, results)
        img_ui["image_label"].setPixmap(QPixmap.fromImage(qimg))
        
        # Cập nhật KPIs
        present_count = sum(1 for d in results if d.get("status") in ("present", "uncertain"))
        unknown_count = sum(1 for d in results if d.get("status") == "unknown")
        absent_count = max(0, DEFAULT_TOTAL_STUDENTS - present_count)
        
        img_ui["kpi_cards"].itemAt(1).widget().layout().itemAt(1).layout().itemAt(1).widget().setText(str(present_count))
        img_ui["kpi_cards"].itemAt(2).widget().layout().itemAt(1).layout().itemAt(1).widget().setText(str(absent_count))
        img_ui["kpi_cards"].itemAt(3).widget().layout().itemAt(1).layout().itemAt(1).widget().setText(str(unknown_count))
        
        # Điền bảng
        table = img_ui["table"]
        table.setRowCount(0)
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Chỉ lấy những người có mặt
        detected_students = [d for d in results if d.get("status") != "unknown"]
        for row_idx, student in enumerate(detected_students):
            table.insertRow(row_idx)
            table.setItem(row_idx, 0, QTableWidgetItem(str(row_idx + 1))) # STT
            table.setItem(row_idx, 1, QTableWidgetItem(student.get("student_id", ""))) # MSSV
            table.setItem(row_idx, 2, QTableWidgetItem(student.get("name", ""))) # Name
            table.setItem(row_idx, 3, QTableWidgetItem("N/A")) # Lớp (tạm ẩn)
            
            # Cột trạng thái
            status_text = "Có mặt" if student.get("status") == "present" else "Cần xem xét"
            item_status = QTableWidgetItem(status_text)
            from PyQt6.QtGui import QColor
            color = "#34D399" if student.get("status") == "present" else "#FBBF24"
            item_status.setForeground(QColor(color))
            table.setItem(row_idx, 4, item_status)
            
            table.setItem(row_idx, 5, QTableWidgetItem(time_str)) # Time
            
        img_ui["btn_upload"].setText("Chọn ảnh tải lên...")
        
    img_ui["btn_upload"].clicked.connect(on_upload_image)

def main():
    app = QApplication(sys.argv)
    
    # 1. Dựng giao diện
    ui = build_main_window()
    
    # 2. Gắn kết logic (Nút bấm -> Camera -> AI -> Vẽ hình)
    setup_app_logic(ui)
    setup_student_manage_logic(ui)
    setup_image_attendance_logic(ui)
    
    # 3. Hiển thị
    ui["window"].showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
