import tkinter as tk
from admin_window import AdminsWindow 


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Wallet System")
        self.root.geometry("600x400")

        # firt screen will appear example.log in
        self.show_login_window()

    def clear_window(self):
        # will remove  all the widgets from the window before opening a new screen
        # شفتو لما نتفح نافذع جديده مابي النوافذ تتكدس على بعض يعني ابي نافذه وحده كل مره لذلك نسوي هذي الداله 
        for widget in self.root.winfo_children():
            widget.destroy()

    # ==================== Login screen -EXAMPLE -   ===============================

    def show_login_window(self):
        # here is the real log in screen !!!!!!!!!!
        self.clear_window()

        title = tk.Label(self.root, text="Login Window", font=("Arial", 18))
        title.pack(pady=20)

        # temprary button for the admin screen 
        admin_btn = tk.Button(self.root, text="Login as Admin", command=self.show_admin_window)
        admin_btn.pack(pady=10)

        # another temp button 
        student_btn = tk.Button(self.root, text="Login as Student", command=self.show_student_window)
        student_btn.pack(pady=10)

    # ====================== admin screen   ==========================

    def show_admin_window(self):
        # opening the admin window 
        self.clear_window()

        # نرسل للـ AdminWindow:
        # 1) root
        # 2) دالة الرجعة show_login_window
        
        self.admin_window = AdminsWindow(self.root, go_back_callback=self.show_login_window)

    # ==================== STudent screen - EXAMPLE- =====================

    def show_student_window(self):
        # example ! stdent screen - gui -
        self.clear_window()

        label = tk.Label(self.root, text="Student Wallet Window", font=("Arial", 16))
        label.pack(pady=20)

        back_btn = tk.Button(self.root, text="Back", command=self.show_login_window)
        back_btn.pack(pady=20)


# ==================== MAIN ====================

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()