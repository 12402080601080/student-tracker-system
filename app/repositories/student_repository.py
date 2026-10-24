from datetime import datetime
from bson.objectid import ObjectId
from app.extensions import get_db

class StudentRepository:
    def __init__(self):
        pass

    @property
    def col(self):
        return get_db().students

    def create(self, data):
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        if "status" not in data:
            data["status"] = "active"
        result = self.col.insert_one(data)
        data["_id"] = result.inserted_id
        return data

    def get_by_id(self, student_id):
        return self.col.find_one({"student_id": str(student_id).strip()})

    def get_by_mongo_id(self, oid):
        try:
            return self.col.find_one({"_id": ObjectId(oid)})
        except Exception:
            return None

    def get_by_roll(self, roll_number):
        return self.col.find_one({"roll_number": str(roll_number).strip()})

    def update(self, student_id, data):
        data["updated_at"] = datetime.utcnow()
        self.col.update_one({"student_id": student_id}, {"$set": data})
        return self.get_by_id(student_id)

    def archive(self, student_id, reason="Archived by user"):
        return self.col.update_one(
            {"student_id": student_id},
            {"$set": {"status": "archived", "archive_reason": reason, "updated_at": datetime.utcnow()}}
        )

    def restore(self, student_id):
        return self.col.update_one(
            {"student_id": student_id},
            {"$set": {"status": "active", "updated_at": datetime.utcnow()}}
        )

    def list_students(self, filters=None, search=None, sort_field="student_id", sort_dir=1, page=1, per_page=15):
        query = {}
        if filters:
            if filters.get("department"):
                query["department"] = filters["department"]
            if filters.get("semester"):
                query["semester"] = int(filters["semester"])
            if filters.get("status"):
                query["status"] = filters["status"]
            else:
                # Default to non-archived or all depending on request
                pass

        if search:
            s = str(search).strip()
            query["$or"] = [
                {"student_id": {"$regex": s, "$options": "i"}},
                {"roll_number": {"$regex": s, "$options": "i"}},
                {"first_name": {"$regex": s, "$options": "i"}},
                {"last_name": {"$regex": s, "$options": "i"}},
                {"email": {"$regex": s, "$options": "i"}},
            ]

        total = self.col.count_documents(query)
        skip = (page - 1) * per_page
        cursor = self.col.find(query).sort(sort_field, sort_dir).skip(skip).limit(per_page)
        items = list(cursor)

        total_pages = (total + per_page - 1) // per_page if total > 0 else 1
        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages
        }

    def get_all_active(self):
        return list(self.col.find({"status": "active"}).sort("first_name", 1))

    def count_by_status(self, status="active"):
        return self.col.count_documents({"status": status})

    def count_total(self):
        return self.col.count_documents({})

student_repo = StudentRepository()
