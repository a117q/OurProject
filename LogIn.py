import tkinter as tk
from tkinter import messagebox
import hashlib
from DataCenter import DataCenter

class LogIn:
    def __init__(self, root, show_signup_window, show_student_cb, show_admin_cb, is_admin_mode=False):
        self.root = root
        self.dc = DataCenter()
        
        self.show_signup_window = show_signup_window   # open signup 
        self.show_student_cb = show_student_cb         # when student logs in
        self.show_admin_cb = show_admin_cb             # when manager logs in

        self.is_admin_mode = is_admin_mode

        self.root.title("KSU Wallet - Log In")
        self.root.configure(bg="#B7D4FF")
        self.root.geometry("550x550")

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, padx=20, pady=20, bg="#B7D4FF")
        main_frame.pack(expand=True, fill="both")

        self.L1 = tk.Label(main_frame, text="Log in Window", fg="black", bg="#B7D4FF")
        self.L1.pack(pady=20)

        self.L2 = tk.Label(main_frame, text="Enter Your ID: ", fg="black", bg="#B7D4FF")
        self.L2.pack(pady=10)

        self.id_entry = tk.Entry(main_frame, fg="black", bg="#F0F0F0")
        self.id_entry.pack(pady=5)

        self.L3 = tk.Label(main_frame, text="Enter Your Password: ", fg="black", bg="#B7D4FF")
        self.L3.pack(pady=10)

        self.password_entry = tk.Entry(main_frame, fg="black", bg="#F0F0F0", show="*")
        self.password_entry.pack(pady=5)

        self.show_var = tk.IntVar()
        self.show_check = tk.Checkbutton(
            main_frame,
            text="Show Password",
            bg="#B7D4FF",
            variable=self.show_var,
            command=self.toggle_password
        )
        self.show_check.pack(pady=5)

        self.B1 = tk.Button(
            main_frame,
            text="Log In",
            fg="black",
            bg="#F0F0F0",
            command=self.action
        )
        self.B1.pack(pady=20)

        if self.is_admin_mode:
            button_text = "← Back to Role Selection"
        else:
            button_text = "Don't have an account? Back to Sign Up"

        tk.Button(
            main_frame,
            text=button_text,
            command=self.show_signup_window,
            bg="#B7D4FF"
        ).pack(pady=10)

    #-------------------------------------------------------
    def toggle_password(self):
        if self.show_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
            
    def check_login(self):
        id_text = self.id_entry.get().strip()
        password = self.password_entry.get()

        
        if not id_text or not password:
            messagebox.showwarning("Error", "Please enter both ID and password.")
            return

        # ID must be 10 digits
        if not (id_text.isdigit() and len(id_text) == 10):
            messagebox.showerror("Error", "ID must contain exactly 10 digits.")
            return

        student_id_int = int(id_text)   # for Students table (INT)
        manager_id_str = id_text        # for Managers table (TEXT)

        try:
            h_pwd = hashlib.sha256(password.encode("utf-8")).hexdigest()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during password hashing: {e}")
            return

        # ==========================================================
        # Admin checking
        # ==========================================================
        try:
            if self.dc.check_manager_login(manager_id_str, h_pwd):
                manager_info = self.dc.get_manager_info(manager_id_str)
                if manager_info:
                    full_name = f"{manager_info['first_name']} {manager_info['last_name']}"
                    messagebox.showinfo("Success", f"Login successful (Admin): {full_name}")
                else:
                    messagebox.showinfo("Success", "Login successful (Admin).")

                # ⚠️ IMPORTANT: callback with NO parameters,
                # because MainApp.show_admin_window(self) expects only self.
                self.show_admin_cb()
                return
        except Exception as e:
            messagebox.showerror("Database Error", f"Error checking admin login:\n{e}")
            return

        # ==========================================================
        #Student checking
        # ==========================================================
        try:
            if self.dc.check_student_login(student_id_int, h_pwd):
                messagebox.showinfo("Success", "Login successful (Student).")
                self.show_student_cb(student_id_int)
                return
        except Exception as e:
            messagebox.showerror("Database Error", f"Error checking student login:\n{e}")
            return

        #====================================================
        try:
            if self.dc.check_student_id_exists(student_id_int):
                messagebox.showerror("Error", "Incorrect password.")
            else:
                messagebox.showerror("Error", "There is no account with this ID.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Database error:\n{e}")

    def action(self):
        self.check_login()
