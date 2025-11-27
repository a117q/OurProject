import sqlite3
import random
from datetime import datetime
import hashlib

class DataCenter:
    def __init__(self, db_name="Database.db"):
        # connect to database
        self.conn = sqlite3.connect(db_name)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cur = self.conn.cursor()
        # create tables if they don't exist
        self._create_tables()

    # -------------------------------------------------
    # Tables
    # -------------------------------------------------
    def _create_tables(self):
        # Wallet table
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Wallets(
            Wallet_ID   INT(10) PRIMARY KEY NOT NULL,
            Owner_type  TEXT NOT NULL,   -- 'student' or 'ksu'
            Balance     FLOAT,
            Create_time DATETIME
        )
        """)

        # Managers table
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Managers(
            Manager_ID TEXT PRIMARY KEY NOT NULL,
            Password   TEXT NOT NULL,
            FirstName  TEXT NOT NULL,
            LastName   TEXT NOT NULL
        )
        """)

        # Students table
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Students(
            Student_ID INT(10) PRIMARY KEY NOT NULL,
            FirstName  TEXT NOT NULL,
            LastName   TEXT NOT NULL,
            email      TEXT NOT NULL,
            PhoneNo    INT,
            wallet_id  INT(10),
            password   TEXT NOT NULL CHECK (LENGTH(password) >= 8),
            FOREIGN KEY (wallet_id) REFERENCES Wallets(Wallet_ID)
        )
        """)

        # Ensure password column exists (for old DBs)
        has_password = False
        for row in self.cur.execute("PRAGMA table_info(Students)"):
            if len(row) > 1 and row[1] == "password":
                has_password = True
                break
        if not has_password:
            self.cur.execute("ALTER TABLE Students ADD COLUMN password TEXT")
            self.conn.commit()

        # KSU_Entities table
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS KSU_Entities(
            Entity_ID INT(10) PRIMARY KEY NOT NULL,
            Name      TEXT NOT NULL,
            wallet_id INT(10),
            FOREIGN KEY (wallet_id) REFERENCES Wallets(Wallet_ID)
        )
        """)

        # Transactions table
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Transactions(
            Transaction_ID  INT PRIMARY KEY NOT NULL,
            from_wallet_id  INT(10),
            to_wallet_id    INT(10) NOT NULL,
            Type            TEXT,
            Time            DATETIME,
            FOREIGN KEY (to_wallet_id)   REFERENCES Wallets(Wallet_ID),
            FOREIGN KEY (from_wallet_id) REFERENCES Wallets(Wallet_ID)
        )
        """)

        self.conn.commit()

    # -------------------------------------------------
    # Wallet / Student helpers
    # -------------------------------------------------
    def generate_unique_wallet_id(self):
        """Generates a unique 10-digit Wallet ID."""
        while True:
            wallet_id = random.randint(1000000000, 9999999999)
            exists = False
            for _ in self.cur.execute(
                "SELECT 1 FROM Wallets WHERE Wallet_ID = ?",
                (wallet_id,)
            ):
                exists = True
                break
            if not exists:
                return wallet_id

    def check_student_id_exists(self, student_id):
        """Checks if a Student ID is already in the database."""
        for _ in self.cur.execute(
            "SELECT 1 FROM Students WHERE Student_ID = ?",
            (student_id,)
        ):
            return True
        return False

    def check_email_exists(self, email):
        """Checks if an email is already used by a student."""
        for _ in self.cur.execute(
            "SELECT 1 FROM Students WHERE email = ?",
            (email,)
        ):
            return True
        return False

    def check_student_login(self, student_id, hashed_password):
        """Returns True if (Student_ID, password) match in Students table."""
        for _ in self.cur.execute(
            "SELECT 1 FROM Students WHERE Student_ID = ? AND password = ?",
            (student_id, hashed_password)
        ):
            return True
        return False

    def get_all_students_with_wallet(self):
        """
        Returns a list of tuples:
        (Student_ID, FirstName, LastName, Email, Wallet_ID, Balance)
        """
        result = []
        self.cur.execute(
            """
            SELECT 
                S.Student_ID,
                S.FirstName,
                S.LastName,
                S.email,
                W.Wallet_ID,
                W.Balance
            FROM Students S
            JOIN Wallets W ON S.wallet_id = W.Wallet_ID
            ORDER BY S.Student_ID
            """
        )
        for row in self.cur:
            result.append(row)
        return result

    # -------------------------------------------------
    # Manager helpers
    # -------------------------------------------------
    def add_initial_manager(self):
        """
        Adds one default manager if Managers table is empty.
        ID:        1234567890
        Password:  ad223344 (stored as SHA-256 hash)
        Name:      Admin User
        """
        try:
            # if any manager exists, do nothing
            for _ in self.cur.execute("SELECT 1 FROM Managers LIMIT 1"):
                return

            manager_id = "1234567890"
            plain_password = "ad223344"
            hashed_password = hashlib.sha256(
                plain_password.encode("utf-8")
            ).hexdigest()

            self.cur.execute(
                "INSERT INTO Managers (Manager_ID, Password, FirstName, LastName) VALUES (?, ?, ?, ?)",
                (manager_id, hashed_password, "Admin", "User")
            )
            self.conn.commit()

        except Exception as e:
            print(f"Error adding initial manager: {e}")

    def check_manager_login(self, manager_id, hashed_password):
        """Returns True if (Manager_ID, Password) match in Managers table."""
        for _ in self.cur.execute(
            "SELECT 1 FROM Managers WHERE Manager_ID = ? AND Password = ?",
            (manager_id, hashed_password)
        ):
            return True
        return False

    def get_manager_info(self, manager_id):
        """
        Returns dict with manager info, or None if not found:
        {
            'manager_id': ...,
            'first_name': ...,
            'last_name': ...
        }
        """
        for row in self.cur.execute(
            "SELECT Manager_ID, FirstName, LastName FROM Managers WHERE Manager_ID = ?",
            (manager_id,)
        ):
            return {
                "manager_id": row[0],
                "first_name": row[1],
                "last_name": row[2],
            }
        return None

    def check_manager_id_exists(self, manager_id):
        """Returns True if this ID already exists in Managers table."""
        for _ in self.cur.execute(
            "SELECT 1 FROM Managers WHERE Manager_ID = ?",
            (manager_id,)
        ):
            return True
        return False

    # -------------------------------------------------
    # Insert student + wallet + entity
    # -------------------------------------------------
    def add_student_and_wallet(
        self,
        student_id,
        first_name,
        last_name,
        email,
        phone_no,
        hashed_password,
        initial_balance
    ):
        """
        Inserts:
        1) Wallet row in Wallets
        2) Student row in Students
        3) Entity row in KSU_Entities (so every student appears as an entity too)
        """
        try:
            wallet_id = self.generate_unique_wallet_id()
            create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 1) Wallet
            self.cur.execute(
                """
                INSERT INTO Wallets (Wallet_ID, Owner_type, Balance, Create_time)
                VALUES (?, ?, ?, ?)
                """,
                (wallet_id, "student", initial_balance, create_time)
            )

            # 2) Student
            self.cur.execute(
                """
                INSERT INTO Students (Student_ID, FirstName, LastName, email, PhoneNo, wallet_id, password)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (student_id, first_name, last_name, email, phone_no, wallet_id, hashed_password)
            )

            # 3) Entity (student also saved as an entity)
            full_name = f"{first_name} {last_name}"
            self.cur.execute(
                """
                INSERT INTO KSU_Entities (Entity_ID, Name, wallet_id)
                VALUES (?, ?, ?)
                """,
                (student_id, full_name, wallet_id)
            )

            self.conn.commit()
            return True

        except Exception as e:
            self.conn.rollback()
            raise e

    # -------------------------------------------------
    def close(self):
        self.conn.close()
