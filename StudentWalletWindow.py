import tkinter as tk
from tkinter import messagebox
from DataCenter import DataCenter, Student, Wallet, Transaction
from datetime import datetime


class StudentWalletWindow:

    def __init__(self, root, student_id, go_back_callback):
        self.root = root
        self.student_id = student_id
        self.go_back_callback = go_back_callback
        self.dc = DataCenter()

        # Get wallet id + balance
        self.student_info = self._get_student_info()

        self.root.title("KSU Wallet - Student Wallet")
        self.root.configure(bg="#B7D4FF")
        self.root.geometry("550x550")

        self.create_widgets()

    # -----------------------------------------
    # Get student info (ID + wallet + balance)
    # -----------------------------------------
    def _get_student_info(self):
        """
        Retrieves:
        - Student_ID
        - Wallet_ID
        - Balance
        Using DataCenter helpers (SQLAlchemy inside DataCenter).
        """
        try:
            rows = self.dc.get_all_students_with_wallet()
            # rows شكلها:
            # (Student_ID, FirstName, LastName, Email, Wallet_ID, Balance)

            for row in rows:
                student_id = row[0]
                wallet_id = row[4]
                balance = row[5]

                if student_id == self.student_id:
                    return {
                        "student_id": student_id,
                        "wallet_id": wallet_id,
                        "balance": balance,
                    }

            messagebox.showerror("Error", "Could not retrieve wallet information.")
            return None

        except Exception as e:
            messagebox.showerror("Database Error", f"Error retrieving student info:\n{e}")
            return None

    # -----------------------------------------
    # UI
    # -----------------------------------------
    def create_widgets(self):
        main_frame = tk.Frame(self.root, padx=30, pady=30, bg="#B7D4FF")
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Title
        tk.Label(
            main_frame,
            text="Student Wallet Dashboard",
            font=("Arial", 16, "bold"),
            bg="#B7D4FF",
        ).grid(row=0, column=0, columnspan=2, pady=(0, 15))

        # Wallet line
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
            pady=8,
        )
        self.header_info_label.grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20)
        )

        # ===== Payment Fields =====
        transfer_frame = tk.LabelFrame(
            main_frame, text="Make a Payment", padx=20, pady=10, bg="#B7D4FF"
        )
        transfer_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        tk.Label(
            transfer_frame,
            text="Recipient Wallet Number:",
            bg="#B7D4FF",
        ).grid(row=0, column=0, sticky="w", pady=5)
        self.target_wallet_entry = tk.Entry(transfer_frame, width=30)
        self.target_wallet_entry.grid(row=0, column=1, sticky="ew", padx=10)

        tk.Label(
            transfer_frame,
            text="Amount to Pay (SR):",
            bg="#B7D4FF",
        ).grid(row=1, column=0, sticky="w", pady=5)
        self.amount_entry = tk.Entry(transfer_frame, width=30)
        self.amount_entry.grid(row=1, column=1, sticky="ew", padx=10)

        tk.Button(
            transfer_frame,
            text="Pay",
            command=self.pay_action,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
        ).grid(row=2, column=0, columnspan=2, pady=15, sticky="ew")

        tk.Button(
            main_frame,
            text="Back to Sign Up/Login",
            command=self.go_back_callback,
            bg="#F44336",
            fg="white",
        ).grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

    # -----------------------------------------
    # Payment Logic using SQLAlchemy
    # -----------------------------------------
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
            messagebox.showerror(
                "Error",
                "Wallet Number must be digits and Amount must be a valid number.",
            )
            return

        if amount <= 0:
            messagebox.showerror("Error", "Amount must be greater than zero.")
            return

        if not self.student_info:
            messagebox.showerror("Error", "No wallet information available.")
            return

        source_wallet_id = self.student_info["wallet_id"]
        current_balance = self.student_info["balance"]

        if target_wallet_id == source_wallet_id:
            messagebox.showerror("Error", "Cannot transfer to your own wallet.")
            return

        if amount > current_balance:
            messagebox.showerror(
                "Error", "There is not enough money (Insufficient Balance)."
            )
            return

        try:
            with self.dc.SessionLocal() as session:
                # Get source and target wallets
                source_wallet = session.get(Wallet, source_wallet_id)
                target_wallet = session.get(Wallet, target_wallet_id)

                if target_wallet is None:
                    messagebox.showerror(
                        "Error", "The entered Wallet Number does not exist."
                    )
                    return

                if source_wallet is None:
                    messagebox.showerror(
                        "Error", "Source wallet could not be found."
                    )
                    return

                if source_wallet.Balance < amount:
                    messagebox.showerror(
                        "Error",
                        "There is not enough money (Insufficient Balance).",
                    )
                    return

                # Update balances
                source_wallet.Balance -= amount
                target_wallet.Balance += amount

                # Add transaction (Transaction_ID auto)
                tx = Transaction(
                    from_wallet_id=source_wallet_id,
                    to_wallet_id=target_wallet_id,
                    Type="Payment",
                    Time=datetime.now(),
                )
                session.add(tx)

                session.commit()

                new_source_balance = source_wallet.Balance

            # Update local state + GUI
            self.student_info["balance"] = new_source_balance
            self.balance_label_update()
            self.target_wallet_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)

            messagebox.showinfo(
                "Success",
                f"Payment of {amount:.2f} SR to Wallet {target_wallet_id} successful.\n"
                f"Your new balance is {new_source_balance:.2f} SR.",
            )

        except Exception as e:
            messagebox.showerror("Database Error", f"Transaction failed:\n{e}")

    def balance_label_update(self):
        wallet_text = (
            f"Wallet ID: {self.student_info['wallet_id']}   |   "
            f"Balance: {self.student_info['balance']:.2f} SR"
        )
        self.header_info_label.config(text=wallet_text)

    def go_back(self):
        if self.go_back_callback:
            self.go_back_callback()