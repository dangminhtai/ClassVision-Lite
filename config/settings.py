import os
from pathlib import Path

# Thư mục gốc của project (chỉnh về ngay trong thư mục refactor)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Cấu hình Ứng dụng
APP_NAME = "ClassVision Attendance"
DEFAULT_CAMERA_INDEX = 0
TARGET_FPS = 30 # Tốc độ khung hình mục tiêu của Camera
DEFAULT_TOTAL_STUDENTS = 41 # Sĩ số sinh viên mặc định

# Cấu hình AI & Nhận diện
LIVE_RECOGNITION_INTERVAL_MS = 150
MIN_STABLE_FRAMES = 5
INSIGHTFACE_MODEL = "buffalo_s"
INSIGHTFACE_DET_SIZE = (640, 640)
INSIGHTFACE_USE_GPU = False
FACE_MATCH_THRESHOLD = 0.45   # Giảm để nhận diện ảnh nhóm xa/góc nghiêng tốt hơn
FACE_UNCERTAIN_MARGIN = 0.0   # Tắt vùng uncertain → tất cả match đều là "Có mặt"

# Cấu hình Đường dẫn (Paths)
DATA_DIR = PROJECT_ROOT / "data"
STUDENTS_CSV = DATA_DIR / "students.csv"
GALLERY_PATH = DATA_DIR / "gallery.npz"
ATTENDANCE_SESSIONS_DIR = DATA_DIR / "attendance_sessions"

# Đảm bảo các thư mục tồn tại
for d in [DATA_DIR, ATTENDANCE_SESSIONS_DIR]:
    d.mkdir(parents=True, exist_ok=True)
