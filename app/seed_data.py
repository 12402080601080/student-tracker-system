from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash
from app.extensions import get_db

def seed_initial_data(force=False):
    db = get_db()
    if db is None:
        return

    # Check if already seeded
    if not force and db.users.count_documents({}) > 0:
        return

    print("[SEED] Populating database with realistic academic data...")

    # 1. Users
    admin_user = {
        "username": "admin",
        "email": "admin@college.edu",
        "password_hash": generate_password_hash("Admin@123"),
        "role": "admin",
        "full_name": "Dr. Sarah Mitchell (Dean)",
        "department": "Computer Science & Engineering",
        "status": "active",
        "created_at": datetime.utcnow()
    }
    faculty_user = {
        "username": "faculty",
        "email": "prof.robert@college.edu",
        "password_hash": generate_password_hash("Faculty@123"),
        "role": "faculty",
        "full_name": "Prof. Robert Davis",
        "department": "Computer Science & Engineering",
        "status": "active",
        "created_at": datetime.utcnow()
    }
    db.users.update_one({"username": "admin"}, {"$set": admin_user}, upsert=True)
    db.users.update_one({"username": "faculty"}, {"$set": faculty_user}, upsert=True)

    # 2. Faculty
    faculty_records = [
        {
            "faculty_id": "FAC101",
            "name": "Prof. Robert Davis",
            "email": "prof.robert@college.edu",
            "phone": "+91 98765 43210",
            "department": "Computer Science & Engineering",
            "designation": "Associate Professor",
            "assigned_subjects": ["CS301", "CS302"],
            "status": "active"
        },
        {
            "faculty_id": "FAC102",
            "name": "Dr. Emily Watson",
            "email": "emily.watson@college.edu",
            "phone": "+91 98765 43211",
            "department": "Computer Science & Engineering",
            "designation": "Assistant Professor",
            "assigned_subjects": ["CS303"],
            "status": "active"
        },
        {
            "faculty_id": "FAC103",
            "name": "Prof. Michael Chang",
            "email": "m.chang@college.edu",
            "phone": "+91 98765 43212",
            "department": "Information Technology",
            "designation": "Head of Department",
            "assigned_subjects": ["IT301", "IT302"],
            "status": "active"
        }
    ]
    for f in faculty_records:
        db.faculty.update_one({"faculty_id": f["faculty_id"]}, {"$set": f}, upsert=True)

    # 3. Courses & Subjects
    courses = [
        {
            "course_id": "BTECH-CSE",
            "course_name": "B.Tech Computer Science & Engineering",
            "department": "Computer Science & Engineering",
            "semester": 5,
            "academic_year": "2025-2026",
            "subjects": [
                {"code": "CS301", "name": "Data Structures & Algorithms", "credits": 4, "faculty": "Prof. Robert Davis"},
                {"code": "CS302", "name": "Database Management Systems", "credits": 4, "faculty": "Prof. Robert Davis"},
                {"code": "CS303", "name": "Operating Systems", "credits": 3, "faculty": "Dr. Emily Watson"},
                {"code": "CS304", "name": "Computer Networks", "credits": 3, "faculty": "Prof. Alan Turing"}
            ]
        },
        {
            "course_id": "BTECH-IT",
            "course_name": "B.Tech Information Technology",
            "department": "Information Technology",
            "semester": 5,
            "academic_year": "2025-2026",
            "subjects": [
                {"code": "IT301", "name": "Web Technologies", "credits": 4, "faculty": "Prof. Michael Chang"},
                {"code": "IT302", "name": "Cloud Computing", "credits": 3, "faculty": "Prof. Michael Chang"}
            ]
        }
    ]
    for c in courses:
        db.courses.update_one({"course_id": c["course_id"]}, {"$set": c}, upsert=True)

    # 4. Students
    sample_students = [
        ("STU1001", "22CS01", "Aarav", "Sharma", "aarav.sharma@student.edu", "+91 91234 56001", "Computer Science & Engineering", "BTECH-CSE", 5, "2025-2026", "active"),
        ("STU1002", "22CS02", "Diya", "Patel", "diya.patel@student.edu", "+91 91234 56002", "Computer Science & Engineering", "BTECH-CSE", 5, "2025-2026", "active"),
        ("STU1003", "22CS03", "Rohan", "Verma", "rohan.verma@student.edu", "+91 91234 56003", "Computer Science & Engineering", "BTECH-CSE", 5, "2025-2026", "active"),
        ("STU1004", "22CS04", "Ananya", "Iyer", "ananya.iyer@student.edu", "+91 91234 56004", "Computer Science & Engineering", "BTECH-CSE", 5, "2025-2026", "active"),
        ("STU1005", "22CS05", "Kabir", "Mehta", "kabir.mehta@student.edu", "+91 91234 56005", "Computer Science & Engineering", "BTECH-CSE", 5, "2025-2026", "active"),
        ("STU1006", "22CS06", "Zara", "Khan", "zara.khan@student.edu", "+91 91234 56006", "Computer Science & Engineering", "BTECH-CSE", 5, "2025-2026", "active"),
        ("STU1007", "22CS07", "Vikram", "Reddy", "vikram.reddy@student.edu", "+91 91234 56007", "Computer Science & Engineering", "BTECH-CSE", 5, "2025-2026", "active"),
        ("STU1008", "22CS08", "Priya", "Nair", "priya.nair@student.edu", "+91 91234 56008", "Computer Science & Engineering", "BTECH-CSE", 5, "2025-2026", "active"),
        ("STU1009", "22IT01", "Arjun", "Kapoor", "arjun.kapoor@student.edu", "+91 91234 56009", "Information Technology", "BTECH-IT", 5, "2025-2026", "active"),
        ("STU1010", "22IT02", "Ishita", "Gupta", "ishita.gupta@student.edu", "+91 91234 56010", "Information Technology", "BTECH-IT", 5, "2025-2026", "archived"),
    ]

    for sid, roll, fn, ln, email, phone, dept, course, sem, ay, status in sample_students:
        sdoc = {
            "student_id": sid,
            "roll_number": roll,
            "first_name": fn,
            "last_name": ln,
            "email": email,
            "phone": phone,
            "department": dept,
            "course": course,
            "semester": sem,
            "academic_year": ay,
            "status": status,
            "enrollment_date": "2022-08-15",
            "created_at": datetime.utcnow()
        }
        db.students.update_one({"student_id": sid}, {"$set": sdoc}, upsert=True)

    # 5. Assessments
    assessments = [
        {"assessment_id": "ASS-CS301-M1", "name": "Mid-Term Exam (Unit 1 & 2)", "subject_code": "CS301", "max_marks": 50.0, "assessment_date": "2026-09-15", "academic_year": "2025-2026", "semester": 5},
        {"assessment_id": "ASS-CS302-Q1", "name": "Quiz 1 - SQL Queries & Normalization", "subject_code": "CS302", "max_marks": 25.0, "assessment_date": "2026-09-20", "academic_year": "2025-2026", "semester": 5},
        {"assessment_id": "ASS-CS303-T1", "name": "Class Test - Process Scheduling", "subject_code": "CS303", "max_marks": 30.0, "assessment_date": "2026-09-28", "academic_year": "2025-2026", "semester": 5},
    ]
    for a in assessments:
        db.assessments.update_one({"assessment_id": a["assessment_id"]}, {"$set": a}, upsert=True)

    # 6. Marks (Varied marks to showcase A+, A, B, C, D, and F/Support Needed)
    # Aarav: Outstanding (46/50 = 92%)
    # Diya: Excellent (43/50 = 86%)
    # Kabir: Needs support (21/50 = 42% -> F)
    # Zara: Good (34/50 = 68% -> C)
    marks_data = [
        ("STU1001", "ASS-CS301-M1", 46.0, "Outstanding problem solving"),
        ("STU1002", "ASS-CS301-M1", 43.5, "Strong theoretical foundation"),
        ("STU1003", "ASS-CS301-M1", 38.0, "Good performance"),
        ("STU1004", "ASS-CS301-M1", 35.5, "Satisfactory work"),
        ("STU1005", "ASS-CS301-M1", 21.0, "Needs academic mentoring in Dynamic Programming"),
        ("STU1006", "ASS-CS301-M1", 34.0, "Average understanding"),
        ("STU1007", "ASS-CS301-M1", 47.0, "Top score in batch"),
        ("STU1008", "ASS-CS301-M1", 29.0, "Can improve time management"),

        ("STU1001", "ASS-CS302-Q1", 24.0, "Perfect join execution"),
        ("STU1002", "ASS-CS302-Q1", 22.5, "Well organized ER design"),
        ("STU1005", "ASS-CS302-Q1", 11.0, "Failed normalization test - remedial assigned"),
        ("STU1007", "ASS-CS302-Q1", 25.0, "Flawless answers"),
    ]
    for sid, aid, score, rem in marks_data:
        db.marks.update_one(
            {"student_id": sid, "assessment_id": aid},
            {"$set": {
                "student_id": sid,
                "assessment_id": aid,
                "marks_obtained": score,
                "max_marks": 50.0 if "M1" in aid else 25.0,
                "remarks": rem,
                "updated_by": "Prof. Robert Davis",
                "updated_at": datetime.utcnow()
            }},
            upsert=True
        )

    # 7. Attendance Sessions for the past 10 days
    base_date = datetime.utcnow().date()
    for day_offset in range(1, 10):
        dt_str = (base_date - timedelta(days=day_offset)).strftime("%Y-%m-%d")
        for sid, _, _, _, _, _, _, _, _, _, st in sample_students:
            if st != "active":
                continue

            # Give Kabir low attendance (~60%) to test low-attendance alert!
            if sid == "STU1005":
                status = "absent" if day_offset % 2 == 0 else "present"
            elif sid == "STU1004" and day_offset == 3:
                status = "excused"
            elif day_offset == 5 and sid in ["STU1003", "STU1006"]:
                status = "late"
            else:
                status = "present"

            db.attendance.update_one(
                {"student_id": sid, "subject_code": "CS301", "date": dt_str},
                {"$set": {
                    "student_id": sid,
                    "subject_code": "CS301",
                    "date": dt_str,
                    "status": status,
                    "notes": "Regular class session",
                    "recorded_by": "Prof. Robert Davis",
                    "created_at": datetime.utcnow()
                }},
                upsert=True
            )

    # 8. Assignments
    assignments = [
        {
            "assignment_id": "ASG-CS301-01",
            "title": "Red-Black Tree & AVL Tree Implementation in C++",
            "description": "Implement insertion, deletion, and rotation operations for balanced binary search trees. Include test benchmark results.",
            "subject_code": "CS301",
            "semester": 5,
            "deadline": (datetime.utcnow() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "max_score": 100,
            "created_by": "Prof. Robert Davis",
            "created_at": datetime.utcnow()
        },
        {
            "assignment_id": "ASG-CS302-02",
            "title": "Normalized Schema Design for Hospital Management",
            "description": "Design an ER diagram and convert it to 3NF/BCNF relations with complete SQL DDL and sample queries.",
            "subject_code": "CS302",
            "semester": 5,
            "deadline": (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d"),  # Overdue assignment
            "max_score": 50,
            "created_by": "Prof. Robert Davis",
            "created_at": datetime.utcnow() - timedelta(days=10)
        }
    ]
    for asg in assignments:
        db.assignments.update_one({"assignment_id": asg["assignment_id"]}, {"$set": asg}, upsert=True)

    # Submissions
    db.submissions.update_one(
        {"assignment_id": "ASG-CS301-01", "student_id": "STU1001"},
        {"$set": {
            "assignment_id": "ASG-CS301-01",
            "student_id": "STU1001",
            "status": "graded",
            "grade": "98/100",
            "feedback": "Clean code and optimal rotation logic.",
            "submission_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        }},
        upsert=True
    )
    db.submissions.update_one(
        {"assignment_id": "ASG-CS301-01", "student_id": "STU1002"},
        {"$set": {
            "assignment_id": "ASG-CS301-01",
            "student_id": "STU1002",
            "status": "submitted",
            "grade": "",
            "feedback": "",
            "submission_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        }},
        upsert=True
    )

    # 9. Initial Audit Logs
    audit_entries = [
        {"user": "admin", "action": "SYSTEM_INIT", "affected_record": "Database", "details": "Initial academic term 2025-2026 configured.", "timestamp": datetime.utcnow() - timedelta(days=20)},
        {"user": "Prof. Robert Davis", "action": "MARKS_ENTERED", "affected_record": "ASS-CS301-M1", "details": "Entered Mid-Term marks for Section A.", "timestamp": datetime.utcnow() - timedelta(days=10)},
        {"user": "Prof. Robert Davis", "action": "ATTENDANCE_RECORDED", "affected_record": "CS301 (Today)", "details": "Marked daily attendance for Semester 5.", "timestamp": datetime.utcnow() - timedelta(hours=2)},
    ]
    db.audit_logs.insert_many(audit_entries)

    print("[SEED] Completed populating initial sample data.")
