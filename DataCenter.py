# DataCenter.py
# DataCenter.py
import sqlite3
import random
from datetime import datetime

class DataCenter:
    def __init__(self, db_name="Database.db"):
        # connect to database
        self.conn = sqlite3.connect(db_name)     
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cur = self.conn.cursor()
        # create tables if they don't exist
        self._create_tables()

    def _create_tables(self):
        # Wallet table (must be created first)
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS Wallets(
            Wallet_ID   INT(10) PRIMARY KEY NOT NULL,
            Owner_type  TEXT NOT NULL,   -- 'student' or 'ksu'
            Balance     FLOAT,
            Create_time DATETIME
        )
        """)

        # Students table (with password)
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

    def generate_unique_wallet_id(self):
        #Generates a unique 10-digit Wallet ID.
        while True:
            # Generate a 10-digit number
            wallet_id = random.randint(1000000000, 9999999999)
            exists = False
            for _ in self.cur.execute("SELECT 1 FROM Wallets WHERE Wallet_ID = ?", (wallet_id,)):
                exists = True
                break
            if not exists:
                return wallet_id
        
    def check_student_id_exists(self, student_id):
        #Checks if a Student ID is already in the database.
        for _ in self.cur.execute("SELECT 1 FROM Students WHERE Student_ID = ?", (student_id,)):
            return True
        return False

    def check_email_exists(self, email):
        for _ in self.cur.execute("SELECT 1 FROM Students WHERE email = ?", (email,)):
            return True
        return False

    def add_student_and_wallet(self, student_id, first_name, last_name, email, phone_no, hashed_password, initial_balance):
        """Performs two inserts: Wallets and Students in one transaction."""
        try:
            wallet_id = self.generate_unique_wallet_id()
            create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Insert into Wallets table
            self.cur.execute(
            """
            INSERT INTO Wallets (Wallet_ID, Owner_type, Balance, Create_time)
            VALUES (?, ?, ?, ?)
            """,
                (wallet_id, "student", initial_balance, create_time)
            )

        # 2. Insert into Students table (using the HASHED password)
            self.cur.execute(
            """
            INSERT INTO Students (Student_ID, FirstName, LastName, email, PhoneNo, wallet_id, password)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (student_id, first_name, last_name, email, phone_no, wallet_id, hashed_password)
            )
        
            self.conn.commit()
            return True

        except Exception as e:
            self.conn.rollback()
            raise e

    def close(self):
        self.conn.close()
