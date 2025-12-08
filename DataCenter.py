import random
import hashlib
from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Text,
    exists,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class Wallet(Base):
    __tablename__ = "Wallets"

    Wallet_ID = Column(Integer, primary_key=True)
    Owner_type = Column(String, nullable=False)    # 'student' or 'ksu'
    Balance = Column(Float, default=0)
    Create_time = Column(DateTime)

    student = relationship("Student", back_populates="wallet", uselist=False)
    entity = relationship("KSUEntity", back_populates="wallet", uselist=False)

    from_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.from_wallet_id",
        back_populates="from_wallet",
    )
    to_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.to_wallet_id",
        back_populates="to_wallet",
    )


class Manager(Base):
    __tablename__ = "Managers"

    Manager_ID = Column(String, primary_key=True)
    Password = Column(Text, nullable=False)
    FirstName = Column(String, nullable=False)
    LastName = Column(String, nullable=False)
    
class Student(Base):
    __tablename__ = "Students"

    Student_ID = Column(Integer, primary_key=True)   # 10-digit
    FirstName = Column(String, nullable=False)
    LastName = Column(String, nullable=False)
    email = Column(String, nullable=False)
    PhoneNo = Column(Integer)
    wallet_id = Column(Integer, ForeignKey("Wallets.Wallet_ID"))
    password = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint("length(password) >= 8", name="ck_students_password_len"),
    )

    wallet = relationship("Wallet", back_populates="student")


class KSUEntity(Base):
    __tablename__ = "KSU_Entities"

    Entity_ID = Column(Integer, primary_key=True)
    Name = Column(String, nullable=False)
    wallet_id = Column(Integer, ForeignKey("Wallets.Wallet_ID"))

    wallet = relationship("Wallet", back_populates="entity")


class Transaction(Base):
    __tablename__ = "Transactions"

    Transaction_ID = Column(Integer, primary_key=True)
    from_wallet_id = Column(Integer, ForeignKey("Wallets.Wallet_ID"))
    to_wallet_id = Column(Integer, ForeignKey("Wallets.Wallet_ID"), nullable=False)
    Type = Column(String)
    Time = Column(DateTime)

    from_wallet = relationship(
        "Wallet",
        foreign_keys=[from_wallet_id],
        back_populates="from_transactions",
    )
    to_wallet = relationship(
        "Wallet",
        foreign_keys=[to_wallet_id],
        back_populates="to_transactions",
    )

class DataCenter:
    def __init__(self, db_url="sqlite:///Database.db"):
        #SQLAlchemy
        self.engine = create_engine(db_url, echo=False, future=True)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

    # Wallet / Student helpers 
    def generate_unique_wallet_id(self):
        """Generates a unique 10-digit Wallet ID."""
        with self.SessionLocal() as session:
            while True:
                wallet_id = random.randint(1000000000, 9999999999)
                exists_q = session.query(
                    exists().where(Wallet.Wallet_ID == wallet_id)
                ).scalar()
                if not exists_q:
                    return wallet_id

    def check_student_id_exists(self, student_id):
        """Checks if a Student ID is already in the database."""
        with self.SessionLocal() as session:
            return session.query(
                exists().where(Student.Student_ID == student_id)
            ).scalar()

    def check_email_exists(self, email):
        """Checks if an email is already used by a student."""
        with self.SessionLocal() as session:
            return session.query(
                exists().where(Student.email == email)
            ).scalar()

    def check_student_login(self, student_id, hashed_password):
        """Returns True if (Student_ID, password) match in Students table."""
        with self.SessionLocal() as session:
            return session.query(
                exists().where(
                    (Student.Student_ID == student_id)
                    & (Student.password == hashed_password)
                )
            ).scalar()

    def get_all_students_with_wallet(self):
        """
        Returns a list of tuples:
        (Student_ID, FirstName, LastName, Email, Wallet_ID, Balance)
        """
        with self.SessionLocal() as session:
            rows = (
                session.query(
                    Student.Student_ID,
                    Student.FirstName,
                    Student.LastName,
                    Student.email,
                    Wallet.Wallet_ID,
                    Wallet.Balance,
                )
                .join(Wallet, Student.wallet_id == Wallet.Wallet_ID)
                .order_by(Student.Student_ID)
                .all()
            )
            return rows

    # Manager helpers 
    def add_initial_manager(self):
        """
        Adds one default manager if Managers table is empty.
        ID:        1234567890
        Password:  ad223344 (stored as SHA-256 hash)
        Name:      Admin User
        """
        with self.SessionLocal() as session:
            any_manager = session.query(Manager).first()
            if any_manager:
                return

            manager_id = "1234567890"
            plain_password = "ad223344"
            hashed_password = hashlib.sha256(
                plain_password.encode("utf-8")
            ).hexdigest()

            m = Manager(
                Manager_ID=manager_id,
                Password=hashed_password,
                FirstName="Admin",
                LastName="User",
            )
            session.add(m)
            session.commit()

    def check_manager_login(self, manager_id, hashed_password):
        """Returns True if (Manager_ID, Password) match in Managers table."""
        with self.SessionLocal() as session:
            return session.query(
                exists().where(
                    (Manager.Manager_ID == manager_id)
                    & (Manager.Password == hashed_password)
                )
            ).scalar()

    def get_manager_info(self, manager_id):
        """
        Returns dict with manager info, or None if not found:
        {
            'manager_id': ...,
            'first_name': ...,
            'last_name': ...
        }
        """
        with self.SessionLocal() as session:
            m = (
                session.query(Manager)
                .filter(Manager.Manager_ID == manager_id)
                .first()
            )
            if m is None:
                return None
            return {
                "manager_id": m.Manager_ID,
                "first_name": m.FirstName,
                "last_name": m.LastName,
            }

    def check_manager_id_exists(self, manager_id):
        """Returns True if this ID already exists in Managers table."""
        with self.SessionLocal() as session:
            return session.query(
                exists().where(Manager.Manager_ID == manager_id)
            ).scalar()

    # Insert student + wallet + entity 
    def add_student_and_wallet(
        self,
        student_id,
        first_name,
        last_name,
        email,
        phone_no,
        hashed_password,
        initial_balance,
    ):
        """
        Inserts:
        1) Wallet row in Wallets
        2) Student row in Students
        3) Entity row in KSU_Entities (so every student appears as an entity too)
        """
        with self.SessionLocal() as session:
            try:
                wallet_id = self.generate_unique_wallet_id()
                create_time = datetime.now()

                #Wallet

                wallet = Wallet(
                    Wallet_ID=wallet_id,
                    Owner_type="student",
                    Balance=initial_balance,
                    Create_time=create_time,
                )
                session.add(wallet)

                # Student
                student = Student(
                    Student_ID=student_id,
                    FirstName=first_name,
                    LastName=last_name,
                    email=email,
                    PhoneNo=phone_no,
                    wallet_id=wallet_id,
                    password=hashed_password,
                )
                session.add(student)

                #Entity (student also saved as an entity)
                full_name = f"{first_name} {last_name}"
                entity = KSUEntity(
                    Entity_ID=student_id,
                    Name=full_name,
                    wallet_id=wallet_id,
                )
                session.add(entity)

                session.commit()
                return True

            except Exception:
                session.rollback()
                raise

    def close(self):
        """For compatibility with old code (nothing special needed here)."""
        self.engine.dispose()
