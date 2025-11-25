import tkinter as tk
from DataCenter import DataCenter
from admin_window import AdminsWindow 
from LogIn import LogIn
from SignupWindow import SignupWindow 
from StudentWalletWindow import StudentWalletWindow
from selectRole import selectRole

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KSU Wallet System")
        self.root.geometry("550x550") 

        self.dc = DataCenter()
        self.dc.add_initial_manager("0123456789", "ad223344", "Admin")
        
        self.show_select_Role()
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ==================== Student and Admin Callbacks ===============================
    
    
    def show_student_window(self, student_id):
        """Displays the Student Wallet Window after successful login."""
        self.clear_window()
        # Initializes the actual StudentWalletWindow
        self.student_wallet_window = StudentWalletWindow(
            root=self.root,
            student_id=student_id,
            go_back_callback=self.show_login_window 
        )



   

    def show_admin_window(self):
        self.clear_window()
        self.admin_window = AdminsWindow(self.root, go_back_callback=self.show_login_window)


    # ==================== Sign Up screen ===============================

    def show_signup_window(self):
        self.clear_window()
        
        self.signup_window = SignupWindow(
            root=self.root, 
            login_cb=self.show_login_window 
        )


    # ==================== Login screen ===============================

    def show_login_window(self):
        self.clear_window()
        
   
        self.login_window = LogIn(
            root=self.root,
            show_signup_window=self.show_signup_window, 
            show_student_cb=self.show_student_window,  
            show_admin_cb=self.show_admin_window       
        )
    # ==================== New Role Selector screen ===============================

    def show_select_Role(self):
        self.clear_window()
        self.select_Role = selectRole(self.root, self) 

    # ==================== Admin Login Mode  ===============================

    def show_login_admin_mode(self):
        """Dedicated Login screen for the Admin."""
        self.clear_window()
        
        self.login_window = LogIn(
            root=self.root,
            show_signup_window=self.show_select_Role, 
            show_student_cb=self.show_student_window,
            show_admin_cb=self.show_admin_window,
            is_admin_mode=True
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()