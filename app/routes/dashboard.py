from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.services.report_service import report_service
from app.services.attendance_service import attendance_service
from app.services.marks_service import marks_service
from app.repositories.student_repository import student_repo
from app.repositories.academic_repository import academic_repo
from app.extensions import get_db

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    metrics = report_service.get_dashboard_metrics()
    recent_students = student_repo.list_students(page=1, per_page=5, sort_field="created_at", sort_dir=-1)["items"]

    # Grade distribution aggregated across all assessments
    db = get_db()
    all_marks = list(db.marks.find()) if db is not None else []
    grade_counts = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for m in all_marks:
        max_m = float(m.get("max_marks", 100))
        if max_m > 0:
            pct = (float(m.get("marks_obtained", 0)) / max_m) * 100
            grade, _ = marks_service.calculate_grade(pct)
            if grade in grade_counts:
                grade_counts[grade] += 1

    # Attendance breakdown for Chart.js
    att_summary = metrics["today_attendance"]
    attendance_chart_data = {
        "labels": ["Present", "Late", "Absent", "Excused"],
        "values": [
            att_summary.get("present", 0),
            att_summary.get("late", 0),
            att_summary.get("absent", 0),
            att_summary.get("excused", 0)
        ]
    }

    # If today's attendance has 0 recorded yet, fallback to recent overall attendance summary for chart visualization
    if sum(attendance_chart_data["values"]) == 0 and db is not None:
        p_count = db.attendance.count_documents({"status": "present"})
        l_count = db.attendance.count_documents({"status": "late"})
        a_count = db.attendance.count_documents({"status": "absent"})
        e_count = db.attendance.count_documents({"status": "excused"})
        attendance_chart_data["values"] = [p_count, l_count, a_count, e_count]

    return render_template(
        "dashboard.html",
        metrics=metrics,
        recent_students=recent_students,
        grade_counts=grade_counts,
        attendance_chart_data=attendance_chart_data,
        is_mock_db=getattr(db, "name", "") == "test_student_tracker"
    )
