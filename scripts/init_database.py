"""
Script tạo file classvision.db (SQLite Database)
=================================================
Quét thư mục data/students/ và tạo bảng students trong SQLite database.
Thông tin sinh viên (student_id, full_name, class_name) được suy luận
từ tên thư mục ảnh của mỗi sinh viên.

Database này được sử dụng bởi giao diện Quản lý Sinh viên và Báo cáo Điểm danh.

Cách chạy:
    cd refactor
    python scripts/init_database.py
    python scripts/init_database.py --reset     # Xóa DB cũ rồi tạo mới
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

# Thêm thư mục gốc của refactor vào sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

from config.settings import DATA_DIR

# ==============================================================
# Hằng số
# ==============================================================
DB_PATH = DATA_DIR / "classvision.db"
STUDENTS_DIR = DATA_DIR / "students"


# ==============================================================
# Hàm tạo bảng SQLite
# ==============================================================
def create_tables(conn: sqlite3.Connection) -> None:
    """Tạo tất cả bảng cần thiết cho ứng dụng."""
    conn.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            class_name TEXT NOT NULL DEFAULT '',
            folder TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS attendance_sessions (
            session_id TEXT PRIMARY KEY,
            class_name TEXT NOT NULL DEFAULT '',
            subject TEXT NOT NULL DEFAULT '',
            room TEXT NOT NULL DEFAULT '',
            session_date TEXT NOT NULL DEFAULT '',
            start_time TEXT NOT NULL DEFAULT '',
            late_after_minutes INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS attendance_records (
            session_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            full_name TEXT NOT NULL DEFAULT '',
            class_name TEXT NOT NULL DEFAULT '',
            subject TEXT NOT NULL DEFAULT '',
            room TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT '',
            first_seen_time TEXT NOT NULL DEFAULT '',
            confidence TEXT NOT NULL DEFAULT '',
            distance TEXT NOT NULL DEFAULT '',
            source TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (session_id, student_id)
        );

        CREATE TABLE IF NOT EXISTS review_items (
            record_id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT '',
            suggested_student_id TEXT NOT NULL DEFAULT '',
            suggested_name TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT '',
            confidence TEXT NOT NULL DEFAULT '',
            distance TEXT NOT NULL DEFAULT '',
            source TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)


def infer_student_from_folder(folder: Path) -> dict[str, str]:
    """Suy luận thông tin sinh viên từ tên thư mục."""
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
# Logic chính: Init Database
# ==============================================================
def init_database(*, reset: bool = False) -> None:
    """
    Tạo file classvision.db và nhập thông tin sinh viên từ thư mục ảnh.
    
    Quy trình:
    1. Tạo cấu trúc bảng SQLite (students, attendance_sessions, attendance_records, review_items)
    2. Quét thư mục data/students/ để lấy danh sách sinh viên
    3. Insert/Update thông tin sinh viên vào bảng students
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if reset and DB_PATH.exists():
        DB_PATH.unlink()
        print(f"[INFO] Đã xóa database cũ: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    try:
        create_tables(conn)
        print(f"[OK] Đã tạo cấu trúc bảng: {DB_PATH}")

        if not STUDENTS_DIR.exists():
            print(f"[WARN] Không tìm thấy thư mục: {STUDENTS_DIR}")
            print("Database đã tạo nhưng chưa có dữ liệu sinh viên.")
            return

        # Quét thư mục sinh viên
        student_folders = sorted(p for p in STUDENTS_DIR.iterdir() if p.is_dir())
        if not student_folders:
            print("[WARN] Không tìm thấy thư mục sinh viên nào.")
            return

        inserted = 0
        updated = 0
        for folder in student_folders:
            info = infer_student_from_folder(folder)
            if not info["student_id"]:
                continue

            # Kiểm tra đã tồn tại chưa
            cursor = conn.execute(
                "SELECT student_id FROM students WHERE student_id = ?",
                (info["student_id"],),
            )
            exists = cursor.fetchone() is not None

            if exists:
                conn.execute(
                    """UPDATE students SET full_name=?, class_name=?, folder=?, updated_at=CURRENT_TIMESTAMP
                       WHERE student_id=?""",
                    (info["full_name"], info["class_name"], info["folder"], info["student_id"]),
                )
                updated += 1
            else:
                conn.execute(
                    """INSERT INTO students (student_id, full_name, class_name, folder, updated_at)
                       VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                    (info["student_id"], info["full_name"], info["class_name"], info["folder"]),
                )
                inserted += 1

        conn.commit()
        total = inserted + updated
        print(f"[OK] Đã nhập {total} sinh viên (mới: {inserted}, cập nhật: {updated})")

    finally:
        conn.close()

    print(f"\n[DONE] Database sẵn sàng tại: {DB_PATH}")


# ==============================================================
# CLI Entry Point
# ==============================================================
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Khởi tạo ClassVision SQLite Database (classvision.db)")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Xóa database cũ và tạo lại từ đầu.",
    )
    args = parser.parse_args(argv)

    try:
        init_database(reset=args.reset)
        return 0
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
