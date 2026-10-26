import customtkinter as ctk
import json
import os
import sys
import socket
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from datetime import date, datetime, time, timedelta
from datetime import date, datetime, time, timedelta
from tkinter import messagebox
import pystray
from PIL import Image, ImageDraw
from winotify import Notification


# ---------------- WINDOW SETUP ----------------
INSTANCE_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    INSTANCE_SOCKET.bind(("127.0.0.1", 47291))
except OSError:
    sys.exit(0)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ---------------- MIDNIGHT EDITORIAL DESIGN ----------------

FONT_FAMILY = "Segoe UI"

FONT_BRAND = (FONT_FAMILY, 17, "bold")
FONT_PAGE_TITLE = (FONT_FAMILY, 30, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 13)

FONT_SECTION = (FONT_FAMILY, 15, "bold")
FONT_BODY = (FONT_FAMILY, 14)
FONT_SMALL = (FONT_FAMILY, 12)
FONT_BUTTON = (FONT_FAMILY, 12, "bold")

FONT_STAT = (FONT_FAMILY, 15)
FONT_METRIC = (FONT_FAMILY, 23, "bold")
FONT_TASK = (FONT_FAMILY, 14)
FONT_LABEL = (FONT_FAMILY, 13)
FONT_DATA = (FONT_FAMILY, 14)

BG_APP = "#17191E"
BG_SIDEBAR = "#14161A"
BG_SURFACE = "#202329"
BG_SURFACE_ALT = "#252932"
BG_INPUT = "#191C22"

BORDER_COLOR = "#30343D"
TEXT_PRIMARY = "#E8EAF0"
TEXT_SECONDARY = "#969EAC"

# Blue is the default. Existing saved accent preferences still apply.

app = ctk.CTk()
app.title("My Productivity")
app.geometry("1100x800")
app.minsize(950, 700)
app.configure(fg_color=BG_APP)


# ---------------- DATA STORAGE ----------------

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "MyToDoList"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TASKS_FILE = DATA_DIR / "tasks.json"
OLD_TASKS_FILE = BASE_DIR / "tasks.json"
ACCOUNTABILITY_FILE = DATA_DIR / "accountability.json"
BROWSER_LOCK_FILE = DATA_DIR / "browser_lock.json"
ACCOUNTABILITY_LOCK_FILE = DATA_DIR / "accountability_lock.json"

def load_tasks():
    if TASKS_FILE.exists():
        with open(TASKS_FILE, "r") as file:
            return json.load(file)

    if OLD_TASKS_FILE.exists():
        with open(OLD_TASKS_FILE, "r") as file:
            old_tasks = json.load(file)

        with open(TASKS_FILE, "w") as file:
            json.dump(old_tasks, file, indent=4)

        return old_tasks

    return []


def save_tasks():
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)


def load_accountability():
    if ACCOUNTABILITY_FILE.exists():
        with open(ACCOUNTABILITY_FILE, "r") as file:
            data = json.load(file)
    else:
        data = {}

    data.setdefault("daily_target", 3)
    data.setdefault("daily_targets", {})
    data.setdefault("daily_records", {})

    return data


def save_accountability():
    with open(ACCOUNTABILITY_FILE, "w") as file:
        json.dump(accountability_data, file, indent=4)


tasks = load_tasks()

# Add missing fields while preserving existing task data.
# Add missing fields while preserving existing task data.
for task in tasks:
    task.setdefault("id", str(uuid.uuid4()))
    task.setdefault("comment", "")
    task.setdefault("due_date", "")
    task.setdefault("completed_on", "")

    if "planned_date" not in task:
        if task.get("done") and task.get("completed_on"):
            task["planned_date"] = task["completed_on"]
        else:
            task["planned_date"] = date.today().isoformat()

save_tasks()
accountability_data = load_accountability()


# ---------------- HABIT STORAGE ----------------

HABITS_FILE = DATA_DIR / "habits.json"


def load_habits():
    if HABITS_FILE.exists():
        with open(HABITS_FILE, "r") as file:
            return json.load(file)
    return []


def save_habits():
    with open(HABITS_FILE, "w") as file:
        json.dump(habits, file, indent=4)


habits = load_habits()


# ---------------- APPEARANCE SETTINGS ----------------

SETTINGS_FILE = DATA_DIR / "settings.json"

ACCENT_COLORS = {
    "Blue": ("#1F6AA5", "#174D78"),
    "Purple": ("#805AD5", "#6243A5"),
    "Green": ("#269B65", "#1D754C"),
    "Red": ("#D94F4F", "#A93838"),
    "Orange": ("#D97726", "#A8581D"),
    "Teal": ("#159A9C", "#107476"),
}


def load_settings():
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    return {"accent_color": "Blue"}


settings = load_settings()

if settings.get("accent_color") not in ACCENT_COLORS:
    settings["accent_color"] = "Blue"

ACCENT_COLOR = ACCENT_COLORS[settings["accent_color"]][0]
ACCENT_HOVER = ACCENT_COLORS[settings["accent_color"]][1]


def save_settings():
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)


# ---------------- APP LAYOUT ----------------

sidebar = ctk.CTkFrame(
    app,
    width=225,
    corner_radius=0,
    fg_color=BG_SIDEBAR
)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

content_frame = ctk.CTkFrame(app, corner_radius=0, fg_color="transparent")
content_frame.pack(side="left", fill="both", expand=True, padx=20, pady=15)

