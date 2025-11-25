
import tkinter as tk

class selectRole:
    def __init__(self, root, main_app):
        self.root = root
        self.main_app = main_app 
        
        self.root.title("KSU Wallet - Select Role")
        self.root.configure(bg="#B7D4FF") 
        self.root.geometry('550x550') 
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, padx=30, pady=30, bg="#B7D4FF")
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        tk.Label(main_frame, text="Welcome to KSU Wallet System!  \n  Please select your role:", 
                 font=("Arial", 14, "bold"), bg="#B7D4FF", fg="#333333").pack(pady=20)
        
        tk.Button(main_frame, text="Student", width=20, height=2, 
                  command=self.main_app.show_signup_window, 
                  font=("Arial", 12), bg="#F0F0F0").pack(pady=15)
        
        tk.Button(main_frame, text="Admin", width=20, height=2, 
                  command=self.main_app.show_login_admin_mode, 
                  font=("Arial", 12), bg="#F0F0F0").pack(pady=15)