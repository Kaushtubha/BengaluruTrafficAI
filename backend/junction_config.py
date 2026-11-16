"""
junction_config.py
------------------
Centralized configuration, validation, and geodesic distance calculations
for junction monitoring and commuter telemetry.
"""

import math
import os

DEFAULT_JUNCTION_NAME = "Silk Board, Bengaluru"
DEFAULT_JUNCTION_LAT = 12.9176
DEFAULT_JUNCTION_LON = 77.6238
MAX_COORD_PARAM_LENGTH = 32


def get_junction_config() -> dict:
    """
    Extract and validate configured junction reference coordinates from environment.
    Falls back gracefully to Silk Board defaults if not explicitly configured.

    Returns:
        dict: {
            "name": str,
            "latitude": float or None,
            "longitude": float or None,
            "is_configurable": True,
            "configuration_error": str or None
        }
    """
    junction_name = os.environ.get("JUNCTION_NAME", DEFAULT_JUNCTION_NAME).strip() or DEFAULT_JUNCTION_NAME
    lat_env = os.environ.get("JUNCTION_LAT")
    lon_env = os.environ.get("JUNCTION_LON")

    if lat_env is None and lon_env is None:
        return {
            "name": junction_name,
            "latitude": DEFAULT_JUNCTION_LAT,
            "longitude": DEFAULT_JUNCTION_LON,
            "is_configurable": True,
            "configuration_error": None,
        }

    lat_str = str(lat_env).strip() if lat_env is not None else ""
    lon_str = str(lon_env).strip() if lon_env is not None else ""

    if len(lat_str) > MAX_COORD_PARAM_LENGTH or len(lon_str) > MAX_COORD_PARAM_LENGTH:
        return {
            "name": junction_name,
            "latitude": None,
            "longitude": None,
            "is_configurable": True,
            "configuration_error": "Configured junction coordinates exceed maximum allowed length of 32 characters",
        }

    try:
        j_lat = float(lat_str)
        j_lon = float(lon_str)
    except (ValueError, TypeError):
        return {
            "name": junction_name,
            "latitude": None,
            "longitude": None,
            "is_configurable": True,
            "configuration_error": "Configured junction coordinates have invalid numeric format",
        }

    if math.isnan(j_lat) or math.isnan(j_lon) or math.isinf(j_lat) or math.isinf(j_lon):
        return {
            "name": junction_name,
            "latitude": None,
            "longitude": None,
            "is_configurable": True,
            "configuration_error": "Configured junction coordinates have invalid numeric format",
        }

    if not (-90.0 <= j_lat <= 90.0 and -180.0 <= j_lon <= 180.0):
        return {
            "name": junction_name,
            "latitude": None,
            "longitude": None,
            "is_configurable": True,
            "configuration_error": f"Configured junction coordinates out of range (-90..90, -180..180): lat={j_lat}, lon={j_lon}",
        }

    return {
        "name": junction_name,
        "latitude": j_lat,
        "longitude": j_lon,
        "is_configurable": True,
        "configuration_error": None,
    }


def calculate_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two geographic points
    using the Haversine spherical formula.

    Returns:
        float: Distance in kilometers rounded to 2 decimal places.
    """
    earth_radius_km = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    return round(earth_radius_km * c, 2)


def validate_coordinates(lat_param, lon_param, junction_lat, junction_lon) -> tuple:
    """
    Validate commuter-supplied GPS query parameters and calculate aerial distance.

    Returns:
        tuple: (distance_km, status_string)
    """
    if lat_param is not None and lon_param is None:
        return None, "INCOMPLETE_COORDINATES_MISSING_LON"
    if lat_param is None and lon_param is not None:
        return None, "INCOMPLETE_COORDINATES_MISSING_LAT"
    if lat_param is None and lon_param is None:
        return None, "COORDINATES_NOT_PROVIDED"

    lat_str = str(lat_param).strip()
    lon_str = str(lon_param).strip()

    if len(lat_str) > MAX_COORD_PARAM_LENGTH or len(lon_str) > MAX_COORD_PARAM_LENGTH:
        return None, "INVALID_COORDINATE_FORMAT"

    try:
        driver_lat = float(lat_str)
        driver_lon = float(lon_str)
    except (ValueError, TypeError):
        return None, "INVALID_COORDINATE_FORMAT"

    if (
        math.isnan(driver_lat)
        or math.isnan(driver_lon)
        or math.isinf(driver_lat)
        or math.isinf(driver_lon)
    ):
        return None, "INVALID_COORDINATE_FORMAT"

    if not (-90.0 <= driver_lat <= 90.0 and -180.0 <= driver_lon <= 180.0):
        return None, "COORDINATES_OUT_OF_RANGE"

    if junction_lat is None or junction_lon is None:
        return None, "JUNCTION_COORDINATES_CONFIG_ERROR"

    distance = calculate_haversine(driver_lat, driver_lon, junction_lat, junction_lon)
    return distance, "CALCULATED"
