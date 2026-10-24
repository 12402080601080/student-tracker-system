from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.repositories.academic_repository import academic_repo
from app.repositories.student_repository import student_repo

assignments_bp = Blueprint("assignments", __name__, url_prefix="/assignments")

@assignments_bp.route("/")
@login_required
def index():
    subject = request.args.get("subject", "").strip()
    semester = request.args.get("semester", "").strip()

    assignments = academic_repo.list_assignments(
        subject_code=subject if subject else None,
        semester=semester if semester else None
    )

    now_str = datetime.utcnow().strftime("%Y-%m-%d")
    decorated_assignments = []
    total_active_students = student_repo.count_by_status("active")

    for a in assignments:
        submissions = academic_repo.get_assignment_submissions(a["assignment_id"])
        submitted_count = len(submissions)
        is_overdue = a.get("deadline", "") < now_str
        pending_count = max(0, total_active_students - submitted_count)

        decorated_assignments.append({
            **a,
            "submitted_count": submitted_count,
            "pending_count": pending_count,
            "is_overdue": is_overdue,
            "total_students": total_active_students
        })

    subjects = academic_repo.list_subjects()

    return render_template(
        "assignments/index.html",
        assignments=decorated_assignments,
        subjects=subjects,
        selected_subject=subject,
        selected_sem=semester,
        today_date=now_str
    )

@assignments_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    subjects = academic_repo.list_subjects()

    if request.method == "POST":
        assignment_id = request.form.get("assignment_id", "").strip().upper()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        subject_code = request.form.get("subject_code", "").strip().upper()
        semester = int(request.form.get("semester", 5))
        deadline = request.form.get("deadline", "").strip()
        max_score = int(request.form.get("max_score", 100))

        if not (assignment_id and title and subject_code and deadline):
            flash("Please fill in Assignment ID, Title, Subject, and Deadline.", "danger")
            return render_template("assignments/form.html", subjects=subjects)

        if academic_repo.get_assignment(assignment_id):
            flash(f"Assignment ID '{assignment_id}' already exists.", "danger")
            return render_template("assignments/form.html", subjects=subjects)

        data = {
            "assignment_id": assignment_id,
            "title": title,
            "description": description,
            "subject_code": subject_code,
            "semester": semester,
            "deadline": deadline,
            "max_score": max_score,
            "created_by": current_user.full_name or current_user.username
        }
        academic_repo.create_assignment(data)
        academic_repo.log_action(current_user.username, "ASSIGNMENT_CREATED", assignment_id, f"Created {title} due {deadline}.")
        flash(f"Assignment '{title}' created successfully!", "success")
        return redirect(url_for("assignments.index"))

    return render_template("assignments/form.html", subjects=subjects)

@assignments_bp.route("/<assignment_id>/submissions")
@login_required
def submissions(assignment_id):
    assignment = academic_repo.get_assignment(assignment_id)
    if not assignment:
        flash("Assignment not found.", "warning")
        return redirect(url_for("assignments.index"))

    students = student_repo.get_all_active()
    sub_list = academic_repo.get_assignment_submissions(assignment_id)
    sub_map = {s["student_id"]: s for s in sub_list}

    now_str = datetime.utcnow().strftime("%Y-%m-%d")
    is_overdue = assignment.get("deadline", "") < now_str

    student_submission_rows = []
    for st in students:
        sid = st["student_id"]
        sub = sub_map.get(sid)
        if sub:
            status = sub.get("status", "submitted")
        else:
            status = "overdue" if is_overdue else "pending"

        student_submission_rows.append({
            "student": st,
            "submission": sub,
            "computed_status": status
        })

    return render_template(
        "assignments/submissions.html",
        assignment=assignment,
        rows=student_submission_rows,
        is_overdue=is_overdue
    )

@assignments_bp.route("/<assignment_id>/grade", methods=["POST"])
@login_required
def grade(assignment_id):
    student_id = request.form.get("student_id")
    feedback = request.form.get("feedback", "").strip()
    grade_val = request.form.get("grade", "").strip()

    academic_repo.update_submission_grade(assignment_id, student_id, feedback, grade_val)
    academic_repo.log_action(
        current_user.username,
        "ASSIGNMENT_GRADED",
        f"{assignment_id} - {student_id}",
        f"Awarded score/grade: {grade_val}"
    )
    flash(f"Submission for student {student_id} graded successfully.", "success")
    return redirect(url_for("assignments.submissions", assignment_id=assignment_id))
