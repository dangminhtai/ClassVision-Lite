"""
Script đo tốc độ (FPS) của mô hình InsightFace
=============================================
Script này sẽ tạo một ảnh giả (dummy image) và chạy mô hình qua N vòng lặp
để tính toán thời gian suy luận trung bình (Inference Time) và FPS trung bình.
Điều này giúp bạn biết được máy tính của mình có thể xử lý tối đa bao nhiêu khung hình/giây.

Cách chạy:
    cd refactor
    python scripts/benchmark_fps.py
"""
import sys
import time
from pathlib import Path

import cv2
import numpy as np

# Thêm thư mục gốc của refactor vào sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import INSIGHTFACE_DET_SIZE, INSIGHTFACE_MODEL, INSIGHTFACE_USE_GPU

def create_face_analyzer():
    import onnxruntime as ort
    from insightface.app import FaceAnalysis

    providers = ["CPUExecutionProvider"]
    ctx_id = -1
    if INSIGHTFACE_USE_GPU and "CUDAExecutionProvider" in ort.get_available_providers():
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        ctx_id = 0

    app = FaceAnalysis(
        name=INSIGHTFACE_MODEL,
        providers=providers,
        allowed_modules=["detection", "recognition"],
    )
    app.prepare(ctx_id=ctx_id, det_size=INSIGHTFACE_DET_SIZE)
    return app

def benchmark(iterations=100):
    print("="*50)
    print(" BẮT ĐẦU ĐO HIỆU NĂNG (BENCHMARK) ")
    print("="*50)
    
    print("[1/3] Đang tải mô hình InsightFace...")
    try:
        app = create_face_analyzer()
    except Exception as e:
        print(f"[ERROR] Lỗi khi tải mô hình: {e}")
        return
    print("[OK] Mô hình đã tải xong.\n")

    # Tạo một ảnh ngẫu nhiên 640x480 để test
    print(f"[2/3] Đang khởi động nóng (Warm-up)...")
    img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    for _ in range(3):
        app.get(img)
    print("[OK] Đã xong warm-up.\n")

    print(f"[3/3] Đang chạy benchmark ({iterations} vòng lặp)...")
    times = []
    
    # Process bar đơn giản
    for i in range(iterations):
        t0 = time.perf_counter()
        _ = app.get(img)
        t1 = time.perf_counter()
        
        times.append(t1 - t0)
        
        # In tiến độ
        if (i + 1) % 20 == 0:
            print(f"      Đã chạy {i+1}/{iterations} vòng...")

    # Tính toán kết quả
    avg_time_sec = sum(times) / len(times)
    avg_time_ms = avg_time_sec * 1000
    fps = 1.0 / avg_time_sec

    print("\n" + "="*50)
    print(" KẾT QUẢ BENCHMARK ")
    print("="*50)
    print(f"Tổng số vòng lặp: {iterations}")
    print(f"Thời gian xử lý 1 ảnh (Trung bình): {avg_time_ms:.2f} ms")
    print(f"FPS ước tính (Khung hình/giây):      {fps:.2f} FPS")
    print("="*50)

if __name__ == '__main__':
    benchmark(iterations=100)
