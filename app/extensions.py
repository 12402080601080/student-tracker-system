import os
import sys
import logging
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import pymongo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"

def _get_mongomock():
    """Safely import mongomock, providing a lightweight pkg_resources shim if missing on Python 3.12+."""
    if "pkg_resources" not in sys.modules:
        try:
            import pkg_resources
        except (ImportError, ModuleNotFoundError):
            import types
            dummy = types.ModuleType("pkg_resources")
            class Dist:
                version = "4.1.2"
            dummy.get_distribution = lambda name: Dist()
            sys.modules["pkg_resources"] = dummy
    import mongomock
    return mongomock

class DatabaseManager:
    """Manages MongoDB connection with resilient fallback."""
    def __init__(self):
        self.client = None
        self.db = None
        self.is_mock = False

    def init_app(self, app):
        mongo_uri = app.config.get("MONGO_URI", "mongodb://localhost:27017/student_tracker")
        db_name = app.config.get("DATABASE_NAME", "student_tracker")
        
        is_cloud = bool(
            os.getenv("VERCEL") or 
            os.getenv("AWS_LAMBDA_FUNCTION_NAME") or 
            os.getenv("VERCEL_ENV")
        )
        is_localhost_uri = "localhost" in mongo_uri or "127.0.0.1" in mongo_uri

        # Explicit test or mongomock URI
        if mongo_uri.startswith("mongomock://") or app.config.get("TESTING"):
            try:
                mm = _get_mongomock()
                self.client = mm.MongoClient()
                self.db = self.client[db_name]
                self.is_mock = True
                self._ensure_indexes()
                return
            except Exception as mock_err:
                logger.warning(f"[DB] mongomock initialization warning: {mock_err}")

        try:
            # In cloud environments without Atlas configured, localhost cannot exist; skip timeout
            if is_cloud and is_localhost_uri:
                raise ConnectionError("Localhost MongoDB is not reachable in serverless cloud.")

            # Try connecting to live MongoDB (local or Atlas)
            self.client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=1500)
            self.client.admin.command("ping")
            self.db = self.client[db_name]
            self.is_mock = False
            logger.info(f"[DB] Successfully connected to live MongoDB database '{db_name}'.")
        except Exception as e:
            logger.warning(f"[DB] Live MongoDB not reachable ({e}). Initializing in-memory store.")
            try:
                mm = _get_mongomock()
                self.client = mm.MongoClient()
                self.db = self.client[db_name]
                self.is_mock = True
            except Exception as fallback_err:
                logger.error(f"[DB] Critical: mongomock fallback error: {fallback_err}")

        self._ensure_indexes()

    def _ensure_indexes(self):
        """Ensure unique and lookup indexes across collections."""
        if self.db is None:
            return
        try:
            # Users
            self.db.users.create_index("username", unique=True)
            self.db.users.create_index("email", unique=True)

            # Students
            self.db.students.create_index("student_id", unique=True)
            self.db.students.create_index("roll_number", unique=True)
            self.db.students.create_index("email")
            self.db.students.create_index("department")
            self.db.students.create_index("semester")
            self.db.students.create_index("status")

            # Faculty
            self.db.faculty.create_index("faculty_id", unique=True)
            self.db.faculty.create_index("email", unique=True)

            # Courses
            self.db.courses.create_index("course_id", unique=True)

            # Attendance: prevent duplicate attendance for student + subject + class date
            self.db.attendance.create_index(
                [("student_id", 1), ("subject_code", 1), ("date", 1)],
                unique=True
            )

            # Assessments
            self.db.assessments.create_index("assessment_id", unique=True)

            # Marks: prevent duplicate marks for student + assessment
            self.db.marks.create_index(
                [("student_id", 1), ("assessment_id", 1)],
                unique=True
            )

            # Assignments
            self.db.assignments.create_index("assignment_id", unique=True)

            # Submissions: prevent duplicate submission for student + assignment
            self.db.submissions.create_index(
                [("assignment_id", 1), ("student_id", 1)],
                unique=True
            )

            # Audit logs
            self.db.audit_logs.create_index([("timestamp", -1)])
            logger.info("[DB] Indexes verified successfully.")
        except Exception as idx_err:
            logger.warning(f"[DB] Index creation notice: {idx_err}")

db_manager = DatabaseManager()

def get_db():
    return db_manager.db

class User(UserMixin):
    def __init__(self, user_data):
        self.data = user_data
        self.id = str(user_data.get("_id"))
        self.username = user_data.get("username", "")
        self.email = user_data.get("email", "")
        self.role = user_data.get("role", "faculty")  # 'admin' or 'faculty'
        self.full_name = user_data.get("full_name", self.username)
        self.status = user_data.get("status", "active")
        self.department = user_data.get("department", "")

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_faculty(self):
        return self.role == "faculty"

    @property
    def is_active(self):
        return self.status == "active"

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    if db is None:
        return None
    try:
        user_doc = db.users.find_one({"_id": ObjectId(user_id)})
        if user_doc:
            return User(user_doc)
    except Exception:
        pass
    return None
