# This file will hold modular functions and refactored UI components

import tkinter as tk
from tkinter import messagebox
import db

READ_ONLY_FIELDS = ["user_id", "email", "talent_id", "recruiter_id"]


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def render_profile_form(section, data, parent_frame, form_fields, color):
    row = tk.Label(parent_frame, text=f"{section}:", fg=color, font=('Arial', 10, 'bold'))
    row.grid(row=len(form_fields), column=0, columnspan=2, sticky="w", pady=(10, 0))

    for i, (key, value) in enumerate(data.items()):
        label = tk.Label(parent_frame, text=key)
        label.grid(row=len(form_fields) + i + 1, column=0, sticky="e", padx=(0, 10))

        entry = tk.Entry(parent_frame, width=50)
        entry.insert(0, str(value))
        if key in READ_ONLY_FIELDS:
            entry.config(state='readonly')

        entry.grid(row=len(form_fields) + i + 1, column=1, sticky="w")
        form_fields[f"{section}:{key}"] = entry


def show_missing_profile_options(user_id, parent_frame, on_create_talent, on_create_recruiter):
    label = tk.Label(parent_frame, text=f"User ID {user_id} has no talent or recruiter profile.",
                     fg="red", font=('Arial', 10, 'italic'))
    label.pack(pady=(5, 0))

    button_frame = tk.Frame(parent_frame)
    button_frame.pack(pady=5)

    tk.Button(button_frame, text="Create Talent Profile", command=lambda: on_create_talent(user_id)).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Create Recruiter Profile", command=lambda: on_create_recruiter(user_id)).pack(side=tk.LEFT, padx=10)


def create_empty_talent_profile(user_id):
    try:
        conn = db.get_connection("local")
        cur = conn.cursor()
        cur.execute("INSERT INTO talent_profiles (user_id) VALUES (%s)", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("Created", "Empty talent profile created.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


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
