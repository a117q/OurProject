import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from DataCenter import DataCenter , Wallet , KSUEntity

class AdminsWindow:
    def __init__(self, root, go_back_callback=None):
        self.root = root
        self.go_back_callback = go_back_callback

        self.root.title("Admin Window")
        self.root.geometry("550x550")

        # SQLAlchemy DataCenter
        self.dc = DataCenter()

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

        list_frame = tk.Frame(self.view_tab, bg="#333333")
        list_frame.pack(pady=5, fill="both", expand=True)

        self.entities_listbox = tk.Listbox(
            list_frame,
            height=10,
            bg="#111111",
            fg="white"
        )
        self.entities_listbox.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=5)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.entities_listbox.yview)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=5)
        self.entities_listbox.config(yscrollcommand=scrollbar.set)

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

        try:
            with self.dc.SessionLocal() as session:
                rows = (
                    session.query(
                        KSUEntity.Entity_ID,
                        KSUEntity.Name,
                        Wallet.Owner_type,
                        KSUEntity.wallet_id,
                        Wallet.Balance,
                    )
                    .join(Wallet, KSUEntity.wallet_id == Wallet.Wallet_ID)
                    .order_by(KSUEntity.Name)
                    .all()
                )

                for row in rows:
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

                    self.entities_data.append(
                        {
                            "entity_id": entity_id,
                            "name": name,
                            "type": type_str,
                            "wallet_id": wallet_id,
                            "balance": balance,
                        }
                    )

                    self.entities_listbox.insert(tk.END, display)

        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load entities:\n{e}")

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
        Add a new KSU entity with its own wallet using SQLAlchemy.
        """
        entity_name = self.add_name_entry.get().strip()

        if not entity_name:
            messagebox.showerror("Error", "Entity name cannot be empty.")
            return

        try:
            with self.dc.SessionLocal() as session:
                # check duplicate
                exists = (
                    session.query(KSUEntity)
                    .filter(KSUEntity.Name == entity_name)
                    .first()
                )
                if exists:
                    messagebox.showerror(
                        "Error", f"Entity '{entity_name}' is already registered."
                    )
                    return

                # new unique wallet id (10 digits) from DataCenter helper
                wallet_id = self.dc.generate_unique_wallet_id()
                create_time = datetime.now()

                # insert wallet
                wallet = Wallet(
                    Wallet_ID=wallet_id,
                    Owner_type="ksu",
                    Balance=0.0,
                    Create_time=create_time,
                )
                session.add(wallet)

                # insert entity
                entity = KSUEntity(
                    Entity_ID=wallet_id,
                    Name=entity_name,
                    wallet_id=wallet_id,
                )
                session.add(entity)

                session.commit()

            messagebox.showinfo(
                "Success",
                f"Entity '{entity_name}' added successfully.\n"
                f"Wallet ID: {wallet_id}\n"
                f"Initial Balance: 0 SR",
            )

            self.add_name_entry.delete(0, tk.END)
            self.load_entities()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while adding the entity:\n{e}")

    # ========================= Manage Tab =====================

    def create_manage_tab(self):
        title = tk.Label(self.manage_tab, text="Manage", font=("Arial", 14))
        title.pack(pady=10)

        pay_btn = tk.Button(
            self.manage_tab,
            text="Pay Stipends",
            command=self.pay_stipends,
        )
        pay_btn.pack(pady=10)

        cashout_btn = tk.Button(
            self.manage_tab,
            text="Cash Out",
            command=self.clear_balances,
        )
        cashout_btn.pack(pady=10)

        back_btn = tk.Button(
            self.manage_tab,
            text="Back",
            command=self.go_back,
        )
        back_btn.pack(pady=20)

    def pay_stipends(self):
        """
        Add 1000 SR to all student wallets, then refresh the View tab.
        """
        try:
            with self.dc.SessionLocal() as session:
                session.query(Wallet).filter(
                    Wallet.Owner_type == "student"
                ).update(
                    {Wallet.Balance: Wallet.Balance + 1000},
                    synchronize_session=False,
                )
                session.commit()

            self.load_entities()
            messagebox.showinfo("Success", "1000 SR deposited to all student wallets.")
        except Exception as e:
            messagebox.showerror(
                "Error", f"An error occurred while paying stipends:\n{e}"
            )

    def clear_balances(self):
        """
        Set ALL wallet balances (students + KSU entities) to 0, then refresh View.
        """
        try:
            with self.dc.SessionLocal() as session:
                session.query(Wallet).update(
                    {Wallet.Balance: 0}, synchronize_session=False
                )
                session.commit()

            self.load_entities()
            messagebox.showinfo(
                "Success", "All wallets have been cashed out (balance = 0)."
            )
        except Exception as e:
            messagebox.showerror(
                "Error", f"An error occurred while clearing balances:\n{e}"
            )

    def go_back(self):
        """Back button: go back to Sign Up/Login window (via callback from MainApp)."""
        if self.go_back_callback:
            self.go_back_callback()
        else:
            self.root.destroy()