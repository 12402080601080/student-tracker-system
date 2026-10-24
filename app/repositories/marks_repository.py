from datetime import datetime
from bson.objectid import ObjectId
from app.extensions import get_db

class MarksRepository:
    def __init__(self):
        pass

    @property
    def assessments_col(self):
        return get_db().assessments

    @property
    def marks_col(self):
        return get_db().marks

    # --- Assessment Methods ---
    def create_assessment(self, assessment_id, name, subject_code, max_marks, assessment_date, academic_year, semester):
        doc = {
            "assessment_id": str(assessment_id).strip(),
            "name": str(name).strip(),
            "subject_code": str(subject_code).strip(),
            "max_marks": float(max_marks),
            "assessment_date": str(assessment_date).strip(),
            "academic_year": str(academic_year).strip(),
            "semester": int(semester),
            "created_at": datetime.utcnow()
        }
        self.assessments_col.update_one(
            {"assessment_id": doc["assessment_id"]},
            {"$set": doc},
            upsert=True
        )
        return doc

    def get_assessment(self, assessment_id):
        return self.assessments_col.find_one({"assessment_id": str(assessment_id).strip()})

    def list_assessments(self, subject_code=None, semester=None):
        query = {}
        if subject_code:
            query["subject_code"] = subject_code
        if semester:
            query["semester"] = int(semester)
        return list(self.assessments_col.find(query).sort("assessment_date", -1))

    # --- Marks Entry & Retrieval ---
    def enter_mark(self, student_id, assessment_id, marks_obtained, updated_by, remarks=""):
        assessment = self.get_assessment(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment '{assessment_id}' not found.")

        marks_num = float(marks_obtained)
        if marks_num < 0:
            raise ValueError("Marks obtained cannot be negative.")
        if marks_num > float(assessment["max_marks"]):
            raise ValueError(f"Marks obtained ({marks_num}) cannot exceed maximum allowed marks ({assessment['max_marks']}).")

        doc = {
            "student_id": str(student_id).strip(),
            "assessment_id": str(assessment_id).strip(),
            "subject_code": assessment.get("subject_code"),
            "max_marks": float(assessment["max_marks"]),
            "marks_obtained": marks_num,
            "remarks": remarks or "",
            "updated_by": updated_by,
            "updated_at": datetime.utcnow()
        }

        self.marks_col.update_one(
            {"student_id": doc["student_id"], "assessment_id": doc["assessment_id"]},
            {"$set": doc},
            upsert=True
        )
        return doc

    def get_student_marks(self, student_id):
        return list(self.marks_col.find({"student_id": str(student_id).strip()}))

    def get_assessment_marks(self, assessment_id):
        return list(self.marks_col.find({"assessment_id": str(assessment_id).strip()}))

    def get_student_mark_for_assessment(self, student_id, assessment_id):
        return self.marks_col.find_one({
            "student_id": str(student_id).strip(),
            "assessment_id": str(assessment_id).strip()
        })

marks_repo = MarksRepository()
