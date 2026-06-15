import cv2
import time
import matplotlib.pyplot as plt
import numpy as np
import os

def measure_fps(backend_name, backend_flag, num_frames=100):
    print(f"\n--- Testing Camera with Backend: {backend_name} ---")
    cap = cv2.VideoCapture(0, backend_flag)
    
    # Ép camera chạy ở 60 FPS nếu phần cứng hỗ trợ
    cap.set(cv2.CAP_PROP_FPS, 60)
    
    if not cap.isOpened():
        print("Cannot open camera!")
        return None
        
    # Warmup
    for _ in range(10):
        cap.read()
        
    times = []
    print(f"Start capturing {num_frames} frames...")
    
    start_total = time.time()
    for _ in range(num_frames):
        t0 = time.time()
        ret, frame = cap.read()
        if not ret: break
        t1 = time.time()
        times.append(t1 - t0)
        
    end_total = time.time()
    cap.release()
    
    if not times: return None
    
    avg_fps = len(times) / (end_total - start_total)
    print(f"Completed. Avg FPS: {avg_fps:.2f} FPS")
    
    return times

def main():
    msmf_times = measure_fps("MSMF", cv2.CAP_MSMF)
    dshow_times = measure_fps("DirectShow", cv2.CAP_DSHOW)
    
    # Vẽ biểu đồ
    plt.figure(figsize=(10, 6))
    
    if msmf_times:
        fps_msmf = [1.0 / t if t > 0 else 0 for t in msmf_times]
        plt.plot(fps_msmf, label='MSMF FPS', color='red', alpha=0.7)
        
    if dshow_times:
        fps_dshow = [1.0 / t if t > 0 else 0 for t in dshow_times]
        plt.plot(fps_dshow, label='DirectShow FPS', color='blue', alpha=0.7)
        
    plt.axhline(y=30, color='gray', linestyle='--', label='30 FPS (Standard)')
    plt.axhline(y=60, color='green', linestyle='--', label='60 FPS (High Speed)')
    
    plt.title('Biểu đồ tốc độ khung hình (FPS) thực tế qua thời gian')
    plt.xlabel('Khung hình thứ n')
    plt.ylabel('FPS tức thời')
    plt.legend()
    plt.grid(True)
    
    output_path = r"C:\Users\minh tai\.gemini\antigravity-ide\brain\d31e4b04-6f2a-4649-9563-c8ea701b98f7\fps_chart.png"
    plt.savefig(output_path)
    print(f"\nĐã lưu biểu đồ vào: {output_path}")

if __name__ == '__main__':
    main()
