"""
Runtime attendance state.
Manages in-memory attendance records for the current session.
"""

# Biến toàn cục để lưu báo cáo điểm danh (In-memory Lite)
# Cấu trúc: student_id -> {"name": ..., "class": ..., "time": ..., "source": ...}
global_attendance = {}

def add_attendance_record(student_id, name, class_name, time_str, source):
    """Thêm một bản ghi điểm danh vào bộ nhớ"""
    if student_id and student_id not in global_attendance:
        global_attendance[student_id] = {
            "name": name,
            "class": class_name,
            "time": time_str,
            "source": source
        }
        return True
    return False

def get_attendance_records():
    """Lấy tất cả bản ghi điểm danh hiện tại"""
    return global_attendance

def get_present_count():
    """Đếm số sinh viên đã điểm danh"""
    return len(global_attendance)

def clear_attendance():
    """Xóa toàn bộ dữ liệu điểm danh (reset session)"""
    global global_attendance
    global_attendance = {}
