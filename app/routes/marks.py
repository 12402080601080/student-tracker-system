from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.repositories.marks_repository import marks_repo
from app.repositories.student_repository import student_repo
from app.repositories.academic_repository import academic_repo
from app.services.marks_service import marks_service

marks_bp = Blueprint("marks", __name__, url_prefix="/marks")

@marks_bp.route("/")
@login_required
def index():
    subject = request.args.get("subject", "").strip()
    semester = request.args.get("semester", "").strip()

    assessments = marks_repo.list_assessments(
        subject_code=subject if subject else None,
        semester=semester if semester else None
    )

    assessment_summaries = []
    for a in assessments:
        analytics = marks_service.get_assessment_analytics(a["assessment_id"])
        assessment_summaries.append({
            "assessment": a,
            "analytics": analytics
        })

    subjects = academic_repo.list_subjects()
    at_risk = marks_service.get_at_risk_students()

    return render_template(
        "marks/index.html",
        assessment_summaries=assessment_summaries,
        subjects=subjects,
        selected_subject=subject,
        selected_sem=semester,
        at_risk=at_risk
    )

@marks_bp.route("/assessments/add", methods=["GET", "POST"])
@login_required
def add_assessment():
    subjects = academic_repo.list_subjects()

    if request.method == "POST":
        assessment_id = request.form.get("assessment_id", "").strip().upper()
        name = request.form.get("name", "").strip()
        subject_code = request.form.get("subject_code", "").strip().upper()
        max_marks = request.form.get("max_marks", "100").strip()
        assessment_date = request.form.get("assessment_date", "").strip()
        academic_year = request.form.get("academic_year", "2025-2026").strip()
        semester = request.form.get("semester", "5").strip()

        if not (assessment_id and name and subject_code and max_marks):
            flash("Please fill in Assessment ID, Name, Subject, and Maximum Marks.", "danger")
            return render_template("marks/assessment_form.html", subjects=subjects)

        try:
            max_m_val = float(max_marks)
            if max_m_val <= 0:
                raise ValueError
        except ValueError:
            flash("Maximum marks must be a positive number.", "danger")
            return render_template("marks/assessment_form.html", subjects=subjects)

        marks_repo.create_assessment(
            assessment_id=assessment_id,
            name=name,
            subject_code=subject_code,
            max_marks=max_m_val,
            assessment_date=assessment_date,
            academic_year=academic_year,
            semester=semester
        )
        academic_repo.log_action(current_user.username, "ASSESSMENT_CREATED", assessment_id, f"Created {name} (Max: {max_m_val}).")
        flash(f"Assessment '{name}' created successfully!", "success")
        return redirect(url_for("marks.entry", assessment_id=assessment_id))

    return render_template("marks/assessment_form.html", subjects=subjects)

@marks_bp.route("/entry/<assessment_id>", methods=["GET", "POST"])
@login_required
def entry(assessment_id):
    assessment = marks_repo.get_assessment(assessment_id)
    if not assessment:
        flash("Assessment not found.", "warning")
        return redirect(url_for("marks.index"))

    students = student_repo.get_all_active()

    if request.method == "POST":
        student_ids = request.form.getlist("student_ids[]")
        entered_count = 0
        errors = []

        for sid in student_ids:
            score_str = request.form.get(f"marks_{sid}", "").strip()
            remarks = request.form.get(f"remarks_{sid}", "").strip()

            if score_str == "":
                continue

            try:
                score = float(score_str)
                marks_repo.enter_mark(
                    student_id=sid,
                    assessment_id=assessment_id,
                    marks_obtained=score,
                    updated_by=current_user.full_name or current_user.username,
                    remarks=remarks
                )
                entered_count += 1
            except ValueError as ve:
                errors.append(f"Student {sid}: {str(ve)}")

        if errors:
            for err in errors:
                flash(err, "danger")
        if entered_count > 0:
            academic_repo.log_action(
                current_user.username,
                "MARKS_ENTERED",
                assessment_id,
                f"Entered/updated marks for {entered_count} students."
            )
            flash(f"Successfully saved marks for {entered_count} students!", "success")
            return redirect(url_for("marks.results", assessment_id=assessment_id))

    # Existing marks map
    existing_marks = {m["student_id"]: m for m in marks_repo.get_assessment_marks(assessment_id)}

    return render_template(
        "marks/entry.html",
        assessment=assessment,
        students=students,
        existing_marks=existing_marks
    )

@marks_bp.route("/results/<assessment_id>")
@login_required
def results(assessment_id):
    analytics = marks_service.get_assessment_analytics(assessment_id)
    if not analytics:
        flash("Assessment not found.", "warning")
        return redirect(url_for("marks.index"))

    return render_template("marks/results.html", analytics=analytics)