current_page = "tasks"
nav_buttons = {}


# ---------------- SIDEBAR ----------------

brand_label = ctk.CTkLabel(
    sidebar,
    text="MY PRODUCTIVITY",
    font=FONT_BRAND,
    wraplength=190
)
brand_label.pack(padx=10, pady=(30, 35))

sidebar_subtitle = ctk.CTkLabel(
    sidebar,
    text="WORKSPACE",
    font=FONT_SUBTITLE,
    text_color=TEXT_SECONDARY
)
sidebar_subtitle.pack(anchor="w", padx=20, pady=(0, 10))




def update_sidebar_selection():
    for page_name, button in nav_buttons.items():
        if page_name == current_page:
            button.configure(
                fg_color=ACCENT_COLOR,
                hover_color=ACCENT_HOVER,
                text_color="#FFFFFF"
            )
        else:
            button.configure(
                fg_color="transparent",
                hover_color=BG_SURFACE_ALT,
                text_color=TEXT_SECONDARY
            )


def apply_accent_color():
    primary_buttons = {
        "Add Task",
        "Save Target",
        "Add Habit",
        "Save Changes",
        "Save Comment"
    }

    def update_buttons(parent):
        for widget in parent.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                button_text = widget.cget("text")

                if button_text == "Delete":
                    widget.configure(
                        fg_color="#812F38",
                        hover_color="#A33A46",
                        text_color="#FFFFFF",
                        font=FONT_BUTTON
                    )

                elif button_text in primary_buttons:
                    widget.configure(
                        fg_color=ACCENT_COLOR,
                        hover_color=ACCENT_HOVER,
                        text_color="#FFFFFF",
                        font=FONT_BUTTON,
                        corner_radius=9
                    )

                elif widget not in nav_buttons.values():
                    widget.configure(
                        fg_color=BG_SURFACE_ALT,
                        hover_color=BORDER_COLOR,
                        text_color=TEXT_PRIMARY,
                        font=FONT_BODY,
                        corner_radius=9
                    )

            update_buttons(widget)

    update_buttons(app)
    update_sidebar_selection()

def open_appearance_settings():
    settings_window = ctk.CTkToplevel(app)
    settings_window.title("Appearance")
    settings_window.geometry("350x360")
    settings_window.resizable(False, False)
    settings_window.transient(app)

    ctk.CTkLabel(
        settings_window,
        text="APPEARANCE",
        font=("Arial", 22, "bold")
    ).pack(pady=(25, 8))

    ctk.CTkLabel(
        settings_window,
        text="Choose your accent colour",
        text_color="gray"
    ).pack(pady=(0, 15))

    for color_name, color_values in ACCENT_COLORS.items():
        swatch = ctk.CTkButton(
            settings_window,
            text=color_name,
            fg_color=color_values[0],
            hover_color=color_values[1],
            width=190,
            command=lambda name=color_name: choose_accent_color(name)
        )
        swatch.pack(pady=4)

    ctk.CTkLabel(
        settings_window,
        text="Your selection is saved automatically.",
        text_color="gray",
        font=("Arial", 11)
    ).pack(pady=12)


def choose_accent_color(color_name):
    global ACCENT_COLOR, ACCENT_HOVER

    settings["accent_color"] = color_name
    ACCENT_COLOR, ACCENT_HOVER = ACCENT_COLORS[color_name]

    save_settings()
    apply_accent_color()

def navigate(page_name):
    global current_page

    current_page = page_name

    for widget in content_frame.winfo_children():
        widget.destroy()

    update_sidebar_selection()

    if page_name == "tasks":
        build_tasks_page()
    elif page_name == "daily":
        build_daily_check_page()
    elif page_name == "habits":
        build_habit_page()
    apply_accent_color()


nav_buttons["tasks"] = ctk.CTkButton(
    sidebar,
    text="Today's Tasks",
    anchor="w",
    height=42,
    corner_radius=8,
    font=FONT_BODY,
    command=lambda: navigate("tasks")
)
nav_buttons["tasks"].pack(fill="x", padx=12, pady=5)

nav_buttons["daily"] = ctk.CTkButton(
    sidebar,
    text="Daily Check",
    anchor="w",
    height=42,
    corner_radius=8,
    font=FONT_BODY,
    command=lambda: navigate("daily")
)
nav_buttons["daily"].pack(fill="x", padx=12, pady=5)

nav_buttons["habits"] = ctk.CTkButton(
    sidebar,
    text="Habit Tracker",
    anchor="w",
    height=42,
    corner_radius=8,
    font=FONT_BODY,
    command=lambda: navigate("habits")
)
nav_buttons["habits"].pack(fill="x", padx=12, pady=5)


appearance_button = ctk.CTkButton(
    sidebar,
    text="Appearance / Colours",
    anchor="w",
    height=38,
    fg_color="transparent",
    text_color=("gray10", "gray90"),
    hover_color=("gray85", "gray25"),
    command=open_appearance_settings
)
appearance_button.pack(
    side="bottom",
    fill="x",
    padx=12,
)
sidebar_footer = ctk.CTkLabel(
    sidebar,
    text="Worlds Strongest Man \nvs \nA Man With A Promise",
    font=(FONT_FAMILY, 13),
text_color=TEXT_SECONDARY
)
sidebar_footer.pack(side="bottom", pady=25)


# ---------------- SHARED HELPERS ----------------


