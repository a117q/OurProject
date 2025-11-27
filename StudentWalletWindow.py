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
        self.go_back_callback = go_back_callback
        self.dc = DataCenter()
        
        # Get wallet id + balance (NO fetchone)
        self.student_info = self._get_student_info()

        self.root.title("KSU Wallet - Student Wallet")
        self.root.configure(bg="#B7D4FF")
        self.root.geometry('550x550') 
        
        self.create_widgets()
        
    def _get_student_info(self):
        """
        Retrieves:
        - Student_ID
        - Wallet_ID
        - Balance
        WITHOUT using fetchone/fetchall
        """
        try:
            cur = self.dc.cur
            cur.execute(
                """
                SELECT 
                    Students.Student_ID,
                    Wallets.Wallet_ID,
                    Wallets.Balance
                FROM Students
                JOIN Wallets ON Students.wallet_id = Wallets.Wallet_ID
                WHERE Students.Student_ID = ?
                """,
                (self.student_id,)
            )

            # read first row with for-loop instead of fetchone
            for row in cur:
                return {
                    "student_id": row[0],
                    "wallet_id": row[1],
                    "balance": row[2],
                }

            messagebox.showerror("Error", "Could not retrieve wallet information.")
            return None

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Database error:\n{e}")
            return None

    def create_widgets(self):
        main_frame = tk.Frame(self.root, padx=30, pady=30, bg="#B7D4FF")
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Title
        tk.Label(
            main_frame,
            text="Student Wallet Dashboard",
            font=("Arial", 16, "bold"),
            bg="#B7D4FF"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # === Single line: Wallet ID + Balance ===
        if self.student_info:
            wallet_text = (
                f"Wallet ID: {self.student_info['wallet_id']}   |   "
                f"Balance: {self.student_info['balance']:.2f} SR"
            )
        else:
            wallet_text = "Wallet information not available."

        self.header_info_label = tk.Label(
            main_frame,
            text=wallet_text,
            bg="#FFFFFF",
            fg="black",
            font=("Arial", 11, "bold"),
            anchor="w",
            padx=10,
            pady=8
        )
        self.header_info_label.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))

        # ===== Payment Fields =====
        transfer_frame = tk.LabelFrame(main_frame, text="Make a Payment", padx=20, pady=10, bg="#B7D4FF")
        transfer_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky='ew')
        
        tk.Label(transfer_frame, text="Recipient Wallet Number:", bg="#B7D4FF").grid(row=0, column=0, sticky='w', pady=5)
        self.target_wallet_entry = tk.Entry(transfer_frame, width=30)
        self.target_wallet_entry.grid(row=0, column=1, sticky='ew', padx=10)

        tk.Label(transfer_frame, text="Amount to Pay (SR):", bg="#B7D4FF").grid(row=1, column=0, sticky='w', pady=5)
        self.amount_entry = tk.Entry(transfer_frame, width=30)
        self.amount_entry.grid(row=1, column=1, sticky='ew', padx=10)

        tk.Button(
            transfer_frame,
            text="Pay",
            command=self.pay_action,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white"
        ).grid(row=2, column=0, columnspan=2, pady=15, sticky='ew')

        tk.Button(
            main_frame,
            text="Back to Sign Up/Login",
            command=self.go_back_callback, 
            bg="#F44336",
            fg="white"
        ).grid(row=3, column=0, columnspan=2, pady=10, sticky='ew')

    # ===== Payment Logic (still no fetchone) =====
    def pay_action(self):
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
            
        current_balance = self.student_info['balance']
        source_wallet_id = self.student_info['wallet_id']

        if amount > current_balance:
            messagebox.showerror("Error", "There is not enough money (Insufficient Balance).")
            return
        
        if target_wallet_id == source_wallet_id:
            messagebox.showerror("Error", "Cannot transfer to your own wallet.")
            return

        conn = sqlite3.connect("Database.db")
        cur = conn.cursor()
        
        try:
            # Check target wallet without fetchone
            target_exists = False
            target_balance = 0.0
            cur.execute("SELECT Balance FROM Wallets WHERE Wallet_ID = ?", (target_wallet_id,))
            for row in cur:
                target_exists = True
                target_balance = row[0]
                break

            if not target_exists:
                messagebox.showerror("Error", "The entered Wallet Number does not exist.")
                return
            
            conn.execute("BEGIN TRANSACTION")

            new_source_balance = current_balance - amount
            cur.execute(
                "UPDATE Wallets SET Balance = ? WHERE Wallet_ID = ?",
                (new_source_balance, source_wallet_id)
            )

            new_target_balance = target_balance + amount
            cur.execute(
                "UPDATE Wallets SET Balance = ? WHERE Wallet_ID = ?",
                (new_target_balance, target_wallet_id)
            )

            transaction_id = self._generate_transaction_id(cur)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                """
                INSERT INTO Transactions (Transaction_ID, from_wallet_id, to_wallet_id, Type, Time)
                VALUES (?, ?, ?, ?, ?)
                """,
                (transaction_id, source_wallet_id, target_wallet_id, "Payment", current_time)
            )

            conn.commit()
            
            # Update local state + GUI
            self.student_info['balance'] = new_source_balance
            self.balance_label_update()
            self.target_wallet_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)
            
            messagebox.showinfo(
                "Success",
                f"Payment of {amount:.2f} SR to Wallet {target_wallet_id} successful.\n"
                f"Your new balance is {new_source_balance:.2f} SR."
            )

        except sqlite3.Error as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Transaction failed:\n{e}")
        finally:
            conn.close()

    def balance_label_update(self):
        # Update the header line text after payment
        wallet_text = (
            f"Wallet ID: {self.student_info['wallet_id']}   |   "
            f"Balance: {self.student_info['balance']:.2f} SR"
        )
        self.header_info_label.config(text=wallet_text)

    def _generate_transaction_id(self, cur):
        """Generates a unique 7-digit Transaction ID (without fetchone)."""
        while True:
            t_id = random.randint(1000000, 9999999)
            exists = False
            cur.execute("SELECT 1 FROM Transactions WHERE Transaction_ID = ?", (t_id,))
            for _ in cur:
                exists = True
                break
            if not exists:
                return t_id

    def go_back(self):
        if self.go_back_callback:
            self.go_back_callback()
