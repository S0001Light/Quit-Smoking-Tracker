import tkinter as tk
from tkinter import messagebox, ttk
import time
import json
import os
from datetime import datetime, timedelta

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DATA_FILE = "smoking_log.json"

# ------------------------------
# Data Handling
# ------------------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "timestamps": [],
            "mode": "tracking",
            "avg_interval": None,
            "cutback_start": None,
            "current_interval": None,
            "settings": {
                "daily_limit": 20,
                "quit_date": None,
                "interval_step": 0.05,
                "theme": "mobile",
                "tracking_weeks": 1,
                "cutback_plan": "3-month"
            },
            "next_notification_time": None
        }
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# ------------------------------
# Theme / Mobile Style
# ------------------------------

def apply_theme():
    theme = data["settings"].get("theme", "mobile")
    if theme == "mobile":
        root.configure(bg="#222222")
        for w in root.winfo_children():
            if isinstance(w, (tk.Button, ttk.Button)):
                w.configure(bg="#444444", fg="white", activebackground="#666666")
            elif isinstance(w, tk.Label):
                w.configure(bg="#222222", fg="white")
            elif isinstance(w, tk.Listbox):
                w.configure(bg="#111111", fg="white")
    else:
        root.configure(bg=None)

# ------------------------------
# Core Logic
# ------------------------------

def get_today_count():
    today = datetime.now().date()
    return sum(1 for t in data["timestamps"]
               if datetime.fromtimestamp(t).date() == today)

def track_smoke():
    now = time.time()
    data["timestamps"].append(now)
    save_data(data)
    update_log()
    update_graph()
    check_daily_limit()
    messagebox.showinfo("Logged", "Cigarette logged.")

def check_daily_limit():
    limit = data["settings"]["daily_limit"]
    count = get_today_count()
    if count > limit:
        messagebox.showwarning("Daily Limit Exceeded",
                               f"You've logged {count} cigarettes today.\n"
                               f"Your limit is {limit}.")

def calculate_average():
    weeks = data["settings"]["tracking_weeks"]
    stamps = data["timestamps"]

    if len(stamps) < 2:
        messagebox.showerror("Error", "Not enough data to calculate average.")
        return

    cutoff = time.time() - (weeks * 7 * 24 * 3600)
    filtered = [t for t in stamps if t >= cutoff]

    if len(filtered) < 2:
        messagebox.showerror("Error", "Not enough data in selected timeframe.")
        return

    intervals = [filtered[i] - filtered[i - 1] for i in range(1, len(filtered))]
    avg = sum(intervals) / len(intervals)

    data["avg_interval"] = avg
    data["mode"] = "cutback"
    data["cutback_start"] = time.time()
    data["current_interval"] = avg
    save_data(data)

    messagebox.showinfo("Average Calculated",
                        f"Average interval: {avg/60:.1f} minutes.\n"
                        "Cutback mode activated.")

