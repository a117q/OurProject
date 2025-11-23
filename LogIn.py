from DataCenter import DataCenter
from admin_window import AdminsWindow
#from StudentWalletWindow import StudentWalletWindow
import tkinter as tk
from tkinter import messagebox
import sqlite3

class LogIn:
    def __init__(self):
        self.dc = DataCenter()

        self.window = tk.Tk()
        self.window.title("KSU Wallet - Log In")
        self.window.configure(bg="#B7D4FF")
        self.window.geometry('600x400')
        
        self.L1 = tk.Label(self.window, text='Log in Window', fg="black", bg="#B7D4FF")
        self.L1.pack(pady=20)
        
        self.L2 = tk.Label(self.window, text="Enter Your ID: ", fg="black", bg="#B7D4FF")
        self.L2.pack(pady=10)
        
        self.id_entry = tk.Entry(self.window, fg="white", bg="#9D9D9D")
        self.id_entry.pack(pady=5)
        
        self.L3 = tk.Label(self.window, text="Enter Your Password: ", fg="black", bg="#B7D4FF")
        self.L3.pack(pady=10)
        
        self.password_entry = tk.Entry(self.window, fg="white", bg="#9D9D9D", show="*")
        self.password_entry.pack(pady=5)
        
        self.show_var = tk.IntVar()
        self.show_check = tk.Checkbutton(self.window, text="Show Password", bg="#B7D4FF",
                                            variable=self.show_var, command=self.toggle_password)
        self.show_check.pack(pady=5)
        
        self.B1 = tk.Button(self.window, text='Log In', fg='black', bg="#B7D4FF", command=self.action)
        self.B1.pack(pady=20)
        
        self.window.mainloop()

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

        try:
            cur = self.dc.cur

            role = None
            for row in cur.execute(
                "SELECT role FROM Students WHERE Student_ID = ? AND password = ?",
                (student_id, password)
            ):
                role = row[0]
                break

            if role is None:
                id_exists = False
                for _ in cur.execute(
                    "SELECT 1 FROM Students WHERE Student_ID = ?",
                    (student_id,)
                ):
                    id_exists = True
                    break

                if id_exists:
                    messagebox.showerror("Error", "Incorrect password.")
                else:
                    messagebox.showerror("Error", "There is no account with this ID.")
                return

            if role == "manager":
                messagebox.showinfo("Success", "Login successful (Manager).")
                self.open_admin_window()
            elif role == "student":
                messagebox.showinfo("Success", "Login successful (Student).")
                self.open_student_window(student_id)
            else:
                messagebox.showerror("Error", "Unknown role for this account.")

        except sqlite3.OperationalError as e:
            messagebox.showerror("Database Error", f"Database structure error:\n{e}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Database error:\n{e}")
            
    def open_admin_window(self):
        self.window.destroy()
        AdminsWindow()

    def open_student_window(self, student_id):
        self.window.destroy()
        # StudentWalletWindow(student_id)

    def action(self):
        self.check_login()

Login = LogIn()
