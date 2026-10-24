# VIVA VOCE PREPARATION GUIDE & INTERVIEW QUESTIONS
## B.Tech Mini Project — Student Tracker System

---

## CATEGORY 1: ARCHITECTURE & FLASK CONCEPTS

### Q1: What architectural pattern is implemented in this project?
**Answer**:
The project follows a **Separation of Concerns (SoC) / 3-Tier Layered Architecture**:
1. **Presentation / Routing Layer (`app/routes/`)**: Handled by Flask Blueprints that process HTTP requests, parse query/form parameters, enforce authentication, and render Jinja2 HTML templates.
2. **Business Logic / Service Layer (`app/services/`)**: Implements academic business rules such as attendance percentage calculation (with excused session deductions), grade boundary mapping, at-risk student detection, and CSV generation.
3. **Data Access / Repository Layer (`app/repositories/`)**: Encapsulates all PyMongo queries, projections, updates, and indexing so the business layer remains decoupled from database specifics.

### Q2: Why did you use the Application Factory Pattern (`create_app()`)?
**Answer**:
The Application Factory pattern (`create_app()` in `app/__init__.py`) dynamically creates and configures the Flask application instance depending on the environment (`development`, `testing`, or `production`). This allows:
- Creating isolated test instances with `mongomock` in `pytest` without interfering with development data.
- Registering blueprints, filters, and extensions cleanly.
- Preventing circular import dependencies.

### Q3: What are Flask Blueprints and why are they used?
**Answer**:
Blueprints (`Blueprint`) allow modularizing a Flask application into logical, reusable components with their own URL prefixes, view handlers, and templates. In our project, separate blueprints exist for:
- `auth`: Authentication and login/logout.
- `dashboard`: Executive KPI statistics and Chart.js feeds.
- `students`: Student directory and profile management.
- `faculty`: Teaching staff assignments.
- `courses`: Academic programs and curriculum.
- `attendance`: Session attendance and audited amendments.
- `marks`: Assessments and grade entries.
- `assignments`: Coursework and submissions.
- `reports`: CSV exports and audit logs.

### Q4: How does session management and authentication work?
**Answer**:
Authentication is managed via `Flask-Login` and `Werkzeug`:
1. When a user logs in, their password hash is verified using `werkzeug.security.check_password_hash()`.
2. On successful verification, `login_user(user, remember=remember)` writes an encrypted, HTTP-only session cookie to the client browser.
3. Protected routes are annotated with `@login_required`. Unauthorized requests are redirected to `/auth/login` with flash warnings.
4. The user loader callback `load_user(user_id)` fetches the user document from MongoDB by `ObjectId`.

---

## CATEGORY 2: MONGODB & DATABASE DESIGN

### Q5: Why choose MongoDB (NoSQL) over a traditional Relational Database (MySQL/PostgreSQL)?
**Answer**:
1. **Flexible Document Model**: Academic structures vary across departments (e.g. varying subject lists, credits, flexible feedback formats). MongoDB BSON documents naturally represent hierarchical data without requiring complex join tables.
2. **Schema Evolution**: Adding new assessment categories or custom attributes to student profiles does not require complex SQL migrations or table locks.
3. **High Performance**: MongoDB's memory-mapped storage engine and compound indexing provide sub-millisecond query performance for large student cohorts.
4. **Resilient Local & Cloud Compatibility**: The application seamlessly connects to MongoDB Atlas or local MongoDB instances, and provides an automatic fallback to `mongomock` for zero-configuration testing.

### Q6: How do you prevent duplicate attendance records and duplicate marks in MongoDB?
**Answer**:
We enforce compound unique indexes at the database level:
- For Attendance:
  ```python
  db.attendance.create_index([("student_id", 1), ("subject_code", 1), ("date", 1)], unique=True)
  ```
  This ensures a student cannot have more than one attendance entry for the same subject on the same calendar day.
- For Marks:
  ```python
  db.marks.create_index([("student_id", 1), ("assessment_id", 1)], unique=True)
  ```
  This guarantees that a student cannot have duplicate marks records for a single assessment.

### Q7: What is an "upsert" operation in MongoDB and where is it used in the project?
**Answer**:
An `upsert` (`update_one(filter, update, upsert=True)`) updates a document if it matches the filter criteria, or automatically inserts a new document if no match is found. We utilize upserts in:
- Attendance marking: Updates existing records if attendance is amended, or creates new records on first marking.
- Marks entry: Allows faculty to re-enter or revise marks without creating duplicate documents.

### Q8: Why did you implement soft archiving instead of deleting student records?
**Answer**:
Permanently deleting (`DELETE` / `remove`) a student would create dangling foreign keys and destroy past academic history (historical attendance logs, transcripts, class averages). Instead, we mark `status: "archived"` with a recorded reason. Archived students are excluded from active session rosters, while their historical transcripts remain fully intact.

---

## CATEGORY 3: BUSINESS LOGIC & SECURITY

### Q9: How is the attendance percentage calculated when a student has excused absences?
**Answer**:
According to standard college academic regulations, an approved medical or institutional excused absence should not penalize the student:
$$\text{Attendance } \% = \frac{\text{Present Sessions} + \text{Late Sessions}}{\text{Total Sessions} - \text{Excused Sessions}} \times 100$$
If all sessions are excused, the percentage is defined as $100\%$. If the rate drops below the configurable $75\%$ threshold, the system flags the student with a warning badge.

### Q10: How do you validate marks entered by faculty?
**Answer**:
Marks validation occurs both client-side and server-side:
1. **Client-side**: JavaScript listens to the input event, verifies $0 \le \text{marks} \le \text{max\_marks}$, and computes real-time percentage and grade previews.
2. **Server-side (`MarksRepository.enter_mark`)**: Validates that marks are non-negative and do not exceed the assessment's `max_marks`. If a violation occurs, a `ValueError` is raised and presented to the user via flash notifications.

### Q11: How are passwords secured in the database?
**Answer**:
Passwords are never stored in plain text. We utilize `werkzeug.security.generate_password_hash()`, which implements the **PBKDF2** algorithm with **SHA-256** and a cryptographically secure random salt. This protects against rainbow table attacks and credential leaks.

### Q12: What is the purpose of the Audit Log module?
**Answer**:
Academic systems require traceability for compliance and accreditation. The `audit_logs` collection records:
- User identity who performed the action.
- Action type (`ATTENDANCE_RECORDED`, `ATTENDANCE_EDITED`, `MARKS_ENTERED`, `STUDENT_ARCHIVED`).
- Target record / entity ID.
- Mandatory reason for sensitive changes (e.g., attendance amendments).
- High-precision UTC timestamp.

---

## CATEGORY 4: TESTING & DEPLOYMENT

### Q13: How was automated testing conducted?
**Answer**:
We implemented an automated test suite using `pytest` located in `tests/test_tracker.py`:
- Configured a test client fixture (`tests/conftest.py`) using `mongomock`.
- Tests cover authentication, unauthenticated route guards, student CRUD, attendance calculation formulas, marks boundary rules, input validation, and CSV export streaming.

### Q14: How does the application handle database disconnection or testing environments?
**Answer**:
In `app/extensions.py`, the `DatabaseManager` tests the connection to MongoDB with a short timeout (`serverSelectionTimeoutMS=2000`). If a connection cannot be established or during automated testing, it gracefully falls back to `mongomock`. This guarantees the application can run and be demonstrated anytime, anywhere, without dependency on external server states.
