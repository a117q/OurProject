import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib # MODIFICATION: Added for SHA256 password verification

from DataCenter import DataCenter
from admin_window import AdminsWindow
# from StudentWalletWindow import StudentWalletWindow # Note: Student Wallet Window must be imported here when ready

class LogIn:
    # MODIFICATION: Changed initialization to accept 'root' (main window) and callbacks
    def __init__(self, root, show_signup_window, show_student_cb, show_admin_cb):
        self.root = root  # Use MainApp's root window for integration
        self.dc = DataCenter()
        self.show_signup_window = show_signup_window
        self.show_student_cb = show_student_cb
        self.show_admin_cb = show_admin_cb

        # ERROR (Original design assumed LogIn creates its own window):
        # self.window = tk.Tk() 
        
        self.root.title("KSU Wallet - Log In")
        self.root.configure(bg="#B7D4FF")
        self.root.geometry('600x400')
        
        self.create_widgets()

    def create_widgets(self):
        # Use a main frame built on root for clean structure
        main_frame = tk.Frame(self.root, padx=20, pady=20, bg="#B7D4FF") 
        main_frame.pack(expand=True, fill='both')

        # ERROR: Widgets originally built on 'self.window'. MODIFICATION: Building on 'main_frame'/'self.root'
        
        self.L1 = tk.Label(main_frame, text='Log in Window', fg="black", bg="#B7D4FF")
        self.L1.pack(pady=20)
        
        self.L2 = tk.Label(main_frame, text="Enter Your ID: ", fg="black", bg="#B7D4FF")
        self.L2.pack(pady=10)
        
        self.id_entry = tk.Entry(main_frame, fg="black", bg="#F0F0F0") # Changed bg color for visibility
        self.id_entry.pack(pady=5)
        
        self.L3 = tk.Label(main_frame, text="Enter Your Password: ", fg="black", bg="#B7D4FF")
        self.L3.pack(pady=10)
        
        self.password_entry = tk.Entry(main_frame, fg="black", bg="#F0F0F0", show="*")
        self.password_entry.pack(pady=5)
        
        self.show_var = tk.IntVar()
        self.show_check = tk.Checkbutton(main_frame, text="Show Password", bg="#B7D4FF",
                                            variable=self.show_var, command=self.toggle_password)
        self.show_check.pack(pady=5)
        
        self.B1 = tk.Button(main_frame, text='Log In', fg='black', bg="#F0F0F0", command=self.action)
        self.B1.pack(pady=20)
        
        # MODIFICATION: Add 'Go to Signup' button for navigation consistency
        tk.Button(main_frame, text="Go to Sign Up", command=self.show_signup_window, bg="#B7D4FF").pack(pady=10)
        
        # ERROR: Original code had window.mainloop() here which blocks execution
        # self.window.mainloop() 


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

        if not (id_text.isdigit() and len(id_text) == 10):
            messagebox.showerror("Error", "ID must contain exactly 10 digits.")
            return

        student_id = int(id_text)
        
        # MODIFICATION: HASH the input password using SHA256 for security comparison
        h_pwd = hashlib.sha256(password.encode('utf-8')).hexdigest()

        try:
            cur = self.dc.cur

            # ERROR: Original query was likely flawed (checking for 'role' and using plain password)
            # MODIFICATION: Use HASHED password to check Students table
            cur.execute(
                "SELECT wallet_id FROM Students WHERE Student_ID = ? AND password = ?",
                (student_id, h_pwd) # Use h_pwd for secure check
            )
            student_wallet_id = cur.fetchone()

            # MODIFICATION: Example Admin check (replace with actual DB check if needed)
            is_admin = (student_id == 1111111111 and password == "admin123") # Example Admin Check

            if is_admin:
                messagebox.showinfo("Success", "Login successful (Admin).")
                self.show_admin_cb()
            elif student_wallet_id:
                messagebox.showinfo("Success", "Login successful (Student).")
                self.show_student_cb(student_id)
            else:
                # Check if ID exists to give more specific error
                cur.execute(
                    "SELECT 1 FROM Students WHERE Student_ID = ?",
                    (student_id,)
                )
                if cur.fetchone():
                    messagebox.showerror("Error", "Incorrect password.")
                else:
                    messagebox.showerror("Error", "There is no account with this ID.")
        
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Database error:\n{e}")
            
    # ERROR: Original LogIn.py contained open_admin_window and open_student_window methods. 
    # MODIFICATION: These are redundant as MainApp handles window navigation via callbacks.
    # self.open_admin_window() should be replaced with self.show_admin_cb()
    # self.open_student_window(student_id) should be replaced with self.show_student_cb(student_id)
    # The redundant methods were removed, and logic was streamlined to use callbacks.

    def action(self):
        self.check_login()

# ERROR (Original design executed the file upon import):
# Login = LogIn() # This line was outside the class and caused auto-execution