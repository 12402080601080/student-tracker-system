# Student Tracker System — B.Tech Mini Project

A centralized web-based academic management and student performance tracking application developed with **Python 3, Flask, MongoDB (Atlas / Local / In-Memory Mock), Bootstrap 5, and Chart.js**.

---

## 🌟 Key Highlights & Features

1. **Authentication & Role-Based Access Control**:
   - Secure login & logout for **Admin (Dean/HOD)** and **Faculty**.
   - Password hashing via Werkzeug (`pbkdf2:sha256`).
   - Protected routes and session management via `Flask-Login`.

2. **Executive Academic Dashboard**:
   - Real-time summary statistic cards: Total Enrolled, Active Students, Total Faculty, Today's Attendance %, Average Marks %, and Pending Coursework.
   - Dynamic **Chart.js** visualizations:
     - **Attendance Breakdown**: Doughnut chart of Present, Late, Absent, and Excused sessions.
     - **Academic Grade Distribution**: Bar chart categorizing students across grade bands (A+, A, B, C, D, F).
   - Instant banners for **Low-Attendance Alerts (< 75%)** and **Students Requiring Academic Support (Grade F)**.
   - Recent students table and real-time audit activity feed.

3. **Student Profile Management**:
   - Add, view, edit, and archive students.
   - Comprehensive student profile with personal details, contact info, and program enrollment.
   - Multi-criteria filtering by Department, Semester, Status, and search by Name, Student ID, or Roll Number.
   - Soft archiving policy: preserves historical transcripts and records while removing inactive students from active class lists.
   - **Printable Student Academic Transcript / Report Card** formatted for official college submission.

4. **Faculty & Curriculum Catalog**:
   - Faculty management with assigned subject codes and designations.
   - Course and curriculum catalog with departments, semesters, subjects, and credits.

5. **Attendance Management (75% Threshold Rule)**:
   - Daily attendance recording for class sessions with **Present, Late, Absent, and Excused** statuses.
   - "Mark All Present" one-click action for fast bulk entry.
   - Business rule: Approved excused sessions are factored into eligible session calculations.
   - Attendance amendment modal with mandatory reason logging for audit compliance.
   - Low attendance alert watchlist highlighting at-risk students below 75%.

6. **Marks & Academic Performance Evaluation**:
   - Assessment creation (Mid-Terms, Tests, Quizzes) with customizable Maximum Marks.
   - Interactive marks entry form with real-time percentage and grade preview.
   - Server-side validation preventing negative marks or scores exceeding maximum marks.
   - Configurable grade calculation (`A+`, `A`, `B`, `C`, `D`, `F`).
   - Assessment performance analytics (Class Average, High Score, Low Score, and Grade breakdown).

7. **Assignment & Coursework Tracking**:
   - Create assignments with deadlines, descriptions, and maximum scores.
   - Submission tracking: Submitted, Pending, Graded, and Overdue indicators.
   - Evaluator grading and constructive feedback modal.

8. **Reports, Exports & Audit Trail**:
   - One-click CSV exports:
     - `students_record.csv` (Full student directory)
     - `attendance_summary.csv` (Attendance stats and 75% alert status)
     - `marks_report.csv` (Assessment scores, percentages, and grades)
   - Tamper-evident administrative audit log tracking user logins, attendance edits, grade entries, and record updates.

9. **Zero-Configuration Resilient Database Layer**:
   - Connects to **MongoDB Atlas** or **Local MongoDB** via `MONGO_URI`.
   - Automatic fallback to high-fidelity in-memory store (`mongomock`) if no live database server is reachable, ensuring the system runs immediately for demonstrations and testing without configuration barriers!

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Flask 3.0.3, Flask-Login, Werkzeug
- **Database**: MongoDB (Atlas / Local MongoDB with PyMongo 4.8), mongomock fallback
- **Frontend**: HTML5, CSS3 (Modern Indigo Design System), Vanilla JavaScript, Bootstrap 5.3.3
- **Data Visualizations**: Chart.js 4.4.2
- **Testing**: pytest 8.2.2

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed
- (Optional) Local MongoDB or MongoDB Atlas URI. If omitted, the app runs seamlessly in mock store mode.

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone <repo-url>
cd student-tracker
pip install -r requirements.txt
```

### 3. Environment Configuration
The application comes preconfigured with default `.env`. You can modify `.env` as needed:
```env
SECRET_KEY=dev-secret-key-student-tracker-2026-btech
MONGO_URI=mongodb://localhost:27017/student_tracker
DATABASE_NAME=student_tracker
PORT=5000
ATTENDANCE_LOW_THRESHOLD=75
```

### 4. Running the Application
```bash
python run.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### 5. Default Demonstration Credentials

