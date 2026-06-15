import cv2
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QImage, QPixmap
from PyQt6.QtWidgets import (
    QAbstractItemView, QFrame, QHBoxLayout, QHeaderView, 
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)

# ==========================================
# 1. GIAO DIỆN (THEME & CSS TỐI GIẢN)
# ==========================================
DESIGN_TOKENS = {
    "bg": "#07090F", "bg2": "#0C101A", "panel": "rgba(255, 255, 255, 0.03)",
    "ink": "#F8FAFC", "ink2": "#94A3B8", "muted": "#64748B",
    "gold": "#E2C285", "mint": "#34D399", "coral": "#FB7185", "cyan": "#38BDF8", "amber": "#FBBF24"
}

APP_STYLE = """
* { font-family: "Segoe UI", sans-serif; font-size: 14px; color: @ink; }
QMainWindow, QWidget#AppRoot { background: @bg; }
QFrame#Sidebar { background: @bg2; border-right: 1px solid rgba(255,255,255,0.08); }
QFrame#Panel { background: @panel; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; }
QLabel#Title { font-size: 24px; font-weight: bold; color: @gold; }
QPushButton { background: @panel; border: 1px solid @gold; border-radius: 8px; padding: 10px; color: @gold; }
QPushButton:hover { background: @gold; color: @bg; }
QTableWidget { background: transparent; border: none; gridline-color: rgba(255,255,255,0.08); }
QHeaderView::section { background: @bg2; color: @ink2; padding: 8px; border: none; font-weight: bold; }
"""
for token, value in sorted(DESIGN_TOKENS.items(), key=lambda kv: -len(kv[0])):
    APP_STYLE = APP_STYLE.replace(f"@{token}", value)

# ==========================================
# 2. HÀM TẠO WIDGETS (KHÔNG DÙNG CLASS)
# ==========================================

def create_button(text: str) -> QPushButton:
    """Tạo nút bấm tiêu chuẩn"""
    btn = QPushButton(text)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    return btn

def create_kpi_card(title: str, value: str, accent_color: str) -> QFrame:
    """Tạo thẻ hiển thị thông số (VD: Tổng số SV, Có mặt)"""
    card = QFrame()
    card.setObjectName("Panel")
    layout = QHBoxLayout(card)
    
    # Vạch màu bên trái
    bar = QFrame()
    bar.setFixedWidth(4)
    bar.setStyleSheet(f"background: {accent_color}; border-radius: 2px;")
    
    text_layout = QVBoxLayout()
    lbl_title = QLabel(title.upper())
    lbl_title.setStyleSheet("color: #94A3B8; font-size: 12px;")
    lbl_value = QLabel(value)
    lbl_value.setStyleSheet("font-size: 24px; font-weight: bold;")
    
    text_layout.addWidget(lbl_title)
    text_layout.addWidget(lbl_value)
    
    layout.addWidget(bar)
    layout.addLayout(text_layout)
    return card

def create_attendance_table() -> QTableWidget:
    """Tạo bảng danh sách sinh viên điểm danh"""
    cols = ["MSSV", "Họ tên", "Lớp", "Trạng thái", "Thời gian"]
    table = QTableWidget(0, len(cols))
    table.setHorizontalHeaderLabels(cols)
    
    v_header = table.verticalHeader()
    if v_header is not None:
        v_header.setVisible(False)
        
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    
    h_header = table.horizontalHeader()
    if h_header is not None:
        h_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Cột Tên co giãn
        
    return table

def add_row_to_table(table: QTableWidget, student_id: str, name: str, class_name: str, status: str, time_str: str):
    """Thêm 1 dòng dữ liệu vào bảng điểm danh"""
    row = table.rowCount()
    table.insertRow(row)
    
    items = [
        QTableWidgetItem(student_id),
        QTableWidgetItem(name),
        QTableWidgetItem(class_name),
        QTableWidgetItem(status),
        QTableWidgetItem(time_str)
    ]
    
    # Tô màu cột Trạng thái
    color = DESIGN_TOKENS["mint"] if status == "Có mặt" else DESIGN_TOKENS["coral"]
    items[3].setForeground(QColor(color))
    
    for col, item in enumerate(items):
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(row, col, item)

def create_video_label() -> QLabel:
    """Tạo màn hình hiển thị Camera (Dùng QLabel cực kỳ đơn giản)"""
    lbl = QLabel("Đang chờ Camera...")
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet("background: #000; border: 1px solid #E2C285; border-radius: 12px; font-size: 16px;")
    lbl.setMinimumSize(640, 480)
    return lbl

def draw_boxes_on_image(cv_image, detections: list) -> QPixmap:
    """
    Vẽ khung nhận diện khuôn mặt lên ảnh bằng OpenCV thuần túy, 
    sau đó convert sang QPixmap để gắn vào QLabel.
    """
    img = cv_image.copy()
    height, width, _ = img.shape
    
    for det in detections:
        # det = {"student_id": "123", "name": "Nguyễn Văn A", "box": (x, y, w, h), "status": "present"}
        x, y, w, h = det.get("box", (0, 0, 0, 0))
        x1, y1 = int(x * width), int(y * height)
        x2, y2 = int((x + w) * width), int((y + h) * height)
        
        color = (153, 211, 52) if det.get("status") == "present" else (133, 113, 251) # BGR
        
        # Vẽ khung
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        # Vẽ tên
        name = det.get("name", "Unknown")
        cv2.putText(img, name, (x1, max(20, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Convert sang QPixmap
    rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    # Lỗi chí tử của PyQt6: QImage sẽ trỏ tới bộ nhớ của rgb_image.data
    # Nếu hàm kết thúc, rgb_image bị xóa -> QImage hiển thị màn hình đen hoặc crash.
    # Giải pháp: .copy() để ép QImage giữ dữ liệu riêng.
    qimg = QImage(rgb_image.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()
    return QPixmap.fromImage(qimg)

if __name__ == "__main__":
    print("Test file ui_components.py: OK!")
