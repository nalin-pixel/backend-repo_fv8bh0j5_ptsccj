import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "ecommerce_db")

_client = MongoClient(DATABASE_URL)
_db = _client[DATABASE_NAME]


def collection(name: str) -> Collection:
    return _db[name]


def create_document(collection_name: str, data: Dict[str, Any]) -> str:
    now = datetime.utcnow()
    data["created_at"] = now
    data["updated_at"] = now
    result = collection(collection_name).insert_one(data)
    return str(result.inserted_id)


def update_document(collection_name: str, filter_dict: Dict[str, Any], data: Dict[str, Any]) -> int:
    data["updated_at"] = datetime.utcnow()
    res = collection(collection_name).update_one(filter_dict, {"$set": data})
    return res.modified_count


def get_documents(collection_name: str, filter_dict: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[Dict[str, Any]]:
    cur = collection(collection_name).find(filter_dict or {}).limit(limit)
    items: List[Dict[str, Any]] = []
    for d in cur:
        d["id"] = str(d.pop("_id"))
        items.append(d)
    return items


def get_document(collection_name: str, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    d = collection(collection_name).find_one(filter_dict)
    if not d:
        return None
    d["id"] = str(d.pop("_id"))
    return d


def delete_document(collection_name: str, filter_dict: Dict[str, Any]) -> int:
    res = collection(collection_name).delete_one(filter_dict)
    return res.deleted_count
