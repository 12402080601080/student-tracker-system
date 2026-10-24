import os
from flask import Flask, render_template
from config import config_by_name
from app.extensions import db_manager, login_manager
from app.seed_data import seed_initial_data

def create_app(config_name=None):
    if not config_name:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Initialize extensions
    db_manager.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.students import students_bp
    from app.routes.faculty import faculty_bp
    from app.routes.courses import courses_bp
    from app.routes.attendance import attendance_bp
    from app.routes.marks import marks_bp
    from app.routes.assignments import assignments_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(marks_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(reports_bp)

    # Custom Jinja filters
    @app.template_filter("status_badge")
    def status_badge(status):
        status = str(status).lower()
        if status in ["active", "present", "graded"]:
            return "badge-success"
        elif status in ["absent", "fail", "overdue", "archived"]:
            return "badge-danger"
        elif status in ["late", "pending"]:
            return "badge-warning"
        elif status in ["excused"]:
            return "badge-info"
        return "badge-secondary"

    @app.template_filter("grade_badge")
    def grade_badge(grade):
        grade = str(grade).upper()
        if grade in ["A+", "A"]:
            return "badge-success"
        elif grade in ["B", "C"]:
            return "badge-primary"
        elif grade == "D":
            return "badge-warning"
        elif grade == "F":
            return "badge-danger"
        return "badge-secondary"

    # Context processors
    @app.context_processor
    def inject_globals():
        return {
            "app_name": "Student Tracker System",
            "app_version": "1.0.0",
            "academic_year_current": "2025-2026",
            "is_mock_database": db_manager.is_mock
        }

    # Custom error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/500.html"), 500

    # Populate seed data if database is initialized
    with app.app_context():
        try:
            seed_initial_data()
        except Exception as seed_err:
            app.logger.warning(f"Could not auto-seed data: {seed_err}")

    return app
