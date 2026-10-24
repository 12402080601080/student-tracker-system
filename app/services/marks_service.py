from flask import current_app
from app.repositories.marks_repository import marks_repo
from app.repositories.student_repository import student_repo

class MarksService:
    def __init__(self):
        pass

    def get_grade_boundaries(self):
        if current_app:
            return current_app.config.get("GRADE_BOUNDARIES", [])
        return [
            {"grade": "A+", "min": 90.0, "description": "Outstanding"},
            {"grade": "A",  "min": 80.0, "description": "Excellent"},
            {"grade": "B",  "min": 70.0, "description": "Very Good"},
            {"grade": "C",  "min": 60.0, "description": "Good"},
            {"grade": "D",  "min": 50.0, "description": "Pass"},
            {"grade": "F",  "min": 0.0,  "description": "Fail"},
        ]

    def calculate_grade(self, percentage):
        boundaries = self.get_grade_boundaries()
        for b in boundaries:
            if percentage >= b["min"]:
                return b["grade"], b.get("description", "")
        return "F", "Fail"

    def get_student_academic_summary(self, student_id):
        marks_records = marks_repo.get_student_marks(student_id)
        if not marks_records:
            return {
                "records": [],
                "total_assessments": 0,
                "overall_percentage": 0.0,
                "overall_grade": "N/A",
                "needs_support": False,
                "failed_count": 0
            }

        total_obtained = 0.0
        total_max = 0.0
        failed_count = 0
        detailed_records = []

        for m in marks_records:
            obtained = float(m.get("marks_obtained", 0))
            max_m = float(m.get("max_marks", 100))
            pct = round((obtained / max_m) * 100.0, 2) if max_m > 0 else 0.0
            grade, desc = self.calculate_grade(pct)

            if grade == "F":
                failed_count += 1

            total_obtained += obtained
            total_max += max_m

            detailed_records.append({
                **m,
                "percentage": pct,
                "grade": grade,
                "grade_desc": desc
            })

        overall_pct = round((total_obtained / total_max) * 100.0, 2) if total_max > 0 else 0.0
        overall_grade, _ = self.calculate_grade(overall_pct)
        needs_support = (overall_pct < 50.0) or (failed_count > 0)

        return {
            "records": detailed_records,
            "total_assessments": len(marks_records),
            "total_obtained": total_obtained,
            "total_max": total_max,
            "overall_percentage": overall_pct,
            "overall_grade": overall_grade,
            "needs_support": needs_support,
            "failed_count": failed_count
        }

    def get_assessment_analytics(self, assessment_id):
        assessment = marks_repo.get_assessment(assessment_id)
        if not assessment:
            return None

        marks = marks_repo.get_assessment_marks(assessment_id)
        if not marks:
            return {
                "assessment": assessment,
                "count": 0,
                "average_pct": 0.0,
                "highest_marks": 0.0,
                "lowest_marks": 0.0,
                "grade_distribution": {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0},
                "student_results": []
            }

        max_marks = float(assessment.get("max_marks", 100))
        scores = [float(m.get("marks_obtained", 0)) for m in marks]
        grade_dist = {"A+": 0, "A": 0, "B": 0, "C": 0, "D": 0, "F": 0}

        student_results = []
        for m in marks:
            obtained = float(m.get("marks_obtained", 0))
            pct = round((obtained / max_marks) * 100.0, 2)
            grd, _ = self.calculate_grade(pct)
            if grd in grade_dist:
                grade_dist[grd] += 1
            st = student_repo.get_by_id(m.get("student_id"))
            student_results.append({
                **m,
                "student_name": f"{st.get('first_name', '')} {st.get('last_name', '')}".strip() if st else m.get("student_id"),
                "roll_number": st.get("roll_number", "") if st else "",
                "percentage": pct,
                "grade": grd
            })

        avg_score = sum(scores) / len(scores)
        avg_pct = round((avg_score / max_marks) * 100.0, 2)

        return {
            "assessment": assessment,
            "count": len(marks),
            "average_marks": round(avg_score, 2),
            "average_pct": avg_pct,
            "highest_marks": max(scores),
            "lowest_marks": min(scores),
            "grade_distribution": grade_dist,
            "student_results": student_results
        }

    def get_at_risk_students(self):
        """Identifies active students needing academic assistance."""
        students = student_repo.get_all_active()
        at_risk = []
        for s in students:
            summary = self.get_student_academic_summary(s["student_id"])
            if summary["total_assessments"] > 0 and summary["needs_support"]:
                at_risk.append({
                    "student": s,
                    "summary": summary
                })
        return at_risk

marks_service = MarksService()
