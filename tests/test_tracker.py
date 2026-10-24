import pytest
from app.services.attendance_service import attendance_service
from app.services.marks_service import marks_service
from app.repositories.marks_repository import marks_repo
from app.repositories.student_repository import student_repo
from app.repositories.attendance_repository import attendance_repo

def test_login_success(client):
    res = client.post("/auth/login", data={"username": "admin", "password": "Admin@123"}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Academic Dashboard" in res.data or b"Dashboard" in res.data

def test_login_invalid(client):
    res = client.post("/auth/login", data={"username": "admin", "password": "WrongPassword"}, follow_redirects=True)
    assert b"Invalid credentials" in res.data

def test_protected_route_redirects_unauthenticated(client):
    res = client.get("/students/", follow_redirects=False)
    assert res.status_code == 302
    assert "/auth/login" in res.headers["Location"]

def test_student_crud(auth_client, app):
    with app.app_context():
        # Create student
        new_student = {
            "student_id": "TEST999",
            "roll_number": "22TEST99",
            "first_name": "Test",
            "last_name": "User",
            "email": "test.user@test.edu",
            "phone": "+91 99999 88888",
            "department": "Computer Science & Engineering",
            "course": "BTECH-CSE",
            "semester": 5,
            "academic_year": "2025-2026",
            "status": "active"
        }
        created = student_repo.create(new_student)
        assert created["student_id"] == "TEST999"

        # Read
        found = student_repo.get_by_id("TEST999")
        assert found is not None
        assert found["first_name"] == "Test"

        # Update
        student_repo.update("TEST999", {"first_name": "UpdatedName"})
        updated = student_repo.get_by_id("TEST999")
        assert updated["first_name"] == "UpdatedName"

        # Archive
        student_repo.archive("TEST999", reason="Test archiving")
        archived = student_repo.get_by_id("TEST999")
        assert archived["status"] == "archived"

def test_attendance_calculations(app):
    with app.app_context():
        # Record 4 sessions: 2 present, 1 late, 1 absent -> Attended = 3, Eligible = 4 -> 75%
        student_id = "TEST_ATT"
        attendance_repo.record_attendance(student_id, "CS101", "2026-10-01", "present", "Tester")
        attendance_repo.record_attendance(student_id, "CS101", "2026-10-02", "present", "Tester")
        attendance_repo.record_attendance(student_id, "CS101", "2026-10-03", "late", "Tester")
        attendance_repo.record_attendance(student_id, "CS101", "2026-10-04", "absent", "Tester")

        stats = attendance_service.calculate_student_attendance(student_id)
        assert stats["total_sessions"] == 4
        assert stats["attended_sessions"] == 3
        assert stats["percentage"] == 75.0
        assert stats["is_low"] is False

        # Add 1 more absent session -> Attended = 3, Eligible = 5 -> 60% -> low attendance (<75%)
        attendance_repo.record_attendance(student_id, "CS101", "2026-10-05", "absent", "Tester")
        stats_low = attendance_service.calculate_student_attendance(student_id)
        assert stats_low["percentage"] == 60.0
        assert stats_low["is_low"] is True

def test_marks_grade_rules(app):
    with app.app_context():
        # Test grade boundaries
        assert marks_service.calculate_grade(95)[0] == "A+"
        assert marks_service.calculate_grade(85)[0] == "A"
        assert marks_service.calculate_grade(75)[0] == "B"
        assert marks_service.calculate_grade(65)[0] == "C"
        assert marks_service.calculate_grade(52)[0] == "D"
        assert marks_service.calculate_grade(45)[0] == "F"

def test_marks_max_validation(app):
    with app.app_context():
        marks_repo.create_assessment("ASS_TEST", "Unit Test", "CS101", 50.0, "2026-10-01", "2025-2026", 5)

        # Marks within max should pass
        doc = marks_repo.enter_mark("STU1001", "ASS_TEST", 45.0, "Evaluator")
        assert doc["marks_obtained"] == 45.0

        # Marks exceeding max (55 > 50) should raise ValueError
        with pytest.raises(ValueError):
            marks_repo.enter_mark("STU1001", "ASS_TEST", 55.0, "Evaluator")

        # Negative marks should raise ValueError
        with pytest.raises(ValueError):
            marks_repo.enter_mark("STU1001", "ASS_TEST", -5.0, "Evaluator")

def test_csv_exports(auth_client):
    res_students = auth_client.get("/reports/export/students")
    assert res_students.status_code == 200
    assert b"Student ID,Roll Number,First Name" in res_students.data

    res_attendance = auth_client.get("/reports/export/attendance")
    assert res_attendance.status_code == 200
    assert b"Attendance %" in res_attendance.data

    res_marks = auth_client.get("/reports/export/marks")
    assert res_marks.status_code == 200
    assert b"Marks Obtained" in res_marks.data
