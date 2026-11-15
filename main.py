# main.py
# Starts the Tkinter program and builds the main window.

import math
import os
import random
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

import analysis
from manager import AsteroidManager

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_FOLDER, "data", "asteroids.json")
WATCHLIST_FILE = os.path.join(BASE_FOLDER, "data", "watchlist.json")

COLORS = {
    "bg": "#060a16",
    "panel": "#0c1424",
    "panel2": "#111d33",
    "space": "#04070f",
    "line": "#1d2c49",
    "text": "#e8effb",
    "muted": "#8194b8",
    "accent": "#5dd6ff",
    "small": "#63e6b0",
    "medium": "#ffc857",
    "large": "#ff6b76",
    "field": "#08101d",
    "selection": "#193a5c",
}

TABLE_COLUMNS = (
    ("id", "ID", 85, "center"),
    ("name", "NAME", 200, "w"),
    ("diameter", "DIAMETER (M)", 100, "e"),
    ("speed", "SPEED (KM/S)", 100, "e"),
    ("miss", "MISS DISTANCE (KM)", 140, "e"),
    ("date", "APPROACH", 110, "center"),
    ("size", "SIZE", 75, "center"),
)


class AstrolyticsApp:
    def __init__(self, root):
        self.root = root
        self.manager = AsteroidManager(DATA_FILE, WATCHLIST_FILE)
        self.load_message = self.manager.load_data()
        self.selected_id = None
        self.table_asteroids = []
        self.map_points = {}
        self.last_map_width = 0
        self.last_map_height = 0

        self.setup_window()
        self.setup_styles()
        self.build_header()
        self.build_body()
        self.build_footer()

        self.refresh_views()
        count = len(self.manager.view_all())
        word = "record" if count == 1 else "records"
        self.set_status("Loaded " + str(count) + " " + word + ".")
        if self.load_message != "":
            self.root.after(250, self.show_load_warning)

    # ---------- window and theme ----------

    def setup_window(self):
        self.root.title("Astrolytics Desktop | Near-Earth Asteroid Records")
        self.root.configure(bg=COLORS["bg"])

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = max(1060, min(1280, screen_width - 80))
        height = max(640, min(840, screen_height - 100))
        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2 - 15)

        self.root.geometry(str(width) + "x" + str(height) + "+" + str(x) + "+" + str(y))
        self.root.minsize(1060, 640)
        self.root.option_add("*Font", ("Segoe UI", 9))

        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

    def setup_styles(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Space.Treeview",
                        background=COLORS["space"],
                        fieldbackground=COLORS["space"],
                        foreground=COLORS["text"],
                        rowheight=27,
                        borderwidth=0,
                        font=("Segoe UI", 9))
        style.configure("Space.Treeview.Heading",
                        background=COLORS["panel2"],
                        foreground=COLORS["muted"],
                        relief="flat",
                        font=("Segoe UI", 8, "bold"),
                        padding=(4, 7))
        style.map("Space.Treeview",
                  background=[("selected", COLORS["selection"])],
                  foreground=[("selected", "#ffffff")])
        style.map("Space.Treeview.Heading",
                  background=[("active", COLORS["line"])])

        for name in ("Space.Vertical.TScrollbar", "Space.Horizontal.TScrollbar"):
            style.configure(name,
                            background=COLORS["panel2"],
                            troughcolor=COLORS["space"],
                            borderwidth=0,
                            arrowcolor=COLORS["muted"])

    def make_button(self, parent, text, command, kind="secondary"):
        if kind == "primary":
            background = COLORS["accent"]
            foreground = "#07111f"
            hover = "#8ee6ff"
        elif kind == "danger":
            background = "#3b1720"
            foreground = "#ff9aa2"
            hover = "#54202b"
        elif kind == "ghost":
            background = COLORS["panel"]
            foreground = COLORS["muted"]
            hover = COLORS["panel2"]
        else:
            background = COLORS["panel2"]
            foreground = COLORS["text"]
            hover = COLORS["line"]

        button = tk.Button(parent, text=text, command=command,
                           bg=background, fg=foreground,
                           activebackground=hover, activeforeground=foreground,
                           relief="flat", bd=0, padx=12, pady=7,
                           cursor="hand2", font=("Segoe UI", 9, "bold"))
        button.bind("<Enter>", lambda event: button.configure(bg=hover))
        button.bind("<Leave>", lambda event: button.configure(bg=background))
        return button

    def make_chip(self, parent, label_text):
        chip = tk.Frame(parent, bg=COLORS["panel"],
                        highlightbackground=COLORS["line"], highlightthickness=1)
        value = tk.StringVar(value="0")
        tk.Label(chip, textvariable=value, bg=COLORS["panel"], fg=COLORS["text"],
                 font=("Segoe UI", 13, "bold")).pack(side="left", padx=(10, 4), pady=3)
        tk.Label(chip, text=label_text, bg=COLORS["panel"], fg=COLORS["muted"],
                 font=("Segoe UI", 7, "bold")).pack(side="left", padx=(0, 10), pady=3)
        return chip, value

    # ---------- main layout ----------

    def build_header(self):
        header = tk.Frame(self.root, bg=COLORS["bg"])
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))

        left = tk.Frame(header, bg=COLORS["bg"])
        left.pack(side="left")

        logo = tk.Canvas(left, width=48, height=48, bg=COLORS["bg"], highlightthickness=0)
        logo.pack(side="left", padx=(0, 10))
        logo.create_oval(14, 14, 34, 34, fill=COLORS["accent"], outline="")
        logo.create_oval(6, 20, 42, 28, outline=COLORS["muted"], width=1)
        logo.create_oval(35, 22, 39, 26, fill=COLORS["medium"], outline="")

        title_box = tk.Frame(left, bg=COLORS["bg"])
        title_box.pack(side="left")
        tk.Label(title_box, text="ASTROLYTICS", bg=COLORS["bg"], fg=COLORS["text"],
                 font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(title_box, text="NEAR-EARTH ASTEROID LABORATORY", bg=COLORS["bg"],
                 fg=COLORS["muted"], font=("Segoe UI", 7, "bold")).pack(anchor="w")

        save_button = self.make_button(header, "SAVE DATA", self.save_clicked, "primary")
        save_button.pack(side="right")

        chips = tk.Frame(header, bg=COLORS["bg"])
        chips.pack(side="right", padx=(0, 14))

        records_chip, self.records_chip_var = self.make_chip(chips, "RECORDS")
        records_chip.pack(side="left", padx=3)
        watchlist_chip, self.watchlist_chip_var = self.make_chip(chips, "WATCHLIST")
        watchlist_chip.pack(side="left", padx=3)
        large_chip, self.large_chip_var = self.make_chip(chips, "LARGE")
        large_chip.pack(side="left", padx=3)

    def build_body(self):
        body = tk.Frame(self.root, bg=COLORS["bg"])
        body.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=0, minsize=350)
        body.grid_rowconfigure(0, weight=1)

        main = tk.Frame(body, bg=COLORS["bg"])
        main.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(0, weight=0)
        main.grid_rowconfigure(1, weight=1)

        self.build_map_panel(main)
        self.build_records_panel(main)

        side = tk.Frame(body, bg=COLORS["bg"])
        side.grid(row=0, column=1, sticky="nsew")
        side.grid_columnconfigure(0, weight=1)

        self.build_form_panel(side)
        self.build_actions_panel(side)

    def make_panel(self, parent):
        return tk.Frame(parent, bg=COLORS["panel"],
                        highlightbackground=COLORS["line"], highlightthickness=1)

    # ---------- orbital map ----------

    def build_map_panel(self, parent):
        panel = self.make_panel(parent)
        panel.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        panel.grid_columnconfigure(0, weight=1)

        head = tk.Frame(panel, bg=COLORS["panel"])
        head.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 6))
        tk.Label(head, text="ORBITAL MAP", bg=COLORS["panel"], fg=COLORS["accent"],
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Label(head, text="angle = date  |  radius = miss distance  |  click a dot",
                 bg=COLORS["panel"], fg=COLORS["muted"],
                 font=("Segoe UI", 7)).pack(side="right")

        self.map_canvas = tk.Canvas(panel, bg=COLORS["space"], height=240,
                                    highlightthickness=0)
        self.map_canvas.grid(row=1, column=0, sticky="ew", padx=12)
        self.map_canvas.bind("<Configure>", self.map_resized)
        self.map_canvas.bind("<Button-1>", self.map_clicked)

        legend = tk.Frame(panel, bg=COLORS["panel"])
        legend.grid(row=2, column=0, sticky="ew", padx=14, pady=(6, 10))
        self.add_legend_item(legend, COLORS["small"], "SMALL")
        self.add_legend_item(legend, COLORS["medium"], "MEDIUM")
        self.add_legend_item(legend, COLORS["large"], "LARGE")
        tk.Label(legend, text="ring = watchlist", bg=COLORS["panel"], fg=COLORS["muted"],
                 font=("Segoe UI", 7)).pack(side="right")

    def add_legend_item(self, parent, color, text):
        swatch = tk.Frame(parent, bg=color, width=8, height=8)
        swatch.pack(side="left", padx=(0, 4))
        swatch.pack_propagate(False)
        tk.Label(parent, text=text, bg=COLORS["panel"], fg=COLORS["muted"],
                 font=("Segoe UI", 7, "bold")).pack(side="left", padx=(0, 14))

    def draw_orbital_map(self):
        canvas = self.map_canvas
        canvas.delete("all")
        self.map_points = {}

        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width < 200 or height < 120:
            return

        # Starfield with fixed random positions.
        rng = random.Random(11)
        for _ in range(90):
            x = rng.randint(0, width)
            y = rng.randint(0, height)
            size = rng.choice((1, 1, 1, 2))
            color = rng.choice(("#24324d", "#3a4a6d", "#6c7fa5", "#dce9ff"))
            canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")

        for x, y in ((width * 0.12, height * 0.22),
                     (width * 0.82, height * 0.18),
                     (width * 0.68, height * 0.78)):
            canvas.create_line(x - 2, y, x + 2, y, fill="#8fa6c9")
            canvas.create_line(x, y - 2, x, y + 2, fill="#8fa6c9")

        center_x = width / 2
        center_y = height * 0.54
        max_rx = min(width * 0.42, 340)
        max_ry = min(max_rx * 0.52, height * 0.37)

        for fraction in (0.36, 0.56, 0.76, 1.0):
            rx = max_rx * fraction
            ry = max_ry * fraction
            canvas.create_oval(center_x - rx, center_y - ry,
                               center_x + rx, center_y + ry,
                               outline="#1e2d4a", width=1)

        planets = ((0.36, 205, 3, "#8ba0c4"),
                   (0.56, 330, 4, "#d6b27a"),
                   (0.76, 70, 5, "#5fb4dc"),
                   (1.0, 145, 4, "#b96b5d"))
        for fraction, angle_degrees, size, color in planets:
            angle = math.radians(angle_degrees)
            px = center_x + max_rx * fraction * math.cos(angle)
            py = center_y + max_ry * fraction * math.sin(angle)
            canvas.create_oval(px - size, py - size, px + size, py + size,
                               fill=color, outline="")

        for angle in range(0, 360, 30):
            radians = math.radians(angle)
            canvas.create_line(center_x + 20 * math.cos(radians),
                               center_y + 20 * math.sin(radians),
                               center_x + 28 * math.cos(radians),
                               center_y + 28 * math.sin(radians),
                               fill="#5b2a0d")

        glow = ((26, "#4a240c"), (21, "#7a3a0c"), (16, "#b55c0d"),
                (12, "#ef8b1f"), (8, "#ffc857"), (5, "#fff3c4"))
        for radius, color in glow:
            canvas.create_oval(center_x - radius, center_y - radius,
                               center_x + radius, center_y + radius,
                               fill=color, outline="")
        canvas.create_text(center_x, center_y + 34, text="SUN", fill="#9a7b57",
                           font=("Segoe UI", 7, "bold"))

        asteroids = self.manager.view_all()
        if len(asteroids) == 0:
            canvas.create_text(center_x, center_y + max_ry + 26,
                               text="No records to plot. Add a record or load data/asteroids.json.",
                               fill=COLORS["muted"], font=("Segoe UI", 9))
        else:
            max_miss = 0
            for asteroid in asteroids:
                if asteroid.miss_distance_km > max_miss:
                    max_miss = asteroid.miss_distance_km

            dot_sizes = {"Small": 3, "Medium": 4, "Large": 6}
            dot_colors = {"Small": COLORS["small"],
                          "Medium": COLORS["medium"],
                          "Large": COLORS["large"]}

            for asteroid in asteroids:
                angle = self.date_angle(asteroid.approach_date)
                fraction = math.sqrt(asteroid.miss_distance_km / max_miss)
                rx = 34 + fraction * (max_rx - 34)
                ry = 24 + fraction * (max_ry - 24)
                x = center_x + rx * math.cos(angle)
                y = center_y + ry * math.sin(angle)

                category = asteroid.size_category()
                dot = dot_sizes[category]
                color = dot_colors[category]

                canvas.create_oval(x - dot, y - dot, x + dot, y + dot,
                                   fill=color, outline="#050a14", width=1)

                if asteroid.asteroid_id in self.manager.watchlist:
                    canvas.create_oval(x - dot - 4, y - dot - 4,
                                       x + dot + 4, y + dot + 4,
                                       outline=COLORS["accent"], width=1)

                if asteroid.asteroid_id == self.selected_id:
                    canvas.create_oval(x - dot - 7, y - dot - 7,
                                       x + dot + 7, y + dot + 7,
                                       outline="#ffffff", width=2)
                    self.draw_map_label(x, y, width, asteroid)

                self.map_points[asteroid.asteroid_id] = (x, y, dot + 6)

        canvas.create_text(width - 10, height - 8, text="Not to scale",
                           anchor="se", fill="#536789", font=("Segoe UI", 7))

    def date_angle(self, date_text):
        date_object = datetime.strptime(date_text, "%Y-%m-%d")
        day_number = date_object.timetuple().tm_yday
        return 2 * math.pi * day_number / 365

    def draw_map_label(self, x, y, width, asteroid):
        name = asteroid.name
        if len(name) > 30:
            name = name[:27] + "..."

        if x > width - 190:
            anchor = "e"
            text_x = x - 10
        else:
            anchor = "w"
            text_x = x + 10

        text_y = y - 10
        if text_y < 14:
            text_y = y + 14

        item = self.map_canvas.create_text(
            text_x, text_y, text=name + " | " + asteroid.size_category(),
            anchor=anchor, fill="#ffffff", font=("Segoe UI", 8, "bold"))
        box = self.map_canvas.bbox(item)
        if box is not None:
            rectangle = self.map_canvas.create_rectangle(
                box[0] - 4, box[1] - 2, box[2] + 4, box[3] + 2,
                fill=COLORS["panel2"], outline=COLORS["line"])
            self.map_canvas.tag_lower(rectangle, item)

    def map_resized(self, event):
        if (abs(event.width - self.last_map_width) < 6
                and abs(event.height - self.last_map_height) < 6):
            return
        self.last_map_width = event.width
        self.last_map_height = event.height
        self.draw_orbital_map()

    def map_clicked(self, event):
        closest_id = None
        closest_distance = 999

        for asteroid_id, point in self.map_points.items():
            x, y, radius = point
            distance = math.hypot(event.x - x, event.y - y)
            if distance <= radius and distance < closest_distance:
                closest_id = asteroid_id
                closest_distance = distance

        if closest_id is None:
            return

        if not self.table.exists(closest_id):
            self.search_entry.delete(0, "end")
            self.show_asteroids(self.manager.view_all())

        self.table.selection_set(closest_id)
        self.table.focus(closest_id)
        self.table.see(closest_id)
        self.load_record_into_form(closest_id)

    # ---------- records table ----------

    def build_records_panel(self, parent):
        panel = self.make_panel(parent)
        panel.grid(row=1, column=0, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        head = tk.Frame(panel, bg=COLORS["panel"])
        head.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 8))

        title_box = tk.Frame(head, bg=COLORS["panel"])
        title_box.pack(side="left")
        tk.Label(title_box, text="ASTEROID RECORDS", bg=COLORS["panel"],
                 fg=COLORS["accent"], font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.table_count_var = tk.StringVar(value="0 records")
        tk.Label(title_box, textvariable=self.table_count_var, bg=COLORS["panel"],
                 fg=COLORS["muted"], font=("Segoe UI", 7)).pack(anchor="w")

        search_box = tk.Frame(head, bg=COLORS["panel"])
        search_box.pack(side="right")
        tk.Label(search_box, text="SEARCH", bg=COLORS["panel"], fg=COLORS["muted"],
                 font=("Segoe UI", 7, "bold")).pack(side="left", padx=(0, 6))
        self.search_entry = tk.Entry(
            search_box, width=22, bg=COLORS["field"], fg=COLORS["text"],
            insertbackground=COLORS["accent"], relief="flat",
            highlightthickness=1, highlightbackground=COLORS["line"],
            highlightcolor=COLORS["accent"], selectbackground=COLORS["selection"],
            font=("Segoe UI", 9))
        self.search_entry.pack(side="left", ipady=4)
        self.search_entry.bind("<Return>", lambda event: self.search_clicked())
        self.make_button(search_box, "SEARCH", self.search_clicked,
                         "secondary").pack(side="left", padx=(6, 0))

        table_frame, self.table = self.create_table(panel, 8)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.table.bind("<<TreeviewSelect>>", self.row_selected)

    def create_table(self, parent, height):
        frame = tk.Frame(parent, bg=COLORS["space"])
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        keys = []
        for column in TABLE_COLUMNS:
            keys.append(column[0])

        tree = ttk.Treeview(frame, columns=keys, show="headings",
                            height=height, selectmode="browse",
                            style="Space.Treeview")
        for key, heading, width, anchor in TABLE_COLUMNS:
            tree.heading(key, text=heading)
            tree.column(key, width=width, minwidth=65, anchor=anchor,
                        stretch=(key == "name"))

        tree.tag_configure("Small", foreground="#9ae6c4")
        tree.tag_configure("Medium", foreground="#efd699")
        tree.tag_configure("Large", foreground="#eba7ad")

        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview,
                                 style="Space.Vertical.TScrollbar")
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview,
                                 style="Space.Horizontal.TScrollbar")
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        return frame, tree

    # ---------- form and actions ----------

    def build_form_panel(self, parent):
        panel = self.make_panel(parent)
        panel.grid(row=0, column=0, sticky="ew")
        panel.grid_columnconfigure(0, weight=1)

        head = tk.Frame(panel, bg=COLORS["panel"])
        head.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 2))
        tk.Label(head, text="RECORD EDITOR", bg=COLORS["panel"], fg=COLORS["accent"],
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Label(head, text="ADD / UPDATE", bg=COLORS["panel"], fg=COLORS["muted"],
                 font=("Segoe UI", 7, "bold")).pack(side="right")

        self.form_hint_var = tk.StringVar(
            value="All fields are required. Select a table row to edit it.")
        tk.Label(panel, textvariable=self.form_hint_var, bg=COLORS["panel"],
                 fg=COLORS["muted"], font=("Segoe UI", 7), justify="left",
                 wraplength=320).grid(row=1, column=0, sticky="w", padx=14)

        form = tk.Frame(panel, bg=COLORS["panel"])
        form.grid(row=2, column=0, sticky="ew", padx=12, pady=(2, 10))
        form.grid_columnconfigure(0, weight=1, uniform="form")
        form.grid_columnconfigure(1, weight=1, uniform="form")

        self.id_entry = self.add_field(form, "ASTEROID ID", 0, 0)
        self.date_entry = self.add_field(form, "APPROACH DATE (YYYY-MM-DD)", 0, 1)
        self.name_entry = self.add_field(form, "NAME", 2, 0, 2)
        self.diameter_entry = self.add_field(form, "DIAMETER (M)", 4, 0)
        self.speed_entry = self.add_field(form, "SPEED (KM/S)", 4, 1)
        self.miss_entry = self.add_field(form, "MISS DISTANCE (KM)", 6, 0, 2)

        buttons = tk.Frame(form, bg=COLORS["panel"])
        buttons.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        for column in range(3):
            buttons.grid_columnconfigure(column, weight=1)

        self.make_button(buttons, "ADD", self.add_clicked, "primary").grid(
            row=0, column=0, sticky="ew", padx=(0, 4))
        self.make_button(buttons, "UPDATE", self.update_clicked, "secondary").grid(
            row=0, column=1, sticky="ew", padx=4)
        self.make_button(buttons, "CLEAR", self.clear_form_clicked, "ghost").grid(
            row=0, column=2, sticky="ew", padx=(4, 0))

    def add_field(self, parent, label_text, row, column=0, columnspan=1):
        tk.Label(parent, text=label_text, bg=COLORS["panel"], fg=COLORS["muted"],
                 font=("Segoe UI", 7, "bold")).grid(
            row=row, column=column, columnspan=columnspan,
            sticky="w", padx=2, pady=(6, 2))

        entry = tk.Entry(parent, bg=COLORS["field"], fg=COLORS["text"],
                         insertbackground=COLORS["accent"], relief="flat",
                         highlightthickness=1, highlightbackground=COLORS["line"],
                         highlightcolor=COLORS["accent"],
                         selectbackground=COLORS["selection"],
                         readonlybackground=COLORS["field"],
                         font=("Segoe UI", 10))
        entry.grid(row=row + 1, column=column, columnspan=columnspan,
                   sticky="ew", padx=2, ipady=5)
        return entry

    def build_actions_panel(self, parent):
        panel = self.make_panel(parent)
        panel.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        panel.grid_columnconfigure(0, weight=1)

        head = tk.Frame(panel, bg=COLORS["panel"])
        head.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 2))
        tk.Label(head, text="ACTIONS", bg=COLORS["panel"], fg=COLORS["accent"],
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Label(head, text="SELECT A ROW", bg=COLORS["panel"], fg=COLORS["muted"],
                 font=("Segoe UI", 7, "bold")).pack(side="right")

        inner = tk.Frame(panel, bg=COLORS["panel"])
        inner.grid(row=1, column=0, sticky="ew", padx=12, pady=(4, 10))
        inner.grid_columnconfigure(0, weight=1)
        inner.grid_columnconfigure(1, weight=1)

        self.make_button(inner, "DELETE", self.delete_clicked, "danger").grid(
            row=0, column=0, sticky="ew", padx=(0, 4), pady=3)
        self.make_button(inner, "ADD TO WATCHLIST", self.add_watchlist_clicked,
                         "secondary").grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=3)
        self.make_button(inner, "VIEW WATCHLIST", self.view_watchlist_clicked,
                         "secondary").grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=3)
        self.make_button(inner, "SHOW SUMMARY", self.summary_clicked,
                         "secondary").grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=3)
        self.make_button(inner, "SHOW UNUSUAL ASTEROIDS", self.unusual_clicked,
                         "secondary").grid(row=2, column=0, columnspan=2,
                                           sticky="ew", pady=3)

    def build_footer(self):
        footer = tk.Frame(self.root, bg=COLORS["bg"])
        footer.grid(row=2, column=0, sticky="ew", padx=16, pady=(2, 8))

        tk.Label(footer,
                 text="EDUCATIONAL TOOL - NOT A HAZARD WARNING SYSTEM. Sample data is for demonstration.",
                 bg=COLORS["bg"], fg=COLORS["muted"],
                 font=("Segoe UI", 7)).pack(side="left")

        status_box = tk.Frame(footer, bg=COLORS["bg"])
        status_box.pack(side="right")
        dot = tk.Frame(status_box, bg=COLORS["accent"], width=6, height=6)
        dot.pack(side="left", padx=(0, 6))
        dot.pack_propagate(False)
        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(status_box, textvariable=self.status_var, bg=COLORS["bg"],
                 fg=COLORS["muted"], font=("Segoe UI", 7)).pack(side="left")

    def set_status(self, message):
        self.status_var.set(message)

    def show_load_warning(self):
        messagebox.showwarning("Data file notice", self.load_message, parent=self.root)

    # ---------- form helpers ----------

    def get_form_values(self):
        return (self.id_entry.get().strip(),
                self.name_entry.get().strip(),
                self.diameter_entry.get().strip(),
                self.speed_entry.get().strip(),
                self.miss_entry.get().strip(),
                self.date_entry.get().strip())

    def clear_entries(self):
        for entry in (self.id_entry, self.name_entry, self.diameter_entry,
                      self.speed_entry, self.miss_entry, self.date_entry):
            entry.configure(state="normal")
            entry.delete(0, "end")

    def load_record_into_form(self, asteroid_id):
        asteroid = self.manager.find_by_id(asteroid_id)
        if asteroid is None:
            return

        self.selected_id = asteroid.asteroid_id
        self.clear_entries()
        self.id_entry.insert(0, asteroid.asteroid_id)
        self.name_entry.insert(0, asteroid.name)
        self.diameter_entry.insert(0, str(asteroid.diameter_m))
        self.speed_entry.insert(0, str(asteroid.speed_kms))
        self.miss_entry.insert(0, str(asteroid.miss_distance_km))
        self.date_entry.insert(0, asteroid.approach_date)
        self.id_entry.configure(state="readonly",
                                readonlybackground=COLORS["field"])
        self.form_hint_var.set("Editing ID " + asteroid.asteroid_id
                               + ". The ID is fixed while editing.")
        self.draw_orbital_map()
        self.set_status("Selected " + asteroid.name + ".")

    def clear_selection(self):
        self.selected_id = None
        self.table.selection_remove(*self.table.selection())
        self.clear_entries()
        self.id_entry.configure(state="normal")
        self.form_hint_var.set("All fields are required. Select a table row to edit it.")
        self.draw_orbital_map()

    def row_selected(self, event):
        selected = self.table.selection()
        if len(selected) == 0:
            return
        self.load_record_into_form(selected[0])

    # ---------- button actions ----------

    def add_clicked(self):
        ok, message = self.manager.add_asteroid(*self.get_form_values())
        if ok:
            messagebox.showinfo("Added", message, parent=self.root)
            self.reset_after_change("Record added and saved.")
        else:
            messagebox.showerror("Cannot add", message, parent=self.root)
            self.set_status("Add failed. Fix the form and try again.")

    def update_clicked(self):
        asteroid_id = self.selected_id
        if asteroid_id is None:
            asteroid_id = self.id_entry.get().strip()

        if asteroid_id == "":
            messagebox.showerror("Cannot update",
                                 "Select a table row or type an Asteroid ID first.",
                                 parent=self.root)
            return

        values = self.get_form_values()
        ok, message = self.manager.update_asteroid(
            asteroid_id, values[1], values[2], values[3], values[4], values[5])
        if ok:
            messagebox.showinfo("Updated", message, parent=self.root)
            self.reset_after_change("Record updated and saved.")
        else:
            messagebox.showerror("Cannot update", message, parent=self.root)
            self.set_status("Update failed. Fix the form and try again.")

    def delete_clicked(self):
        if self.selected_id is None:
            messagebox.showwarning("Delete", "Select a table row first.",
                                   parent=self.root)
            return

        asteroid = self.manager.find_by_id(self.selected_id)
        if asteroid is None:
            messagebox.showerror("Delete", "Record not found.", parent=self.root)
            return

        answer = messagebox.askyesno(
            "Confirm delete",
            "Delete " + asteroid.name + " (ID " + asteroid.asteroid_id + ")?\n"
            "This cannot be undone.",
            parent=self.root)
        if not answer:
            return

        ok, message = self.manager.delete_asteroid(asteroid.asteroid_id)
        if ok:
            messagebox.showinfo("Deleted", message, parent=self.root)
            self.reset_after_change("Record deleted and saved.")
        else:
            messagebox.showerror("Delete failed", message, parent=self.root)

    def search_clicked(self):
        text = self.search_entry.get().strip()
        matches = self.manager.search(text)
        self.show_asteroids(matches)

        if self.selected_id is not None and not self.table.exists(self.selected_id):
            self.clear_selection()

        if text == "":
            self.set_status("Showing all records.")
        elif len(matches) == 0:
            messagebox.showinfo("Search", "No asteroid matched \"" + text + "\".",
                                parent=self.root)
            self.set_status("No matching records.")
        else:
            word = "record" if len(matches) == 1 else "records"
            self.set_status("Found " + str(len(matches)) + " matching " + word + ".")

    def save_clicked(self):
        ok, message = self.manager.save_data()
        if ok:
            messagebox.showinfo("Saved", "All records and the watchlist were saved.",
                                parent=self.root)
            self.set_status("Data saved to the data folder.")
        else:
            messagebox.showerror("Save failed", message, parent=self.root)

    def add_watchlist_clicked(self):
        if self.selected_id is None:
            messagebox.showwarning("Watchlist", "Select a table row first.",
                                   parent=self.root)
            return

        ok, message = self.manager.add_to_watchlist(self.selected_id)
        if ok:
            messagebox.showinfo("Watchlist", message, parent=self.root)
            self.update_chips()
            self.draw_orbital_map()
            self.set_status("Watchlist updated.")
        else:
            messagebox.showwarning("Watchlist", message, parent=self.root)

    # ---------- extra windows ----------

    def view_watchlist_clicked(self):
        window = tk.Toplevel(self.root)
        window.title("Watchlist | Astrolytics")
        window.configure(bg=COLORS["bg"])
        window.transient(self.root)
        window.minsize(760, 380)
        self.center_window(window, 940, 480)

        head = tk.Frame(window, bg=COLORS["bg"])
        head.pack(fill="x", padx=16, pady=(14, 6))
        tk.Label(head, text="WATCHLIST", bg=COLORS["bg"], fg=COLORS["accent"],
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        count_var = tk.StringVar(value="0 watched")
        tk.Label(head, textvariable=count_var, bg=COLORS["bg"], fg=COLORS["muted"],
                 font=("Segoe UI", 8)).pack(side="left", padx=12)

        empty_var = tk.StringVar(value="")
        tk.Label(window, textvariable=empty_var, bg=COLORS["bg"], fg=COLORS["muted"],
                 font=("Segoe UI", 9)).pack(fill="x", padx=18, pady=(0, 4))

        table_frame, table = self.create_table(window, 10)
        table_frame.pack(fill="both", expand=True, padx=16, pady=6)

        def refresh_list():
            watched = self.manager.view_watchlist()
            self.fill_table(table, watched)
            count_var.set(str(len(watched)) + " watched")
            if len(watched) == 0:
                empty_var.set("The watchlist is empty. Select a record and use Add to Watchlist.")
            else:
                empty_var.set("Removing here updates the saved watchlist immediately.")

        def remove_selected():
            selected = table.selection()
            if len(selected) == 0:
                messagebox.showwarning("Watchlist", "Select a watched asteroid first.",
                                       parent=window)
                return
            ok, message = self.manager.remove_from_watchlist(selected[0])
            if ok:
                messagebox.showinfo("Watchlist", message, parent=window)
                refresh_list()
                self.update_chips()
                self.draw_orbital_map()
                self.set_status("Removed from watchlist.")
            else:
                messagebox.showwarning("Watchlist", message, parent=window)

        buttons = tk.Frame(window, bg=COLORS["bg"])
        buttons.pack(fill="x", padx=16, pady=(0, 14))
        self.make_button(buttons, "REMOVE SELECTED", remove_selected, "danger").pack(side="left")
        self.make_button(buttons, "CLOSE", window.destroy, "secondary").pack(side="right")

        refresh_list()

    def summary_clicked(self):
        asteroids = self.manager.view_all()
        if len(asteroids) == 0:
            messagebox.showinfo("Summary", "There are no records to summarise.",
                                parent=self.root)
            return

        stats = analysis.get_all_statistics(asteroids)
        counts = analysis.count_by_size(asteroids)

        window = tk.Toplevel(self.root)
        window.title("Summary | Astrolytics")
        window.configure(bg=COLORS["bg"])
        window.transient(self.root)
        window.minsize(760, 480)
        self.center_window(window, 840, 520)

        head = tk.Frame(window, bg=COLORS["bg"])
        head.pack(fill="x", padx=18, pady=(14, 2))
        tk.Label(head, text="MISSION SUMMARY", bg=COLORS["bg"], fg=COLORS["accent"],
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(head, text=str(len(asteroids)) + " records analysed",
                 bg=COLORS["bg"], fg=COLORS["muted"],
                 font=("Segoe UI", 8)).pack(side="right")

        tk.Label(window, text="NumPy statistics for the current data set",
                 bg=COLORS["bg"], fg=COLORS["muted"],
                 font=("Segoe UI", 8)).pack(fill="x", padx=20, pady=(0, 6))

        columns = ("measure", "average", "minimum", "maximum", "median", "std")
        table = ttk.Treeview(window, columns=columns, show="headings",
                             height=3, style="Space.Treeview")
        headings = ("MEASURE", "AVERAGE", "MINIMUM", "MAXIMUM", "MEDIAN", "STD. DEV.")
        widths = (170, 110, 110, 110, 110, 110)
        for column, heading, width in zip(columns, headings, widths):
            table.heading(column, text=heading)
            table.column(column, width=width, anchor="center")

        for measure in stats:
            values = stats[measure]
            table.insert("", "end", values=(
                measure,
                self.format_stat(values["average"], measure),
                self.format_stat(values["minimum"], measure),
                self.format_stat(values["maximum"], measure),
                self.format_stat(values["median"], measure),
                self.format_stat(values["std_dev"], measure)))
        table.pack(fill="x", padx=18, pady=(0, 12))

        tk.Label(window, text="SIZE CATEGORY COUNTS", bg=COLORS["bg"],
                 fg=COLORS["accent"], font=("Segoe UI", 9, "bold")).pack(
            anchor="w", padx=18, pady=(2, 6))

        tiles = tk.Frame(window, bg=COLORS["bg"])
        tiles.pack(fill="x", padx=14, pady=(0, 10))
        tile_data = (("Small", "UNDER 50 M", COLORS["small"]),
                     ("Medium", "50 - 300 M", COLORS["medium"]),
                     ("Large", "OVER 300 M", COLORS["large"]))
        for index, (category, range_text, color) in enumerate(tile_data):
            tile = tk.Frame(tiles, bg=COLORS["panel"],
                            highlightbackground=color, highlightthickness=1)
            tile.grid(row=0, column=index, sticky="nsew", padx=5)
            tiles.grid_columnconfigure(index, weight=1)
            tk.Label(tile, text=str(counts[category]), bg=COLORS["panel"], fg=color,
                     font=("Segoe UI", 24, "bold")).pack(pady=(8, 0))
            tk.Label(tile, text=category.upper(), bg=COLORS["panel"], fg=COLORS["text"],
                     font=("Segoe UI", 8, "bold")).pack()
            tk.Label(tile, text=range_text, bg=COLORS["panel"], fg=COLORS["muted"],
                     font=("Segoe UI", 7)).pack(pady=(0, 8))

        tk.Label(window,
                 text="Standard deviation is the population value returned by NumPy (np.std).",
                 bg=COLORS["bg"], fg=COLORS["muted"],
                 font=("Segoe UI", 7)).pack(fill="x", padx=20, pady=(2, 8))

        self.make_button(window, "CLOSE", window.destroy, "secondary").pack(
            side="right", padx=18, pady=(0, 14))

    def unusual_clicked(self):
        asteroids = self.manager.view_all()
        if len(asteroids) == 0:
            messagebox.showinfo("Unusual asteroids", "There are no records to check.",
                                parent=self.root)
            return

        unusual = analysis.find_unusual(asteroids)
        if len(unusual) == 0:
            messagebox.showinfo("Unusual asteroids",
                                "No unusual asteroids were found in this data set.",
                                parent=self.root)
            return

        window = tk.Toplevel(self.root)
        window.title("Unusual Asteroids | Astrolytics")
        window.configure(bg=COLORS["bg"])
        window.transient(self.root)
        window.minsize(760, 420)
        self.center_window(window, 840, 540)

        head = tk.Frame(window, bg=COLORS["bg"])
        head.pack(fill="x", padx=18, pady=(14, 2))
        tk.Label(head, text="UNUSUAL ASTEROIDS", bg=COLORS["bg"], fg=COLORS["accent"],
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(head, text=str(len(unusual)) + " flagged", bg=COLORS["bg"],
                 fg=COLORS["muted"], font=("Segoe UI", 8)).pack(side="right")

        tk.Label(window,
                 text="Rule: speed or diameter is 1.5 standard deviations above average, "
                      "or miss distance is below 5% of the average.",
                 bg=COLORS["bg"], fg=COLORS["muted"], justify="left",
                 wraplength=780, font=("Segoe UI", 8)).pack(fill="x", padx=20, pady=(0, 6))

        text_frame = tk.Frame(window, bg=COLORS["bg"])
        text_frame.pack(fill="both", expand=True, padx=18, pady=4)

        text_box = tk.Text(text_frame, bg=COLORS["space"], fg=COLORS["text"],
                           insertbackground=COLORS["accent"], relief="flat",
                           wrap="word", padx=12, pady=10,
                           selectbackground=COLORS["selection"],
                           font=("Segoe UI", 9))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical",
                                  command=text_box.yview,
                                  style="Space.Vertical.TScrollbar")
        text_box.configure(yscrollcommand=scrollbar.set)
        text_box.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        text_box.tag_configure("name", foreground=COLORS["medium"],
                               font=("Segoe UI", 10, "bold"))
        text_box.tag_configure("reason", foreground=COLORS["muted"],
                               font=("Segoe UI", 9))

        for asteroid, reasons in unusual:
            text_box.insert("end", asteroid.name + "  (ID " + asteroid.asteroid_id + ")\n",
                            "name")
            for reason in reasons:
                text_box.insert("end", "   - " + reason + "\n", "reason")
            text_box.insert("end", "\n")
        text_box.configure(state="disabled")

        self.make_button(window, "CLOSE", window.destroy, "secondary").pack(
            side="right", padx=18, pady=(6, 14))

    # ---------- view refresh ----------

    def fill_table(self, table, asteroids):
        for item in table.get_children():
            table.delete(item)

        for asteroid in asteroids:
            table.insert("", "end", iid=asteroid.asteroid_id, values=(
                asteroid.asteroid_id,
                asteroid.name,
                format(asteroid.diameter_m, ",.0f"),
                format(asteroid.speed_kms, ",.2f"),
                format(asteroid.miss_distance_km, ",.0f"),
                asteroid.approach_date,
                asteroid.size_category()
            ), tags=(asteroid.size_category(),))

    def show_asteroids(self, asteroids):
        self.fill_table(self.table, asteroids)
        self.table_asteroids = list(asteroids)
        word = "record" if len(asteroids) == 1 else "records"
        self.table_count_var.set(str(len(asteroids)) + " " + word + " shown")

    def update_chips(self):
        asteroids = self.manager.view_all()
        self.records_chip_var.set(str(len(asteroids)))
        self.watchlist_chip_var.set(str(len(self.manager.view_watchlist())))
        counts = analysis.count_by_size(asteroids)
        self.large_chip_var.set(str(counts["Large"]))

    def refresh_views(self):
        self.update_chips()
        self.draw_orbital_map()
        self.show_asteroids(self.manager.view_all())

    def reset_after_change(self, status_text):
        self.selected_id = None
        self.clear_entries()
        self.id_entry.configure(state="normal")
        self.search_entry.delete(0, "end")
        self.form_hint_var.set("All fields are required. Select a table row to edit it.")
        self.refresh_views()
        self.set_status(status_text)

    def clear_form_clicked(self):
        self.clear_selection()
        self.set_status("Form cleared.")

    def center_window(self, window, width, height):
        self.root.update_idletasks()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        width = min(width, screen_width - 80)
        height = min(height, screen_height - 100)
        x = self.root.winfo_rootx() + max(0, (self.root.winfo_width() - width) // 2)
        y = self.root.winfo_rooty() + max(0, (self.root.winfo_height() - height) // 2)
        window.geometry(str(width) + "x" + str(height) + "+" + str(x) + "+" + str(y))

    def format_stat(self, value, measure):
        if "Miss" in measure:
            return format(value, ",.0f")
        return format(value, ",.2f")


def main():
    root = tk.Tk()
    AstrolyticsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
