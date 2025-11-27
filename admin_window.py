import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random
from datetime import datetime

class AdminsWindow:
    def __init__(self, root, go_back_callback=None):
        self.root = root
        self.go_back_callback = go_back_callback

        self.root.title("Admin Window")
        self.root.geometry("550x550")

        self.notebook = ttk.Notebook(self.root)
        self.view_tab = ttk.Frame(self.notebook)
        self.add_tab = ttk.Frame(self.notebook)
        self.manage_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.view_tab, text="View")
        self.notebook.add(self.add_tab, text="Add")
        self.notebook.add(self.manage_tab, text="Manage")
        self.notebook.pack(pady=10, expand=True, fill="both")

        # to keep raw data for each row in listbox (for View Balance)
        self.entities_data = []

        self.create_view_tab()
        self.create_add_tab()
        self.create_manage_tab()

        # Load all entities (students + KSU entities)
        self.load_entities()

    # ================== View Tab ==================

    def create_view_tab(self):
        title = tk.Label(self.view_tab, text="View KSU Entities & Students", font=("Arial", 14))
        title.pack(pady=10)

        # Frame
        list_frame = tk.Frame(self.view_tab, bg="#333333")
        list_frame.pack(pady=5, fill="both", expand=True)

        # Listbox
        self.entities_listbox = tk.Listbox(
            list_frame,
            height=10,
            bg="#111111",
            fg="white"
        )
        self.entities_listbox.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)

        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.entities_listbox.yview)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=5)
        self.entities_listbox.config(yscrollcommand=scrollbar.set)

        # View Balance button
        view_balance_btn = tk.Button(
            self.view_tab,
            text="View Balance",
            command=self.view_selected_balance
        )
        view_balance_btn.pack(pady=10)

    def load_entities(self):
        """
        Loads ALL entities into the listbox in this format:

        ID: 2020123456 | Name: Sara Ali | Type: Student | Wallet: 1234567890 | Balance: 1000.00 SR
        ID: 5550001111 | Name: Bookstore | Type: KSU Entity | Wallet: 5550001111 | Balance: 0.00 SR
        """
        self.entities_listbox.delete(0, tk.END)
        self.entities_data = []

        conn = sqlite3.connect("Database.db")
        cur = conn.cursor()

        try:
            cur.execute(
                """
                SELECT 
                    KSU_Entities.Entity_ID,
                    KSU_Entities.Name,
                    Wallets.Owner_type,
                    KSU_Entities.wallet_id,
                    Wallets.Balance
                FROM KSU_Entities
                JOIN Wallets ON KSU_Entities.wallet_id = Wallets.Wallet_ID
                ORDER BY KSU_Entities.Name
                """
            )

            for row in cur:
                entity_id, name, owner_type, wallet_id, balance = row

                if balance is None:
                    balance = 0.0

                if owner_type == "student":
                    type_str = "Student"
                else:
                    type_str = "KSU Entity"

                display = (
                    f"ID: {entity_id} | "
                    f"Name: {name} | "
                    f"Type: {type_str} | "
                    f"Wallet: {wallet_id} | "
                    f"Balance: {balance:.2f} SR"
                )

                # save raw data for View Balance
                self.entities_data.append({
                    "entity_id": entity_id,
                    "name": name,
                    "type": type_str,
                    "wallet_id": wallet_id,
                    "balance": balance
                })

                self.entities_listbox.insert(tk.END, display)

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not load entities:\n{e}")
        finally:
            conn.close()

    def view_selected_balance(self):
        selection = self.entities_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select an entity from the list.")
            return

        index = selection[0]
        if index < 0 or index >= len(self.entities_data):
            messagebox.showerror("Error", "Invalid selection.")
            return

        data = self.entities_data[index]
        name = data["name"]
        balance = data["balance"]
        type_str = data["type"]

        messagebox.showinfo(
            "Entity Balance",
            f"Entity: {name}\nType: {type_str}\nCurrent Balance: {balance} SR"
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
        Add a new KSU entity with its own wallet.
        """
        entity_name = self.add_name_entry.get().strip()

        if not entity_name:
            messagebox.showerror("Error", "Entity name cannot be empty.")
            return

        conn = sqlite3.connect("Database.db")
        cur = conn.cursor()

        try:
            # check duplicate without fetchone()
            exists = False
            for _ in cur.execute("SELECT 1 FROM KSU_Entities WHERE Name = ?", (entity_name,)):
                exists = True
                break

            if exists:
                messagebox.showerror("Error", f"Entity '{entity_name}' is already registered.")
                return

            # new unique wallet id (10 digits)
            wallet_id = self.generate_unique_wallet_id(cur)

            # current time
            create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # insert wallet
            cur.execute(
                """
                INSERT INTO Wallets (Wallet_ID, Owner_type, Balance, Create_time)
                VALUES (?, ?, ?, ?)
                """,
                (wallet_id, "ksu", 0.0, create_time)
            )

            # insert entity
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

            # clear + reload list
            self.add_name_entry.delete(0, tk.END)
            self.load_entities()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while adding the entity:\n{e}")
        finally:
            conn.close()

    def generate_unique_wallet_id(self, cur):
        # new wallet number with 10 digits that is unique (no fetchone)
        while True:
            wallet_id = random.randint(10**9, 10**10 - 1)  # 1,000,000,000 to 9,999,999,999
            exists = False
            for _ in cur.execute("SELECT 1 FROM Wallets WHERE Wallet_ID = ?", (wallet_id,)):
                exists = True
                break
            if not exists:
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
        """
        Add 1000 SR to all student wallets, then refresh the View tab.
        """
        try:
            conn = sqlite3.connect("Database.db")
            cur = conn.cursor()

            cur.execute(
                "UPDATE Wallets SET Balance = Balance + 1000 WHERE Owner_type = 'student'"
            )

            conn.commit()
            conn.close()

            # refresh the list in the View tab
            self.load_entities()

            messagebox.showinfo("Success", "1000 SR deposited to all student wallets.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while paying stipends:\n{e}")

    def clear_balances(self):
        """
        Set ALL wallet balances (students + KSU entities) to 0, then refresh View.
        If you only want KSU entities, change the WHERE clause to Owner_type = 'ksu'.
        """
        try:
            conn = sqlite3.connect("Database.db")
            cur = conn.cursor()

            # zero ALL wallets
            cur.execute("UPDATE Wallets SET Balance = 0")

            conn.commit()
            conn.close()

            # refresh the list in the View tab
            self.load_entities()

            messagebox.showinfo("Success", "All wallets have been cashed out (balance = 0).")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while clearing balances:\n{e}")

    def go_back(self):
        """Back button: go back to Sign Up/Login window (via callback from MainApp)."""
        if self.go_back_callback:
            self.go_back_callback()
        else:
            self.root.destroy()
