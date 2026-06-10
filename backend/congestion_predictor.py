import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Initialize and train simulated Random Forest Model on load
# Features: [Hour, Total Vehicles, Active Lane Vehicles]
X_train = []
y_train = []

# Generate synthetic representative traffic data
for hour in range(24):
    for total_vehicles in range(0, 120, 5):
        # Active lane usually takes a good portion of traffic
        active_lane_count = int(total_vehicles * 0.4)
        X_train.append([hour, total_vehicles, active_lane_count])
        
        # Labels: 0 = Low, 1 = Medium, 2 = High Congestion
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
print("🌲 Random Forest Traffic Congestion Predictor Model trained and ready.")

def predict_congestion(hour, total_vehicles, active_lane_count):
    """
    Predict congestion level based on live features.
    Returns: "Low" | "Medium" | "High"
    """
    try:
        features = np.array([[hour, total_vehicles, active_lane_count]])
        prediction = model.predict(features)[0]
        levels = {0: "Low", 1: "Medium", 2: "High"}
        return levels[prediction]
    except Exception as e:
        print(f"❌ Congestion prediction failed: {e}")
        return "Medium"
