import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import cv2
import threading

# Chú ý: import trực tiếp, không dùng 'refactor.' để tránh lỗi khi chạy trực tiếp file này
from logic import recognize_faces_in_frame
from config import DEFAULT_CAMERA_INDEX, TARGET_FPS

# Biến toàn cục để quản lý luồng
camera_running = False
latest_frame = None
latest_ai_results = []

def _ai_loop():
    """Luồng chạy ngầm liên tục AI trên khung hình mới nhất. Giúp không giật lag camera."""
    global camera_running, latest_frame, latest_ai_results
    while camera_running:
        if latest_frame is not None:
            # Copy frame để phân tích, tránh việc bị đổi ảnh giữa chừng
            frame_to_process = latest_frame.copy()
            # Bước này tốn khoảng 100-300ms
            results = recognize_faces_in_frame(frame_to_process)
            latest_ai_results = results
        else:
            time.sleep(0.01)

def _camera_loop(on_frame_ready, on_error):
    """Hàm chạy vòng lặp đọc camera liên tục ở 30 FPS"""
    global camera_running, latest_frame, latest_ai_results
    camera_running = True
    latest_frame = None
    latest_ai_results = []
    
    # Khởi động luồng AI song song
    ai_thread = threading.Thread(target=_ai_loop, daemon=True)
    ai_thread.start()
    
    # Thêm cv2.CAP_DSHOW để tránh lỗi MSMF (-1072873821) trên Windows
    cap = cv2.VideoCapture(DEFAULT_CAMERA_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        on_error("Lỗi: Không thể kết nối với Camera!")
        camera_running = False
        return

    while camera_running:
        ret, frame = cap.read()
        if not ret:
            on_error("Lỗi: Mất kết nối Camera!")
            break
            
        # Cập nhật khung hình mới nhất cho luồng AI lấy đi phân tích
        latest_frame = frame
        
        # Gửi ngay frame VÀ kết quả AI cũ lên giao diện để mượt mà
        on_frame_ready(frame, latest_ai_results)
        time.sleep(1.0 / TARGET_FPS)  # Tính toán độ trễ dựa theo cấu hình FPS
        
    cap.release()

def start_camera(on_frame_ready, on_error):
    """Bật camera trong một luồng (thread) chạy ngầm"""
    global camera_running
    if camera_running:
        return # Nếu đang chạy rồi thì bỏ qua
    
    t = threading.Thread(target=_camera_loop, args=(on_frame_ready, on_error), daemon=True)
    t.start()

def stop_camera():
    """Tắt camera"""
    global camera_running
    camera_running = False

if __name__ == "__main__":
    print("Test file workers.py: OK!")
