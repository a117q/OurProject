import sqlite3

#connect to database
conn = sqlite3.connect('Database.db')
cur= conn.cursor()
print('Database created successfully')
#student
cur.execute("""CREATE TABLE Students( 
            Student_ID INT(10) PRIMARY KEY NOT NULL,
            FirstName TEXT NOT NULL,
            LastName TEXT NOT NULL,
            email TEXT NOT NULL,
            PhoneNo INT,
            wallet_id INT(10),
            FOREIGN KEY (wallet_id) REFERENCES Wallets(Wallet_ID)
        )""")
print('Students table created successfully')

#entities
cur.execute("""CREATE TABLE KSU_Entities(
            Entity_ID INT(10) PRIMARY KEY NOT NULL,
            Name TEXT NOT NULL,
            wallet_id INT(10),
            FOREIGN KEY (wallet_id) REFERENCES Wallets(Wallet_ID)
        )""")
print('KSU_Entities table created successfully')

#Wallet
cur.execute("""CREATE TABLE Wallets(
            Wallet_ID INT(10) PRIMARY KEY NOT NULL,
            Owner_type TEXT NOT NULL,   -- 'student' or 'ksu'
            Balance FLOAT,
            Create_time DATETIME
        )""")
print('Wallet table created successfully')

#Transaction
cur.execute("""CREATE TABLE Transactions(
            Transaction_ID INT PRIMARY KEY NOT NULL,
            from_wallet_id INT(10),
            to_wallet_id INT(10) NOT NULL,
            Type TEXT, 
            Time DATETIME,
            FOREIGN KEY (to_wallet_id) REFERENCES Wallets(Wallet_ID),
            FOREIGN KEY (from_wallet_id) REFERENCES Wallets(Wallet_ID)
        )""")
print('Transactions table created successfully')

conn.commit()
conn.close()