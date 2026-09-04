import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

# ------------------------------
# Core Calculations
# ------------------------------

def calculate():
    try:
        daily = float(entry_daily.get())
        pack_price = float(entry_price.get())
        cigs_per_pack = float(entry_pack.get())
    except:
        messagebox.showerror("Error", "Enter valid numbers.")
        return

    # Basic totals
    weekly = daily * 7
    monthly = daily * 30

    # Cost calculations
    cost_per_cig = pack_price / cigs_per_pack
    daily_cost = daily * cost_per_cig
    weekly_cost = weekly * cost_per_cig
    monthly_cost = monthly * cost_per_cig

    # Plan selection
    plan = plan_var.get()
    months = {"3-month": 3, "6-month": 6, "9-month": 9, "12-month": 12}[plan]

    plan_total_cigs = monthly * months
    plan_total_cost = plan_total_cigs * cost_per_cig

    # Reduction schedule
    reduction_map = {
        "3-month": 0.25,
        "6-month": 0.40,
        "9-month": 0.60,
        "12-month": 0.80
    }

    target_daily = daily * (1 - reduction_map[plan])
    target_weekly = target_daily * 7
    target_monthly = target_daily * 30

    # Quit date projection
    quit_days = int((daily - target_daily) * 10)  # simple formula
    quit_date = datetime.now() + timedelta(days=quit_days)

    # Update labels
    weekly_label.config(text=f"Weekly Total: {weekly:.1f}")
    monthly_label.config(text=f"Monthly Total: {monthly:.1f}")

    daily_cost_label.config(text=f"Daily Cost: ${daily_cost:.2f}")
    weekly_cost_label.config(text=f"Weekly Cost: ${weekly_cost:.2f}")
    monthly_cost_label.config(text=f"Monthly Cost: ${monthly_cost:.2f}")

    plan_label.config(text=f"{plan} Total Cigarettes: {plan_total_cigs:.1f}")
    plan_cost_label.config(text=f"{plan} Total Cost: ${plan_total_cost:.2f}")

    target_daily_label.config(text=f"Target Daily: {target_daily:.1f}")
    target_weekly_label.config(text=f"Target Weekly: {target_weekly:.1f}")
    target_monthly_label.config(text=f"Target Monthly: {target_monthly:.1f}")

    quit_label.config(text=f"Projected Quit Date: {quit_date.strftime('%Y-%m-%d')}")

# ------------------------------
# GUI
# ------------------------------

root = tk.Tk()
root.title("Year, Quit Smoking, Planning Calculator")
root.geometry("450x700")

# Daily cigarettes
tk.Label(root, text="Daily Cigarettes:", font=("Arial", 16)).pack(pady=5)
entry_daily = tk.Entry(root, font=("Arial", 16))
entry_daily.pack(pady=5)

# Pack price
tk.Label(root, text="Price per Pack ($):", font=("Arial", 16)).pack(pady=5)
entry_price = tk.Entry(root, font=("Arial", 16))
entry_price.pack(pady=5)

# Cigarettes per pack
tk.Label(root, text="Cigarettes per Pack:", font=("Arial", 16)).pack(pady=5)
entry_pack = tk.Entry(root, font=("Arial", 16))
entry_pack.pack(pady=5)

# Plan selector
tk.Label(root, text="Choose Reduction Plan:", font=("Arial", 16)).pack(pady=10)
plan_var = tk.StringVar(value="3-month")
plan_box = ttk.Combobox(root, textvariable=plan_var,
                        values=["3-month", "6-month", "9-month", "12-month"])
plan_box.pack()

# Calculate button
tk.Button(root, text="Calculate", font=("Arial", 16),
          command=calculate).pack(pady=20)

# Output labels
weekly_label = tk.Label(root, font=("Arial", 14))
weekly_label.pack()

monthly_label = tk.Label(root, font=("Arial", 14))
monthly_label.pack()

daily_cost_label = tk.Label(root, font=("Arial", 14))
daily_cost_label.pack()

weekly_cost_label = tk.Label(root, font=("Arial", 14))
weekly_cost_label.pack()

monthly_cost_label = tk.Label(root, font=("Arial", 14))
monthly_cost_label.pack()

plan_label = tk.Label(root, font=("Arial", 14))
plan_label.pack()

plan_cost_label = tk.Label(root, font=("Arial", 14))
plan_cost_label.pack()

target_daily_label = tk.Label(root, font=("Arial", 14))
target_daily_label.pack()

target_weekly_label = tk.Label(root, font=("Arial", 14))
target_weekly_label.pack()

target_monthly_label = tk.Label(root, font=("Arial", 14))
target_monthly_label.pack()

quit_label = tk.Label(root, font=("Arial", 16, "bold"))
quit_label.pack(pady=20)

root.mainloop()
