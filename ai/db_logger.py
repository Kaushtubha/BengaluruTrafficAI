from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "bengaluru_traffic")

db_active = False
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
    client.server_info() # Check if connection succeeds
    db = client[DB_NAME]
    violations_collection = db["violations"]
    traffic_collection = db["traffic_stats"]
    db_active = True
    print("✅ MongoDB connection active.")
except Exception:
    print("⚠️ MongoDB server is offline. Database logging disabled (will use console only).")


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
    if db_active:
        try:
            result = violations_collection.insert_one(doc)
            print(f"✅ Violation logged to DB: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Failed to log violation to MongoDB: {e}")
    else:
        print(f"ℹ️ [Simulated DB Log] Violation: {doc['type']} | Vehicle #{doc['track_id']}")
    return "simulated_id"

def log_traffic_stats(vehicle_counts: dict, congestion_level: str):
    """Save traffic stats every few seconds"""
    doc = {
        "vehicle_counts": vehicle_counts,
        "congestion_level": congestion_level,
        "total": sum(vehicle_counts.values()),
        "timestamp": datetime.now()
    }
    if db_active:
        try:
            traffic_collection.insert_one(doc)
        except Exception as e:
            print(f"❌ Failed to log traffic stats to MongoDB: {e}")
    else:
        print(f"ℹ️ [Simulated DB Log] Traffic Stats - Total: {doc['total']} | Congestion: {congestion_level}")

def get_violations_from_db(limit=20):
    """Fetch recent violations from DB"""
    if db_active:
        try:
            results = violations_collection.find(
                {}, {"_id": 0}
            ).sort("created_at", -1).limit(limit)
            return list(results)
        except Exception:
            return []
    return []

def get_violation_stats():
    """Get count by violation type"""
    if db_active:
        try:
            pipeline = [
                {"$group": {"_id": "$type", "count": {"$sum": 1}}}
            ]
            return list(violations_collection.aggregate(pipeline))
        except Exception:
            return []
    return []