| Role | Username | Password | Quick Fill Button |
| :--- | :--- | :--- | :--- |
| **Administrator (Dean)** | `admin` | `Admin@123` | ✅ Available on Login page |
| **Faculty Member** | `faculty` | `Faculty@123` | ✅ Available on Login page |

---

## 🧪 Running Automated Tests

Run the complete test suite with `pytest`:
```bash
pytest tests/
```
All 8 test suites verify authentication, CRUD operations, attendance percentage formulas, marks validation, grading rules, and CSV exports.

---

## 📁 Project Structure

```
student-tracker/
|-- app/
|   |-- __init__.py                  # Flask Application Factory & Jinja filters
|   |-- extensions.py                # DatabaseManager & Flask-Login setup
|   |-- seed_data.py                 # Realistic sample academic dataset
|   |-- routes/
|   |   |-- auth.py                  # Login, Logout, Session handling
|   |   |-- dashboard.py             # Dashboard metrics & Chart.js data
|   |   |-- students.py              # Student CRUD, Search, Filter, Archive
|   |   |-- faculty.py               # Faculty management & subject assign
|   |   |-- courses.py               # Course & syllabus management
|   |   |-- attendance.py            # Attendance marking & audited edits
|   |   |-- marks.py                 # Assessments & validated marks entry
|   |   |-- assignments.py           # Assignment creation & grading
|   |   |-- reports.py               # CSV export endpoints & audit view
|   |-- services/
|   |   |-- attendance_service.py    # Attendance percentage & 75% rule
|   |   |-- marks_service.py         # Grading boundaries & risk alerts
|   |   |-- report_service.py        # CSV generators & dashboard metrics
|   |-- repositories/
|   |   |-- student_repository.py    # Student MongoDB queries
|   |   |-- attendance_repository.py # Attendance queries & aggregations
|   |   |-- marks_repository.py      # Assessment & marks queries
|   |   |-- academic_repository.py   # Faculty, courses, assignments & audit
|   |-- templates/
|   |   |-- base.html                # Master layout with sidebar & topbar
|   |   |-- login.html               # Login page with demo quick fill
|   |   |-- dashboard.html           # Metric cards, Chart.js & feeds
|   |   |-- students/                # Directory, form, profile & print transcript
|   |   |-- faculty/                 # Faculty index & edit form
|   |   |-- courses/                 # Course index & dynamic subject form
|   |   |-- attendance/              # Roster view & daily marking table
|   |   |-- marks/                   # Assessment overview, entry & results
|   |   |-- assignments/             # Assignments list & grading modal
|   |   |-- reports/                 # CSV export cards & audit trail
|   |   |-- errors/                  # 404, 403, 500 error pages
|   |-- static/
|   |   |-- css/style.css            # Custom modern Indigo design stylesheet
|   |   |-- js/main.js               # Interactive scripts & confirmations
|-- tests/
|   |-- conftest.py                  # Pytest fixtures
|   |-- test_tracker.py              # Complete automated test suite
|-- config.py                        # Environment configurations
|-- run.py                           # Application startup entrypoint
|-- requirements.txt                 # Dependencies
|-- .env                             # Environment configuration
|-- .gitignore                       # Git ignore file
|-- README.md                        # Documentation
```

---

## 📜 Academic Submission Deliverables

- Complete source code with modular architecture
- Detailed Project Report: [docs/project_report.md](docs/project_report.md)
- College Presentation Outline: [docs/presentation_slides.md](docs/presentation_slides.md)
- Viva Voce Questions & Answers Guide: [docs/viva_preparation.md](docs/viva_preparation.md)
