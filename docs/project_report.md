# STUDENT TRACKER SYSTEM — B.TECH MINI PROJECT REPORT

**Degree**: Bachelor of Technology (B.Tech) in Computer Science & Engineering  
**Academic Year**: 2025 – 2026  
**Project Title**: Student Tracker System  

---

## 1. ABSTRACT
The **Student Tracker System** is an enterprise-grade academic management web application engineered using Python 3, Flask, MongoDB, Bootstrap 5, and Chart.js. The primary objective is to streamline academic tracking by consolidating student records, daily attendance tracking with automated 75% threshold alerts, validated marks entry with configurable grade computation, assignment deadline and submission tracking, and real-time executive dashboard visualizations. By leveraging NoSQL MongoDB document architecture, the system guarantees low latency queries, high scalability, and an audited event log for academic compliance.

---

## 2. INTRODUCTION & PROBLEM STATEMENT

### 2.1 Background
Conventional college administrative workflows often rely on disparate spreadsheets, paper registers, or siloed software. This fragmentation leads to:
- Time-consuming manual attendance percentage computations.
- Delays in identifying students at academic risk or below statutory attendance thresholds (75%).
- Vulnerabilities in grade and marks records without audit logging.
- Inefficiencies in tracking assignment submission deadlines across semesters.

### 2.2 Proposed Solution
The Student Tracker System provides:
- A centralized web dashboard for administrators (Deans/HODs) and faculty members.
- Automated percentage and grade calculation rules (`A+`, `A`, `B`, `C`, `D`, `F`).
- Daily session attendance recording with quick actions and amendment audit tracking.
- Interactive Chart.js charts for attendance trends and grade distributions.
- Instant CSV data export and printable academic transcripts.

---

## 3. SYSTEM ARCHITECTURE & DESIGN

```
+-----------------------------------------------------------+
|                   Client Web Browser                      |
|       (HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js)     |
+-----------------------------+-----------------------------+
                              | HTTPS / HTTP
                              v
+-----------------------------------------------------------+
|                   Flask Application Server                |
|  +--------------------+  +-----------------------------+  |
|  | Route Blueprints   |  | Authentication / Sessions   |  |
|  | - Auth             |  | - Flask-Login               |  |
|  | - Dashboard        |  | - Werkzeug Security         |  |
|  | - Students         |  +-----------------------------+  |
|  | - Attendance       |  +-----------------------------+  |
|  | - Marks            |  | Services Layer              |  |
|  | - Assignments      |  | - Attendance Calculation    |  |
|  | - Reports          |  | - Grading & Performance     |  |
|  +--------------------+  | - CSV & Metrics Aggregation |  |
|                          +-----------------------------+  |
+-----------------------------+-----------------------------+
                              | PyMongo Driver
                              v
+-----------------------------------------------------------+
|                 MongoDB Database Engine                   |
|  Collections: users, students, faculty, courses,          |
|  attendance, assessments, marks, assignments, submissions,|
|  audit_logs                                               |
+-----------------------------------------------------------+
```

---

## 4. DATABASE SCHEMA (MONGODB COLLECTIONS)

| Collection | Key Fields | Indexes & Constraints |
| :--- | :--- | :--- |
| `users` | `username`, `email`, `password_hash`, `role`, `status` | Unique on `username`, `email` |
| `students` | `student_id`, `roll_number`, `first_name`, `last_name`, `email`, `department`, `semester`, `status` | Unique on `student_id`, `roll_number` |
| `faculty` | `faculty_id`, `name`, `email`, `department`, `assigned_subjects`, `status` | Unique on `faculty_id`, `email` |
| `courses` | `course_id`, `course_name`, `department`, `semester`, `subjects` | Unique on `course_id` |
| `attendance` | `student_id`, `subject_code`, `date`, `status`, `recorded_by`, `edit_reason` | Compound unique on `(student_id, subject_code, date)` |
| `assessments` | `assessment_id`, `name`, `subject_code`, `max_marks`, `assessment_date` | Unique on `assessment_id` |
| `marks` | `student_id`, `assessment_id`, `marks_obtained`, `max_marks`, `remarks` | Compound unique on `(student_id, assessment_id)` |
| `assignments` | `assignment_id`, `title`, `description`, `subject_code`, `deadline`, `max_score` | Unique on `assignment_id` |
| `submissions` | `assignment_id`, `student_id`, `status`, `submission_date`, `feedback`, `grade` | Compound unique on `(assignment_id, student_id)` |
| `audit_logs` | `user`, `action`, `affected_record`, `details`, `timestamp` | Descending index on `timestamp` |

---

## 5. BUSINESS RULES IMPLEMENTATION

1. **Attendance Calculation Formula**:
   $$\text{Attendance } \% = \frac{\text{Present} + \text{Late}}{\text{Total Sessions} - \text{Excused Sessions}} \times 100$$
   *Excused absences (verified medical leaves) reduce the required session count without penalizing the student.*

2. **Low Attendance Alert**:
   - Compares overall rate with configurable threshold ($75\%$).
   - Flags students on the dashboard and student detail profile.

3. **Academic Grading Rules**:
   - `A+`: $\ge 90\%$ (Outstanding)
   - `A`: $\ge 80\%$ (Excellent)
   - `B`: $\ge 70\%$ (Very Good)
   - `C`: $\ge 60\%$ (Good)
   - `D`: $\ge 50\%$ (Pass)
   - `F`: $< 50\%$ (Fail / Needs Academic Support)

4. **Marks Validation**:
   $$0 \le \text{Marks Obtained} \le \text{Maximum Marks}$$

5. **Soft Archival Policy**:
   Students are marked `status: 'archived'` rather than permanently deleted from the database. This guarantees academic record retention for official transcripts.

---

## 6. TESTING & VALIDATION

Automated testing was conducted using `pytest`. All 8 core test suites passed:
- `test_login_success`: Validates session generation and dashboard landing.
- `test_login_invalid`: Verifies rejection of incorrect credentials.
- `test_protected_route_redirects_unauthenticated`: Confirms route guards.
- `test_student_crud`: Verifies student creation, retrieval, updates, and archival.
- `test_attendance_calculations`: Verifies $75\%$ threshold and formula calculations.
- `test_marks_grade_rules`: Validates grading scale boundaries (`A+` to `F`).
- `test_marks_max_validation`: Ensures negative marks or marks exceeding max are rejected with exceptions.
- `test_csv_exports`: Validates headers and data integrity across Student, Attendance, and Marks CSV exports.

---

## 7. CONCLUSION & FUTURE ENHANCEMENTS

The Student Tracker System successfully fulfills all functional, architectural, and security requirements of the B.Tech mini project specification. It delivers a production-grade, intuitive, and responsive platform for college management.

### Future Scope:
- Biometric & RFID attendance integration.
- Automated SMS and Email notifications to parents for low attendance (<75%).
- AI-driven predictive analytics forecasting student dropout risks.
- Mobile application using React Native connecting to the Flask REST API.
