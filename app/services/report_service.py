import csv
import io
from app.repositories.student_repository import student_repo
from app.repositories.attendance_repository import attendance_repo
from app.repositories.marks_repository import marks_repo
from app.repositories.academic_repository import academic_repo
from app.services.attendance_service import attendance_service
from app.services.marks_service import marks_service
from app.extensions import get_db

class ReportService:
    def __init__(self):
        pass

    def export_students_csv(self, department=None, semester=None, status=None):
        filters = {}
        if department:
            filters["department"] = department
        if semester:
            filters["semester"] = semester
        if status:
            filters["status"] = status

        res = student_repo.list_students(filters=filters, page=1, per_page=10000)
        students = res["items"]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Student ID", "Roll Number", "First Name", "Last Name",
            "Email", "Phone", "Department", "Course", "Semester",
            "Academic Year", "Status", "Enrollment Date"
        ])

        for s in students:
            writer.writerow([
                s.get("student_id", ""),
                s.get("roll_number", ""),
                s.get("first_name", ""),
                s.get("last_name", ""),
                s.get("email", ""),
                s.get("phone", ""),
                s.get("department", ""),
                s.get("course", ""),
                s.get("semester", ""),
                s.get("academic_year", ""),
                s.get("status", ""),
                s.get("enrollment_date", s.get("created_at", ""))
            ])

        output.seek(0)
        return output.getvalue()

    def export_attendance_csv(self, subject_code=None):
        students = student_repo.get_all_active()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Student ID", "Roll Number", "Student Name", "Department", "Semester",
            "Total Sessions", "Present", "Late", "Absent", "Excused",
            "Attendance %", "Low Attendance Alert (<75%)"
        ])

        for s in students:
            stats = attendance_service.calculate_student_attendance(s["student_id"], subject_code)
            name = f"{s.get('first_name', '')} {s.get('last_name', '')}".strip()
            writer.writerow([
                s.get("student_id", ""),
                s.get("roll_number", ""),
                name,
                s.get("department", ""),
                s.get("semester", ""),
                stats["total_sessions"],
                stats["present"],
                stats["late"],
                stats["absent"],
                stats["excused"],
                f"{stats['percentage']}%",
                "YES" if stats["is_low"] and stats["total_sessions"] > 0 else "NO"
            ])

        output.seek(0)
        return output.getvalue()

    def export_marks_csv(self, assessment_id=None):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Student ID", "Roll Number", "Student Name", "Assessment ID",
            "Assessment Name", "Subject Code", "Max Marks", "Marks Obtained",
            "Percentage", "Grade", "Status"
        ])

        if assessment_id:
            assessments = [marks_repo.get_assessment(assessment_id)]
        else:
            assessments = marks_repo.list_assessments()

        for a in assessments:
            if not a:
                continue
            aid = a["assessment_id"]
            marks_list = marks_repo.get_assessment_marks(aid)
            for m in marks_list:
                st = student_repo.get_by_id(m.get("student_id"))
                st_name = f"{st.get('first_name', '')} {st.get('last_name', '')}".strip() if st else m.get("student_id")
                roll = st.get("roll_number", "") if st else ""
                obtained = float(m.get("marks_obtained", 0))
                max_m = float(a.get("max_marks", 100))
                pct = round((obtained / max_m) * 100, 2) if max_m > 0 else 0
                grade, _ = marks_service.calculate_grade(pct)

                writer.writerow([
                    m.get("student_id"),
                    roll,
                    st_name,
                    aid,
                    a.get("name"),
                    a.get("subject_code"),
                    max_m,
                    obtained,
                    f"{pct}%",
                    grade,
                    "Pass" if grade != "F" else "Needs Support"
                ])

        output.seek(0)
        return output.getvalue()

    def get_dashboard_metrics(self):
        db = get_db()
        total_students = student_repo.count_total()
        active_students = student_repo.count_by_status("active")
        total_faculty = db.faculty.count_documents({"status": "active"}) if db is not None else 0
        today_att = attendance_repo.get_today_summary()

        # Overall average marks
        marks_cursor = list(db.marks.find()) if db is not None else []
        if marks_cursor:
            pct_list = [
                (float(m.get("marks_obtained", 0)) / float(m.get("max_marks", 100))) * 100
                for m in marks_cursor if float(m.get("max_marks", 0)) > 0
            ]
            avg_marks_pct = round(sum(pct_list) / len(pct_list), 1) if pct_list else 0.0
        else:
            avg_marks_pct = 0.0

        # Pending assignments
        total_assignments = db.assignments.count_documents({}) if db is not None else 0
        total_submissions = db.submissions.count_documents({"status": "submitted"}) if db is not None else 0

        # Recent activities / audit logs
        recent_activity = academic_repo.get_recent_audit_logs(limit=8)

        # Low attendance and at-risk counts
        low_att_students = attendance_service.get_low_attendance_students()
        at_risk_students = marks_service.get_at_risk_students()

        return {
            "total_students": total_students,
            "active_students": active_students,
            "total_faculty": total_faculty,
            "today_attendance": today_att,
            "average_marks_pct": avg_marks_pct,
            "total_assignments": total_assignments,
            "pending_submissions": max(0, (total_assignments * active_students) - total_submissions),
            "recent_activity": recent_activity,
            "low_attendance_count": len(low_att_students),
            "at_risk_count": len(at_risk_students),
            "low_attendance_list": low_att_students[:5],
            "at_risk_list": at_risk_students[:5]
        }

report_service = ReportService()
