import tkinter as tk
from tkinter import messagebox
from DataCenter import DataCenter
import sqlite3
from datetime import datetime
import random 

class StudentWalletWindow:
    
    def __init__(self, root, student_id, go_back_callback):
        self.root = root
        self.student_id = student_id
        # Callback to return to the Sign Up/Login screen [cite: 54]
        self.go_back_callback = go_back_callback
        self.dc = DataCenter()
        
        # Retrieve necessary student and wallet details
        self.wallet_info = self._get_student_wallet_info()

        # Window setup
        self.root.title("KSU Wallet - Student Wallet")
        self.root.configure(bg="#B7D4FF")
        self.root.geometry('600x450') 
        
        self.create_widgets()
        
    def _get_student_wallet_info(self):
        """Retrieves the student's Wallet ID and current Balance."""
        try:
            cur = self.dc.cur
            cur.execute(
                """
                SELECT Wallets.Wallet_ID, Wallets.Balance
                FROM Students
                JOIN Wallets ON Students.wallet_id = Wallets.Wallet_ID
                WHERE Students.Student_ID = ?
                """,
                (self.student_id,)
            )
            info = cur.fetchone()
            if info:
                # Return Wallet Number and current balance [cite: 45, 46]
                return {"wallet_id": info[0], "balance": info[1]}
            else:
                # This should ideally not happen if login was successful
                messagebox.showerror("Error", "Could not retrieve wallet information.")
                return None
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Database error:\n{e}")
            return None

    def create_widgets(self):
        # Main Frame centered
        main_frame = tk.Frame(self.root, padx=30, pady=30, bg="#B7D4FF")
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(
            main_frame,
            text="Student Wallet Dashboard",
            font=("Arial", 16, "bold"),
            bg="#B7D4FF"
        ).grid(row=0, column=0, columnspan=2, pady=15)

        ## Wallet Information Display ##
        info_frame = tk.LabelFrame(main_frame, text="My Wallet Info", padx=20, pady=10, bg="#FFFFFF")
        info_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky='ew')
        
        if self.wallet_info:
            tk.Label(info_frame, text="Wallet Number:", bg="#FFFFFF", font=("Arial", 10)).grid(row=0, column=0, sticky='w')
            tk.Label(info_frame, text=f"{self.wallet_info['wallet_id']}", bg="#FFFFFF", font=("Arial", 10, "bold")).grid(row=0, column=1, sticky='w', padx=10)
            
            tk.Label(info_frame, text="Current Balance:", bg="#FFFFFF", font=("Arial", 10)).grid(row=1, column=0, sticky='w')
            # Label to hold and update the current balance [cite: 46]
            self.balance_label = tk.Label(info_frame, text=f"{self.wallet_info['balance']:.2f} SR", bg="#FFFFFF", font=("Arial", 10, "bold", "underline"), fg="green")
            self.balance_label.grid(row=1, column=1, sticky='w', padx=10)
        
        ## Payment Fields ##
        transfer_frame = tk.LabelFrame(main_frame, text="Make a Payment", padx=20, pady=10, bg="#B7D4FF")
        transfer_frame.grid(row=2, column=0, columnspan=2, pady=20, sticky='ew')
        
        # Field for Recipient Wallet Number [cite: 47]
        tk.Label(transfer_frame, text="Recipient Wallet Number:", bg="#B7D4FF").grid(row=0, column=0, sticky='w', pady=5)
        self.target_wallet_entry = tk.Entry(transfer_frame, width=30)
        self.target_wallet_entry.grid(row=0, column=1, sticky='ew', padx=10)

        # Field for Amount to Pay [cite: 48]
        tk.Label(transfer_frame, text="Amount to Pay (SR):", bg="#B7D4FF").grid(row=1, column=0, sticky='w', pady=5)
        self.amount_entry = tk.Entry(transfer_frame, width=30)
        self.amount_entry.grid(row=1, column=1, sticky='ew', padx=10)

        # Pay button [cite: 49]
        tk.Button(
            transfer_frame,
            text="Pay",
            command=self.pay_action,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white"
        ).grid(row=2, column=0, columnspan=2, pady=15, sticky='ew')

        # Back button: Takes the user to the Sign Up window [cite: 54]
        tk.Button(
            main_frame,
            text="Back to Sign Up/Login",
            command=self.go_back_callback, 
            bg="#F44336",
            fg="white"
        ).grid(row=3, column=0, columnspan=2, pady=10, sticky='ew')



