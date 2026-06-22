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
QMainWindow, QWidget#AppRoot, QDialog { background: @bg; }
QLineEdit { background: @bg2; color: @ink; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; padding: 6px; }
QFrame#Sidebar { background: @bg2; border-right: 1px solid rgba(255,255,255,0.08); }
QFrame#Panel { background: @panel; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; }
QLabel#Title { font-size: 24px; font-weight: bold; color: @gold; }
QPushButton { background: @panel; border: 1px solid @gold; border-radius: 8px; padding: 10px; color: @gold; }
QPushButton:hover { background: @gold; color: @bg; }
QTableWidget { background: transparent; border: none; gridline-color: rgba(255,255,255,0.08); }
QHeaderView::section { background: @bg2; color: @ink2; padding: 8px; border: none; font-weight: bold; }
QTableWidget::item:selected { background: @gold; color: @bg; font-weight: bold; }
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
    cols = ["STT", "MSSV", "Họ tên", "Lớp", "Trạng thái", "Nguồn", "Thời gian"]
    table = QTableWidget(0, len(cols))
    table.setHorizontalHeaderLabels(cols)
    
    v_header = table.verticalHeader()
    if v_header is not None:
        v_header.setVisible(False)
        
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    
    h_header = table.horizontalHeader()
    if h_header is not None:
        h_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # Cột STT vừa đủ
        h_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # Cột Tên co giãn
        
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

class ScalableImageLabel(QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background: #000; border: 1px solid #E2C285; border-radius: 12px; font-size: 16px;")
        self.setMinimumSize(400, 300)
        self._pixmap = None

    def setPixmap(self, a0):
        self._pixmap = a0
        self._update_pixmap()

    def resizeEvent(self, a0):
        if self._pixmap:
            self._update_pixmap()
        super().resizeEvent(a0)

    def _update_pixmap(self):
        if self._pixmap and not self._pixmap.isNull():
            scaled = self._pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            super().setPixmap(scaled)

def create_video_label() -> QLabel:
    """Tạo màn hình hiển thị Camera tự động co giãn vừa khung hình"""
    lbl = ScalableImageLabel("Đang chờ Camera...")
    return lbl

def create_team_banner() -> QFrame:
    """Tạo banner thông tin nhóm hiển thị ở Header"""
    banner = QFrame()
    banner.setObjectName("Panel")
    # Sử dụng background gradient mượt mà với viền vàng
    banner.setStyleSheet("""
        QFrame#Panel {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0C101A, stop:1 #1E293B);
            border-bottom: 2px solid #E2C285;
            border-radius: 0px;
        }
    """)
    banner.setFixedHeight(95) # Fixed height cho Header đủ rộng để không khuất chữ
    
    layout = QHBoxLayout(banner)
    layout.setContentsMargins(20, 10, 20, 10)
    layout.setSpacing(15)
    
    # 1. Logo trường hoặc Icon (dùng chữ nếu không có ảnh)
    icon_lbl = QLabel("🎓")
    icon_lbl.setStyleSheet("font-size: 36px; background: transparent; border: none;")
    layout.addWidget(icon_lbl)
    
    # 2. Thông tin chính (Vbox: Lớp + Danh sách SV)
    info_layout = QVBoxLayout()
    info_layout.setSpacing(2)
    
    class_lbl = QLabel("LỚP: DIPR430685_06CLC")
    class_lbl.setStyleSheet("color: #E2C285; font-size: 18px; font-weight: bold; background: transparent; border: none;")
    
    info_layout.addWidget(class_lbl)
    
    # Sử dụng QHBoxLayout để đảm bảo các tên nằm ngang
    members_layout = QHBoxLayout()
    members_layout.setSpacing(15)
    
    members = [
        "<b>Dương Minh Duy:</b> 23110083",
        "<b>Đặng Minh Tài:</b> 23110148",
        "<b>Nguyễn Vũ Bảo:</b> 23110079",
        "<b>Phan Hồng Phúc:</b> 23110141"
    ]
    
    for i, member in enumerate(members):
        lbl = QLabel(member)
        lbl.setStyleSheet("color: #F8FAFC; font-size: 14px; background: transparent; border: none;")
        members_layout.addWidget(lbl)
        
        # Thêm dấu phân cách nếu không phải phần tử cuối
        if i < len(members) - 1:
            sep = QLabel("|")
            sep.setStyleSheet("color: #64748B; font-size: 14px; background: transparent; border: none;")
            members_layout.addWidget(sep)
            
    members_layout.addStretch()
    info_layout.addLayout(members_layout)
    
    layout.addLayout(info_layout)
    layout.addStretch() # Đẩy mọi thứ sang trái
    
    return banner

def draw_boxes_on_image(cv_image, detections: list) -> QImage:
    """
    Vẽ khung nhận diện khuôn mặt lên ảnh bằng OpenCV thuần túy.
    Trả về QImage để có thể chạy an toàn ở luồng ngầm (Background thread).
    """
    img = cv_image.copy()
    height, width, _ = img.shape
    
    for det in detections:
        # det = {"student_id": "123", "name": "Nguyễn Văn A", "box": (x, y, w, h), "status": "present"}
        x, y, w, h = det.get("box", (0, 0, 0, 0))
        x1, y1 = int(x * width), int(y * height)
        x2, y2 = int((x + w) * width), int((y + h) * height)
        status = det.get("status")
        if status == "present":
            color = (153, 211, 52) # Xanh lá (BGR)
        elif status == "uncertain":
            color = (0, 165, 255) # Cam (BGR)
        else:
            color = (133, 113, 251) # Đỏ (BGR)
            
        # Vẽ khung
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        # Khắc phục lỗi font OpenCV không hỗ trợ tiếng Việt
        name = det.get("name", "Unknown")
        import unicodedata
        name_no_accents = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
        name_no_accents = name_no_accents.replace('đ', 'd').replace('Đ', 'D')
        
        # Vẽ tên với kích thước chữ to hơn (0.9 thay vì 0.6)
        cv2.putText(img, name_no_accents, (x1, max(25, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    # Convert sang QPixmap
    rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    # Lỗi chí tử của PyQt6: QImage sẽ trỏ tới bộ nhớ của rgb_image.data
    # Nếu hàm kết thúc, rgb_image bị xóa -> QImage hiển thị màn hình đen hoặc crash.
    # Giải pháp: .copy() để ép QImage giữ dữ liệu riêng.
    qimg = QImage(rgb_image.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()
    return qimg

if __name__ == "__main__":
    print("Test file ui_components.py: OK!")