def make_page_title(title_text, subtitle_text):
    title = ctk.CTkLabel(
        content_frame,
        text=title_text,
        font=FONT_PAGE_TITLE,
        text_color=TEXT_PRIMARY
    )
    title.pack(anchor="w", pady=(4, 5))

    subtitle = ctk.CTkLabel(
        content_frame,
        text=subtitle_text,
        font=FONT_SUBTITLE,
        text_color=TEXT_SECONDARY
    )
    subtitle.pack(anchor="w", pady=(0, 24))

# ---------------- TODAY'S TASKS PAGE ----------------


def build_tasks_page():
    global task_frame, progress_label
    global task_entry, priority_menu, due_date_entry
    global planned_date_entry, input_inner_frame

    make_page_title(
        "Today's Tasks",
        "Organise your work and track what you complete."
    )

    
    task_frame = ctk.CTkScrollableFrame(
    content_frame,
    label_text="YOUR TASKS",
    label_font=FONT_SECTION,
    fg_color=BG_SURFACE,
    corner_radius=14,
    border_width=1,
    border_color=BORDER_COLOR
    )
    task_frame.pack(fill="both", expand=True, pady=(0, 12))

    progress_label = ctk.CTkLabel(
        content_frame,
        text="Completed: 0 / 0",
        font=FONT_LABEL,
text_color=TEXT_SECONDARY
    )
    progress_label.pack(pady=(0, 10))

    input_frame = ctk.CTkFrame(
    content_frame,
    fg_color=BG_SURFACE,
    corner_radius=14,
    border_width=1,
    border_color=BORDER_COLOR
)
    input_frame.pack(fill="x", pady=(0, 5))

    ctk.CTkLabel(
        input_frame,
        text="ADD A TASK",
font=FONT_SECTION,
text_color=TEXT_PRIMARY
    ).pack(pady=(12, 5))

    input_inner_frame = ctk.CTkFrame(
        input_frame,
        fg_color="transparent"
    )
    input_inner_frame.pack(fill="x", padx=10, pady=(3, 12))

    input_inner_frame.grid_columnconfigure(0, weight=1)
    input_inner_frame.grid_columnconfigure(6, weight=1)

    task_entry = ctk.CTkEntry(
        input_inner_frame,
        placeholder_text="Enter a task...",
        width=190,
        height=40
    )
    task_entry.grid(row=0, column=1, padx=4, pady=5)

    priority_menu = ctk.CTkOptionMenu(
        input_inner_frame,
        values=["High", "Medium", "Low"],
        width=95
    )
    priority_menu.grid(row=0, column=2, padx=4, pady=5)

    planned_date_entry = ctk.CTkEntry(
        input_inner_frame,
        placeholder_text="Planned YYYY-MM-DD",
        width=140,
        height=40
    )
    planned_date_entry.grid(row=0, column=3, padx=4, pady=5)
    planned_date_entry.insert(0, date.today().isoformat())

    due_date_entry = ctk.CTkEntry(
        input_inner_frame,
        placeholder_text="Deadline YYYY-MM-DD",
        width=140,
        height=40
    )
    due_date_entry.grid(row=0, column=4, padx=4, pady=5)

    add_button = ctk.CTkButton(
        input_inner_frame,
        text="Add Task",
        command=add_task,
        width=90,
        height=40
    )
    add_button.grid(row=0, column=5, padx=4, pady=5)

    task_entry.bind("<Return>", lambda event: add_task())
    planned_date_entry.bind("<Return>", lambda event: add_task())
    due_date_entry.bind("<Return>", lambda event: add_task())

    display_tasks()


def update_progress():
    completed = sum(1 for task in tasks if task["done"])
    total = len(tasks)

    if total > 0 and completed == total:
        progress_label.configure(
            text=f"All tasks completed! {completed} / {total}"
        )
    else:
        progress_label.configure(
            text=f"Completed: {completed} / {total}"
        )


def display_tasks():
    for widget in task_frame.winfo_children():
        widget.destroy()

    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    priority_colors = {
        "High": "#E74C3C",
        "Medium": "#F39C12",
        "Low": "#2ECC71"
    }

    sorted_tasks = sorted(
        tasks,
        key=lambda task: (
            task["done"],
            priority_order[task["priority"]]
        )
    )

    today = date.today()

    for task in sorted_tasks:
        row = ctk.CTkFrame(
    task_frame,
    fg_color=BG_SURFACE_ALT,
    corner_radius=10,
    border_width=1,
    border_color=BORDER_COLOR
)
        row.pack(fill="x", padx=6, pady=5)
        checkbox = ctk.CTkCheckBox(
    row,
    text=task["name"],
    font=FONT_TASK,
    text_color=TEXT_PRIMARY,
    command=lambda t=task: toggle_task(t)
)
        checkbox.pack(side="left", padx=12, pady=12)

        if task["done"]:
            checkbox.select()

        priority_label = ctk.CTkLabel(
            row,
            text=task["priority"].upper(),
            width=75,
            text_color=priority_colors[task["priority"]],
            font=FONT_SMALL
        )
        priority_label.pack(side="left", padx=5)
        
        planned_date = task.get("planned_date", "")

        if planned_date:
            planned_label = ctk.CTkLabel(
                row,
                text=f"Plan: {planned_date}",
                text_color=TEXT_SECONDARY,
                font=FONT_SMALL
            )
            planned_label.pack(side="left", padx=5)

        due_date = task.get("due_date", "")

        if due_date:
            try:
                deadline = date.fromisoformat(due_date)

                if task["done"]:
                    due_text = f"Due: {due_date}"
                    due_color = "gray"
                elif deadline < today:
                    due_text = f"OVERDUE: {due_date}"
                    due_color = "#FF4444"
                elif deadline == today:
                    due_text = "DUE TODAY"
                    due_color = "#F39C12"
                else:
                    due_text = f"Due: {due_date}"
                    due_color = "gray"

            except ValueError:
                due_text = "Invalid date"
                due_color = "#FF4444"

            due_label = ctk.CTkLabel(
                row,
                text=due_text,
                text_color=due_color,
                font=(FONT_FAMILY, 12, "bold")
            )
            due_label.pack(side="left", padx=5)

        delete_button = ctk.CTkButton(
            row,
            text="Delete",
            width=60,
            fg_color="#9B3030",
            hover_color="#702020",
            command=lambda t=task: delete_task(t)
        )
        delete_button.pack(side="right", padx=5, pady=5)

        comment_button = ctk.CTkButton(
            row,
            text="Comment",
            width=75,
            command=lambda t=task: edit_comment(t)
        )
        comment_button.pack(side="right", padx=3, pady=5)

        edit_button = ctk.CTkButton(
            row,
            text="Edit",
            width=55,
            command=lambda t=task: edit_task(t)
        )
        edit_button.pack(side="right", padx=3, pady=5)

    update_progress()


