# validation.py
# Functions that check user input before it goes into a record.
# Each function returns (True, clean_value) or (False, error_message).

import math
from datetime import datetime


def check_text(value, field_name):
    # ID and name must not be empty.
    if value is None:
        return False, field_name + " cannot be empty."

    text = str(value).strip()
    if text == "":
        return False, field_name + " cannot be empty."
    return True, text


def check_positive_number(value, field_name):
    # Convert the text to a number and reject zero, negatives, nan and inf.
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False, field_name + " must be a number (example: 340.5)."

    if not math.isfinite(number) or number <= 0:
        return False, field_name + " must be a normal number greater than 0."
    return True, number


def check_duplicate_id(asteroid_id, existing_ids):
    # existing_ids is the set kept by the manager.
    if asteroid_id in existing_ids:
        return False, "ID " + asteroid_id + " already exists. Use a different ID."
    return True, asteroid_id


def check_date(value):
    # The date must be a real calendar date written exactly as YYYY-MM-DD.
    text = str(value).strip()
    try:
        date_object = datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        return False, "Date must be a real date in YYYY-MM-DD format (example: 2029-04-13)."

    # strptime accepts 2029-4-13, so compare the text with the standard format.
    if date_object.strftime("%Y-%m-%d") != text:
        return False, "Date must be in YYYY-MM-DD format (example: 2029-04-13)."
    return True, text


def validate_asteroid(asteroid_id, name, diameter, speed, miss_distance,
                      date, existing_ids, check_duplicate=True):
    # Check every field in order and stop at the first problem.
    # When all fields are fine, return a dictionary of clean values.
    ok, asteroid_id = check_text(asteroid_id, "Asteroid ID")
    if not ok:
        return False, asteroid_id

    if check_duplicate:
        ok, message = check_duplicate_id(asteroid_id, existing_ids)
        if not ok:
            return False, message

    ok, name = check_text(name, "Name")
    if not ok:
        return False, name

    ok, diameter = check_positive_number(diameter, "Diameter")
    if not ok:
        return False, diameter

    ok, speed = check_positive_number(speed, "Speed")
    if not ok:
        return False, speed

    ok, miss_distance = check_positive_number(miss_distance, "Miss distance")
    if not ok:
        return False, miss_distance

    ok, date = check_date(date)
    if not ok:
        return False, date

    clean_values = {
        "asteroid_id": asteroid_id,
        "name": name,
        "diameter_m": diameter,
        "speed_kms": speed,
        "miss_distance_km": miss_distance,
        "approach_date": date,
    }
    return True, clean_values
