
import tkinter as tk
from tkinter import ttk, messagebox
import db
import platform
from admin_console_ui import (
    render_profile_form,
    clear_frame,
    show_missing_profile_options,
    create_empty_recruiter_profile,
    create_blank_talent_form
)
from admin_notes_and_applications import (
    show_talent_applications,
    render_admin_notes
)

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ScoutJar Admin Console")
        self.env = tk.StringVar(value="local")
        self.env.trace("w", self.on_env_change)
        self.target_type = tk.StringVar(value="User Profiles")
        self.selected_user_id = None
        self.record_type = None
        self.current_data = {}

        system = platform.system()
        if system == "Windows":
            try:
                self.root.state("zoomed")
            except:
                self.maximize_fallback()
        else:
            self.maximize_fallback()

        self.setup_ui()

    def maximize_fallback(self):
        self.root.update_idletasks()
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        self.root.geometry(f"{width}x{height}+0+0")

    def setup_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Label(top_frame, text="Environment:").pack(side=tk.LEFT)
        env_menu = ttk.Combobox(top_frame, textvariable=self.env, values=["local", "production"], width=15)
        env_menu.pack(side=tk.LEFT, padx=5)

        tk.Label(top_frame, text="Target:").pack(side=tk.LEFT, padx=(20, 0))
        target_menu = ttk.Combobox(top_frame, textvariable=self.target_type, values=["Talent", "Recruiter", "User Profiles"], width=15)
        target_menu.pack(side=tk.LEFT, padx=5)

        tk.Label(top_frame, text="Search:").pack(side=tk.LEFT, padx=(20, 0))
        self.query_entry = tk.Entry(top_frame, width=40)
        self.query_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(top_frame, text="Search", command=self.search_records).pack(side=tk.LEFT, padx=10)

        self.env_label = tk.Label(self.root, text=f"🔍 Showing results from: {self.env.get().upper()}", fg="blue")
        self.env_label.pack()

        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(tree_frame, show='headings')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        hsb = ttk.Scrollbar(self.root, orient="horizontal", command=self.tree.xview)
        hsb.pack(fill="x")
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.edit_frame = tk.Frame(self.bottom_frame)
        self.edit_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.right_pane = tk.Frame(self.bottom_frame)
        self.right_pane.pack(side=tk.RIGHT, fill=tk.Y)

        self.form_fields = {}
        tk.Button(self.root, text="Save Changes", command=self.save_changes).pack(pady=(0, 10))

    def on_env_change(self, *args):
        self.tree.delete(*self.tree.get_children())
        self.env_label.config(text=f"🔍 Showing results from: {self.env.get().upper()}")

    def animate_running_man(self):
        try:
            self.running_image = tk.PhotoImage(file="running_man.png")
            if hasattr(self, 'runner_label') and self.runner_label:
                self.runner_label.destroy()
            self.runner_label = tk.Label(self.root, image=self.running_image, bd=0)
            self.runner_label.place(x=0, y=60)
            self.root.update()

            def move():
                x = 0
                while x < self.root.winfo_width() - 100:
                    self.runner_label.place(x=x, y=60)
                    self.root.update_idletasks()
                    self.root.after(5)
                    x += 10
                self.runner_label.destroy()

            self.root.after(0, move)
        except Exception as e:
            print("Animation error:", e)

    def search_records(self):
        self.animate_running_man()
        query = self.query_entry.get().strip()
        if not query:
            return

        try:
            conn = db.get_connection(self.env.get())
            cur = conn.cursor()
            target = self.target_type.get().lower()

            cur.execute("SELECT user_id FROM user_profiles WHERE email ILIKE %s", (f"%{query}%",))
            email_matches = [str(row[0]) for row in cur.fetchall()]
            search_ids = tuple(set(email_matches + [query]))

            if target == "talent":
                cur.execute("""
                    SELECT * FROM talent_profiles
                    WHERE CAST(user_id AS TEXT) ILIKE %s
                       OR CAST(talent_id AS TEXT) ILIKE %s
                       OR user_id IN %s
                    LIMIT 10
                """, (f"%{query}%", f"%{query}%", search_ids))

            elif target == "recruiter":
                cur.execute("""
                    SELECT * FROM talent_recruiters
                    WHERE CAST(user_id AS TEXT) ILIKE %s
                       OR CAST(recruiter_id AS TEXT) ILIKE %s
                       OR user_id IN %s
                    LIMIT 10
                """, (f"%{query}%", f"%{query}%", search_ids))

            else:
                cur.execute("""
                    SELECT * FROM user_profiles
                    WHERE CAST(user_id AS TEXT) ILIKE %s
                       OR email ILIKE %s
                    LIMIT 10
                """, (f"%{query}%", f"%{query}%"))

            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            self.display_result(target, colnames, rows)

            cur.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_result(self, section, columns, rows):
        self.tree.delete(*self.tree.get_children())
        if not rows:
            self.tree["columns"] = ["Info"]
            self.tree.heading("Info", text="Info")
            self.tree.insert("", "end", values=["No results found."])
            return
        self.tree["columns"] = ["Section"] + columns
        for col in ["Section"] + columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="w", stretch=True)
        for row in rows:
            self.tree.insert("", "end", values=[section] + list(row))

    def on_row_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, 'values')
        if not values or len(values) < 2:
            return

        columns = self.tree["columns"]
        try:
            if "user_id" in columns:
                idx = columns.index("user_id")
                user_id = int(values[idx])
                self.load_specific_profile(user_id)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_specific_profile(self, user_id):
        self.selected_user_id = user_id
        self.current_data = {}
        clear_frame(self.edit_frame)
        clear_frame(self.right_pane)
        self.form_fields.clear()

        try:
            conn = db.get_connection(self.env.get())
            cur = conn.cursor()

            cur.execute("SELECT * FROM talent_profiles WHERE user_id = %s", (user_id,))
            talent_row = cur.fetchone()
            if talent_row:
                self.record_type = "talent"
                talent_cols = [desc[0] for desc in cur.description]
                self.current_data["talent_profiles"] = dict(zip(talent_cols, talent_row))
                render_profile_form("Talent Profile", self.current_data["talent_profiles"], self.edit_frame, self.form_fields, "green")
                show_talent_applications(user_id, self.right_pane)
                render_admin_notes(user_id, self.right_pane)
                return

            cur.execute("SELECT * FROM talent_recruiters WHERE user_id = %s", (user_id,))
            recruiter_row = cur.fetchone()
            if recruiter_row:
                self.record_type = "recruiter"
                recruiter_cols = [desc[0] for desc in cur.description]
                self.current_data["talent_recruiters"] = dict(zip(recruiter_cols, recruiter_row))
                render_profile_form("Recruiter Profile", self.current_data["talent_recruiters"], self.edit_frame, self.form_fields, "blue")
                render_admin_notes(user_id, self.right_pane)
                return

            show_missing_profile_options(
                user_id, self.edit_frame,
                on_create_talent=self._create_talent_and_reload,
                on_create_recruiter=self._create_recruiter_and_reload
            )
            render_admin_notes(user_id, self.right_pane)

            cur.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load record: {str(e)}")

    def save_changes(self):
        if not self.record_type or not self.form_fields:
            messagebox.showwarning("No Record", "No record loaded to save.")
            return

        table = "talent_profiles" if self.record_type == "talent" else "talent_recruiters"
        id_field = "talent_id" if self.record_type == "talent" else "recruiter_id"

        # Optional: add known enum choices
        valid_availability = {"available", "unavailable", "immediately", "later"}
        valid_profile_modes = {"active", "passive"}
        valid_employment_types = {"Fulltime", "Parttime", "Contract", "Freelance"}

        data = {}
        for field, entry in self.form_fields.items():
            col_name = field.split(":", 1)[1] if ":" in field else field
            value = entry.get()

            if value == "":
                data[col_name] = None
            elif col_name in ["skills", "industry_experience"]:
                data[col_name] = [v.strip() for v in value.split(",") if v.strip()]
            elif col_name in ["job_alerts_enabled", "requires_two_weeks_notice"]:
                data[col_name] = value.lower() in ["true", "yes", "1"]
            elif col_name == "time_availability":
                data[col_name] = value if value.strip() else "{}"
            elif col_name == "availability":
                value_norm = value.strip().lower()
                if value_norm not in valid_availability:
                    messagebox.showerror("Invalid availability", f"'{value}' is not one of {', '.join(valid_availability)}")
                    return
                data[col_name] = value_norm
            elif col_name == "profile_mode":
                value_norm = value.strip().lower()
                data[col_name] = value_norm if value_norm in valid_profile_modes else "active"

            elif col_name == "employment_type":
                value_norm = value.strip().capitalize()
                data[col_name] = value_norm if value_norm in valid_employment_types else "Fulltime"
            else:
                data[col_name] = value

        try:
            conn = db.get_connection(self.env.get())
            cur = conn.cursor()

            if not data.get(id_field):  # INSERT
                cols = list(data.keys())
                vals = [data[col] for col in cols]
                placeholders = ", ".join(["%s"] * len(cols))
                query = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
                # ✅ Add this debug print
                print("\n-- DEBUG: SQL INSERT --")
                print("Table:", table)
                print("Query:", query)
                print("Values:", vals)
                print("-- END DEBUG --\n")
                cur.execute(query, vals)
                conn.commit()
                messagebox.showinfo("Inserted", f"{self.record_type.capitalize()} profile created.")
            else:  # UPDATE
                record_id = data[id_field]
                updates = ", ".join([f"{col} = %s" for col in data if col != id_field])
                values = [data[col] for col in data if col != id_field]
                query = f"UPDATE {table} SET {updates} WHERE {id_field} = %s"
                print("\n-- DEBUG: SQL UPDATE --")
                print("Table:", table)
                print("Query:", query)
                print("Values:", values + [record_id])
                print("-- END DEBUG --\n")
                cur.execute(query, values + [record_id])
                conn.commit()
                messagebox.showinfo("Saved", f"{self.record_type.capitalize()} profile saved successfully.")

            cur.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
            
        
   
    def _create_talent_and_reload(self, user_id):
        self.record_type = "talent"
        self.selected_user_id = user_id
        self.current_data = {}
        clear_frame(self.edit_frame)
        clear_frame(self.right_pane)
        self.form_fields.clear()

        create_blank_talent_form(user_id, self.edit_frame, self.form_fields)


    def _create_recruiter_and_reload(self, user_id):
        create_empty_recruiter_profile(user_id)
        self.load_specific_profile(user_id)

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()
