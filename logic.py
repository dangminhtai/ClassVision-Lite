import csv
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from datetime import datetime
from config import STUDENTS_CSV, ATTENDANCE_SESSIONS_DIR

# ---------------------------------------------------------
# QUẢN LÝ SINH VIÊN (Từ file CSV)
# ---------------------------------------------------------

def load_students_from_csv() -> list[dict]:
    """Đọc toàn bộ sinh viên từ students.csv"""
    if not STUDENTS_CSV.exists():
        return []
    
    students = []
    with open(STUDENTS_CSV, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            students.append(row)
    return students

def get_classes() -> list[str]:
    """Lấy danh sách các lớp học hiện có trong CSV"""
    students = load_students_from_csv()
    classes = set()
    for s in students:
        class_name = s.get("class_name", "").strip()
        if class_name:
            # Lớp học có thể phân tách bằng dấu chấm phẩy
            parts = [p.strip() for p in class_name.split(";") if p.strip()]
            classes.update(parts)
    return sorted(list(classes))

def get_students_by_class(class_name: str) -> list[dict]:
    """Lấy danh sách sinh viên thuộc một lớp cụ thể"""
    students = load_students_from_csv()
    result = []
    for s in students:
        c_name = s.get("class_name", "")
        if class_name.lower() in [c.strip().lower() for c in c_name.split(";")]:
            result.append(s)
    return result

# ---------------------------------------------------------
# QUẢN LÝ ĐIỂM DANH (Lưu file CSV cho từng phiên)
# ---------------------------------------------------------

def create_attendance_session(class_name: str, subject: str, room: str) -> dict:
    """Tạo một phiên điểm danh mới"""
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    return {
        "session_id": session_id,
        "class_name": class_name,
        "subject": subject,
        "room": room,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "start_time": datetime.now().strftime("%H:%M:%S")
    }

def save_attendance_to_csv(session: dict, attendance_records: dict):
    """Lưu kết quả điểm danh của một phiên ra file CSV"""
    session_id = session["session_id"]
    file_path = ATTENDANCE_SESSIONS_DIR / f"session_{session_id}.csv"
    
    fieldnames = ["student_id", "status", "time", "method"]
    
    with open(file_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for student_id, record in attendance_records.items():
            writer.writerow({
                "student_id": student_id,
                "status": record.get("status", "absent"),
                "time": record.get("time", ""),
                "method": record.get("method", "")
            })
    return file_path

# ---------------------------------------------------------
# XỬ LÝ AI - NHẬN DIỆN KHUÔN MẶT
# ---------------------------------------------------------

import numpy as np
import warnings
import onnxruntime as ort
from insightface.app import FaceAnalysis

# Các biến toàn cục lưu Model và Gallery để không phải khởi tạo lại
_face_app = None
_gallery = None

def init_face_model():
    """Hàm tải model InsightFace và đọc file gallery.npz (Chạy 1 lần duy nhất)"""
    global _face_app, _gallery
    from config import INSIGHTFACE_MODEL, INSIGHTFACE_USE_GPU, INSIGHTFACE_DET_SIZE, GALLERY_PATH
    
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

def recognize_faces_in_frame(frame, threshold=0.38, uncertain_margin=0.08):
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
            query_emb = query_emb / norm
            
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

def get_all_classes():
    """Lấy danh sách các lớp học độc nhất từ cơ sở dữ liệu sinh viên"""
    import sqlite3
    from config import DATA_DIR
    db_path = DATA_DIR / "classvision.db"
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT class_name FROM students WHERE class_name != '' ORDER BY class_name")
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Lỗi đọc class_name từ DB: {e}")
        return []
    finally:
        if conn is not None:
            conn.close()

def get_students(search_text=""):
    """Lấy danh sách sinh viên, có hỗ trợ tìm kiếm theo MSSV hoặc Tên"""
    import sqlite3
    from config import DATA_DIR
    db_path = DATA_DIR / "classvision.db"
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        if search_text:
            query = f"%{search_text}%"
            cursor.execute("SELECT student_id, full_name, class_name FROM students WHERE student_id LIKE ? OR full_name LIKE ? ORDER BY student_id", (query, query))
        else:
            cursor.execute("SELECT student_id, full_name, class_name FROM students ORDER BY student_id")
        return cursor.fetchall()
    except Exception as e:
        print(f"Lỗi đọc DB: {e}")
        return []
    finally:
        if conn: conn.close()

def add_student(student_id, full_name, class_name):
    import sqlite3
    from config import DATA_DIR
    db_path = DATA_DIR / "classvision.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("INSERT INTO students (student_id, full_name, class_name) VALUES (?, ?, ?)", (student_id, full_name, class_name))
        conn.commit()
        return True, "Thêm thành công!"
    except sqlite3.IntegrityError:
        return False, "MSSV đã tồn tại!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_student(student_id, full_name, class_name):
    import sqlite3
    from config import DATA_DIR
    db_path = DATA_DIR / "classvision.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("UPDATE students SET full_name=?, class_name=? WHERE student_id=?", (full_name, class_name, student_id))
        conn.commit()
        return True, "Cập nhật thành công!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def delete_student(student_id):
    import sqlite3
    from config import DATA_DIR
    db_path = DATA_DIR / "classvision.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("DELETE FROM students WHERE student_id=?", (student_id,))
        conn.commit()
        return True, "Xóa thành công!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
                    