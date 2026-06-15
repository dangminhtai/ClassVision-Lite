import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import cv2
import threading

# Chú ý: import trực tiếp, không dùng 'refactor.' để tránh lỗi khi chạy trực tiếp file này
from logic import recognize_faces_in_frame
from config import DEFAULT_CAMERA_INDEX

# Biến toàn cục để tắt/bật camera
camera_running = False

def _camera_loop(on_frame_ready, on_error):
    """Hàm chạy vòng lặp đọc camera liên tục"""
    global camera_running
    camera_running = True
    
    # Thêm cv2.CAP_DSHOW để tránh lỗi MSMF (-1072873821) trên Windows
    cap = cv2.VideoCapture(DEFAULT_CAMERA_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        on_error("Lỗi: Không thể kết nối với Camera!")
        return

    while camera_running:
        ret, frame = cap.read()
        if not ret:
            on_error("Lỗi: Mất kết nối Camera!")
            break
        
        # Gọi hàm callback để trả frame về giao diện
        on_frame_ready(frame)
        time.sleep(0.03)  # Giới hạn ~30 FPS để máy không bị nóng
        
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

def run_ai_recognition(frame, on_result):
    """
    Xử lý nhận diện khuôn mặt (AI) trong một luồng riêng biệt.
    Không dùng class, chỉ cần hàm callback.
    """
    def _task():
        # Gọi logic AI
        result = recognize_faces_in_frame(frame)
        # Trả kết quả về giao diện
        on_result(result)
        
    t = threading.Thread(target=_task, daemon=True)
    t.start()

if __name__ == "__main__":
    print("Test file workers.py: OK!")
