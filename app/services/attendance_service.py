from app.repositories.attendance_repository import attendance_repo
from app.repositories.student_repository import student_repo
from flask import current_app

class AttendanceService:
    def __init__(self):
        pass

    def calculate_student_attendance(self, student_id, subject_code=None):
        records = attendance_repo.get_by_student(student_id, subject_code)
        total_sessions = len(records)
        if total_sessions == 0:
            return {
                "total_sessions": 0,
                "present": 0,
                "absent": 0,
                "late": 0,
                "excused": 0,
                "eligible_sessions": 0,
                "attended_sessions": 0,
                "percentage": 100.0,
                "is_low": False,
                "records": []
            }

        present_count = sum(1 for r in records if r.get("status") == "present")
        late_count = sum(1 for r in records if r.get("status") == "late")
        absent_count = sum(1 for r in records if r.get("status") == "absent")
        excused_count = sum(1 for r in records if r.get("status") == "excused")

        # Business rule: Excused sessions are subtracted from eligible denominator
        eligible_sessions = total_sessions - excused_count
        attended_sessions = present_count + late_count

        if eligible_sessions <= 0:
            percentage = 100.0
        else:
            percentage = round((attended_sessions / eligible_sessions) * 100.0, 2)

        threshold = current_app.config.get("ATTENDANCE_LOW_THRESHOLD", 75.0) if current_app else 75.0
        is_low = percentage < threshold

        return {
            "total_sessions": total_sessions,
            "present": present_count,
            "late": late_count,
            "absent": absent_count,
            "excused": excused_count,
            "eligible_sessions": eligible_sessions,
            "attended_sessions": attended_sessions,
            "percentage": min(percentage, 100.0),
            "is_low": is_low,
            "threshold": threshold,
            "records": records
        }

    def get_low_attendance_students(self, threshold=None):
        """Finds all active students whose overall attendance falls below threshold."""
        if threshold is None:
            threshold = current_app.config.get("ATTENDANCE_LOW_THRESHOLD", 75.0) if current_app else 75.0

        active_students = student_repo.get_all_active()
        low_list = []
        for s in active_students:
            stats = self.calculate_student_attendance(s["student_id"])
            if stats["total_sessions"] > 0 and stats["percentage"] < threshold:
                low_list.append({
                    "student": s,
                    "stats": stats
                })
        return low_list

    def get_subject_wise_attendance(self, student_id, subjects):
        subject_stats = {}
        for sub in subjects:
            code = sub.get("code")
            name = sub.get("name")
            stats = self.calculate_student_attendance(student_id, code)
            subject_stats[code] = {
                "name": name,
                "stats": stats
            }
        return subject_stats

attendance_service = AttendanceService()
