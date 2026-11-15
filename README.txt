ASTROLYTICS DESKTOP
Near-Earth Asteroid Records - CSC 4162 Programming in Python (Midterm Project)
=============================================================================

WHAT IT IS
Astrolytics Desktop is a small desktop app for students and teachers.
You can keep asteroid records, search them, follow a watchlist, and see
simple summaries, size counts and unusual asteroids on a solar system map.

IMPORTANT: This is an EDUCATIONAL tool. It is NOT a hazard warning system.
Do not use it to judge if an asteroid is dangerous.

The map in the window is a simple picture, not a real orbit simulation.
The angle of each dot comes from the approach date and the distance from
the sun comes from the miss distance. It is not to scale.


HOW TO RUN
1. Install Python 3 (3.8 or newer).
2. Install NumPy (the only extra library):
       pip install numpy
   Tkinter comes with Python on Windows and macOS.
   On Linux, if Tkinter is missing:  sudo apt install python3-tk
3. Open a terminal in this folder and run:
       python main.py
   (On some computers use:  python3 main.py)

Keep the "data" folder next to main.py. The program finds its data files there.


FILES
main.py          Starts the program and builds the Tkinter window
asteroid.py      Asteroid class (one record)
manager.py       AsteroidManager class (add, search, update, delete,
                 watchlist, load and save)
analysis.py      NumPy statistics, unusual asteroids, size counts
validation.py    Checks what the user types
data/asteroids.json   The saved asteroid records
data/watchlist.json   The saved watchlist (a list of asteroid IDs)
README.txt       This file

Libraries used: Tkinter, NumPy, and the standard library (json, datetime,
math, os). No other library is used.


HOW TO USE
- Add:     Fill the form on the right and click Add. A wrong value shows
           a message and you can fix it and try again.
- Update:  Click a row (it fills the form and locks the Asteroid ID),
           change the values, click Update. The ID cannot be changed.
- Clear:   Empties the form and unlocks the ID field.
- Delete:  Click a row, click Delete, then confirm with Yes.
- Search:  Type part of a name or ID and click Search.
           Click Search with an empty box to show all records again.
- Add to Watchlist: Click a row, then click this button.
- View Watchlist:   Opens a window with the watched asteroids.
           You can remove one from there.
- Show Summary:     Average, minimum, maximum, median and standard
           deviation for diameter, speed and miss distance, plus the
           number of asteroids in each size category.
- Show Unusual Asteroids: Lists asteroids that look different from the rest,
           with the reason in plain words.
- Save:    Saves everything. The program also saves automatically after
           every add, update, delete and watchlist change.

You can also click a dot on the map to select that asteroid in the table.
A dot gets a ring when the asteroid is on your watchlist.

Size categories:  Small = under 50 m, Medium = 50 to 300 m, Large = over 300 m

Unusual asteroid rules:
  - speed is more than 1.5 standard deviations above the average, OR
  - diameter is more than 1.5 standard deviations above the average, OR
  - miss distance is below 0.05 of the average (5 percent of the average)
Standard deviation here is the population standard deviation (np.std).


SAMPLE DATA - PLEASE READ
The 14 records in data/asteroids.json are SAMPLE RECORDS FOR DEMONSTRATION.
They are based on well-known near-Earth asteroids, but the numbers are
rounded or approximate, and some IDs are only example labels.
They are NOT official NASA data. Do not use them for real science.


HOW TO REPLACE THE SAMPLE DATA WITH REAL NASA DATA (by hand)
You download the data yourself. The program does not connect to the internet.

Option A - NASA NeoWs (Near Earth Object Web Service)
  1. Get a free key at https://api.nasa.gov (the key "DEMO_KEY" works for
     small tests).
  2. Open this address in your browser (change the dates, max 7 days):
     https://api.nasa.gov/neo/rest/v1/feed?start_date=2026-10-01&end_date=2026-10-07&api_key=DEMO_KEY
  3. In the result, each asteroid has these values. Copy them like this:
       asteroid_id       <- neo_reference_id
       name              <- name
       diameter_m        <- estimated_diameter -> meters (use the average of
                            estimated_diameter_min and estimated_diameter_max)
       speed_kms         <- close_approach_data -> relative_velocity ->
                            kilometers_per_second
       miss_distance_km  <- close_approach_data -> miss_distance -> kilometers
       approach_date     <- close_approach_data -> close_approach_date

Option B - JPL Close-Approach Data table (SBDB)
  1. Open https://ssd.jpl.nasa.gov/tools/sbdb_cad.html and download or copy
     the table.
  2. The table gives the date, the distance in AU and the speed in km/s.
       miss_distance_km = distance in AU x 149597870.7
  3. The table does not give the diameter. Get it from NeoWs, or from the
     asteroid's own page on the JPL Small-Body Database.
  (Column names can change, so check the headings of your download.)

How to write the data into the program:
  1. Make a COPY of data/asteroids.json first (a backup).
  2. Open data/asteroids.json in a text editor. Keep the same format:

       [
         {
           "asteroid_id": "2099942",
           "name": "99942 Apophis",
           "diameter_m": 340.0,
           "speed_kms": 7.42,
           "miss_distance_km": 38000.0,
           "approach_date": "2029-04-13"
         }
       ]

  3. Rules: the ID and the name are text in quotes. The three numbers have
     NO quotes and must be greater than 0. The date is "YYYY-MM-DD".
     Every ID must be different.
  4. Save the file and run python main.py.
  5. If a record is wrong, the program shows a message and skips that record.
     If the whole file is broken, it starts with an empty list.
     (The next save will then replace the broken file, so keep your backup.)

The watchlist file only holds a list of IDs, for example:
       ["2099942", "2000433"]
If an ID in the watchlist is not found, the program ignores it.


DATA FILES AND ERRORS
- Records are saved in data/asteroids.json and stay after the program closes.
- If asteroids.json is missing, empty or broken, the program shows a message
  and starts with an empty list. It will not crash.
- If watchlist.json is missing, the watchlist starts empty. If it is broken,
  the program shows a message and starts with an empty watchlist.
- If the data folder is missing, it is created at the first save.

TROUBLESHOOTING
- "No module named numpy"      -> run:  pip install numpy
- "No module named tkinter"    -> on Linux run:  sudo apt install python3-tk
- The table is empty           -> check data/asteroids.json, or add a record.
- Wrong records are skipped    -> read the message at startup, fix the record
                                  in asteroids.json, then run again.
