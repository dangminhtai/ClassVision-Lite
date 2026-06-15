"""
Student database operations.
Handles CRUD operations for students table.
"""
import sqlite3
from pathlib import Path

def get_db_path():
    """Get database file path"""
    from config.settings import DATA_DIR
    return DATA_DIR / "classvision.db"

def get_all_classes():
    """Lấy danh sách các lớp học độc nhất từ cơ sở dữ liệu sinh viên"""
    db_path = get_db_path()
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
    db_path = get_db_path()
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
        if conn: 
            conn.close()

def get_student_class(student_id):
    """Truy vấn nhanh tên lớp của sinh viên từ Database"""
    db_path = get_db_path()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT class_name FROM students WHERE student_id = ?", (student_id,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception:
        pass
    return "Không rõ"

def add_student(student_id, full_name, class_name):
    """Thêm sinh viên mới"""
    db_path = get_db_path()
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
    """Cập nhật thông tin sinh viên"""
    db_path = get_db_path()
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
    """Xóa sinh viên"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("DELETE FROM students WHERE student_id=?", (student_id,))
        conn.commit()
        return True, "Xóa thành công!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
