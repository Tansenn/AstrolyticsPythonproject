# analysis.py
# NumPy is used here only for the statistics.

import numpy as np

from manager import SIZE_CATEGORIES


def calculate_stats(values):
    # Turn a normal Python list into a NumPy array, then calculate five numbers.
    data = np.array(values, dtype=float)
    return {
        "average": float(np.mean(data)),
        "minimum": float(np.min(data)),
        "maximum": float(np.max(data)),
        "median": float(np.median(data)),
        "std_dev": float(np.std(data)),   # population standard deviation
    }


def get_all_statistics(asteroids):
    # Returns statistics for diameter, speed and miss distance.
    if len(asteroids) == 0:
        return {}

    diameters = []
    speeds = []
    miss_distances = []
    for asteroid in asteroids:
        diameters.append(asteroid.diameter_m)
        speeds.append(asteroid.speed_kms)
        miss_distances.append(asteroid.miss_distance_km)

    return {
        "Diameter (m)": calculate_stats(diameters),
        "Speed (km/s)": calculate_stats(speeds),
        "Miss distance (km)": calculate_stats(miss_distances),
    }


def find_unusual(asteroids):
    # Returns a list of (asteroid, list_of_reasons).
    # The three rules are checked with plain if statements.
    if len(asteroids) == 0:
        return []

    stats = get_all_statistics(asteroids)
    diameter_stats = stats["Diameter (m)"]
    speed_stats = stats["Speed (km/s)"]
    miss_stats = stats["Miss distance (km)"]

    diameter_limit = diameter_stats["average"] + 1.5 * diameter_stats["std_dev"]
    speed_limit = speed_stats["average"] + 1.5 * speed_stats["std_dev"]
    miss_limit = 0.05 * miss_stats["average"]

    unusual = []
    for asteroid in asteroids:
        reasons = []

        if asteroid.speed_kms > speed_limit:
            reasons.append(
                "Speed is " + format(asteroid.speed_kms, ".2f") + " km/s, "
                "more than 1.5 standard deviations above the average of "
                + format(speed_stats["average"], ".2f") + " km/s.")

        if asteroid.diameter_m > diameter_limit:
            reasons.append(
                "Diameter is " + format(asteroid.diameter_m, ".1f") + " m, "
                "more than 1.5 standard deviations above the average of "
                + format(diameter_stats["average"], ".1f") + " m.")

        if asteroid.miss_distance_km < miss_limit:
            reasons.append(
                "Miss distance is " + format(asteroid.miss_distance_km, ",.0f")
                + " km, below 5% of the average miss distance ("
                + format(miss_limit, ",.0f") + " km).")

        if len(reasons) > 0:
            unusual.append((asteroid, reasons))

    return unusual


def count_by_size(asteroids):
    # Returns a dictionary like {"Small": 3, "Medium": 5, "Large": 4}.
    counts = {}
    for category in SIZE_CATEGORIES:
        counts[category] = 0

    for asteroid in asteroids:
        counts[asteroid.size_category()] += 1
    return counts
