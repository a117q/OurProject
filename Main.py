import tkinter as tk
# MODIFICATION: Ensure both Admin and Login/Signup classes are imported
from admin_window import AdminsWindow 
from LogIn import LogIn
from SignupWindow import SignupWindow # Assuming SignupWindow is available
from StudentWalletWindow import StudentWalletWindow
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KSU Wallet System")
        # MODIFICATION: Use a larger geometry for better display (can be adjusted)
        self.root.geometry("600x600") 

        # MODIFICATION: The first screen should be Sign Up (based on project flow)
        self.show_signup_window()

    def clear_window(self):
        # Clears all widgets from the main window before opening a new screen
        for widget in self.root.winfo_children():
            widget.destroy()

    # ==================== Student and Admin Callbacks ===============================
    
    # MODIFICATION: Student window must be able to accept student_id from LogIn.py
# ==================== Student and Admin Callbacks ===============================
    
    def show_student_window(self, student_id):
        """Displays the Student Wallet Window after successful login."""
        self.clear_window()
        # Initializes the actual StudentWalletWindow
        self.student_wallet_window = StudentWalletWindow(
            root=self.root,
            student_id=student_id,
            go_back_callback=self.show_login_window # Passes the callback to return to login
        )

    # ... (Keep show_admin_window and other methods as they are)


    ##def show_student_window(self, student_id):
        #self.clear_window()
        # This is a temporary window. Replace with actual StudentWalletWindow initialization later.
        
        #label = tk.Label(self.root, text=f"Student Wallet Window - ID: {student_id}", font=("Arial", 16))
        #label.pack(pady=50)
        #tk.Button(self.root, text="Go Back to Login", command=self.show_login_window).pack(pady=10)

    def show_admin_window(self):
        self.clear_window()
        # Initializes the Admin Window, passing the callback to return to login
        self.admin_window = AdminsWindow(self.root, go_back_callback=self.show_login_window)


    # ==================== Sign Up screen ===============================

    def show_signup_window(self):
        self.clear_window()
        
        # Initialize SignupWindow, passing show_login_window as the callback for navigation
        self.signup_window = SignupWindow(
            root=self.root, 
            login_cb=self.show_login_window # This is the callback for 'Already have an account?' button
        )


    # ==================== Login screen ===============================

    def show_login_window(self):
        self.clear_window()
        
        # MODIFICATION: THIS IS THE FIX. Initialize the integrated LogIn class, 
        # passing all required callbacks for full navigation control.
        self.login_window = LogIn(
            root=self.root,
            show_signup_window=self.show_signup_window, # Callback for 'Go to Sign Up' button in Login screen
            show_student_cb=self.show_student_window,   # Callback for successful Student login
            show_admin_cb=self.show_admin_window        # Callback for successful Admin login
        )

# Main Execution Block
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()