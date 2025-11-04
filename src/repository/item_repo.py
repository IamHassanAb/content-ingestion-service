from src.db.core import mongo_conn
from bson import ObjectId


lectures_collection = mongo_conn.get_db()["lectures"]


# Insert an item
def insert_item(item: dict):
    try:
        result = lectures_collection.insert_one(item)
        return str(result.inserted_id)
    except Exception:
        # Log or handle error as needed
        return None

def insert_many_items(items: list[dict]):
    try:
        result = lectures_collection.insert_many(items)
        if result["acknowledged"]:
            return {"status":"success","data":len(result["insertedIds"])}
    except Exception:
        return None

# Get item by ID
def get_item_by_id(item_id: str):
    try:
        print("lectures_collection.find_one({'id': item_id})")
        return lectures_collection.find_one({"id": item_id})
    except Exception:
        return None


# Update item
def update_item(item_id: str, update_data: dict):
    try:
        result = lectures_collection.update_one(
            {"id": item_id}, {"$set": update_data}
        )
        return result.modified_count
    except Exception:
        return 0


# Delete item
def delete_item(item_id: str):
    try:
        result = lectures_collection.delete_one({"id": item_id})
        return result.deleted_count
    except Exception:
        return 0


# Query multiple lectures (example: filter by type)
def get_lectures_by_type(item_type: str):
    try:
        return list(lectures_collection.find({"type": item_type}))
    except Exception:
        return []


def get_all_lectures():
    try:
        return list(lectures_collection.find())
    except Exception:
        return []

def get_all_lecture_ids():
    try:
        return list(lectures_collection.find({},{"id":1,"_id":0}))
    except Exception:
        return []