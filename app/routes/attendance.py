from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.repositories.attendance_repository import attendance_repo
from app.repositories.student_repository import student_repo
from app.repositories.academic_repository import academic_repo
from app.services.attendance_service import attendance_service

attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")

@attendance_bp.route("/")
@login_required
def index():
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    selected_date = request.args.get("date", today_str)
    selected_subject = request.args.get("subject", "")

    subjects = academic_repo.list_subjects()
    if not selected_subject and subjects:
        selected_subject = subjects[0]["code"]

    session_records = attendance_repo.get_session_attendance(selected_subject, selected_date) if selected_subject else []
    record_map = {r["student_id"]: r for r in session_records}

    students = student_repo.get_all_active()
    low_att_list = attendance_service.get_low_attendance_students()

    return render_template(
        "attendance/index.html",
        selected_date=selected_date,
        selected_subject=selected_subject,
        subjects=subjects,
        students=students,
        record_map=record_map,
        low_att_list=low_att_list
    )

@attendance_bp.route("/mark", methods=["GET", "POST"])
@login_required
def mark():
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    subjects = academic_repo.list_subjects()

    if request.method == "POST":
        date_str = request.form.get("date", today_str).strip()
        subject_code = request.form.get("subject_code", "").strip().upper()
        student_ids = request.form.getlist("student_ids[]")

        if not subject_code or not date_str:
            flash("Please specify both subject and session date.", "danger")
            return redirect(url_for("attendance.mark"))

        marked_count = 0
        for sid in student_ids:
            status = request.form.get(f"status_{sid}", "present")
            notes = request.form.get(f"notes_{sid}", "")
            attendance_repo.record_attendance(
                student_id=sid,
                subject_code=subject_code,
                date_str=date_str,
                status=status,
                recorded_by=current_user.full_name or current_user.username,
                notes=notes
            )
            marked_count += 1

        academic_repo.log_action(
            current_user.username,
            "ATTENDANCE_RECORDED",
            f"{subject_code} ({date_str})",
            f"Recorded attendance for {marked_count} students."
        )
        flash(f"Successfully recorded attendance for {marked_count} students in {subject_code} on {date_str}!", "success")
        return redirect(url_for("attendance.index", date=date_str, subject=subject_code))

    selected_subject = request.args.get("subject", subjects[0]["code"] if subjects else "")
    selected_date = request.args.get("date", today_str)
    students = student_repo.get_all_active()
    existing_records = {r["student_id"]: r for r in attendance_repo.get_session_attendance(selected_subject, selected_date)}

    return render_template(
        "attendance/mark.html",
        subjects=subjects,
        students=students,
        selected_subject=selected_subject,
        selected_date=selected_date,
        existing_records=existing_records
    )

@attendance_bp.route("/edit", methods=["POST"])
@login_required
def edit_record():
    record_id = request.form.get("record_id")
    new_status = request.form.get("status")
    reason = request.form.get("reason", "").strip()

    if not record_id or not new_status or not reason:
        flash("Record ID, new status, and reason for amendment are required.", "danger")
        return redirect(request.referrer or url_for("attendance.index"))

    attendance_repo.update_record(
        record_id=record_id,
        status=new_status,
        reason=reason,
        updated_by=current_user.username
    )
    academic_repo.log_action(
        current_user.username,
        "ATTENDANCE_EDITED",
        record_id,
        f"Status changed to {new_status}. Reason: {reason}"
    )
    flash("Attendance record updated and audit log saved.", "success")
    return redirect(request.referrer or url_for("attendance.index"))
