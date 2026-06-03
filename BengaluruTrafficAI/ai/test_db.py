from db_logger import log_violation, get_violations_from_db, get_violation_stats

# Test logging a violation
test_violation = {
    "type": "Red Light Jump",
    "track_id": 1,
    "timestamp": "2026-06-03 10:00:00",
    "position": {"x1": 100, "y1": 200, "x2": 300, "y2": 400}
}

log_violation(test_violation, "test_snapshot.jpg")
log_violation({"type": "Speeding", "track_id": 2, "timestamp": "2026-06-03 10:01:00"})
log_violation({"type": "Wrong Side", "track_id": 3, "timestamp": "2026-06-03 10:02:00"})

print("\nAll violations from DB:")
for v in get_violations_from_db():
    print(f"  - {v['type']} | Track #{v['track_id']} | {v['timestamp']}")

print("\nViolation stats:")
for s in get_violation_stats():
    print(f"  - {s['_id']}: {s['count']} times")