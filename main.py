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
            
            # Cập nhật KPI Có Mặt
            rt_ui["kpi_cards"].itemAt(1).widget().layout().itemAt(1).layout().itemAt(1).widget().setText(str(len(ai_results)))
            # Cập nhật KPI FPS (Thẻ thứ 5, index 4)
            rt_ui["kpi_cards"].itemAt(4).widget().layout().itemAt(1).layout().itemAt(1).widget().setText(str(fps))
        
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

def main():
    app = QApplication(sys.argv)
    
    # 1. Dựng giao diện
    ui = build_main_window()
    
    # 2. Gắn kết logic (Nút bấm -> Camera -> AI -> Vẽ hình)
    setup_app_logic(ui)
    
    # 3. Hiển thị
    ui["window"].show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