# ---------------- ADD TASK ----------------


def add_task():
    name = task_entry.get().strip()
    priority = priority_menu.get()
    planned_date = planned_date_entry.get().strip()
    due_date = due_date_entry.get().strip()

    if not name:
        return

    if not planned_date:
        planned_date = date.today().isoformat()

    for label, value in [
        ("Planned date", planned_date),
        ("Deadline", due_date)
    ]:
        if value:
            try:
                parsed_date = date.fromisoformat(value)
                if parsed_date.isoformat() != value:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Invalid Date",
                    f"{label} must use YYYY-MM-DD format.",
                    parent=app
                )
                return

    tasks.append({
        "id": str(uuid.uuid4()),
        "name": name,
        "priority": priority,
        "done": False,
        "comment": "",
        "planned_date": planned_date,
        "due_date": due_date,
        "completed_on": ""
    })

    save_tasks()

    task_entry.delete(0, "end")
    planned_date_entry.delete(0, "end")
    planned_date_entry.insert(0, date.today().isoformat())
    due_date_entry.delete(0, "end")

    display_tasks()

# ---------------- CHECK OFF TASK ----------------

def toggle_task(task):
    today_key = date.today().isoformat()
    records = accountability_data["daily_records"]

    if task["done"]:
        task["done"] = False
        completed_date = task.get("completed_on", "")

        if completed_date:
            records[completed_date] = max(
                0,
                records.get(completed_date, 0) - 1
            )

        task["completed_on"] = ""

    else:
        task["done"] = True
        task["completed_on"] = today_key

        records[today_key] = records.get(today_key, 0) + 1

    save_tasks()
    save_accountability()
    update_accountability_lock_after_task_change()
    display_tasks()


# ---------------- DELETE TASK ----------------

def delete_task(task):
    if (
        lock_state["lock_active"]
        and task.get("id") in lock_state["locked_task_ids"]
    ):
        messagebox.showwarning(
            "Task Locked",
            "Complete this task before deleting it. It is part of the active accountability lock.",
            parent=app
        )
        return

    tasks.remove(task)
    save_tasks()
    display_tasks()

# ---------------- EDIT TASK ----------------


def edit_task(task):
    edit_window = ctk.CTkToplevel(app)
    edit_window.title("Edit Task")
    edit_window.geometry("400x430")
    edit_window.resizable(False, False)
    edit_window.transient(app)
    edit_window.grab_set()

    ctk.CTkLabel(
        edit_window,
        text="Edit Task",
        font=("Arial", 20, "bold")
    ).pack(pady=(20, 10))

    edit_entry = ctk.CTkEntry(
        edit_window,
        width=300,
        height=40
    )
    edit_entry.pack(pady=8)
    edit_entry.insert(0, task["name"])

    edit_priority = ctk.CTkOptionMenu(
        edit_window,
        values=["High", "Medium", "Low"],
        width=200
    )
    edit_priority.set(task["priority"])
    edit_priority.pack(pady=8)

    edit_planned_date = ctk.CTkEntry(
        edit_window,
        width=220,
        placeholder_text="Planned date YYYY-MM-DD"
    )
    edit_planned_date.pack(pady=8)
    edit_planned_date.insert(
        0,
        task.get("planned_date", date.today().isoformat())
    )

    edit_due_date = ctk.CTkEntry(
        edit_window,
        width=220,
        placeholder_text="Deadline YYYY-MM-DD"
    )
    edit_due_date.pack(pady=8)
    edit_due_date.insert(0, task.get("due_date", ""))

    def save_edit():
        new_name = edit_entry.get().strip()
        new_priority = edit_priority.get()
        new_planned_date = edit_planned_date.get().strip()
        new_due_date = edit_due_date.get().strip()

        if not new_name:
            return

        if not new_planned_date:
            messagebox.showerror(
                "Invalid Planned Date",
                "Enter a planned date in YYYY-MM-DD format.",
                parent=edit_window
            )
            return

        for label, value in [
            ("Planned date", new_planned_date),
            ("Deadline", new_due_date)
        ]:
            if value:
                try:
                    parsed_date = date.fromisoformat(value)
                    if parsed_date.isoformat() != value:
                        raise ValueError
                except ValueError:
                    messagebox.showerror(
                        "Invalid Date",
                        f"{label} must use YYYY-MM-DD format.",
                        parent=edit_window
                    )
                    return

        task["name"] = new_name
        task["priority"] = new_priority
        task["planned_date"] = new_planned_date
        task["due_date"] = new_due_date

        save_tasks()
        display_tasks()
        edit_window.destroy()

    ctk.CTkButton(
        edit_window,
        text="Save Changes",
        command=save_edit
    ).pack(pady=10)
