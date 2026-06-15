"""
Attendance session management.
Handles CSV-based attendance records.
"""
import csv
from datetime import datetime

def get_sessions_dir():
    """Get attendance sessions directory path"""
    from config.settings import ATTENDANCE_SESSIONS_DIR
    return ATTENDANCE_SESSIONS_DIR

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
    sessions_dir = get_sessions_dir()
    session_id = session["session_id"]
    file_path = sessions_dir / f"session_{session_id}.csv"
    
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
