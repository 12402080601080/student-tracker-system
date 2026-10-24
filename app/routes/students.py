from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.repositories.student_repository import student_repo
from app.repositories.academic_repository import academic_repo
from app.services.attendance_service import attendance_service
from app.services.marks_service import marks_service

students_bp = Blueprint("students", __name__, url_prefix="/students")

@students_bp.route("/")
@login_required
def index():
    search = request.args.get("search", "").strip()
    department = request.args.get("department", "").strip()
    semester = request.args.get("semester", "").strip()
    status = request.args.get("status", "").strip()
    sort_field = request.args.get("sort_field", "student_id")
    sort_dir = int(request.args.get("sort_dir", 1))
    page = int(request.args.get("page", 1))

    filters = {}
    if department:
        filters["department"] = department
    if semester:
        filters["semester"] = semester
    if status:
        filters["status"] = status

    result = student_repo.list_students(
        filters=filters,
        search=search,
        sort_field=sort_field,
        sort_dir=sort_dir,
        page=page,
        per_page=10
    )

    courses = academic_repo.list_courses()
    departments = sorted(list({c.get("department") for c in courses if c.get("department")}))
    if not departments:
        departments = ["Computer Science & Engineering", "Information Technology", "Electronics & Communication"]

    return render_template(
        "students/index.html",
        students=result["items"],
        pagination=result,
        search=search,
        selected_dept=department,
        selected_sem=semester,
        selected_status=status,
        sort_field=sort_field,
        sort_dir=sort_dir,
        departments=departments
    )

@students_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    courses = academic_repo.list_courses()
    departments = sorted(list({c.get("department") for c in courses if c.get("department")}))
    if not departments:
        departments = ["Computer Science & Engineering", "Information Technology", "Electronics & Communication"]

    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip().upper()
        roll_number = request.form.get("roll_number", "").strip().upper()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        department = request.form.get("department", "").strip()
        course = request.form.get("course", "").strip()
        semester = request.form.get("semester", "").strip()
        academic_year = request.form.get("academic_year", "").strip()
        enrollment_date = request.form.get("enrollment_date", "").strip()

        # Validation
        if not (student_id and roll_number and first_name and email and department and semester):
            flash("Please fill in all required fields (Student ID, Roll Number, Name, Email, Department, Semester).", "danger")
            return render_template("students/form.html", action="Add", departments=departments, courses=courses)

        if student_repo.get_by_id(student_id):
            flash(f"Student ID '{student_id}' is already registered. Please use a unique ID.", "danger")
            return render_template("students/form.html", action="Add", departments=departments, courses=courses)

        if student_repo.get_by_roll(roll_number):
            flash(f"Roll number '{roll_number}' is already assigned to another student.", "danger")
            return render_template("students/form.html", action="Add", departments=departments, courses=courses)

        data = {
            "student_id": student_id,
            "roll_number": roll_number,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "department": department,
            "course": course,
            "semester": int(semester),
            "academic_year": academic_year,
            "enrollment_date": enrollment_date,
            "status": "active"
        }

        student_repo.create(data)
        academic_repo.log_action(current_user.username, "STUDENT_ADDED", student_id, f"Added student {first_name} {last_name} ({roll_number}).")
        flash(f"Student {first_name} {last_name} ({student_id}) enrolled successfully!", "success")
        return redirect(url_for("students.detail", student_id=student_id))

    return render_template("students/form.html", action="Add", departments=departments, courses=courses, student=None)

@students_bp.route("/<student_id>")
@login_required
def detail(student_id):
    student = student_repo.get_by_id(student_id)
    if not student:
        flash(f"Student with ID '{student_id}' not found.", "warning")
        return redirect(url_for("students.index"))

    # Attendance calculation
    att_stats = attendance_service.calculate_student_attendance(student_id)

    # Marks summary
    academic_summary = marks_service.get_student_academic_summary(student_id)

    return render_template(
        "students/detail.html",
        student=student,
        att_stats=att_stats,
        academic_summary=academic_summary
    )

@students_bp.route("/<student_id>/print")
@login_required
def print_profile(student_id):
    student = student_repo.get_by_id(student_id)
    if not student:
        flash(f"Student '{student_id}' not found.", "warning")
        return redirect(url_for("students.index"))

    att_stats = attendance_service.calculate_student_attendance(student_id)
    academic_summary = marks_service.get_student_academic_summary(student_id)

    return render_template(
        "students/print_profile.html",
        student=student,
        att_stats=att_stats,
        academic_summary=academic_summary
    )

@students_bp.route("/<student_id>/edit", methods=["GET", "POST"])
@login_required
def edit(student_id):
    student = student_repo.get_by_id(student_id)
    if not student:
        flash("Student not found.", "warning")
        return redirect(url_for("students.index"))

    courses = academic_repo.list_courses()
    departments = sorted(list({c.get("department") for c in courses if c.get("department")}))
    if not departments:
        departments = ["Computer Science & Engineering", "Information Technology", "Electronics & Communication"]

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        department = request.form.get("department", "").strip()
        course = request.form.get("course", "").strip()
        semester = request.form.get("semester", "").strip()
        academic_year = request.form.get("academic_year", "").strip()
        status = request.form.get("status", "active").strip()

        update_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "department": department,
            "course": course,
            "semester": int(semester) if semester.isdigit() else student.get("semester", 1),
            "academic_year": academic_year,
            "status": status
        }

        student_repo.update(student_id, update_data)
        academic_repo.log_action(current_user.username, "STUDENT_UPDATED", student_id, f"Updated profile for {student_id}.")
        flash(f"Student '{student_id}' profile updated successfully.", "success")
        return redirect(url_for("students.detail", student_id=student_id))

    return render_template("students/form.html", action="Edit", student=student, departments=departments, courses=courses)

@students_bp.route("/<student_id>/archive", methods=["POST"])
@login_required
def archive(student_id):
    reason = request.form.get("reason", "Archived by user").strip()
    student_repo.archive(student_id, reason=reason)
    academic_repo.log_action(current_user.username, "STUDENT_ARCHIVED", student_id, f"Reason: {reason}")
    flash(f"Student '{student_id}' has been archived.", "info")
    return redirect(url_for("students.detail", student_id=student_id))

@students_bp.route("/<student_id>/restore", methods=["POST"])
@login_required
def restore(student_id):
    student_repo.restore(student_id)
    academic_repo.log_action(current_user.username, "STUDENT_RESTORED", student_id, "Restored to active status.")
    flash(f"Student '{student_id}' has been restored to active status.", "success")
    return redirect(url_for("students.detail", student_id=student_id))
