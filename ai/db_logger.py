from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "bengaluru_traffic")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

violations_collection = db["violations"]
traffic_collection = db["traffic_stats"]

def log_violation(violation: dict, snapshot_file: str = None):
    """Save violation to MongoDB"""
    doc = {
        "type": violation.get("type"),
        "track_id": violation.get("track_id"),
        "timestamp": violation.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "position": violation.get("position"),
        "snapshot": snapshot_file,
        "created_at": datetime.now()
    }
    result = violations_collection.insert_one(doc)
    print(f"✅ Violation logged to DB: {result.inserted_id}")
    return str(result.inserted_id)

def log_traffic_stats(vehicle_counts: dict, congestion_level: str):
    """Save traffic stats every few seconds"""
    doc = {
        "vehicle_counts": vehicle_counts,
        "congestion_level": congestion_level,
        "total": sum(vehicle_counts.values()),
        "timestamp": datetime.now()
    }
    traffic_collection.insert_one(doc)

def get_violations_from_db(limit=20):
    """Fetch recent violations from DB"""
    results = violations_collection.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).limit(limit)
    return list(results)

def get_violation_stats():
    """Get count by violation type"""
    pipeline = [
        {"$group": {"_id": "$type", "count": {"$sum": 1}}}
    ]
    return list(violations_collection.aggregate(pipeline))