import logging
from typing import Dict, Any

# Configure logger
logger = logging.getLogger(__name__)

# Configurable constants for signal timing
MIN_GREEN = 10   # minimum green light duration in seconds
MAX_GREEN = 60   # maximum green light duration in seconds
BASE_GREEN = 20  # default green light duration when no traffic

class SignalOptimizer:
    """Service to handle adaptive traffic signal optimization logic based on vehicle counts."""
    
    def __init__(self, min_green: int = MIN_GREEN, max_green: int = MAX_GREEN, base_green: int = BASE_GREEN):
        self.min_green = min_green
        self.max_green = max_green
        self.base_green = base_green

    def calculate_green_time(self, vehicle_counts: Dict[str, int]) -> Dict[str, float]:
        """
        Calculates the green light duration for each lane proportionally based on vehicle count.
        
        Args:
            vehicle_counts (Dict[str, int]): Dictionary mapping lane names to vehicle counts.
            
        Returns:
            Dict[str, float]: Dictionary mapping lane names to calculated green light durations.
        """
        if not vehicle_counts:
            logger.warning("Empty vehicle counts received. Returning empty schedule.")
            return {}

        total = sum(vehicle_counts.values())
        green_times = {}

        if total == 0:
            logger.info("No vehicles detected. Allocating base green time to all lanes.")
            for lane in vehicle_counts:
                green_times[lane] = float(self.base_green)
            return green_times

        for lane, count in vehicle_counts.items():
            if count < 0:
                logger.warning(f"Negative vehicle count detected for lane '{lane}'. Defaulting to 0.")
                count = 0
                
            proportion = count / total
            green_time = self.min_green + (proportion * (self.max_green - self.min_green))
            green_times[lane] = round(green_time, 1)

        return green_times

    def get_priority_lane(self, vehicle_counts: Dict[str, int]) -> str:
        """
        Identifies the lane with the highest number of vehicles for priority signaling.
        
        Args:
            vehicle_counts (Dict[str, int]): Dictionary mapping lane names to vehicle counts.
            
        Returns:
            str: Name of the lane with the highest count.
        """
        if not vehicle_counts:
            return ""
        return max(vehicle_counts, key=vehicle_counts.get)

    def get_signal_plan(self, vehicle_counts: Dict[str, int]) -> Dict[str, Any]:
        """
        Generates a complete signal plan including green times, priority lane, and total cycle time.
        
        Args:
            vehicle_counts (Dict[str, int]): Dictionary mapping lane names to vehicle counts.
            
        Returns:
            Dict[str, Any]: The complete signal plan.
        """
        try:
            green_times = self.calculate_green_time(vehicle_counts)
            priority = self.get_priority_lane(vehicle_counts)
            cycle_time = sum(green_times.values())
            
            plan = {
                "green_times": green_times,
                "priority_lane": priority,
                "cycle_time": round(cycle_time, 1)
            }
            logger.debug(f"Generated signal plan: {plan}")
            return plan
        except Exception as e:
            logger.error(f"Error generating signal plan: {str(e)}")
            # Fallback plan ensuring safe default operation
            return {
                "green_times": {lane: float(self.base_green) for lane in vehicle_counts},
                "priority_lane": list(vehicle_counts.keys())[0] if vehicle_counts else "",
                "cycle_time": float(self.base_green * len(vehicle_counts))
            }

# Instantiate a global optimizer for standard functional usage
_optimizer = SignalOptimizer()

def calculate_green_time(vehicle_counts: Dict[str, int]) -> Dict[str, float]:
    """Calculate green time per lane using the default optimizer."""
    return _optimizer.calculate_green_time(vehicle_counts)

def get_priority_lane(vehicle_counts: Dict[str, int]) -> str:
    """Determine the priority lane using the default optimizer."""
    return _optimizer.get_priority_lane(vehicle_counts)

def get_signal_plan(vehicle_counts: Dict[str, int]) -> Dict[str, Any]:
    """Generate the complete signal plan using the default optimizer."""
    return _optimizer.get_signal_plan(vehicle_counts)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    test_counts = {"North": 15, "South": 8, "East": 20, "West": 5}
    test_plan = get_signal_plan(test_counts)
    print("Vehicle Counts:", test_counts)
    print("Green Times:", test_plan["green_times"])
    print("Priority Lane:", test_plan["priority_lane"])
    print("Total Cycle:", test_plan["cycle_time"], "seconds")