# ---------------- EDIT TASK COMMENT ----------------

def edit_comment(task):
    comment_window = ctk.CTkToplevel(app)
    comment_window.title("Task Comment")
    comment_window.geometry("450x350")
    comment_window.resizable(False, False)
    comment_window.transient(app)
    comment_window.grab_set()

    ctk.CTkLabel(
        comment_window,
        text=f"Notes: {task['name']}",
        font=("Arial", 18, "bold"),
        wraplength=400
    ).pack(pady=(20, 10))

    comment_box = ctk.CTkTextbox(
        comment_window,
        width=400,
        height=200,
        wrap="word"
    )
    comment_box.pack(padx=20, pady=10)
    comment_box.insert("1.0", task.get("comment", ""))

    def save_comment():
        task["comment"] = comment_box.get(
            "1.0",
            "end-1c"
        ).strip()

        save_tasks()
        comment_window.destroy()

    ctk.CTkButton(
        comment_window,
        text="Save Comment",
        command=save_comment
    ).pack(pady=10)


# ---------------- DAILY CHECK PAGE ----------------


def build_daily_check_page():
    make_page_title(
        "Daily Check",
        "Measure consistency, daily progress, and streaks."
    )

    today_key = date.today().isoformat()

    # ---------------- DAILY TARGET ----------------

    target_frame = ctk.CTkFrame(content_frame)
    target_frame.pack(fill="x", pady=(0, 15))

    ctk.CTkLabel(
        target_frame,
        text="Daily task target",
        font=FONT_SECTION,
        text_color=TEXT_PRIMARY
    ).pack(side="left", padx=(15, 8), pady=15)

    target_entry = ctk.CTkEntry(target_frame, width=80)
    target_entry.pack(side="left", padx=5, pady=15)

    current_target = accountability_data["daily_targets"].get(
        today_key,
        accountability_data["daily_target"]
    )
    target_entry.insert(0, str(current_target))

    # ---------------- STATISTICS ----------------

    stats_frame = ctk.CTkFrame(content_frame)
    stats_frame.pack(fill="x", pady=(0, 15))
    stats_label = ctk.CTkLabel(
    stats_frame,
    text="",
    font=FONT_STAT,
    text_color=TEXT_PRIMARY,
    justify="left",
    anchor="w"
)
    stats_label.pack(anchor="w", padx=20, pady=20)

    # ---------------- SEVEN-DAY HISTORY ----------------

    history_frame = ctk.CTkFrame(content_frame)
    history_frame.pack(fill="x", pady=(0, 10))

    ctk.CTkLabel(
        history_frame,
        text="LAST 7 DAYS",
        font=FONT_SECTION,
        text_color=TEXT_PRIMARY
    ).pack(anchor="w", padx=20, pady=(15, 5))

    history_label = ctk.CTkLabel(
    history_frame,
    text="",
    font=FONT_DATA,
    text_color=TEXT_SECONDARY,
    justify="left",
    anchor="w"
)
    history_label.pack(anchor="w", padx=20, pady=(5, 20))
    # ---------------- DAILY COUNTING LOGIC ----------------

    def get_day_counts(day_key):
        day_tasks = [
            task for task in tasks
            if task.get("planned_date") == day_key
        ]

        planned_count = len(day_tasks)

        completed_planned = sum(
            1 for task in day_tasks
            if task.get("done", False)
            and task.get("completed_on", "") == day_key
        )

        completed_count = accountability_data[
            "daily_records"
        ].get(day_key, 0)

        return planned_count, completed_planned, completed_count

    def is_successful_day(day_key, day_target):
        planned, completed_planned, completed_count = (
            get_day_counts(day_key)
        )

        met_target = completed_count >= day_target

        finished_plan = (
            planned > 0
            and completed_planned == planned
        )

        return met_target or finished_plan

    # ---------------- REFRESH STATISTICS ----------------

    def refresh_daily_check():
        today = date.today()
        today_key = today.isoformat()

        records = accountability_data["daily_records"]
        targets = accountability_data["daily_targets"]

        target = targets.get(
            today_key,
            accountability_data["daily_target"]
        )

        planned_today, completed_planned_today, completed_today = (
            get_day_counts(today_key)
        )

        remaining = max(0, target - completed_today)

        all_dates = set(records.keys()) | set(targets.keys())

        all_dates.update(
            task.get("planned_date")
            for task in tasks
            if task.get("planned_date")
        )

        successful_dates = set()

        for day_key in all_dates:
            try:
                day_date = date.fromisoformat(day_key)
            except (ValueError, TypeError):
                continue

            if day_date > today:
                continue

            day_target = targets.get(
                day_key,
                accountability_data["daily_target"]
            )

            if is_successful_day(day_key, day_target):
                successful_dates.add(day_key)

        # Current streak
        if today_key in successful_dates:
            check_date = today
        else:
            check_date = today - timedelta(days=1)

        current_streak = 0

        while check_date.isoformat() in successful_dates:
            current_streak += 1
            check_date -= timedelta(days=1)

        # Best streak
        best_streak = 0
        running_streak = 0
        previous_date = None

        for day_key in sorted(successful_dates):
            current_date = date.fromisoformat(day_key)

            if (
                previous_date is not None
                and (current_date - previous_date).days == 1
            ):
                running_streak += 1
            else:
                running_streak = 1

            best_streak = max(best_streak, running_streak)
            previous_date = current_date

        # Today's result
        today_status = (
            "WIN" if today_key in successful_dates
            else "NO WIN YET"
        )

        stats_label.configure(
            text=(
                f"Today's result: {today_status}\n\n"
                f"Tasks completed today: {completed_today}\n"
                f"Daily target: {target}\n"
                f"Planned tasks completed: "
                f"{completed_planned_today}/{planned_today}\n"
                f"Tasks remaining to target: {remaining}\n\n"
                f"Current streak: {current_streak} days\n"
                f"Best streak: {best_streak} days\n"
                f"Total successful days: {len(successful_dates)}"
            )
        )

        # Last seven days
        history_lines = []

        for offset in range(6, -1, -1):
            day = today - timedelta(days=offset)
            day_key = day.isoformat()

            day_target = targets.get(
                day_key,
                accountability_data["daily_target"]
            )

            planned, completed_planned, completed_count = (
                get_day_counts(day_key)
            )

            status = (
                "WIN" if is_successful_day(day_key, day_target)
                else "NO WIN"
            )

            history_lines.append(
                f"{day.strftime('%a, %d %b')}: "
                f"Plan {completed_planned}/{planned}; "
                f"completed {completed_count}/{day_target} target "
                f"— {status}"
            )

        history_label.configure(text="\n".join(history_lines))

    # ---------------- SAVE DAILY TARGET ----------------

    def save_target():
        try:
            target = int(target_entry.get().strip())

            if target < 1:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Target",
                "Enter a whole number greater than zero.",
                parent=app
            )
            return

        today_key = date.today().isoformat()

        accountability_data["daily_target"] = target
        accountability_data["daily_targets"][today_key] = target

        save_accountability()
        refresh_daily_check()

    ctk.CTkButton(
        target_frame,
        text="Save Target",
        command=save_target
    ).pack(side="left", padx=10, pady=15)

    # Initial display
    refresh_daily_check()

