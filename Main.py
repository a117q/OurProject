import tkinter as tk
from DataCenter import DataCenter
from admin_window import AdminsWindow 
from LogIn import LogIn
from SignupWindow import SignupWindow 
from StudentWalletWindow import StudentWalletWindow

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KSU Wallet System")
        self.root.geometry("550x550") 

        self.dc = DataCenter()
        #adding manager
        self.dc.add_initial_manager()
        self.show_signup_window() 
        
    #cleaning the screen before opening a new window (prevent  overlapping)
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    #-----------------------------Student screen---------------------------
    def show_student_window(self, student_id):

        #displaying student wallet window after log in 
        self.clear_window()
        self.student_wallet_window = StudentWalletWindow(
            root=self.root,
            student_id=student_id,
            go_back_callback=self.show_login_window 
        )

    #--------------------Admin screen-----------------------------
    def show_admin_window(self):
        #displaying the admin window after log in
        self.clear_window()

        self.admin_window = AdminsWindow(
            self.root,
            go_back_callback=self.show_login_window  #back to log in window
        )


    #-----------------------------Sign Up screen-----------------------------

    def show_signup_window(self):
        self.clear_window()
        
        self.signup_window = SignupWindow(
            root=self.root, 
            login_cb=self.show_login_window 
        )


    #-----------------------------Login screen-----------------------------

    def show_login_window(self):
        self.clear_window()
        
        self.login_window = LogIn(
            root=self.root,
            show_signup_window=self.show_signup_window, 
            show_student_cb=self.show_student_window,  
            show_admin_cb=self.show_admin_window       
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
