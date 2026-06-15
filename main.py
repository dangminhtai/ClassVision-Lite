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

def main():
    app = QApplication(sys.argv)
    
    # 1. Dựng giao diện
    ui = build_main_window()
    
    # 2. Gắn kết logic (Nút bấm -> Camera -> AI -> Vẽ hình)
    setup_app_logic(ui)
    setup_student_manage_logic(ui)
    
    # 3. Hiển thị
    ui["window"].showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
