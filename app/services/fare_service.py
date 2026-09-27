FARE_BASE = 100
FARE_PER_KM = 50

TEST_MODE = True

DISTANCES = {
    ("Town", "Westlands"): 8.0,
    ("Westlands", "Town"): 8.0,
    ("Town", "Kilimani"): 5.0,
    ("Kilimani", "Town"): 5.0,
    ("Westlands", "Kilimani"): 6.0,
    ("Kilimani", "Westlands"): 6.0,
}
from math import radians, sin, cos, sqrt, atan2

def calculate_distance(
        pickup_latitude,
        pickup_longitude,
        destination_latitude,
        destination_longitude
):
    
    R = 6371

    lat1 = radians(pickup_latitude)
    lat2 = radians(destination_latitude)

    delta_lat = radians(
        destination_latitude - pickup_latitude
    )

    delta_lon = radians(
        destination_longitude - pickup_longitude
    )

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance_km = R * c

    return round(distance_km, 2)

def calculate_fare(
        pickup_latitude,
        pickup_longitude,
        destination_latitude,
        destination_longitude
):
    
    distance_km = calculate_distance(
        pickup_latitude,
        pickup_longitude,
        destination_latitude,
        destination_longitude
    )
    
    if TEST_MODE:
        fare = 1
    else:
      fare = FARE_BASE + (
        distance_km * FARE_PER_KM
    )

    return {
        "distance_km": distance_km,
        "fare": fare
    }