from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.repositories.academic_repository import academic_repo

faculty_bp = Blueprint("faculty", __name__, url_prefix="/faculty")

@faculty_bp.route("/")
@login_required
def index():
    dept = request.args.get("department", "").strip()
    faculty_list = academic_repo.list_faculty(department=dept if dept else None)
    courses = academic_repo.list_courses()
    departments = sorted(list({c.get("department") for c in courses if c.get("department")}))
    if not departments:
        departments = ["Computer Science & Engineering", "Information Technology", "Electronics & Communication"]

    return render_template("faculty/index.html", faculty_list=faculty_list, departments=departments, selected_dept=dept)

@faculty_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    courses = academic_repo.list_courses()
    departments = sorted(list({c.get("department") for c in courses if c.get("department")}))
    if not departments:
        departments = ["Computer Science & Engineering", "Information Technology", "Electronics & Communication"]

    if request.method == "POST":
        faculty_id = request.form.get("faculty_id", "").strip().upper()
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        department = request.form.get("department", "").strip()
        designation = request.form.get("designation", "").strip()
        subjects_raw = request.form.get("assigned_subjects", "").strip()
        assigned_subjects = [s.strip().upper() for s in subjects_raw.split(",") if s.strip()]

        if not (faculty_id and name and email and department):
            flash("Please enter Faculty ID, Name, Email, and Department.", "danger")
            return render_template("faculty/form.html", action="Add", departments=departments, faculty=None)

        if academic_repo.get_faculty(faculty_id):
            flash(f"Faculty ID '{faculty_id}' already exists.", "danger")
            return render_template("faculty/form.html", action="Add", departments=departments, faculty=None)

        data = {
            "faculty_id": faculty_id,
            "name": name,
            "email": email,
            "phone": phone,
            "department": department,
            "designation": designation,
            "assigned_subjects": assigned_subjects,
            "status": "active"
        }
        academic_repo.create_faculty(data)
        academic_repo.log_action(current_user.username, "FACULTY_ADDED", faculty_id, f"Added faculty member {name}.")
        flash(f"Faculty member '{name}' added successfully.", "success")
        return redirect(url_for("faculty.index"))

    return render_template("faculty/form.html", action="Add", departments=departments, faculty=None)

@faculty_bp.route("/<faculty_id>/edit", methods=["GET", "POST"])
@login_required
def edit(faculty_id):
    faculty = academic_repo.get_faculty(faculty_id)
    if not faculty:
        flash("Faculty not found.", "warning")
        return redirect(url_for("faculty.index"))

    courses = academic_repo.list_courses()
    departments = sorted(list({c.get("department") for c in courses if c.get("department")}))
    if not departments:
        departments = ["Computer Science & Engineering", "Information Technology", "Electronics & Communication"]

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        department = request.form.get("department", "").strip()
        designation = request.form.get("designation", "").strip()
        status = request.form.get("status", "active").strip()
        subjects_raw = request.form.get("assigned_subjects", "").strip()
        assigned_subjects = [s.strip().upper() for s in subjects_raw.split(",") if s.strip()]

        data = {
            "name": name,
            "email": email,
            "phone": phone,
            "department": department,
            "designation": designation,
            "assigned_subjects": assigned_subjects,
            "status": status
        }
        academic_repo.update_faculty(faculty_id, data)
        academic_repo.log_action(current_user.username, "FACULTY_UPDATED", faculty_id, f"Updated faculty profile {name}.")
        flash(f"Faculty '{name}' updated successfully.", "success")
        return redirect(url_for("faculty.index"))

    return render_template("faculty/form.html", action="Edit", faculty=faculty, departments=departments)
