import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib 
from DataCenter import DataCenter

class LogIn:
    def __init__(self, root, show_signup_window, show_student_cb, show_admin_cb, is_admin_mode= False ):
        self.root = root  
        self.dc = DataCenter()
        self.show_signup_window = show_signup_window
        self.show_student_cb = show_student_cb
        self.show_admin_cb = show_admin_cb

        self.is_admin_mode = is_admin_mode
      
        
        self.root.title("KSU Wallet - Log In")
        self.root.configure(bg="#B7D4FF")
        self.root.geometry('550x550')
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, padx=20, pady=20, bg="#B7D4FF") 
        main_frame.pack(expand=True, fill='both')

        
        self.L1 = tk.Label(main_frame, text='Log in Window', fg="black", bg="#B7D4FF")
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
        self.show_check = tk.Checkbutton(main_frame, text="Show Password", bg="#B7D4FF",
                                            variable=self.show_var, command=self.toggle_password)
        self.show_check.pack(pady=5)
        
        self.B1 = tk.Button(main_frame, text='Log In', fg='black', bg="#F0F0F0", command=self.action)
        self.B1.pack(pady=20)
        
        

        #-------------------------------------------------------------------------

        if self.is_admin_mode:
            button_text = "← Back to Role Selection"
        else:
            button_text = "Don't have an account? Back to Sign Up"
        
        tk.Button(
            main_frame,
            text=button_text,
            command=self.show_signup_window, 
            bg="#B7D4FF",
            ).pack(pady=10)

            #---------------------------------------------------------------------------------


    def toggle_password(self):
        if self.show_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def check_login(self):
        id_text = self.id_entry.get().strip()
        password = self.password_entry.get()

        # 1. التحقق الأساسي من وجود المدخلات
        if not id_text or not password:
            messagebox.showwarning("Error", "Please enter both ID and password.")
            return

        # التحقق من أن الهوية تتكون من 10 أرقام
        if not (id_text.isdigit() and len(id_text) == 10):
            messagebox.showerror("Error", "ID must contain exactly 10 digits.")
            return

        # تحويل الهوية إلى رقم صحيح (لاستخدامه في التحقق)
        student_id = int(id_text) 
        
        # ==========================================================
        # 2. التحقق من المسؤول (ADMIN CHECK) - باستخدام البيانات الثابتة
        # ==========================================================
        
        # ID المسؤول (0123456789 يُقرأ في بايثون كـ 1234567890 كرقم صحيح)
        ADMIN_ID_INT = 1234567890 
        ADMIN_PASS = "aa223344"
        
        if student_id == ADMIN_ID_INT and password == ADMIN_PASS:
            messagebox.showinfo("Success", "Login successful (Admin).")
            self.show_admin_cb() # الانتقال لواجهة المشرف
            return # إنهاء الدالة بعد دخول المسؤول بنجاح
        
        # ==========================================================
        # 3. تشفير كلمة المرور للتحقق من الطالب (STUDENT CHECK)
        # ==========================================================
        try:
            h_pwd = hashlib.sha256(password.encode('utf-8')).hexdigest()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during password hashing: {e}")
            return
            
        try:
            cur = self.dc.cur
        
            # التحقق من الطالب في جدول Students
            cur.execute(
            "SELECT wallet_id FROM Students WHERE Student_ID = ? AND password = ?",
            (student_id, h_pwd)
            )
            student_wallet_id = cur.fetchone()

            if student_wallet_id:
                messagebox.showinfo("Success", "Login successful (Student).")
                self.show_student_cb(student_id)
            else:
                # 4. معالجة فشل تسجيل الدخول
            
                # التحقق مما إذا كانت الهوية موجودة كطالب (لإعطاء رسالة خطأ أدق)
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
            
    
    def action(self):
        self.check_login()
"""""ة
    def check_login(self):
        id_text = self.id_entry.get().strip()
        password = self.password_entry.get()

        student_id = id_text 

        try:
            h_pwd = hashlib.sha256(password.encode('utf-8')).hexdigest()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during password hashing: {e}")
            return

        try:
            cur = self.dc.cur
        
            # ==========================================================
            # 2. التحقق من المشرف (ADMIN CHECK) - البحث في جدول Managers
            # ==========================================================
            # يجب أن تستخدمي check_manager_login التي أضفناها في DataCenter.py
            if self.dc.check_manager_login(student_id, h_pwd):
                 messagebox.showinfo("Success", "Login successful (Admin).")
                 self.show_admin_cb() # الانتقال لواجهة المشرف
                 return # إنهاء الدالة
        
            # ==========================================================
            # 3. التحقق من الطالب (STUDENT CHECK) - البحث في جدول Students
            # ==========================================================
            # استبدال المنطق القديم للتحقق من الطالب:
            cur.execute(
            "SELECT wallet_id FROM Students WHERE Student_ID = ? AND password = ?",
            (student_id, h_pwd)
            )
            student_wallet_id = cur.fetchone()

            if student_wallet_id:
                messagebox.showinfo("Success", "Login successful (Student).")
                self.show_student_cb(student_id)
            else:
                # 4. معالجة فشل تسجيل الدخول
            
                # التحقق مما إذا كانت الهوية موجودة (سواء طالب أو مشرف لم ينجحا)
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
            
    
    def action(self):
        self.check_login()
"""""