# ---------------- HABIT TRACKER ----------------

def calculate_habit_streak(completed_dates):
    completed_dates = set(completed_dates)
    today = date.today()

    if today.isoformat() in completed_dates:
        check_date = today
    else:
        check_date = today - timedelta(days=1)

    streak = 0

    while check_date.isoformat() in completed_dates:
        streak += 1
        check_date -= timedelta(days=1)

    return streak


def toggle_habit(habit):
    today_key = date.today().isoformat()
    completed_dates = habit.setdefault("completed_dates", [])

    if today_key in completed_dates:
        completed_dates.remove(today_key)
    else:
        completed_dates.append(today_key)

    save_habits()
    render_habits()


def delete_habit(habit):
    if not messagebox.askyesno(
        "Delete Habit",
        f"Delete '{habit['name']}' and its history?",
        parent=app
    ):
        return

    habits.remove(habit)
    save_habits()
    render_habits()


def render_habits():
    for widget in habit_frame.winfo_children():
        widget.destroy()

    today_key = date.today().isoformat()

    if not habits:
        ctk.CTkLabel(
            habit_frame,
            text="No habits yet. Add your first habit above.",
            text_color="gray"
        ).pack(pady=25)
        return

    for habit in habits:
        habit.setdefault("completed_dates", [])

        row = ctk.CTkFrame(habit_frame)
        row.pack(fill="x", padx=5, pady=5)

        completed_dates = set(habit["completed_dates"])
        completed_today = today_key in completed_dates

        checkbox = ctk.CTkCheckBox(
            row,
            text=habit["name"],
            command=lambda h=habit: toggle_habit(h)
        )
        checkbox.pack(side="left", padx=12, pady=12)

        if completed_today:
            checkbox.select()

        streak = calculate_habit_streak(completed_dates)

        ctk.CTkLabel(
            row,
            text=f"Streak: {streak} days",
            text_color=ACCENT_COLOR,
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=8)

        last_seven = []

        for offset in range(6, -1, -1):
            day = date.today() - timedelta(days=offset)
            marker = "✓" if day.isoformat() in completed_dates else "·"
            last_seven.append(marker)

        ctk.CTkLabel(
            row,
            text=" ".join(last_seven),
            text_color="gray",
            font=("Arial", 14)
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            row,
            text="Delete",
            width=60,
            fg_color="#9B3030",
            hover_color="#702020",
            command=lambda h=habit: delete_habit(h)
        ).pack(side="right", padx=10, pady=8)


