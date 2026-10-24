from flask import Blueprint, render_template, Response, request
from flask_login import login_required
from app.services.report_service import report_service
from app.repositories.academic_repository import academic_repo

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

@reports_bp.route("/")
@login_required
def index():
    audit_logs = academic_repo.get_recent_audit_logs(limit=25)
    return render_template("reports/index.html", audit_logs=audit_logs)

@reports_bp.route("/export/students")
@login_required
def export_students():
    dept = request.args.get("department")
    sem = request.args.get("semester")
    csv_data = report_service.export_students_csv(department=dept, semester=sem)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=students_record.csv"}
    )

@reports_bp.route("/export/attendance")
@login_required
def export_attendance():
    subject = request.args.get("subject")
    csv_data = report_service.export_attendance_csv(subject_code=subject)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=attendance_summary.csv"}
    )

@reports_bp.route("/export/marks")
@login_required
def export_marks():
    aid = request.args.get("assessment_id")
    csv_data = report_service.export_marks_csv(assessment_id=aid)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=marks_report.csv"}
    )

@reports_bp.route("/audit-logs")
@login_required
def audit_logs():
    logs = academic_repo.get_recent_audit_logs(limit=100)
    return render_template("reports/audit_logs.html", logs=logs)
