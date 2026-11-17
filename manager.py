
import json
import os

from asteroid import Asteroid
import validation


SIZE_CATEGORIES = ("Small", "Medium", "Large")
FIELD_NAMES = ["asteroid_id", "name", "diameter_m", "speed_kms",
               "miss_distance_km", "approach_date"]


class AsteroidManager:
    def __init__(self, data_file, watchlist_file):
        self.data_file = data_file
        self.watchlist_file = watchlist_file
        self.asteroids = []        
        self.ids = set()           
        self.watchlist = {}        

    def find_by_id(self, asteroid_id):
       
        asteroid_id = str(asteroid_id).strip()
        for asteroid in self.asteroids:
            if asteroid.asteroid_id == asteroid_id:
                return asteroid
        return None

    def add_asteroid(self, asteroid_id, name, diameter, speed, miss_distance, date):
       
        ok, result = validation.validate_asteroid(
            asteroid_id, name, diameter, speed, miss_distance, date, self.ids)
        if not ok:
            return False, result

        new_asteroid = Asteroid.from_dict(result)
        self.asteroids.append(new_asteroid)
        self.ids.add(new_asteroid.asteroid_id)

        saved, message = self.save_data()
        if not saved:
            return True, "Asteroid added in memory, but saving failed.\n" + message
        return True, "Asteroid added and saved."

    def view_all(self):
        
        return list(self.asteroids)

    def search(self, text):
        
        text = str(text).strip().lower()
        if text == "":
            return self.view_all()

        matches = []
        for asteroid in self.asteroids:
            if text in asteroid.name.lower() or text in str(asteroid.asteroid_id).lower():
                matches.append(asteroid)
        return matches

    def update_asteroid(self, asteroid_id, name, diameter, speed, miss_distance, date):
       
        asteroid = self.find_by_id(asteroid_id)
        if asteroid is None:
            return False, "Record not found. Nothing was updated."

        ok, result = validation.validate_asteroid(
            asteroid.asteroid_id, name, diameter, speed, miss_distance, date,
            self.ids, check_duplicate=False)
        if not ok:
            return False, result

        asteroid.name = result["name"]
        asteroid.diameter_m = result["diameter_m"]
        asteroid.speed_kms = result["speed_kms"]
        asteroid.miss_distance_km = result["miss_distance_km"]
        asteroid.approach_date = result["approach_date"]

        if asteroid.asteroid_id in self.watchlist:
            self.watchlist[asteroid.asteroid_id] = asteroid.name

        saved, message = self.save_data()
        if not saved:
            return True, "Asteroid updated in memory, but saving failed.\n" + message
        return True, "Asteroid updated and saved."

    def delete_asteroid(self, asteroid_id):
        asteroid = self.find_by_id(asteroid_id)
        if asteroid is None:
            return False, "Record not found. Nothing was deleted."

        self.asteroids.remove(asteroid)
        self.ids.discard(asteroid.asteroid_id)
        if asteroid.asteroid_id in self.watchlist:
            del self.watchlist[asteroid.asteroid_id]

        saved, message = self.save_data()
        if not saved:
            return True, "Asteroid deleted in memory, but saving failed.\n" + message
        return True, "Asteroid deleted and saved."

    def add_to_watchlist(self, asteroid_id):
        asteroid = self.find_by_id(asteroid_id)
        if asteroid is None:
            return False, "Record not found."

        if asteroid.asteroid_id in self.watchlist:
            return False, asteroid.name + " is already in the watchlist."

        self.watchlist[asteroid.asteroid_id] = asteroid.name
        saved, message = self.save_data()
        if not saved:
            return True, "Added to watchlist in memory, but saving failed.\n" + message
        return True, asteroid.name + " added to the watchlist."

    def remove_from_watchlist(self, asteroid_id):
        asteroid = self.find_by_id(asteroid_id)
        if asteroid is None:
            return False, "Record not found."

        if asteroid.asteroid_id not in self.watchlist:
            return False, asteroid.name + " is not in the watchlist."

        del self.watchlist[asteroid.asteroid_id]
        saved, message = self.save_data()
        if not saved:
            return True, "Removed from watchlist in memory, but saving failed.\n" + message
        return True, asteroid.name + " removed from the watchlist."

    def view_watchlist(self):
       
        watched = []
        for asteroid_id in self.watchlist:
            asteroid = self.find_by_id(asteroid_id)
            if asteroid is not None:
                watched.append(asteroid)
        return watched

    def load_data(self):
        
        self.asteroids = []
        self.ids = set()
        self.watchlist = {}
        messages = []

       
        loaded_a_list = False
        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                records = json.load(file)

            if isinstance(records, list):
                loaded_a_list = True
            else:
                messages.append("asteroids.json must contain a list. "
                                "Starting with an empty list.")
                records = []

        except FileNotFoundError:
            messages.append("asteroids.json was not found. "
                            "Starting with an empty list.")
            records = []
        except ValueError:
            
            messages.append("asteroids.json is empty or broken. "
                            "Starting with an empty list.")
            records = []
        except OSError as error:
            messages.append("asteroids.json could not be read: " + str(error))
            records = []

        skipped = 0
        for record in records:
            
            if not isinstance(record, dict) or not all(
                    field in record for field in FIELD_NAMES):
                skipped += 1
                continue

            ok, result = validation.validate_asteroid(
                record["asteroid_id"], record["name"], record["diameter_m"],
                record["speed_kms"], record["miss_distance_km"],
                record["approach_date"], self.ids)
            if not ok:
                skipped += 1
                continue

            asteroid = Asteroid.from_dict(result)
            self.asteroids.append(asteroid)
            self.ids.add(asteroid.asteroid_id)

        if loaded_a_list and len(records) == 0:
            messages.append("asteroids.json has no records. "
                            "Starting with an empty list.")
        if skipped > 0:
            messages.append(str(skipped) + " bad or duplicate record(s) were skipped.")

       
        try:
            with open(self.watchlist_file, "r", encoding="utf-8") as file:
                saved_ids = json.load(file)

            if not isinstance(saved_ids, list):
                messages.append("watchlist.json must contain a list. "
                                "Starting with an empty watchlist.")
                saved_ids = []
        except FileNotFoundError:
            saved_ids = []   
        except (ValueError, OSError):
            messages.append("watchlist.json is empty or broken. "
                            "Starting with an empty watchlist.")
            saved_ids = []

        missing = 0
        for asteroid_id in saved_ids:
            asteroid = self.find_by_id(asteroid_id)
            if asteroid is None:
                missing += 1
            else:
                self.watchlist[asteroid.asteroid_id] = asteroid.name

        if missing > 0:
            messages.append(str(missing) + " watchlist ID(s) were not found "
                            "and were ignored.")

        return "\n".join(messages)

    def save_data(self):
        # Saves both files. Returns (ok, message).
        try:
            folder = os.path.dirname(self.data_file)
            if folder != "":
                os.makedirs(folder, exist_ok=True)

            records = []
            for asteroid in self.asteroids:
                records.append(asteroid.to_dict())
            with open(self.data_file, "w", encoding="utf-8") as file:
                json.dump(records, file, indent=2)

            watched_ids = list(self.watchlist.keys())
            with open(self.watchlist_file, "w", encoding="utf-8") as file:
                json.dump(watched_ids, file, indent=2)

        except OSError as error:
            return False, "File error: " + str(error)

        return True, "Data saved."
