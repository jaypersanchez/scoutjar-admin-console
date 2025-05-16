import tkinter as tk
from tkinter import ttk, messagebox
import db
import platform

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ScoutJar Admin Console")
        self.env = tk.StringVar(value="local")

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

        tk.Label(top_frame, text="Search:").pack(side=tk.LEFT, padx=(20, 0))
        self.query_entry = tk.Entry(top_frame, width=50)
        self.query_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(top_frame, text="Search", command=self.search_user).pack(side=tk.LEFT, padx=10)

        self.tree = ttk.Treeview(self.root, columns=("Section", "Data"), show='headings')
        self.tree.heading("Section", text="Section")
        self.tree.heading("Data", text="Data")
        self.tree.column("Section", width=150, anchor="w")
        self.tree.column("Data", anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        vsb = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

    def search_user(self):
        query = self.query_entry.get().strip()
        if not query:
            return

        self.tree.delete(*self.tree.get_children())

        try:
            conn = db.get_connection(self.env.get())
            cur = conn.cursor()

            # Search candidates
            cur.execute("""
                SELECT * FROM user_profiles 
                WHERE CAST(user_id AS TEXT) ILIKE %s OR email ILIKE %s
                LIMIT 1
            """, (f"%{query}%", f"%{query}%"))
            user = cur.fetchone()

            if not user:
                self.tree.insert("", "end", values=("Result", "No matching user found."))
                return

            user_id = user[0]
            self.tree.insert("", "end", values=("user_profiles", str(user)))

            # Get talent profile
            cur.execute("SELECT * FROM talent_profiles WHERE CAST(user_id AS TEXT) ILIKE %s OR CAST(talent_id AS TEXT) ILIKE %s LIMIT 1", (f"%{query}%", f"%{query}%"))
            talent = cur.fetchone()
            self.tree.insert("", "end", values=("talent_profiles", str(talent) if talent else "None"))

            # Get recruiter
            cur.execute("SELECT * FROM talent_recruiters WHERE CAST(user_id AS TEXT) ILIKE %s LIMIT 1", (f"%{query}%",))
            recruiter = cur.fetchone()
            self.tree.insert("", "end", values=("talent_recruiters", str(recruiter) if recruiter else "None"))

            # Get job applications
            cur.execute("SELECT * FROM job_applications WHERE CAST(talent_id AS TEXT) ILIKE %s OR CAST(recruiter_id AS TEXT) ILIKE %s LIMIT 5", (f"%{query}%", f"%{query}%"))
            apps = cur.fetchall()
            self.tree.insert("", "end", values=("job_applications (sample)", str(apps) if apps else "[]"))

            cur.close()
            conn.close()

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminApp(root)
    root.mainloop()