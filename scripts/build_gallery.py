"""
Script tạo file gallery.npz (Face Embeddings Gallery)
=====================================================
Quét thư mục data/students/, mỗi thư mục con là 1 sinh viên chứa ảnh khuôn mặt.
InsightFace sẽ trích xuất embedding từ từng ảnh, tính trung bình,
rồi lưu tất cả vào data/gallery.npz để phục vụ nhận diện realtime.

Cách chạy:
    cd refactor
    python scripts/build_gallery.py
    python scripts/build_gallery.py --student-id dang_minh_tai
    python scripts/build_gallery.py --changed-only
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Thêm thư mục gốc của refactor vào sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

import cv2
import numpy as np
from tqdm import tqdm

from config.settings import (
    DATA_DIR,
    GALLERY_PATH,
    INSIGHTFACE_DET_SIZE,
    INSIGHTFACE_MODEL,
    INSIGHTFACE_USE_GPU,
)

# ==============================================================
# Hằng số
# ==============================================================
STUDENTS_DIR = DATA_DIR / "students"
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


# ==============================================================
# Hàm tiện ích
# ==============================================================
def normalize_embedding(embedding: np.ndarray) -> np.ndarray:
    """Chuẩn hóa embedding về vector đơn vị."""
    vector = np.asarray(embedding, dtype=np.float32).reshape(-1)
    norm = float(np.linalg.norm(vector))
    if norm <= 1e-12:
        raise ValueError("Embedding có norm bằng 0, không thể chuẩn hóa.")
    return vector / norm


def create_face_analyzer():
    """Khởi tạo InsightFace analyzer."""
    import onnxruntime as ort
    from insightface.app import FaceAnalysis

    providers = ["CPUExecutionProvider"]
    ctx_id = -1
    if INSIGHTFACE_USE_GPU and "CUDAExecutionProvider" in ort.get_available_providers():
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
        ctx_id = 0
    elif INSIGHTFACE_USE_GPU:
        print("[WARN] Không tìm thấy CUDAExecutionProvider. Chạy bằng CPU.")

    app = FaceAnalysis(
        name=INSIGHTFACE_MODEL,
        providers=providers,
        allowed_modules=["detection", "recognition"],
    )
    app.prepare(ctx_id=ctx_id, det_size=INSIGHTFACE_DET_SIZE)
    return app


def get_largest_face(faces):
    """Trả về khuôn mặt có bounding box lớn nhất."""
    faces = list(faces)
    if not faces:
        return None

    def area(face):
        x1, y1, x2, y2 = np.asarray(face.bbox, dtype=np.float32)
        return float(max(0.0, x2 - x1) * max(0.0, y2 - y1))

    return max(faces, key=area)


def iter_images(folder: Path) -> list[Path]:
    """Liệt kê tất cả ảnh trong thư mục."""
    if not folder.exists():
        return []
    return sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )


def infer_student_from_folder(folder: Path) -> dict[str, str]:
    """Suy luận thông tin sinh viên từ tên thư mục (VD: dang_minh_tai -> Dang Minh Tai)."""
    folder_name = folder.name
    parts = [p for p in folder_name.split("_") if p]
    if parts and parts[0].isdigit() and len(parts) > 1:
        student_id = parts[0]
        name_parts = parts[1:]
    else:
        student_id = folder_name
        name_parts = parts

    full_name = " ".join(p[:1].upper() + p[1:] for p in name_parts) or folder_name
    return {
        "student_id": student_id,
        "full_name": full_name,
        "class_name": "",
        "folder": folder_name,
    }


# ==============================================================
# Logic chính: Build Gallery
# ==============================================================
def build_gallery(*, student_ids: set[str] | None = None, changed_only: bool = False) -> None:
    """
    Quét thư mục data/students/ và tạo file gallery.npz.
    
    Mỗi thư mục con trong data/students/ đại diện cho 1 sinh viên.
    Ảnh trong thư mục sẽ được InsightFace xử lý để trích xuất face embedding.
    Embedding trung bình của tất cả ảnh sẽ được lưu vào gallery.npz.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not STUDENTS_DIR.exists():
        print(f"[ERROR] Không tìm thấy thư mục: {STUDENTS_DIR}")
        print("Hãy tạo thư mục data/students/ và thêm ảnh khuôn mặt sinh viên vào.")
        return

    # Tìm tất cả thư mục sinh viên
    student_folders = sorted(p for p in STUDENTS_DIR.iterdir() if p.is_dir())
    if not student_folders:
        print("[ERROR] Không tìm thấy thư mục sinh viên nào trong data/students/")
        return

    # Load gallery cũ nếu cần (cho chế độ --changed-only)
    existing_gallery: dict[str, dict] = {}
    if changed_only and GALLERY_PATH.exists():
        try:
            with np.load(GALLERY_PATH, allow_pickle=False) as data:
                for i, sid in enumerate(data["student_ids"].astype(str)):
                    existing_gallery[sid] = {
                        "embedding": data["embeddings"][i],
                        "full_name": str(data["full_names"][i]),
                        "class_name": str(data["class_names"][i]),
                    }
        except Exception as e:
            print(f"[WARN] Không đọc được gallery cũ, build lại toàn bộ: {e}")
            existing_gallery = {}

    # Lọc danh sách cần build
    folders_to_process = student_folders
    if student_ids:
        folders_to_process = [f for f in student_folders if f.name in student_ids]
        if not folders_to_process:
            print(f"[WARN] Không tìm thấy thư mục nào khớp với: {student_ids}")
            return

    # Khởi tạo model InsightFace
    print("[INFO] Đang tải model InsightFace...")
    face_app = create_face_analyzer()
    print("[OK] Model đã sẵn sàng!\n")

    # Danh sách kết quả
    all_student_ids: list[str] = []
    all_full_names: list[str] = []
    all_class_names: list[str] = []
    all_embeddings: list[np.ndarray] = []

    for folder in tqdm(folders_to_process, desc="Building gallery"):
        info = infer_student_from_folder(folder)
        sid = info["student_id"]
        full_name = info["full_name"]

        # Nếu chế độ changed-only và sinh viên không thay đổi → dùng embedding cũ
        if changed_only and sid in existing_gallery:
            image_paths = iter_images(folder)
            gallery_mtime = GALLERY_PATH.stat().st_mtime if GALLERY_PATH.exists() else 0.0
            latest_mtime = max((p.stat().st_mtime for p in image_paths), default=0.0)
            if latest_mtime <= gallery_mtime:
                # Giữ nguyên embedding cũ
                all_student_ids.append(sid)
                all_full_names.append(existing_gallery[sid]["full_name"])
                all_class_names.append(existing_gallery[sid]["class_name"])
                all_embeddings.append(existing_gallery[sid]["embedding"])
                continue

        image_paths = iter_images(folder)
        if not image_paths:
            print(f"[WARN] Không có ảnh trong thư mục: {folder.name}")
            continue

        # Trích xuất embedding từ từng ảnh
        face_embeddings: list[np.ndarray] = []
        for img_path in image_paths:
            image = cv2.imread(str(img_path))
            if image is None:
                print(f"[WARN] Không đọc được ảnh: {img_path.name}")
                continue

            faces = face_app.get(image)
            face = get_largest_face(faces)
            if face is None:
                continue
            if not hasattr(face, "embedding") or face.embedding is None:
                continue

            face_embeddings.append(normalize_embedding(face.embedding))

        if not face_embeddings:
            print(f"[WARN] {sid} - Không trích xuất được embedding nào.")
            # Giữ embedding cũ nếu có
            if sid in existing_gallery:
                all_student_ids.append(sid)
                all_full_names.append(existing_gallery[sid]["full_name"])
                all_class_names.append(existing_gallery[sid]["class_name"])
                all_embeddings.append(existing_gallery[sid]["embedding"])
            continue

        # Tính embedding trung bình
        mean_emb = normalize_embedding(np.mean(np.vstack(face_embeddings), axis=0))
        all_student_ids.append(sid)
        all_full_names.append(full_name)
        all_class_names.append(info["class_name"])
        all_embeddings.append(mean_emb)
        print(f"[OK] {sid} - {full_name}: {len(face_embeddings)}/{len(image_paths)} ảnh hợp lệ")

    # Nếu chế độ student_ids hoặc changed_only → merge với gallery cũ
    if (student_ids or changed_only) and existing_gallery:
        rebuilt_ids = set(all_student_ids)
        for sid, entry in existing_gallery.items():
            if sid not in rebuilt_ids:
                all_student_ids.append(sid)
                all_full_names.append(entry["full_name"])
                all_class_names.append(entry["class_name"])
                all_embeddings.append(entry["embedding"])

    if not all_embeddings:
        print("[ERROR] Không có embedding nào để lưu!")
        return

    # Lưu gallery
    np.savez_compressed(
        GALLERY_PATH,
        student_ids=np.asarray(all_student_ids, dtype=str),
        full_names=np.asarray(all_full_names, dtype=str),
        class_names=np.asarray(all_class_names, dtype=str),
        embeddings=np.vstack(all_embeddings).astype(np.float32),
    )
    print(f"\n[SAVE] Gallery đã lưu: {GALLERY_PATH} ({len(all_embeddings)} sinh viên)")


# ==============================================================
# CLI Entry Point
# ==============================================================
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build ClassVision Face Gallery (gallery.npz)")
    parser.add_argument(
        "--student-id",
        action="append",
        help="Chỉ build lại cho sinh viên cụ thể (tên thư mục). Có thể lặp lại nhiều lần.",
    )
    parser.add_argument(
        "--changed-only",
        action="store_true",
        help="Chỉ build lại sinh viên có ảnh mới hơn gallery hiện tại.",
    )
    args = parser.parse_args(argv)

    student_ids: set[str] = set()
    if args.student_id:
        for v in args.student_id:
            for item in v.split(","):
                item = item.strip()
                if item:
                    student_ids.add(item)

    if student_ids and args.changed_only:
        parser.error("--student-id không thể dùng chung với --changed-only")

    try:
        build_gallery(student_ids=student_ids or None, changed_only=args.changed_only)
        return 0
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