def build_habit_page():
    global habit_frame

    make_page_title(
        "Habit Tracker",
        "Build consistent routines and track your progress."
    )

    add_frame = ctk.CTkFrame(content_frame)
    add_frame.pack(fill="x", pady=(0, 15))

    habit_entry = ctk.CTkEntry(
        add_frame,
        placeholder_text="Enter a habit (e.g. Read for 20 minutes)",
        height=40
    )
    habit_entry.pack(
        side="left",
        fill="x",
        expand=True,
        padx=(12, 5),
        pady=12
    )

    def add_habit():
        name = habit_entry.get().strip()

        if not name:
            return

        if any(h["name"].casefold() == name.casefold() for h in habits):
            messagebox.showerror(
                "Duplicate Habit",
                "This habit already exists.",
                parent=app
            )
            return

        habits.append({
            "name": name,
            "completed_dates": []
        })

        save_habits()
        habit_entry.delete(0, "end")
        render_habits()

    ctk.CTkButton(
        add_frame,
        text="Add Habit",
        width=100,
        height=40,
        command=add_habit
    ).pack(side="left", padx=(5, 12), pady=12)

    habit_entry.bind(
        "<Return>",
        lambda event: add_habit()
    )

    ctk.CTkLabel(
        content_frame,
        text="YOUR HABITS",
        font=("Arial", 16, "bold")
    ).pack(anchor="w", pady=(0, 8))

    ctk.CTkLabel(
        content_frame,
        text="Last 7 days: oldest → newest",
        text_color="gray",
        font=("Arial", 11)
    ).pack(anchor="w", pady=(0, 5))

    habit_frame = ctk.CTkScrollableFrame(
        content_frame,
        label_text="Daily Habits"
    )
    habit_frame.pack(fill="both", expand=True)

    render_habits()

    # placeholder_frame = ctk.CTkFrame(content_frame)
    # placeholder_frame.pack(fill="both", expand=True, pady=(0, 10))

    # ctk.CTkLabel(
    #     placeholder_frame,
    #     text="Your habits will live here.",
    #     font=("Arial", 22, "bold")
    # ).pack(pady=(100, 10))

    # ctk.CTkLabel(
    #     placeholder_frame,
    #     text=(
    #         "Next, we'll add custom habits, daily check-offs,\n"
    #         "individual streaks, and weekly history."
    #     ),
    #     font=("Arial", 14),
    #     text_color="gray",
    #     justify="center"
    # ).pack(pady=5)


# ---------------- SYSTEM TRAY ----------------

def create_tray_image():
    image = Image.new("RGB", (64, 64), "#1F6AA5")
    draw = ImageDraw.Draw(image)
    draw.text((19, 13), "T", fill="white")
    return image


def show_window(icon=None, item=None):
    app.after(0, restore_window)


def restore_window():
    app.deiconify()
    app.lift()
    app.focus_force()


def hide_window():
    app.withdraw()


def quit_app(icon=None, item=None):
    app.after(0, close_app)


def close_app():
    tray_icon.stop()
    app.destroy()


tray_menu = pystray.Menu(
    pystray.MenuItem(
        "Open My Productivity",
        show_window,
        default=True
    ),
    pystray.MenuItem("Quit", quit_app)
)

tray_icon = pystray.Icon(
    "MyToDoList",
    create_tray_image(),
    "My Productivity",
    menu=tray_menu
)

# ---------------- ACCOUNTABILITY LOCK ----------------

LOCK_CHECK_INTERVAL = 30 * 1000
WARNING_TIME = time(22, 30)
CHECKPOINT_TIME = time(23, 0)
BRIDGE_HOST = "127.0.0.1"
BRIDGE_PORT = 49252

def load_lock_state():
    if ACCOUNTABILITY_LOCK_FILE.exists():
        with open(ACCOUNTABILITY_LOCK_FILE, "r") as file:
            state = json.load(file)

        state.setdefault("lock_active", False)
        state.setdefault("locked_task_ids", [])
        state.setdefault("locked_task_names", [])
        state.setdefault("warning_date", "")
        state.setdefault("checkpoint_date", "")
        return state

    state = {
        "lock_active": False,
        "locked_task_ids": [],
        "locked_task_names": [],
        "warning_date": "",
        "checkpoint_date": ""
    }

    if BROWSER_LOCK_FILE.exists():
        try:
            with open(BROWSER_LOCK_FILE, "r") as file:
                browser_state = json.load(file)

            if browser_state.get("lock_active") is True:
                state["lock_active"] = True
        except (OSError, json.JSONDecodeError):
            pass

    return state


lock_state = load_lock_state()


def save_lock_state():
    with open(ACCOUNTABILITY_LOCK_FILE, "w") as file:
        json.dump(lock_state, file, indent=4)

    with open(BROWSER_LOCK_FILE, "w") as file:
        json.dump(
            {"lock_active": lock_state["lock_active"]},
            file,
            indent=4
        )


def task_qualifies_for_lock(task, today):
    if task.get("done", False):
        return False

    planned_date = task.get("planned_date", "")
    due_date = task.get("due_date", "")

    if planned_date == today.isoformat():
        return True

    if due_date:
        try:
            if date.fromisoformat(due_date) <= today:
                return True
        except ValueError:
            pass

    return False
def get_qualifying_tasks(today):
    return [task for task in tasks if task_qualifies_for_lock(task, today)]

def send_accountability_notification(title, message):
    notification = Notification(
        app_id="My Productivity",
        title=title,
        msg=message,
        duration="long"
    )
    notification.show()


