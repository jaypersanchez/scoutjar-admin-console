# Utilities to support:
# 1. Displaying job applications for talents
# 2. Adding and saving admin support notes per user

import tkinter as tk
from tkinter import messagebox
import db

def show_talent_applications(user_id, parent_frame):
    for widget in parent_frame.winfo_children():
        widget.destroy()

    try:
        conn = db.get_connection("local")
        cur = conn.cursor()
        cur.execute("""
            SELECT ja.application_id, ja.job_id, j.title, ja.status, ja.applied_on
            FROM job_applications ja
            JOIN jobs j ON ja.job_id = j.job_id
            WHERE ja.talent_id = %s
        """, (user_id,))

        rows = cur.fetchall()
        if not rows:
            tk.Label(parent_frame, text="No job applications found.", fg="gray").pack()
        else:
            for row in rows:
                tk.Label(parent_frame, text=f"#{row[0]} - Job: {row[1]} - {row[2]} | Status: {row[3]} | Date: {row[4]}", anchor="w").pack(fill=tk.X, padx=10, pady=2)

        cur.close()
        conn.close()
    except Exception as e:
        tk.Label(parent_frame, text=f"Error loading job applications: {str(e)}", fg="red").pack()


def render_admin_notes(user_id, parent_frame):
    for widget in parent_frame.winfo_children():
        widget.destroy()

    tk.Label(parent_frame, text="Admin Support Notes:", font=("Arial", 10, "bold")).pack(anchor="w")
    notes_box = tk.Text(parent_frame, width=80, height=6)
    notes_box.pack(padx=5, pady=5)

    try:
        conn = db.get_connection("local")
        cur = conn.cursor()
        cur.execute("SELECT notes FROM support_notes WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        if row:
            notes_box.insert(tk.END, row[0])
        cur.close()
        conn.close()
    except Exception:
        pass  # Silent fail if table does not exist yet

    def save_notes():
        text = notes_box.get("1.0", tk.END).strip()
        try:
            conn = db.get_connection("local")
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO support_notes (user_id, notes)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE SET notes = EXCLUDED.notes
            """, (user_id, text))
            conn.commit()
            cur.close()
            conn.close()
            messagebox.showinfo("Saved", "Support notes updated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(parent_frame, text="Save Notes", command=save_notes).pack(pady=(0, 5))
