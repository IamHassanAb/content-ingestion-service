from src.db.core import mongo_conn
from bson import ObjectId


items_collection = mongo_conn.get_db()["items"]
# Insert an item
def insert_item(item: dict):
    try:
        result = items_collection.insert_one(item)
        return str(result.inserted_id)
    except Exception:
        # Log or handle error as needed
        return None

# Get item by ID
def get_item_by_id(item_id: str):
    try:
        return items_collection.find_one({"_id": ObjectId(item_id)})
    except Exception:
        return None

# Update item
def update_item(item_id: str, update_data: dict):
    try:
        result = items_collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": update_data}
        )
        return result.modified_count
    except Exception:
        return 0

# Delete item
def delete_item(item_id: str):
    try:
        result = items_collection.delete_one({"_id": ObjectId(item_id)})
        return result.deleted_count
    except Exception:
        return 0

# Query multiple items (example: filter by type)
def get_items_by_type(item_type: str):
    try:
        return list(items_collection.find({"type": item_type}))
    except Exception:
        return []

def get_all_items():
    try:
        return list(items_collection.find())
    except Exception:
        return []
