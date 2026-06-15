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
from config import DEFAULT_TOTAL_STUDENTS

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
    kpi_layout.addWidget(create_kpi_card("TỔNG SỐ", str(DEFAULT_TOTAL_STUDENTS), "#E2C285"))    # Vàng Gold
    kpi_layout.addWidget(create_kpi_card("CÓ MẶT", "0", "#34D399"))     # Xanh lá
    kpi_layout.addWidget(create_kpi_card("VẮNG MẶT", str(DEFAULT_TOTAL_STUDENTS), "#FB7185"))   # Đỏ
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

    # Thay vì gán động lên object (gây lỗi Pylance), ta trả về một Dictionary
    return {
        "page": page,
        "btn_start_camera": btn_start_camera,
        "btn_stop_camera": btn_stop_camera,
        "btn_export": btn_export,
        "video_label": video_label,
        "cb_class": cb_class,
        "kpi_cards": kpi_layout
    }


from PyQt6.QtWidgets import QLineEdit, QDialog, QFormLayout, QDialogButtonBox, QMessageBox

def build_student_manage_page() -> dict:
    """Xây dựng trang Quản lý Sinh viên với CRUD cơ bản"""
    page = QWidget()
    layout = QVBoxLayout(page)
    
    title = QLabel("QUẢN LÝ SINH VIÊN")
    title.setObjectName("Title")
    layout.addWidget(title)
    
    # -- Thanh công cụ (Toolbar) --
    toolbar = QHBoxLayout()
    
    txt_search = QLineEdit()
    txt_search.setPlaceholderText("Tìm kiếm theo MSSV hoặc Họ tên...")
    txt_search.setStyleSheet("padding: 8px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); background: #0C101A;")
    toolbar.addWidget(txt_search, stretch=2)
    
    btn_search = create_button("Tìm kiếm")
    toolbar.addWidget(btn_search)
    
    toolbar.addSpacing(20)
    
    btn_add = create_button("+ Thêm mới")
    btn_add.setStyleSheet("background: #34D399; color: #07090F; font-weight: bold; padding: 8px; border-radius: 8px;")
    toolbar.addWidget(btn_add)
    
    btn_edit = create_button("Sửa")
    toolbar.addWidget(btn_edit)
    
    btn_delete = create_button("Xóa")
    btn_delete.setStyleSheet("background: #FB7185; color: #07090F; font-weight: bold; padding: 8px; border-radius: 8px;")
    toolbar.addWidget(btn_delete)
    
    layout.addLayout(toolbar)
    
    # -- Bảng dữ liệu --
    table = create_attendance_table()
    # Ẩn bớt các cột Trạng thái, Thời gian cho trang này vì không dùng đến
    header = table.horizontalHeader()
    if header is not None:
        table.setColumnHidden(4, True) # Trạng thái
        table.setColumnHidden(5, True) # Thời gian
    layout.addWidget(table)
    
    # Nút làm mới
    btn_refresh = create_button("Làm mới danh sách")
    layout.addWidget(btn_refresh)
    
    return {
        "page": page,
        "table": table,
        "txt_search": txt_search,
        "btn_search": btn_search,
        "btn_add": btn_add,
        "btn_edit": btn_edit,
        "btn_delete": btn_delete,
        "btn_refresh": btn_refresh
    }

class StudentDialog(QDialog):
    """Hộp thoại Thêm/Sửa Sinh Viên"""
    def __init__(self, parent=None, student_data=None):
        super().__init__(parent)
        self.setWindowTitle("Thêm Sinh Viên" if student_data is None else "Sửa Sinh Viên")
        self.setMinimumWidth(400)
        self.setStyleSheet("background: #0C101A; color: white;")
        
        layout = QFormLayout(self)
        
        self.txt_mssv = QLineEdit()
        self.txt_name = QLineEdit()
        self.txt_class = QLineEdit()
        
        input_style = "padding: 8px; border: 1px solid #E2C285; border-radius: 4px; background: #07090F;"
        self.txt_mssv.setStyleSheet(input_style)
        self.txt_name.setStyleSheet(input_style)
        self.txt_class.setStyleSheet(input_style)
        
        layout.addRow("MSSV:", self.txt_mssv)
        layout.addRow("Họ Tên:", self.txt_name)
        layout.addRow("Lớp:", self.txt_class)
        
        if student_data:
            self.txt_mssv.setText(student_data[0])
            self.txt_mssv.setReadOnly(True) # Không cho sửa MSSV khi đang Sửa
            self.txt_name.setText(student_data[1])
            self.txt_class.setText(student_data[2])
            
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        # Style cho button
        for btn in self.buttons.buttons():
            btn.setStyleSheet("background: #E2C285; color: #07090F; padding: 6px 12px; border-radius: 4px; font-weight: bold;")
        
        layout.addWidget(self.buttons)
        
    def get_data(self):
        return (
            self.txt_mssv.text().strip(),
            self.txt_name.text().strip(),
            self.txt_class.text().strip()
        )

def build_image_attendance_page() -> dict:
    """Xây dựng trang Điểm danh bằng Ảnh tĩnh"""
    page = QWidget()
    main_layout = QVBoxLayout(page)
    
    # 1. Tiêu đề và nút Tải ảnh
    header_layout = QHBoxLayout()
    title = QLabel("ĐIỂM DANH BẰNG ẢNH")
    title.setObjectName("Title")
    header_layout.addWidget(title)
    
    header_layout.addStretch()
    
    btn_upload = create_button("Chọn ảnh tải lên...")
    btn_upload.setStyleSheet("background: #A855F7; color: #07090F; font-weight: bold; padding: 10px 20px; border-radius: 8px;")
    header_layout.addWidget(btn_upload)
    
    main_layout.addLayout(header_layout)
    
    # 2. Bảng kết quả tổng quan (KPIs cho Ảnh)
    kpi_layout = QHBoxLayout()
    kpi_layout.addWidget(create_kpi_card("TỔNG SỐ", str(DEFAULT_TOTAL_STUDENTS), "#E2C285"))    # Vàng Gold
    kpi_layout.addWidget(create_kpi_card("CÓ MẶT (ẢNH)", "0", "#34D399"))     # Xanh lá
    kpi_layout.addWidget(create_kpi_card("VẮNG MẶT", str(DEFAULT_TOTAL_STUDENTS), "#FB7185"))   # Đỏ
    kpi_layout.addWidget(create_kpi_card("UNKNOWN", "0", "#A855F7"))         # Tím
    main_layout.addLayout(kpi_layout)
    
    # 3. Màn hình Ảnh và Danh sách
    body_layout = QHBoxLayout()
    
    # Khung hiển thị ảnh gốc sau khi vẽ boxes
    image_label = create_video_label()
    image_label.setText("Chưa có ảnh nào được chọn.")
    body_layout.addWidget(image_label, stretch=2)
    
    # Bảng kết quả bên phải
    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(0, 0, 0, 0)
    
    right_layout.addWidget(QLabel("DANH SÁCH NHẬN DIỆN:"))
    table = create_attendance_table()
    right_layout.addWidget(table)
    
    body_layout.addWidget(right_panel, stretch=1)
    
    main_layout.addLayout(body_layout, stretch=1)
    
    return {
        "page": page,
        "btn_upload": btn_upload,
        "image_label": image_label,
        "table": table,
        "kpi_cards": kpi_layout
    }

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Tạo thử trang để test lỗi
    p1 = build_realtime_page()
    p2 = build_student_manage_page()
    
    print("Test file ui_pages.py: OK!")
