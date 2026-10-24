from datetime import datetime
from bson.objectid import ObjectId
from app.extensions import get_db

class AttendanceRepository:
    def __init__(self):
        pass

    @property
    def col(self):
        return get_db().attendance

    def record_attendance(self, student_id, subject_code, date_str, status, recorded_by, notes=""):
        now = datetime.utcnow()
        doc = {
            "student_id": str(student_id).strip(),
            "subject_code": str(subject_code).strip(),
            "date": str(date_str).strip(),
            "status": str(status).strip().lower(),  # 'present', 'absent', 'late', 'excused'
            "notes": notes or "",
            "recorded_by": recorded_by,
            "created_at": now,
            "updated_at": now
        }
        # Upsert or raise duplicate based on requirement
        res = self.col.update_one(
            {"student_id": doc["student_id"], "subject_code": doc["subject_code"], "date": doc["date"]},
            {"$set": doc},
            upsert=True
        )
        return res

    def get_by_student(self, student_id, subject_code=None):
        query = {"student_id": str(student_id).strip()}
        if subject_code:
            query["subject_code"] = subject_code
        return list(self.col.find(query).sort("date", -1))

    def get_session_attendance(self, subject_code, date_str):
        query = {"subject_code": str(subject_code).strip(), "date": str(date_str).strip()}
        return list(self.col.find(query))

    def update_record(self, record_id, status, reason, updated_by):
        now = datetime.utcnow()
        update_data = {
            "status": status.lower(),
            "edit_reason": reason,
            "last_edited_by": updated_by,
            "updated_at": now
        }
        return self.col.update_one({"_id": ObjectId(record_id)}, {"$set": update_data})

    def get_today_summary(self, today_str=None):
        if not today_str:
            today_str = datetime.utcnow().strftime("%Y-%m-%d")
        pipeline = [
            {"$match": {"date": today_str}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        res = list(self.col.aggregate(pipeline))
        summary = {"present": 0, "absent": 0, "late": 0, "excused": 0, "total": 0}
        for item in res:
            st = item["_id"]
            cnt = item["count"]
            if st in summary:
                summary[st] = cnt
            summary["total"] += cnt
        return summary

attendance_repo = AttendanceRepository()
