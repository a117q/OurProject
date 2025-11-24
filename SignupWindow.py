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

        # Apply the consistent background color and title
        self.root.title("KSU Wallet - Sign Up")
        self.root.configure(bg="#B7D4FF") 
        self.root.geometry('600x650') # Slightly increased size to fit new field

        self.create_widgets()
    
    def create_widgets(self):
        # Main Frame centered, using Grid geometry manager
        main_frame = tk.Frame(self.root, padx=30, pady=30, bg="#B7D4FF") 
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Title Label
        tk.Label(main_frame, text="Student Registration (Sign Up)", 
                 font=("Arial", 16, "bold"), bg="#B7D4FF").grid(row=0, column=0, columnspan=2, pady=15)

        field_labels = {
            "FName": "First Name:", 
            "LName": "Last Name:", 
            "SID": "Student ID:", 
            "Email": "Email:", 
            "PhoneNo": "Phone Number:", 
            "PWD": "Password:",
            "CPWD": "Confirm Password:", 
        }

        self.fields = {}
        row_counter = 1
        
        # 1. Use Grid to organize labels and entry fields
        for key, label_text in field_labels.items():
            
            tk.Label(main_frame, text=label_text, bg="#B7D4FF").grid(row=row_counter, column=0, sticky='w', pady=5, padx=10)
            
            entry = tk.Entry(main_frame, width=35)
            entry.grid(row=row_counter, column=1, sticky='ew', pady=5, padx=10)
            self.fields[key] = entry
            row_counter += 1

        # Hide password and confirm password fields
        self.fields["PWD"].config(show="*")
        self.fields["CPWD"].config(show="*")
        
        # 2. NEW: Show Password Checkbox
        self.show_var = tk.IntVar()
        tk.Checkbutton(main_frame, text="Show Password", bg="#B7D4FF",
                       variable=self.show_var, command=self.toggle_password).grid(row=row_counter, column=1, sticky='w', padx=10)
        row_counter += 1

        # 3. Control Buttons (spans both columns)
        tk.Button(main_frame, text="Submit Registration", command=self.submit_action, 
                  font=("Arial", 12, "bold"), bg="#4CAF50", fg="white").grid(row=row_counter, column=0, columnspan=2, pady=20)
        row_counter += 1
        
        tk.Button(main_frame, text="Already have an account? Go to Login", command=self.login_cb, bg="#B7D4FF").grid(row=row_counter, column=0, columnspan=2, pady=10)


    def toggle_password(self):
        """Toggles the visibility of the Password and Confirm Password fields."""
        if self.show_var.get():
            # If checked (Show)
            self.fields["PWD"].config(show="")
            self.fields["CPWD"].config(show="")
        else:
            # If unchecked (Hide)
            self.fields["PWD"].config(show="*")
            self.fields["CPWD"].config(show="*")


    def validate_inputs(self, data):
        """Validates all inputs using RegEx and basic checks."""
        # Check if passwords match (New Security/UX Check)
        if data['PWD'] != data['CPWD']:
            return False, "Password and Confirm Password do not match."

        # Student ID check: exactly 10 digits
        if not re.search(r'^[0-9]{10}$', data['SID']):
            return False, "Student ID must be exactly 10 digits."

        # Password check: minimum 6 characters
        if not re.search(r'^.{6,}$', data['PWD']):
            return False, "Password must be at least 6 characters."

        # Email check: format XXXXXX@student.ksu.edu.sa
        email_pattern = r'^[a-zA-Z0-9._-]+@student\.ksu\.edu\.sa$'
        if not re.search(email_pattern, data['Email']):
            return False, "Email must be in the format: XXXXXX@student.ksu.edu.sa"

        # Phone number check: 05XXXXXXXX (10 digits starting with 05)
        phone_pattern = r'^05[0-9]{8}$'
        if not re.search(phone_pattern, data['PhoneNo']):
            return False, "Phone Number must be in the format: 05XXXXXXXX (10 digits)."
            
        return True, "Success"

    def submit_action(self):
        """Handles submission, validation, hashing, and database insertion."""
        data = {key: entry.get().strip() for key, entry in self.fields.items()}
        
        # Check for empty fields
        if any(not val for val in data.values()):
            messagebox.showerror("Error", "All fields are required.")
            return

        valid, err_msg = self.validate_inputs(data)
        
        if not valid:
            messagebox.showerror("Validation Error", err_msg)
            return

        std_id = int(data['SID'])
        pwd = data['PWD']

        # Check for ID duplication using DataCenter helper method
        if self.dc.check_student_id_exists(std_id):
            messagebox.showerror("Error", f"Student ID {std_id} is already registered.")
            return

        # Security: SHA256 Hashing (Lecture #10)
        h_pwd = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
        
        # Initial Balance (Business Requirement)
        init_bal = 1000.0
        
        try:
            # Database Insertion (via DataCenter helper method)
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
            
            # Navigation to Login screen
            self.login_cb()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"An error occurred during registration:\n{e}")