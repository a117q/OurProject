# DataCenter.py
import sqlite3

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

    def close(self):
        self.conn.close()
