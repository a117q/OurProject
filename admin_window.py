import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random
from datetime import datetime

#new ----------------------------------------

class AdminsWindow:
    def __init__(self, root, go_back_callback=None):
        self.root = root
        self.go_back_callback = go_back_callback

        self.root.title("Admin Window")
        self.root.geometry("600x400")

        self.notebook = ttk.Notebook(self.root)
        self.view_tab = ttk.Frame(self.notebook)
        self.add_tab = ttk.Frame(self.notebook)
        self.manage_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.view_tab, text="View")
        self.notebook.add(self.add_tab, text="Add")
        self.notebook.add(self.manage_tab, text="Manage")
        self.notebook.pack(pady=10, expand=True, fill="both")

        self.create_view_tab()
        self.create_add_tab()
        self.create_manage_tab()

        self.load_entities()

    # ================== View Tab ==================

    def create_view_tab(self):
        title = tk.Label(self.view_tab, text="View KSU Entities", font=("Arial", 14))
        title.pack(pady=10)

        #Frame
        list_frame = tk.Frame(self.view_tab)
        list_frame.pack(pady=5, fill="both", expand=True)

        #Listbox  
        self.entities_listbox = tk.Listbox(list_frame, height=10)
        self.entities_listbox.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)

        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.entities_listbox.yview)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=5)
        self.entities_listbox.config(yscrollcommand=scrollbar.set)

        # button  View Balance
        view_balance_btn = tk.Button(
            self.view_tab,
            text="View Balance",
            command=self.view_selected_balance
        )
        view_balance_btn.pack(pady=10)

    def load_entities(self):
        #load the enitity names into the  Listbox
        self.entities_listbox.delete(0, tk.END)

        conn = sqlite3.connect("Database.db")
        cur = conn.cursor()

        # bring the names 
        cur.execute("SELECT Name FROM KSU_Entities ORDER BY Name")
        rows = cur.fetchall()

        for row in rows:
            self.entities_listbox.insert(tk.END, row[0])

        conn.close()

    def view_selected_balance(self):
        #show the balance for the chosen enntity 
        selection = self.entities_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select an entity from the list.")
            return

        entity_name = self.entities_listbox.get(selection[0])

        conn = sqlite3.connect("Database.db")
        cur = conn.cursor()

        cur.execute(
            """
            SELECT Wallets.Balance
            FROM KSU_Entities
            JOIN Wallets ON KSU_Entities.wallet_id = Wallets.Wallet_ID
            WHERE KSU_Entities.Name = ?
            """,
            (entity_name,)
        )
        row = cur.fetchone()
        conn.close()

        if row is None:
            messagebox.showerror("Error", "No wallet found for this entity.")
        else:
            balance = row[0]
            messagebox.showinfo(
                "Entity Balance",
                f"Entity: {entity_name}\nCurrent Balance: {balance} SR"
            )

    # ================== Add Tab ==================

    def create_add_tab(self):
        title = tk.Label(self.add_tab, text="Add KSU Entity", font=("Arial", 14))
        title.pack(pady=10)

        name_label = tk.Label(self.add_tab, text="Entity Name:")
        name_label.pack(pady=(10, 0))

        self.add_name_entry = tk.Entry(self.add_tab, width=30)
        self.add_name_entry.pack(pady=5)

        submit_btn = tk.Button(self.add_tab, text="Submit", command=self.add_entity)
        submit_btn.pack(pady=10)

    def add_entity(self):
        """
        Submit button:
        - يقرأ اسم الكيان
        - يتحقق مو فاضي ومو مكرر
        - يولد رقم محفظة 10 أرقام
        - يحط Wallet_Type = 'ksu'
        - Balance = 0
        - Create_time = التاريخ والوقت الحالي
        - يضيف البيانات لجدول Wallets و KSU_Entities
        """
        #submit button : reading the entity name - chicking its not empty and not duplicate
        #+ new 10 numbers for the wallet number -
        entity_name = self.add_name_entry.get().strip()

        if not entity_name:
            messagebox.showerror("Error", "Entity name cannot be empty.")
            return

        conn = sqlite3.connect("Database.db")
        cur = conn.cursor()

        try:
            #checking if the name wasnt there 
            cur.execute("SELECT 1 FROM KSU_Entities WHERE Name = ?", (entity_name,))
            if cur.fetchone():
                messagebox.showerror("Error", f"Entity '{entity_name}' is already registered.")
                return
            # new wallet number 10 (unique)

            wallet_id = self.generate_unique_wallet_id(cur)

            # current time
            create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # new qwallet
            cur.execute(
                """
                INSERT INTO Wallets (Wallet_ID, Owner_type, Balance, Create_time)
                VALUES (?, ?, ?, ?)
                """,
                (wallet_id, "ksu", 0.0, create_time)
            )

            #adding entity in the ksu_entity using the enityty id 
            cur.execute(
                """
                INSERT INTO KSU_Entities (Entity_ID, Name, wallet_id)
                VALUES (?, ?, ?)
                """,
                (wallet_id, entity_name, wallet_id)
            )

            conn.commit()

            messagebox.showinfo(
                "Success",
                f"Entity '{entity_name}' added successfully.\n"
                f"Wallet ID: {wallet_id}\n"
                f"Initial Balance: 0 SR"
            )

            # cleane and update
            self.add_name_entry.delete(0, tk.END)
            self.load_entities()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while adding the entity:\n{e}")
        finally:
            conn.close()

    def generate_unique_wallet_id(self, cur):
        # new wallet number with 10 number that is unique 
        while True:
            wallet_id = random.randint(10**9, 10**10 - 1)  # 1,000,000,000 to 9,999,999,999
            cur.execute("SELECT 1 FROM Wallets WHERE Wallet_ID = ?", (wallet_id,))
            if not cur.fetchone():
                return wallet_id


    # ========================= Manage Tab =====================

    def create_manage_tab(self):
        title = tk.Label(self.manage_tab, text="Manage", font=("Arial", 14))
        title.pack(pady=10)

        # Pay Stipends button
        pay_btn = tk.Button(
            self.manage_tab,
            text="Pay Stipends",
            command=self.pay_stipends
        )
        pay_btn.pack(pady=10)

        # Cash Out button
        cashout_btn = tk.Button(
            self.manage_tab,
            text="Cash Out",
            command=self.clear_balances
        )
        cashout_btn.pack(pady=10)

        # Back button
        back_btn = tk.Button(
            self.manage_tab,
            text="Back",
            command=self.go_back
        )
        back_btn.pack(pady=20)

    def pay_stipends(self):
       #add 1000 to all students wallet - pay stipends button
        try:
            conn = sqlite3.connect("Database.db")
            cur = conn.cursor()

            cur.execute(
                "UPDATE Wallets SET Balance = Balance + 1000 WHERE Owner_type = 'student'"
            )

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "1000 SR deposited to all student wallets.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while paying stipends:\n{e}")


    def clear_balances(self):
        #Cash Out button
        try:
            conn = sqlite3.connect("Database.db")
            cur = conn.cursor()

            cur.execute(
                "UPDATE Wallets SET Balance = 0 WHERE Owner_type = 'ksu'"
            )

            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "All KSU entity wallets have been cashed out (balance = 0).")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while clearing balances:\n{e}")


    def go_back(self):
        """
        Back button:
        في السلايدات مكتوب يرجع لواجهة Sign Up
        هنا نستدعي الكول باك اللي يعطينا إياه الـ main
        """
        if self.go_back_callback:
            self.go_back_callback()
        else:
            self.root.destroy()