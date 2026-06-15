import os
import sys
import onnxruntime # Bắt buộc phải import ONNX Runtime ĐẦU TIÊN để tránh xung đột DLL với PyQt6 và OpenCV
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

from main_window import build_main_window
from workers import start_camera, stop_camera
from logic import recognize_faces_in_frame
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
    
    def on_frame_ready(frame):
        # Frame mới từ Camera (đang ở luồng ngầm của camera)
        # 1. Chạy AI NGAY TẠI ĐÂY (đồng bộ) để không đẻ thêm thread rác
        result = recognize_faces_in_frame(frame)
        
        # 2. Đẩy hình lên GUI
        def update_ui():
            pixmap = draw_boxes_on_image(frame, result)
            rt_ui["video_label"].setPixmap(pixmap)
            # Cập nhật KPI Có Mặt
            rt_ui["kpi_cards"].itemAt(1).widget().layout().itemAt(1).layout().itemAt(1).widget().setText(str(len(result)))
        
        invoke_in_gui(update_ui)

    def on_camera_error(err_msg):
        def update_err():
            rt_ui["video_label"].setText(err_msg)
        invoke_in_gui(update_err)

    # Gắn sự kiện cho nút bấm (thêm *args để tránh lỗi tham số checked của PyQt)
    rt_ui["btn_start_camera"].clicked.connect(
        lambda *args: start_camera(on_frame_ready, on_camera_error)
    )
    rt_ui["btn_stop_camera"].clicked.connect(lambda *args: stop_camera())

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