def update_accountability_lock_after_task_change():
    if not lock_state["lock_active"]:
        return

    locked_ids = set(lock_state["locked_task_ids"])

    if not locked_ids:
        return

    tasks_by_id = {
        task.get("id"): task
        for task in tasks
        if task.get("id")
    }

    for task_id in locked_ids:
        task = tasks_by_id.get(task_id)

        if task is None or not task.get("done", False):
            return

    lock_state["lock_active"] = False
    lock_state["locked_task_ids"] = []
    lock_state["locked_task_names"] = []
    save_lock_state()

    send_accountability_notification(
        "Accountability Lock Released",
        "All tasks covered by the lock are complete. Your browser should unblock shortly."
    )


def run_accountability_checkpoint(today):
    today_key = today.isoformat()

    if lock_state["checkpoint_date"] == today_key:
        return

    qualifying_tasks = get_qualifying_tasks(today)
    lock_state["checkpoint_date"] = today_key

    if qualifying_tasks:
        existing_ids = set(lock_state["locked_task_ids"])
        existing_names = set(lock_state["locked_task_names"])

        for task in qualifying_tasks:
            task_id = task.get("id")

            if task_id:
                existing_ids.add(task_id)

            existing_names.add(task.get("name", "Unnamed task"))

        lock_state["locked_task_ids"] = list(existing_ids)
        lock_state["locked_task_names"] = sorted(existing_names)
        lock_state["lock_active"] = True

        save_lock_state()

        send_accountability_notification(
            "Accountability Lock Activated",
            f"{len(qualifying_tasks)} qualifying unfinished task(s) remain. Complete the locked tasks to unblock your browser."
        )
    else:
        save_lock_state()



def process_missed_checkpoints(today):
    yesterday = today - timedelta(days=1)

    last_checkpoint_text = lock_state.get("checkpoint_date", "")

    if last_checkpoint_text:
        try:
            last_checkpoint = date.fromisoformat(last_checkpoint_text)
        except ValueError:
            last_checkpoint = yesterday - timedelta(days=1)
    else:
        last_checkpoint = yesterday - timedelta(days=1)

    while last_checkpoint < yesterday:
        next_checkpoint = last_checkpoint + timedelta(days=1)
        run_accountability_checkpoint(next_checkpoint)
        last_checkpoint = next_checkpoint


def check_accountability_schedule():
    try:
        now = datetime.now()
        today = now.date()
        today_key = today.isoformat()

        process_missed_checkpoints(today)

        if (
            now.time() >= WARNING_TIME
            and lock_state["warning_date"] != today_key
        ):
            qualifying_tasks = get_qualifying_tasks(today)

            if qualifying_tasks:
                names = [
                    task.get("name", "Unnamed task")
                    for task in qualifying_tasks[:5]
                ]

                message = "\n".join(names)

                if len(qualifying_tasks) > 5:
                    message += (
                        f"\nAnd {len(qualifying_tasks) - 5} more task(s)."
                    )

                send_accountability_notification(
                    "10:30 PM Task Warning",
                    message
                )

            lock_state["warning_date"] = today_key
            save_lock_state()

        if now.time() >= CHECKPOINT_TIME:
            run_accountability_checkpoint(today)

    except Exception as error:
        print(f"Accountability scheduler error: {error}")

    finally:
        app.after(
            LOCK_CHECK_INTERVAL,
            check_accountability_schedule
        )
# ---------------- LOCAL BROWSER BRIDGE ----------------

class BrowserBridgeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/status":
            self.send_error(404)
            return

        response_body = json.dumps({
            "lock_active": bool(lock_state["lock_active"])
        }).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))

        origin = self.headers.get("Origin", "")
        if origin.startswith("chrome-extension://"):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")

        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, format_string, *args):
        pass
class LocalThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = False

    def server_bind(self):
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_EXCLUSIVEADDRUSE,
                1
            )

        super().server_bind()

def start_browser_bridge():
    print(f"Starting browser bridge on {BRIDGE_HOST}:{BRIDGE_PORT}")
    try:
        bridge_server = LocalThreadingHTTPServer(
        (BRIDGE_HOST, BRIDGE_PORT),
        BrowserBridgeHandler
        )
        print("Browser bridge started successfully.")
    except OSError as error:
        print(f"Browser bridge could not start: {type(error).__name__}: {error}")
        return None

    bridge_thread = threading.Thread(
        target=bridge_server.serve_forever,
        daemon=True
    )
    bridge_thread.start()
    return bridge_server
# ---------------- TASK REMINDERS ----------------

REMINDER_INTERVAL = 30 * 60 * 1000


def check_pending_tasks():
    pending_tasks = [
        task for task in tasks
        if not task["done"]
    ]

    if pending_tasks:
        count = len(pending_tasks)

        if count == 1:
            message = f"Pending task: {pending_tasks[0]['name']}"
        else:
            message = f"You have {count} unfinished tasks."

        notification = Notification(
            app_id="My To-Do List",
            title="Task Reminder",
            msg=message,
            duration="short"
        )
        notification.show()

    app.after(REMINDER_INTERVAL, check_pending_tasks)


# ---------------- START APP ----------------

navigate("tasks")
apply_accent_color()
app.protocol("WM_DELETE_WINDOW", hide_window)

save_lock_state()
bridge_server = start_browser_bridge()

tray_icon.run_detached()

app.after(REMINDER_INTERVAL, check_pending_tasks)
app.after(1000, check_accountability_schedule)

app.mainloop()