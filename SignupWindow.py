import tkinter as tk
from tkinter import messagebox
import re
import hashlib
import random
from datetime import datetime
from DataCenter import DataCenter

class SignupWindow:
    def __init__(self, root, login_cb):
        self.root = root
        self.dc = DataCenter()
        self.login_cb = login_cb

        self.root.title("KSU Wallet - Sign Up")
        self.root.geometry('600x600')

        self.create_widgets()
    
    def create_widgets(self):
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        tk.Label(main_frame, text="Student Registration (Sign Up)", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

        field_labels = {
            "FName": "First Name:", 
            "LName": "Last Name:", 
            "SID": "Student ID (10 digits):", 
            "Email": "Email (@student.ksu.edu.sa):", 
            "PhoneNo": "Phone Number (05XXXXXXXX):", 
            "PWD": "Password (6+ chars):"
        }

        self.fields = {}
        row_counter = 1
        
        for key, label_text in field_labels.items():
            tk.Label(main_frame, text=label_text).grid(row=row_counter, column=0, sticky='w', pady=5, padx=10)
            entry = tk.Entry(main_frame, width=40)
            entry.grid(row=row_counter, column=1, pady=5, padx=10)
            self.fields[key] = entry
            row_counter += 1

        self.fields["PWD"].config(show="*")

        tk.Button(main_frame, text="Submit Registration", command=self.submit_action, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white").grid(row=row_counter, column=0, columnspan=2, pady=20)
        row_counter += 1
        
        tk.Button(main_frame, text="Already have an account? Go to Login", command=self.login_cb).grid(row=row_counter, column=0, columnspan=2, pady=10)

    def validate_inputs(self, data):
        if not re.search(r'^[0-9]{10}$', data['SID']):
            return False, "Student ID must be exactly 10 digits."

        if not re.search(r'^.{6,}$', data['PWD']):
            return False, "Password must be at least 6 characters."

        email_pattern = r'^[a-zA-Z0-9._-]+@student\.ksu\.edu\.sa$'
        if not re.search(email_pattern, data['Email']):
            return False, "Email must be in the format: XXXXXX@student.ksu.edu.sa"

        phone_pattern = r'^05[0-9]{8}$'
        if not re.search(phone_pattern, data['PhoneNo']):
            return False, "Phone Number must be in the format: 05XXXXXXXX (10 digits)."
            
        return True, "Success"

    def submit_action(self):
        data = {key: entry.get().strip() for key, entry in self.fields.items()}
        
        if any(not val for val in data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return

        valid, err_msg = self.validate_inputs(data)
        
        if not valid:
            messagebox.showerror("Validation Error", err_msg)
            return

        std_id = int(data['SID'])
        pwd = data['PWD']

        if self.dc.check_student_id_exists(std_id):
            messagebox.showerror("Error", f"Student ID {std_id} is already registered.")
            return

        h_pwd = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
        
        init_bal = 1000.0
        
        try:
            self.dc.add_student_and_wallet(
                student_id=std_id,
                first_name=data['FName'],
                last_name=data['LName'],
                email=data['Email'],
                phone_no=int(data['PhoneNo']),
                hashed_password=h_pwd,
                initial_balance=init_bal
            )
            
            messagebox.showinfo("Success", "Registration Complete!\nYou can now log in.")
            
            self.login_cb()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred during registration:\n{e}")