## 💳 Payment Logic (`pay_action`)

    def pay_action(self):
        """
        Handles payment submission: 
        1. Validates input and balance.
        2. Checks if the target wallet exists.
        3. Updates balances in the central database using a transaction. [cite: 49, 50, 51]
        """
        target_wallet_str = self.target_wallet_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        
        if not target_wallet_str or not amount_str:
            messagebox.showerror("Error", "Please fill in all payment fields.")
            return

        try:
            target_wallet_id = int(target_wallet_str)
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Error", "Wallet Number must be digits and Amount must be a valid number.")
            return

        if amount <= 0:
            messagebox.showerror("Error", "Amount must be greater than zero.")
            return
            
        current_balance = self.wallet_info['balance']
        source_wallet_id = self.wallet_info['wallet_id']

        # Check 1: Insufficient Balance [cite: 53]
        if amount > current_balance:
            messagebox.showerror("Error", 'There is not enough money (Insufficient Balance).')
            return
        
        # Prevent self-transfer (Good Practice)
        if target_wallet_id == source_wallet_id:
            messagebox.showerror("Error", "Cannot transfer to your own wallet.")
            return

        conn = sqlite3.connect("Database.db")
        cur = conn.cursor()
        
        try:
            # Check 2: Target Wallet Existence [cite: 49, 52]
            cur.execute("SELECT Balance FROM Wallets WHERE Wallet_ID = ?", (target_wallet_id,))
            target_wallet_data = cur.fetchone()
            
            if target_wallet_data is None:
                messagebox.showerror("Error", "The entered Wallet Number does not exist.") [cite: 52]
                return
            
            target_balance = target_wallet_data[0]
            
            # Start transaction for atomic updates
            conn.execute("BEGIN TRANSACTION")

            # Update Source Wallet (Student): Deduct amount [cite: 50, 51]
            new_source_balance = current_balance - amount
            cur.execute(
                "UPDATE Wallets SET Balance = ? WHERE Wallet_ID = ?",
                (new_source_balance, source_wallet_id)
            )

            # Update Target Wallet (Entity/Other Student): Add amount [cite: 50, 51]
            new_target_balance = target_balance + amount
            cur.execute(
                "UPDATE Wallets SET Balance = ? WHERE Wallet_ID = ?",
                (new_target_balance, target_wallet_id)
            )

            # Record Transaction
            transaction_id = self._generate_transaction_id(cur)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                """
                INSERT INTO Transactions (Transaction_ID, from_wallet_id, to_wallet_id, Type, Time)
                VALUES (?, ?, ?, ?, ?)
                """,
                (transaction_id, source_wallet_id, target_wallet_id, "Payment", current_time)
            )

            conn.commit() # Finalize the transaction
            
            # Update GUI
            self.wallet_info['balance'] = new_source_balance
            self.balance_label.config(text=f"{new_source_balance:.2f} SR")
            self.target_wallet_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)
            
            messagebox.showinfo("Success", f"Payment of {amount:.2f} SR to Wallet {target_wallet_id} successful. Your new balance is {new_source_balance:.2f} SR.")

        except sqlite3.Error as e:
            conn.rollback() # Revert changes if any error occurs
            messagebox.showerror("Database Error", f"Transaction failed:\n{e}")
        finally:
            conn.close()


    def _generate_transaction_id(self, cur):
        """Generates a unique 7-digit Transaction ID."""
        while True:
            t_id = random.randint(1000000, 9999999) 
            cur.execute("SELECT 1 FROM Transactions WHERE Transaction_ID = ?", (t_id,))
            if not cur.fetchone():
                return t_id

    def go_back(self):
        """Redirects back to the Sign Up window using the callback. [cite: 54]"""
        if self.go_back_callback:
            self.go_back_callback()