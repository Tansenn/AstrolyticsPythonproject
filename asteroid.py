


class Asteroid:
    def __init__(self, asteroid_id, name, diameter_m, speed_kms,
                 miss_distance_km, approach_date):
        self.asteroid_id = asteroid_id
        self.name = name
        self.diameter_m = diameter_m
        self.speed_kms = speed_kms
        self.miss_distance_km = miss_distance_km
        self.approach_date = approach_date

    def to_dict(self):
        
        return {
            "asteroid_id": self.asteroid_id,
            "name": self.name,
            "diameter_m": self.diameter_m,
            "speed_kms": self.speed_kms,
            "miss_distance_km": self.miss_distance_km,
            "approach_date": self.approach_date,
        }

    @staticmethod
    def from_dict(data):
        
        return Asteroid(
            data["asteroid_id"],
            data["name"],
            data["diameter_m"],
            data["speed_kms"],
            data["miss_distance_km"],
            data["approach_date"],
        )

    def size_category(self):
       
        if self.diameter_m < 50:
            return "Small"
        elif self.diameter_m <= 300:
            return "Medium"
        else:
            return "Large"

    def __str__(self):
        
        return (f"{self.asteroid_id} | {self.name} | {self.diameter_m} m | "
                f"{self.speed_kms} km/s | {self.miss_distance_km} km | "
                f"{self.approach_date} | {self.size_category()}")
