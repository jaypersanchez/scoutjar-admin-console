import tkinter as tk
from tkinter import messagebox,ttk
import db
from datetime import datetime, date

READ_ONLY_FIELDS = ["user_id", "email", "talent_id", "recruiter_id"]

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def render_profile_form(section, data, parent_frame, form_fields, color):
    clear_frame(parent_frame)

    title_label = tk.Label(parent_frame, text=f"{section} Form", fg=color, font=('Arial', 14, 'bold'))
    title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(10, 10))

    for i, (key, value) in enumerate(data.items(), start=1):
        label = tk.Label(parent_frame, text=key)
        label.grid(row=i, column=0, sticky="e", padx=(0, 10), pady=2)

        # Dropdown configuration
        DROPDOWN_FIELDS = {
            "availability": ["available", "unavailable", "immediately", "later"],
            "employment_type": ["Fulltime", "Parttime", "Contract", "Freelance"],
            "profile_mode": ["active", "passive"]
        }

        field_value = str(value) if value is not None else ""

        if key in DROPDOWN_FIELDS:
            var = tk.StringVar(value=field_value if field_value in DROPDOWN_FIELDS[key] else DROPDOWN_FIELDS[key][0])
            dropdown = ttk.Combobox(parent_frame, textvariable=var, values=DROPDOWN_FIELDS[key], width=57)
            dropdown.grid(row=i, column=1, sticky="w", pady=2)
            form_fields[f"{section}:{key}"] = dropdown
        else:
            entry = tk.Entry(parent_frame, width=60)
            entry.insert(0, field_value)
            if key in READ_ONLY_FIELDS:
                entry.config(state='readonly')
            entry.grid(row=i, column=1, sticky="w", pady=2)
            form_fields[f"{section}:{key}"] = entry


    parent_frame.update_idletasks()

def show_missing_profile_options(user_id, parent_frame, on_create_talent, on_create_recruiter):
    label = tk.Label(parent_frame, text=f"User ID {user_id} has no talent or recruiter profile.",
                     fg="red", font=('Arial', 10, 'italic'))
    label.pack(pady=(5, 0))

    button_frame = tk.Frame(parent_frame)
    button_frame.pack(pady=5)

    tk.Button(button_frame, text="Create Talent Profile", command=lambda: on_create_talent(user_id)).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Create Recruiter Profile", command=lambda: on_create_recruiter(user_id)).pack(side=tk.LEFT, padx=10)

def create_blank_talent_form(user_id, parent_frame, form_fields):
    default_data = {
        "user_id": user_id,
        "desired_salary": "",
        "job_alerts_enabled": True,
        "available_from": str(date.today()),
        "time_availability": '{}',
        "requires_two_weeks_notice": False,
        "years_experience": "",
        "employment_type": "",
        "location": "",
        "industry_experience": "",
        "availability": "available",
        "country": "",
        "country_code": "",
        "profile_mode": "active",
        "resume": "",
        "bio": "",
        "skills": "",
        "experience": "",
        "education": "",
        "work_preferences": ""
    }

    render_profile_form("Talent Profile", default_data, parent_frame, form_fields, "green")

def create_empty_recruiter_profile(user_id):
    try:
        conn = db.get_connection("local")
        cur = conn.cursor()
        cur.execute("INSERT INTO talent_recruiters (user_id) VALUES (%s)", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("Created", "Empty recruiter profile created.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
