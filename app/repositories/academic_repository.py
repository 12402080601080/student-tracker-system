from datetime import datetime
from bson.objectid import ObjectId
from app.extensions import get_db

class AcademicRepository:
    def __init__(self):
        pass

    @property
    def db(self):
        return get_db()

    # --- Faculty ---
    def create_faculty(self, data):
        data["created_at"] = datetime.utcnow()
        data["status"] = data.get("status", "active")
        self.db.faculty.update_one({"faculty_id": data["faculty_id"]}, {"$set": data}, upsert=True)
        return data

    def list_faculty(self, department=None):
        query = {}
        if department:
            query["department"] = department
        return list(self.db.faculty.find(query).sort("name", 1))

    def get_faculty(self, faculty_id):
        return self.db.faculty.find_one({"faculty_id": str(faculty_id).strip()})

    def update_faculty(self, faculty_id, data):
        data["updated_at"] = datetime.utcnow()
        self.db.faculty.update_one({"faculty_id": faculty_id}, {"$set": data})
        return self.get_faculty(faculty_id)

    # --- Courses & Subjects ---
    def create_course(self, data):
        data["created_at"] = datetime.utcnow()
        self.db.courses.update_one({"course_id": data["course_id"]}, {"$set": data}, upsert=True)
        return data

    def list_courses(self):
        return list(self.db.courses.find().sort("course_name", 1))

    def get_course(self, course_id):
        return self.db.courses.find_one({"course_id": str(course_id).strip()})

    def list_subjects(self, semester=None, department=None):
        courses = self.list_courses()
        subjects = []
        for c in courses:
            if department and c.get("department") != department:
                continue
            if semester and int(c.get("semester", 0)) != int(semester):
                continue
            for s in c.get("subjects", []):
                s["department"] = c.get("department")
                s["semester"] = c.get("semester")
                subjects.append(s)
        return subjects

    # --- Assignments ---
    def create_assignment(self, data):
        data["created_at"] = datetime.utcnow()
        self.db.assignments.update_one({"assignment_id": data["assignment_id"]}, {"$set": data}, upsert=True)
        return data

    def list_assignments(self, subject_code=None, semester=None):
        query = {}
        if subject_code:
            query["subject_code"] = subject_code
        if semester:
            query["semester"] = int(semester)
        return list(self.db.assignments.find(query).sort("deadline", 1))

    def get_assignment(self, assignment_id):
        return self.db.assignments.find_one({"assignment_id": str(assignment_id).strip()})

    # --- Submissions ---
    def submit_assignment(self, assignment_id, student_id, submission_notes="", status="submitted"):
        doc = {
            "assignment_id": str(assignment_id).strip(),
            "student_id": str(student_id).strip(),
            "status": status,
            "submission_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
            "notes": submission_notes,
            "updated_at": datetime.utcnow()
        }
        self.db.submissions.update_one(
            {"assignment_id": doc["assignment_id"], "student_id": doc["student_id"]},
            {"$set": doc},
            upsert=True
        )
        return doc

    def get_assignment_submissions(self, assignment_id):
        return list(self.db.submissions.find({"assignment_id": str(assignment_id).strip()}))

    def get_student_submission(self, assignment_id, student_id):
        return self.db.submissions.find_one({
            "assignment_id": str(assignment_id).strip(),
            "student_id": str(student_id).strip()
        })

    def update_submission_grade(self, assignment_id, student_id, feedback, grade_or_marks):
        return self.db.submissions.update_one(
            {"assignment_id": str(assignment_id).strip(), "student_id": str(student_id).strip()},
            {"$set": {
                "feedback": feedback,
                "grade": grade_or_marks,
                "status": "graded",
                "graded_at": datetime.utcnow()
            }}
        )

    # --- Audit Logs ---
    def log_action(self, user_name, action, affected_record, details=""):
        doc = {
            "user": user_name,
            "action": action,
            "affected_record": affected_record,
            "details": details,
            "timestamp": datetime.utcnow()
        }
        self.db.audit_logs.insert_one(doc)

    def get_recent_audit_logs(self, limit=10):
        return list(self.db.audit_logs.find().sort("timestamp", -1).limit(limit))

academic_repo = AcademicRepository()
