from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.extensions import get_db, User
from app.repositories.academic_repository import academic_repo

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        remember = bool(request.form.get("remember"))

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template("login.html")

        db = get_db()
        user_doc = db.users.find_one({"$or": [{"username": username}, {"email": username}]})

        if not user_doc or not check_password_hash(user_doc.get("password_hash", ""), password):
            flash("Invalid credentials. Please verify your username and password.", "danger")
            return render_template("login.html")

        if user_doc.get("status") != "active":
            flash("This account is inactive. Please contact the administrator.", "warning")
            return render_template("login.html")

        user = User(user_doc)
        login_user(user, remember=remember)
        academic_repo.log_action(user.username, "USER_LOGIN", "Authentication", f"User {user.username} logged in successfully.")

        flash(f"Welcome back, {user.full_name}!", "success")
        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)
        return redirect(url_for("dashboard.index"))

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    user_name = current_user.username
    academic_repo.log_action(user_name, "USER_LOGOUT", "Authentication", f"User {user_name} logged out.")
    logout_user()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("auth.login"))
