import time
import cv2
import threading

from face.recognizer import recognize_faces_in_frame
from config.settings import DEFAULT_CAMERA_INDEX, TARGET_FPS, LIVE_RECOGNITION_INTERVAL_MS

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
            
            # QUAN TRỌNG: Ngủ một chút để nhả CPU và GIL cho luồng Camera chạy
            time.sleep(LIVE_RECOGNITION_INTERVAL_MS / 1000.0)
        else:
            time.sleep(0.01)

def _camera_loop(on_frame_ready, on_error, camera_source, is_ip_camera):
    """Hàm chạy vòng lặp đọc camera liên tục ở 30 FPS"""
    global camera_running, latest_frame, latest_ai_results
    camera_running = True
    latest_frame = None
    latest_ai_results = []
    
    # Khởi động luồng AI song song
    ai_thread = threading.Thread(target=_ai_loop, daemon=True)
    ai_thread.start()
    
    cap = cv2.VideoCapture(camera_source)
    if not cap.isOpened():
        on_error("Lỗi: Không thể kết nối với Camera!")
        camera_running = False
        return

    fps_val = 0.0
    prev_time = time.time()
    
    while camera_running:
        ret, frame = cap.read()
        if not ret:
            on_error("Lỗi: Mất kết nối Camera!")
            break
            
        # NẾU là Camera gắn ngoài/Laptop thì lật ảnh như gương
        # NẾU là IP Webcam thì xoay ngược 90 độ (trái) để khắc phục lỗi xoay phải
        if not is_ip_camera:
            frame = cv2.flip(frame, 1)
        else:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
        # Tính FPS
        curr_time = time.time()
        diff = curr_time - prev_time
        if diff > 0:
            fps_val = fps_val * 0.9 + (1.0 / diff) * 0.1
        prev_time = curr_time
        
        # Cập nhật khung hình mới nhất cho luồng AI lấy đi phân tích
        latest_frame = frame
        
        # Gửi ngay frame, kết quả AI cũ VÀ FPS lên giao diện để mượt mà
        on_frame_ready(frame, latest_ai_results, int(fps_val))
        
    cap.release()

def start_camera(on_frame_ready, on_error, camera_source=DEFAULT_CAMERA_INDEX, is_ip_camera=False):
    """Bật camera trong một luồng (thread) chạy ngầm"""
    global camera_running
    if camera_running:
        return # Nếu đang chạy rồi thì bỏ qua
    
    t = threading.Thread(target=_camera_loop, args=(on_frame_ready, on_error, camera_source, is_ip_camera), daemon=True)
    t.start()

def stop_camera():
    """Tắt camera"""
    global camera_running
    camera_running = False

if __name__ == "__main__":
    print("Test file workers.py: OK!")
