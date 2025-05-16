# Admin tools to show/edit user_credentials and recruiter-created jobs

import tkinter as tk
from tkinter import messagebox
import db

def render_user_credentials(user_id, parent_frame):
    for widget in parent_frame.winfo_children():
        widget.destroy()

    frame = tk.LabelFrame(parent_frame, text="User Credentials", padx=10, pady=10)
    frame.pack(fill=tk.X, pady=10)

    creds = {}
    try:
        conn = db.get_connection("local")
        cur = conn.cursor()
        cur.execute("SELECT user_id, provider, password_hash, last_login FROM user_credentials WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        if not row:
            tk.Label(frame, text="No credentials found.").pack()
            return

        fields = ["user_id", "provider", "password_hash", "last_login"]
        creds = dict(zip(fields, row))

        entries = {}
        for i, (key, value) in enumerate(creds.items()):
            label = tk.Label(frame, text=key)
            label.grid(row=i, column=0, sticky="e", padx=(0, 10))
            entry = tk.Entry(frame, width=40)
            entry.insert(0, str(value))
            if key in ["user_id", "provider", "last_login"]:
                entry.config(state='readonly')
            entry.grid(row=i, column=1, sticky="w")
            entries[key] = entry

        def save_creds():
            new_hash = entries["password_hash"].get().strip()
            try:
                cur.execute("""
                    UPDATE user_credentials SET password_hash = %s
                    WHERE user_id = %s
                """, (new_hash, user_id))
                conn.commit()
                messagebox.showinfo("Saved", "Password hash updated.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(frame, text="Save Password Hash", command=save_creds).grid(row=len(creds)+1, columnspan=2, pady=5)

        cur.close()
        conn.close()

    except Exception as e:
        tk.Label(frame, text=f"Error: {str(e)}", fg="red").pack()


def render_recruiter_jobs(user_id, parent_frame):
    job_frame = tk.LabelFrame(parent_frame, text="Jobs by Recruiter", padx=10, pady=10)
    job_frame.pack(fill=tk.X, pady=10)

    try:
        conn = db.get_connection("local")
        cur = conn.cursor()
        cur.execute("""
            SELECT job_id, title, status, description
            FROM jobs
            WHERE recruiter_id = %s
            LIMIT 10
        """, (user_id,))
        rows = cur.fetchall()

        if not rows:
            tk.Label(job_frame, text="No jobs found.").pack()
            return

        job_entries = []
        for idx, row in enumerate(rows):
            job_id, title, status, desc = row
            tk.Label(job_frame, text=f"Job #{job_id}", font=("Arial", 9, "bold"), fg="blue").grid(row=idx*4, columnspan=2, sticky="w")

            t = tk.Entry(job_frame, width=50); t.insert(0, title)
            s = tk.Entry(job_frame, width=20); s.insert(0, status)
            d = tk.Entry(job_frame, width=70); d.insert(0, desc)

            t.grid(row=idx*4+1, column=0, sticky="w"); s.grid(row=idx*4+1, column=1)
            d.grid(row=idx*4+2, columnspan=2, sticky="w")
            job_entries.append((job_id, t, s, d))

        def save_jobs():
            for job_id, t, s, d in job_entries:
                try:
                    cur.execute("""
                        UPDATE jobs SET title = %s, status = %s, description = %s
                        WHERE job_id = %s
                    """, (t.get(), s.get(), d.get(), job_id))
                except Exception as e:
                    messagebox.showerror("Job Error", f"Failed to update job {job_id}: {str(e)}")
            conn.commit()
            messagebox.showinfo("Saved", "All jobs updated.")

        tk.Button(job_frame, text="Save All Jobs", command=save_jobs).grid(row=len(rows)*4, columnspan=2, pady=10)

        cur.close()
        conn.close()

    except Exception as e:
        tk.Label(job_frame, text=f"Error: {str(e)}", fg="red").pack()
