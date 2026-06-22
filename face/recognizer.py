"""
Face recognition engine.
Handles InsightFace model and face matching.
"""
import numpy as np
import onnxruntime as ort
from insightface.app import FaceAnalysis

# Các biến toàn cục lưu Model và Gallery để không phải khởi tạo lại
_face_app = None
_gallery = None

def init_face_model():
    """Hàm tải model InsightFace và đọc file gallery.npz (Chạy 1 lần duy nhất)"""
    global _face_app, _gallery
    # pyrefly: ignore [missing-import]
    from config.settings import INSIGHTFACE_MODEL, INSIGHTFACE_USE_GPU, INSIGHTFACE_DET_SIZE, GALLERY_PATH
    
    if _face_app is None:
        providers = ["CPUExecutionProvider"]
        ctx_id = -1
        if INSIGHTFACE_USE_GPU and "CUDAExecutionProvider" in ort.get_available_providers():
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            ctx_id = 0
            
        _face_app = FaceAnalysis(
            name=INSIGHTFACE_MODEL,
            providers=providers,
            allowed_modules=["detection", "recognition"],
        )
        _face_app.prepare(ctx_id=ctx_id, det_size=INSIGHTFACE_DET_SIZE)
        
    if _gallery is None and GALLERY_PATH.exists():
        data = np.load(GALLERY_PATH, allow_pickle=False)
        _gallery = {
            "student_ids": data["student_ids"].astype(str),
            "full_names": data["full_names"].astype(str),
            "class_names": data["class_names"].astype(str),
            "embeddings": np.asarray(data["embeddings"], dtype=np.float32)
        }
        # Chuẩn hóa (Normalize) các vector trong gallery một lần duy nhất để tính toán cực nhanh
        norms = np.linalg.norm(_gallery["embeddings"], axis=1, keepdims=True)
        _gallery["embeddings"] = _gallery["embeddings"] / np.clip(norms, 1e-12, None)

def recognize_faces_in_frame(frame, threshold=None, uncertain_margin=None):
    # pyrefly: ignore [missing-import]
    from config.settings import FACE_MATCH_THRESHOLD, FACE_UNCERTAIN_MARGIN
    if threshold is None:
        threshold = FACE_MATCH_THRESHOLD
    if uncertain_margin is None:
        uncertain_margin = FACE_UNCERTAIN_MARGIN
    """
    Phân tích 1 frame ảnh từ Camera bằng InsightFace.
    Trả về danh sách kết quả gồm {name, student_id, box, status}
    """
    global _face_app, _gallery
    if _face_app is None:
        init_face_model()
        
    assert _face_app is not None, "Model chưa được tải thành công!"
    faces = _face_app.get(frame)
    detections = []
    
    image_height, image_width = frame.shape[:2]
    
    for face in faces:
        if not hasattr(face, "bbox") or not hasattr(face, "embedding"):
            continue
            
        # Lấy tọa độ bounding box chuẩn hóa theo tỷ lệ màn hình [0.0 - 1.0]
        x1, y1, x2, y2 = np.asarray(face.bbox, dtype=np.float32)
        box = (
            float(np.clip(x1 / image_width, 0.0, 1.0)),
            float(np.clip(y1 / image_height, 0.0, 1.0)),
            float(np.clip((x2 - x1) / image_width, 0.0, 1.0)),
            float(np.clip((y2 - y1) / image_height, 0.0, 1.0)),
        )
        
        # Chuẩn hóa vector khuôn mặt hiện tại
        query_emb = np.asarray(face.embedding, dtype=np.float32)
        norm = np.linalg.norm(query_emb)
        if norm > 1e-12:
            query_emb = query_emb / float(norm)
            
        # Nếu chưa có thư viện sinh viên (gallery.npz bị thiếu)
        if _gallery is None or len(_gallery["embeddings"]) == 0:
            detections.append({"name": "Unknown", "status": "unknown", "box": box})
            continue
            
        # So sánh cosine distance với toàn bộ sinh viên trong thư viện (phép nhân ma trận siêu tốc)
        distances = np.clip(1.0 - np.dot(_gallery["embeddings"], query_emb), 0.0, 2.0)
        best_idx = int(np.argmin(distances))
        best_dist = float(distances[best_idx])
        
        full_name = str(_gallery["full_names"][best_idx])
        student_id = str(_gallery["student_ids"][best_idx])
        
        # Phân loại trạng thái dựa vào khoảng cách
        if best_dist <= threshold:
            detections.append({"name": full_name, "student_id": student_id, "status": "present", "box": box})
        elif best_dist <= threshold + uncertain_margin:
            detections.append({"name": full_name, "student_id": student_id, "status": "uncertain", "box": box})
        else:
            detections.append({"name": "Unknown", "status": "unknown", "box": box})
            
    return detections
