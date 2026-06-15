import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QStackedWidget, QFrame, QLabel
)
from PyQt6.QtCore import Qt

from ui_components import APP_STYLE, create_button
from ui_pages import build_realtime_page, build_student_manage_page, build_image_attendance_page, build_report_page

def build_main_window() -> dict:
    """Khởi tạo Cửa sổ chính chứa Sidebar và các trang"""
    window = QMainWindow()
    window.setWindowTitle("ClassVision - Refactored")
    window.setMinimumSize(1024, 700)
    window.setStyleSheet(APP_STYLE)
    
    root_widget = QWidget()
    root_widget.setObjectName("AppRoot")
    window.setCentralWidget(root_widget)
    
    main_layout = QHBoxLayout(root_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    
    # 1. Tạo Sidebar (Thanh menu bên trái)
    sidebar = QFrame()
    sidebar.setObjectName("Sidebar")
    sidebar.setFixedWidth(240)
    sidebar_layout = QVBoxLayout(sidebar)
    
    lbl_logo = QLabel("CLASSVISION")
    lbl_logo.setObjectName("Title")
    lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
    sidebar_layout.addWidget(lbl_logo)
    sidebar_layout.addSpacing(30)
    
    btn_nav_camera = create_button("Điểm danh Camera")
    btn_nav_image = create_button("Điểm danh Ảnh tĩnh")
    btn_nav_student = create_button("Quản lý Sinh viên")
    btn_nav_report = create_button("Báo cáo Điểm danh")
    sidebar_layout.addWidget(btn_nav_camera)
    sidebar_layout.addWidget(btn_nav_image)
    sidebar_layout.addWidget(btn_nav_student)
    sidebar_layout.addWidget(btn_nav_report)
    sidebar_layout.addStretch()
    
    main_layout.addWidget(sidebar)
    
    # 2. Vùng chứa nội dung trang (QStackedWidget)
    stack = QStackedWidget()
    
    # Khởi tạo các trang từ ui_pages.py (kết quả trả về là dict)
    realtime_ui = build_realtime_page()
    image_ui = build_image_attendance_page()
    student_ui = build_student_manage_page()
    report_ui = build_report_page()
    
    stack.addWidget(realtime_ui["page"])      # index 0
    stack.addWidget(image_ui["page"])         # index 1
    stack.addWidget(student_ui["page"])       # index 2
    stack.addWidget(report_ui["page"])        # index 3
    
    main_layout.addWidget(stack)
    
    # 3. Logic chuyển trang cơ bản
    btn_nav_camera.clicked.connect(lambda: stack.setCurrentIndex(0))
    btn_nav_image.clicked.connect(lambda: stack.setCurrentIndex(1))
    btn_nav_student.clicked.connect(lambda: stack.setCurrentIndex(2))
    btn_nav_report.clicked.connect(lambda: stack.setCurrentIndex(3))
    
    return {
        "window": window,
        "stack": stack,
        "realtime_ui": realtime_ui,
        "image_ui": image_ui,
        "student_ui": student_ui,
        "report_ui": report_ui
    }

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ui = build_main_window()
    ui["window"].show()
    print("Test file main_window.py: OK!")
    sys.exit(app.exec())
