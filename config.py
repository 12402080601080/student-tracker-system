import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "student-tracker-super-secret-key-2026")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/student_tracker")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "student_tracker")
    ATTENDANCE_LOW_THRESHOLD = float(os.getenv("ATTENDANCE_LOW_THRESHOLD", 75.0))

    # Configurable grading scale
    GRADE_BOUNDARIES = [
        {"grade": "A+", "min": 90.0, "description": "Outstanding"},
        {"grade": "A",  "min": 80.0, "description": "Excellent"},
        {"grade": "B",  "min": 70.0, "description": "Very Good"},
        {"grade": "C",  "min": 60.0, "description": "Good"},
        {"grade": "D",  "min": 50.0, "description": "Pass"},
        {"grade": "F",  "min": 0.0,  "description": "Fail (Needs Academic Support)"},
    ]

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set to True in HTTPS production
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    MONGO_URI = "mongomock://localhost/test_student_tracker"
    DATABASE_NAME = "test_student_tracker"
    SECRET_KEY = "test-secret-key"

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