def next_allowed_time():
    if data["mode"] != "cutback":
        messagebox.showinfo("Info", "Still in tracking mode.")
        return

    if not data["timestamps"]:
        messagebox.showerror("Error", "No smoking events logged yet.")
        return

    last_smoke = data["timestamps"][-1]
    interval = data["current_interval"]
    allowed = last_smoke + interval
    allowed_dt = datetime.fromtimestamp(allowed)

    delay_ms = int(max(0, (allowed - time.time()) * 1000))
    data["next_notification_time"] = allowed
    save_data(data)
    root.after(delay_ms, notify_time_to_smoke)

    messagebox.showinfo("Next Cigarette",
                        f"You may smoke at:\n{allowed_dt.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        "A popup will appear when it's time.")

def notify_time_to_smoke():
    if data.get("next_notification_time") and time.time() >= data["next_notification_time"]:
        messagebox.showinfo("Scheduled Cigarette",
                            "It's time for your scheduled cigarette.\n"
                            "If you still feel you need it, smoke mindfully.")
        data["next_notification_time"] = None
        save_data(data)

def increase_interval():
    plan = data["settings"]["cutback_plan"]

    step_map = {
        "3-month": 0.05,
        "6-month": 0.10,
        "9-month": 0.15,
        "12-month": 0.20
    }

    step = step_map.get(plan, 0.05)
    data["current_interval"] *= (1.0 + step)
    save_data(data)

    messagebox.showinfo("Interval Increased",
                        f"New interval: {data['current_interval']/60:.1f} minutes.")

# ------------------------------
# Quit Date Countdown
# ------------------------------

def update_quit_countdown():
    quit_date_str = data["settings"].get("quit_date")
    if not quit_date_str:
        countdown_label.config(text="Quit date: not set")
    else:
        try:
            quit_dt = datetime.strptime(quit_date_str, "%Y-%m-%d")
            now = datetime.now()
            delta = quit_dt - now
            if delta.total_seconds() <= 0:
                countdown_label.config(text="Quit date reached. Stay strong.")
            else:
                days = delta.days
                hours = delta.seconds // 3600
                countdown_label.config(text=f"Quit in {days} days, {hours} hours")
        except ValueError:
            countdown_label.config(text="Quit date: invalid format")

    root.after(60000, update_quit_countdown)

# ------------------------------
# Settings Window
# ------------------------------

def open_settings():
    win = tk.Toplevel(root)
    win.title("Settings")
    win.geometry("300x350")

    tk.Label(win, text="Daily limit:").pack(pady=5)
    daily_var = tk.StringVar(value=str(data["settings"]["daily_limit"]))
    tk.Entry(win, textvariable=daily_var).pack()

    tk.Label(win, text="Quit date (YYYY-MM-DD):").pack(pady=5)
    quit_var = tk.StringVar(value=data["settings"]["quit_date"] or "")
    tk.Entry(win, textvariable=quit_var).pack()

    tk.Label(win, text="Tracking duration (weeks):").pack(pady=5)
    track_var = tk.StringVar(value=str(data["settings"]["tracking_weeks"]))
    ttk.Combobox(win, textvariable=track_var,
                 values=["1", "2", "3", "4"]).pack()

    tk.Label(win, text="Cutback plan:").pack(pady=5)
    plan_var = tk.StringVar(value=data["settings"]["cutback_plan"])
    ttk.Combobox(win, textvariable=plan_var,
                 values=["3-month", "6-month", "9-month", "12-month"]).pack()

    tk.Label(win, text="Theme:").pack(pady=5)
    theme_var = tk.StringVar(value=data["settings"]["theme"])
    ttk.Combobox(win, textvariable=theme_var,
                 values=["mobile", "default"]).pack()

    def save_settings():
        try:
            data["settings"]["daily_limit"] = int(daily_var.get())
        except ValueError:
            messagebox.showerror("Error", "Daily limit must be an integer.")
            return

        qd = quit_var.get().strip()
        if qd:
            try:
                datetime.strptime(qd, "%Y-%m-%d")
                data["settings"]["quit_date"] = qd
            except ValueError:
                messagebox.showerror("Error", "Quit date must be YYYY-MM-DD.")
                return
        else:
            data["settings"]["quit_date"] = None

        data["settings"]["tracking_weeks"] = int(track_var.get())
        data["settings"]["cutback_plan"] = plan_var.get()
        data["settings"]["theme"] = theme_var.get()

        save_data(data)
        apply_theme()
        update_quit_countdown()
        win.destroy()

    tk.Button(win, text="Save", command=save_settings).pack(pady=10)

# ------------------------------
# Progress Graph (Matplotlib)
# ------------------------------

def update_graph():
    counts = {}
    for t in data["timestamps"]:
        d = datetime.fromtimestamp(t).date()
        counts[d] = counts.get(d, 0) + 1

    dates = sorted(counts.keys())
    values = [counts[d] for d in dates]

    fig.clear()
    ax = fig.add_subplot(111)
    if dates:
        ax.bar(range(len(dates)), values, color="#4caf50")
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels([d.strftime("%m-%d") for d in dates],
                           rotation=45, ha="right")
        ax.set_ylabel("Cigarettes")
        ax.set_title("Daily Smoking Progress")
    else:
        ax.text(0.5, 0.5, "No data yet", ha="center", va="center")

    fig.tight_layout()
    canvas.draw()

# ------------------------------
# GUI
# ------------------------------

root = tk.Tk()
root.title("Quit Smoking Tracker")
root.geometry("420x750")

title = tk.Label(root, text="Quit Smoking Tracker", font=("Arial", 20, "bold"))
title.pack(pady=10)

countdown_label = tk.Label(root, text="Quit date: not set", font=("Arial", 12))
countdown_label.pack(pady=5)

track_btn = tk.Button(root, text="Track Cigarette", font=("Arial", 16),
                      command=track_smoke)
track_btn.pack(pady=10, fill="x", padx=20)

avg_btn = tk.Button(root, text="Calculate Average (Tracking Phase)",
                    font=("Arial", 14), command=calculate_average)
avg_btn.pack(pady=10, fill="x", padx=20)

next_btn = tk.Button(root, text="Next Allowed Cigarette", font=("Arial", 14),
                     command=next_allowed_time)
next_btn.pack(pady=10, fill="x", padx=20)

increase_btn = tk.Button(root, text="Increase Interval", font=("Arial", 14),
                         command=increase_interval)
increase_btn.pack(pady=10, fill="x", padx=20)

settings_btn = tk.Button(root, text="Settings", font=("Arial", 14),
                         command=open_settings)
settings_btn.pack(pady=10, fill="x", padx=20)

log_label = tk.Label(root, text="Smoking Log:")
log_label.pack()

log = tk.Listbox(root, width=40, height=8)
log.pack(pady=10)

fig = Figure(figsize=(4, 3), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)

def update_log():
    log.delete(0, tk.END)
    for t in data["timestamps"]:
        log.insert(tk.END, datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"))

apply_theme()
update_log()
update_graph()
update_quit_countdown()

root.mainloop()
