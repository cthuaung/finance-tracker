from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum
import os
from datetime import datetime

# Create database directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data'), exist_ok=True)

# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'finance.db')
engine = create_engine(f'sqlite:///{DB_PATH}')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class TransactionType(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    color = Column(String, default="#3498db")  # Hex color code for visual representation
    type = Column(Enum(TransactionType), nullable=False)
    
    transactions = relationship("Transaction", back_populates="category")
    
    def __repr__(self):
        return f"<Category(name='{self.name}', type='{self.type}')>"

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    date = Column(Date, nullable=False, default=datetime.now().date)
    type = Column(Enum(TransactionType), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    timestamp = Column(DateTime, default=datetime.now)
    
    category = relationship("Category", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(amount='{self.amount}', type='{self.type}', date='{self.date}')>"

class Budget(Base):
    __tablename__ = 'budgets'
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    amount = Column(Float, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    
    category = relationship("Category")
    
    def __repr__(self):
        return f"<Budget(category_id='{self.category_id}', amount='{self.amount}', month='{self.month}', year='{self.year}')>"

def init_db():
    """Initialize the database with tables and default categories"""
    Base.metadata.create_all(engine)
    
    session = Session()
    
    # Check if categories already exist
    if session.query(Category).count() == 0:
        # Add default categories
        default_categories = [
            # Income categories
            Category(name="Salary", type=TransactionType.INCOME, color="#27ae60"),
            Category(name="Investments", type=TransactionType.INCOME, color="#3498db"),
            Category(name="Gifts", type=TransactionType.INCOME, color="#9b59b6"),
            Category(name="Other Income", type=TransactionType.INCOME, color="#f1c40f"),
            
            # Expense categories
            Category(name="Housing", type=TransactionType.EXPENSE, color="#e74c3c"),
            Category(name="Transportation", type=TransactionType.EXPENSE, color="#e67e22"),
            Category(name="Food", type=TransactionType.EXPENSE, color="#d35400"),
            Category(name="Utilities", type=TransactionType.EXPENSE, color="#c0392b"),
            Category(name="Entertainment", type=TransactionType.EXPENSE, color="#8e44ad"),
            Category(name="Health", type=TransactionType.EXPENSE, color="#16a085"),
            Category(name="Shopping", type=TransactionType.EXPENSE, color="#2c3e50"),
            Category(name="Personal", type=TransactionType.EXPENSE, color="#7f8c8d"),
            Category(name="Education", type=TransactionType.EXPENSE, color="#2980b9"),
            Category(name="Other Expenses", type=TransactionType.EXPENSE, color="#95a5a6"),
        ]
        
        session.add_all(default_categories)
        session.commit()
    
    session.close()

if __name__ == "__main__":
    init_db() 