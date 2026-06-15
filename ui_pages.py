import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox
)
from PyQt6.QtCore import Qt

from ui_components import (
    create_button, create_kpi_card, create_attendance_table, create_video_label
)

def build_realtime_page() -> dict:
    """Xây dựng trang Điểm danh Real-time (Camera)"""
    page = QWidget()
    main_layout = QVBoxLayout(page)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(20)

    # 1. Tiêu đề và Nút điều khiển
    header_layout = QHBoxLayout()
    
    title_lbl = QLabel("TRỰC TIẾP TỪ CAMERA")
    title_lbl.setObjectName("Title")
    header_layout.addWidget(title_lbl)
    
    header_layout.addStretch()
    
    # Nút bật/tắt camera
    btn_start_camera = create_button("Bật Camera")
    btn_stop_camera = create_button("Tắt Camera")
    header_layout.addWidget(btn_start_camera)
    header_layout.addWidget(btn_stop_camera)
    
    main_layout.addLayout(header_layout)

    # 2. Thẻ hiển thị số liệu (KPI Cards)
    kpi_layout = QHBoxLayout()
    kpi_layout.addWidget(create_kpi_card("TỔNG SỐ", "0", "#E2C285"))    # Vàng Gold
    kpi_layout.addWidget(create_kpi_card("CÓ MẶT", "0", "#34D399"))     # Xanh lá
    kpi_layout.addWidget(create_kpi_card("VẮNG MẶT", "0", "#FB7185"))   # Đỏ
    kpi_layout.addWidget(create_kpi_card("ĐI TRỄ", "0", "#FBBF24"))      # Cam
    kpi_layout.addWidget(create_kpi_card("FPS", "0", "#A855F7"))         # Tím
    main_layout.addLayout(kpi_layout)

    # 3. Màn hình Camera và Cài đặt
    body_layout = QHBoxLayout()
    
    # Màn hình Video
    video_label = create_video_label()
    body_layout.addWidget(video_label, stretch=2)
    
    # Bảng điều khiển (Sidebar thu nhỏ)
    control_panel = QWidget()
    control_layout = QVBoxLayout(control_panel)
    
    control_layout.addWidget(QLabel("Chọn Lớp học:"))
    cb_class = QComboBox()
    cb_class.addItems(["-- Chọn Lớp --", "20HTTT1", "20HTTT2"])
    control_layout.addWidget(cb_class)
    
    control_layout.addSpacing(20)
    btn_export = create_button("Xuất File CSV")
    control_layout.addWidget(btn_export)
    
    control_layout.addStretch()
    body_layout.addWidget(control_panel, stretch=1)
    
    main_layout.addLayout(body_layout, stretch=1)

    # 4. Bảng danh sách điểm danh
    main_layout.addWidget(QLabel("DANH SÁCH SINH VIÊN:"))
    table = create_attendance_table()
    main_layout.addWidget(table, stretch=1)

    # Thay vì gán động lên object (gây lỗi Pylance), ta trả về một Dictionary
    return {
        "page": page,
        "btn_start_camera": btn_start_camera,
        "btn_stop_camera": btn_stop_camera,
        "btn_export": btn_export,
        "video_label": video_label,
        "table": table,
        "cb_class": cb_class,
        "kpi_cards": kpi_layout
    }


def build_student_manage_page() -> dict:
    """Xây dựng trang Quản lý Sinh viên (đơn giản)"""
    page = QWidget()
    layout = QVBoxLayout(page)
    
    title = QLabel("QUẢN LÝ SINH VIÊN")
    title.setObjectName("Title")
    layout.addWidget(title)
    
    # Ở mức đồ án sinh viên, tạm thời chỉ hiển thị danh sách từ CSV
    table = create_attendance_table()
    # Ẩn bớt các cột không cần thiết cho trang quản lý
    header = table.horizontalHeader()
    if header is not None:
        table.setColumnHidden(3, True) # Ẩn cột trạng thái
        table.setColumnHidden(4, True) # Ẩn cột thời gian
    
    layout.addWidget(table)
    
    # Nút làm mới
    btn_refresh = create_button("Làm mới danh sách")
    layout.addWidget(btn_refresh)
    
    return {
        "page": page,
        "table": table,
        "btn_refresh": btn_refresh
    }

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Tạo thử trang để test lỗi
    p1 = build_realtime_page()
    p2 = build_student_manage_page()
    
    print("Test file ui_pages.py: OK!")
