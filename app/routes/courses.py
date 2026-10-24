from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.repositories.academic_repository import academic_repo

courses_bp = Blueprint("courses", __name__, url_prefix="/courses")

@courses_bp.route("/")
@login_required
def index():
    courses = academic_repo.list_courses()
    return render_template("courses/index.html", courses=courses)

@courses_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        course_id = request.form.get("course_id", "").strip().upper()
        course_name = request.form.get("course_name", "").strip()
        department = request.form.get("department", "").strip()
        semester = int(request.form.get("semester", 1))
        academic_year = request.form.get("academic_year", "").strip()

        # Subjects parsing from form (code, name, credits)
        sub_codes = request.form.getlist("sub_code[]")
        sub_names = request.form.getlist("sub_name[]")
        sub_credits = request.form.getlist("sub_credits[]")

        subjects = []
        for i in range(len(sub_codes)):
            if sub_codes[i].strip():
                subjects.append({
                    "code": sub_codes[i].strip().upper(),
                    "name": sub_names[i].strip() if i < len(sub_names) else "",
                    "credits": int(sub_credits[i]) if i < len(sub_credits) and sub_credits[i].isdigit() else 3
                })

        if not (course_id and course_name and department):
            flash("Please enter Course ID, Course Name, and Department.", "danger")
            return render_template("courses/form.html")

        if academic_repo.get_course(course_id):
            flash(f"Course ID '{course_id}' already exists.", "danger")
            return render_template("courses/form.html")

        data = {
            "course_id": course_id,
            "course_name": course_name,
            "department": department,
            "semester": semester,
            "academic_year": academic_year,
            "subjects": subjects
        }
        academic_repo.create_course(data)
        academic_repo.log_action(current_user.username, "COURSE_CREATED", course_id, f"Created course {course_name}.")
        flash(f"Course '{course_name}' ({course_id}) created with {len(subjects)} subjects.", "success")
        return redirect(url_for("courses.index"))

    return render_template("courses/form.html")
