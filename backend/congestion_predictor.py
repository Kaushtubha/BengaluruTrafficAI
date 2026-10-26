import math
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

# Model Provenance & Transparency Metadata
# Note: This classifier is trained on synthetic rule-generated thresholds.
# It provides an uncalibrated heuristic classification, NOT an empirical sensor-based forecast.
CONGESTION_PROVENANCE = "heuristic_rule_estimate"
IS_SYNTHETIC_MODEL = True

LEVELS = {0: "Low", 1: "Medium", 2: "High"}

# Generate synthetic representative traffic data with dense single-vehicle steps
# to preserve exact boundary transitions:
# < 15: Low (0), 15 - 34: Medium (1), >= 35: High (2)
X_train = []
y_train = []

for hour in range(24):
    for total_vehicles in range(0, 121):
        active_lane_count = int(total_vehicles * 0.4)
        X_train.append([hour, total_vehicles, active_lane_count])
        if total_vehicles < 15:
            y_train.append(0)
        elif total_vehicles < 35:
            y_train.append(1)
        else:
            y_train.append(2)

X_train = np.array(X_train)
y_train = np.array(y_train)

# Fit Random Forest Classifier
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X_train, y_train)

try:
    print("[ML] Congestion Classifier trained on synthetic rule data (Heuristic Estimate).")
except UnicodeEncodeError:
    print("[ML] Congestion Classifier trained on synthetic rule data.")


def _sanitize_inputs(hour, total_vehicles, active_lane_count):
    """
    Validate and sanitize input features for the congestion predictor.
    Returns (cleaned_hour, cleaned_total, cleaned_active) or None if invalid.
    """
    if total_vehicles is None:
        return None

    try:
        tot = float(total_vehicles)
        if math.isnan(tot) or math.isinf(tot) or tot < 0:
            return None
    except (ValueError, TypeError):
        return None

    # Sanitize hour (default to current local hour if None or invalid)
    try:
        if hour is None:
            hr = float(datetime.now().hour)
        else:
            hr = float(hour)
            if math.isnan(hr) or math.isinf(hr):
                hr = float(datetime.now().hour)
            else:
                hr = max(0.0, min(23.0, hr))
    except (ValueError, TypeError):
        hr = float(datetime.now().hour)

    # Sanitize active_lane_count
    try:
        if active_lane_count is None:
            act = float(int(tot * 0.4))
        else:
            act = float(active_lane_count)
            if math.isnan(act) or math.isinf(act) or act < 0:
                act = float(int(tot * 0.4))
            else:
                act = min(act, tot)
    except (ValueError, TypeError):
        act = float(int(tot * 0.4))

    return hr, tot, act


def predict_congestion(hour=None, total_vehicles=None, active_lane_count=None) -> str:
    """
    Predict congestion level based on vehicle count features.

    Returns:
        str: "Low" | "Medium" | "High" | "UNAVAILABLE"
    """
    sanitized = _sanitize_inputs(hour, total_vehicles, active_lane_count)
    if sanitized is None:
        return "UNAVAILABLE"

    hr, tot, act = sanitized
    try:
        features = np.array([[hr, tot, act]])
        prediction = model.predict(features)[0]
        return LEVELS.get(prediction, "Medium")
    except Exception as e:
        print(f"[ML] Heuristic congestion prediction failed: {e}")
        return "UNAVAILABLE"


def get_congestion_details(hour=None, total_vehicles=None, active_lane_count=None) -> dict:
    """
    Return congestion prediction alongside explicit provenance and transparency metadata.
    Avoids fabricating unverified accuracy or model confidence scores.
    """
    level = predict_congestion(hour, total_vehicles, active_lane_count)
    return {
        "congestion_level": level,
        "provenance": CONGESTION_PROVENANCE,
        "is_synthetic_model": IS_SYNTHETIC_MODEL,
        "model_type": "Synthetic Rule-Trained Random Forest",
        "disclaimer": (
            "Congestion classification is derived from heuristic rules trained on synthetic vehicle counts. "
            "It is an uncalibrated algorithmic estimate, not an empirical real-world sensor prediction."
        ),
        "thresholds": {
            "low": "< 15 vehicles",
            "medium": "15 - 34 vehicles",
            "high": ">= 35 vehicles"
        },
        "confidence": None,  # Explicitly None to avoid fabricating model accuracy
    }
