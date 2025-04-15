from datetime import datetime, timedelta
from sqlalchemy import extract, func
import pandas as pd

from .database import Session, Category, Transaction, TransactionType, Budget

class DataManager:
    """
    Handles all database operations for the finance tracker
    """
    @staticmethod
    def add_transaction(amount, description, date, transaction_type, category_id):
        session = Session()
        
        try:
            new_transaction = Transaction(
                amount=amount,
                description=description,
                date=date,
                type=transaction_type,
                category_id=category_id
            )
            
            session.add(new_transaction)
            session.commit()
            return new_transaction.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def update_transaction(transaction_id, **kwargs):
        session = Session()
        
        try:
            transaction = session.query(Transaction).filter_by(id=transaction_id).first()
            
            if not transaction:
                return False
            
            for key, value in kwargs.items():
                if hasattr(transaction, key):
                    setattr(transaction, key, value)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def delete_transaction(transaction_id):
        session = Session()
        
        try:
            transaction = session.query(Transaction).filter_by(id=transaction_id).first()
            
            if not transaction:
                return False
            
            session.delete(transaction)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_transactions(start_date=None, end_date=None, category_id=None, transaction_type=None):
        session = Session()
        
        try:
            query = session.query(Transaction)
            
            if start_date:
                query = query.filter(Transaction.date >= start_date)
            
            if end_date:
                query = query.filter(Transaction.date <= end_date)
            
            if category_id:
                query = query.filter(Transaction.category_id == category_id)
            
            if transaction_type:
                query = query.filter(Transaction.type == transaction_type)
            
            # Execute the query and get all results before closing the session
            transactions = query.order_by(Transaction.date.desc()).all()
            
            # Return a copy of the list so SQLAlchemy doesn't track these objects
            return list(transactions)
        finally:
            session.close()
    
    @staticmethod
    def get_categories(transaction_type=None):
        session = Session()
        
        try:
            query = session.query(Category)
            
            if transaction_type:
                query = query.filter(Category.type == transaction_type)
            
            return query.order_by(Category.name).all()
        finally:
            session.close()
    
    @staticmethod
    def add_category(name, transaction_type, color="#3498db"):
        session = Session()
        
        try:
            new_category = Category(
                name=name,
                type=transaction_type,
                color=color
            )
            
            session.add(new_category)
            session.commit()
            return new_category.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def update_category(category_id, **kwargs):
        session = Session()
        
        try:
            category = session.query(Category).filter_by(id=category_id).first()
            
            if not category:
                return False
            
            for key, value in kwargs.items():
                if hasattr(category, key):
                    setattr(category, key, value)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def delete_category(category_id):
        session = Session()
        
        try:
            # First check if there are any transactions with this category
            transaction_count = session.query(Transaction).filter_by(category_id=category_id).count()
            
            if transaction_count > 0:
                return False  # Cannot delete a category that has transactions
            
            category = session.query(Category).filter_by(id=category_id).first()
            
            if not category:
                return False
            
            session.delete(category)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_transaction_totals(start_date=None, end_date=None, group_by='day'):
        """
        Get transaction totals grouped by specified time period
        group_by: 'day', 'week', 'month', or 'year'
        """
        session = Session()
        
        try:
            if not start_date:
                start_date = datetime.now().date() - timedelta(days=30)
            
            if not end_date:
                end_date = datetime.now().date()
            
            # Base query
            query = session.query(
                Transaction.date,
                Transaction.type,
                func.sum(Transaction.amount).label('total')
            ).filter(
                Transaction.date.between(start_date, end_date)
            )
            
            # Group by the specified time period
            if group_by == 'day':
                query = query.group_by(Transaction.date, Transaction.type)
            elif group_by == 'week':
                # SQLite doesn't have a built-in week function, so we'll handle grouping in Python
                transactions = query.all()
                
                # Convert to DataFrame for easier manipulation
                df = pd.DataFrame([(t.date, t.type.value, t.total) for t in transactions], 
                                 columns=['date', 'type', 'total'])
                
                # Add week column
                df['week'] = df['date'].apply(lambda x: x.isocalendar()[1])
                df['year'] = df['date'].apply(lambda x: x.year)
                
                # Group by week
                return df.groupby(['year', 'week', 'type']).sum().reset_index()
            
            elif group_by == 'month':
                query = query.group_by(
                    extract('year', Transaction.date),
                    extract('month', Transaction.date),
                    Transaction.type
                )
            elif group_by == 'year':
                query = query.group_by(
                    extract('year', Transaction.date),
                    Transaction.type
                )
            
            # Execute the query and return results
            return query.order_by(Transaction.date).all()
        finally:
            session.close()
    
    @staticmethod
    def get_category_breakdown(start_date=None, end_date=None, transaction_type=TransactionType.EXPENSE):
        """Get the breakdown of transactions by category"""
        session = Session()
        
        try:
            if not start_date:
                start_date = datetime.now().date() - timedelta(days=30)
            
            if not end_date:
                end_date = datetime.now().date()
            
            result = session.query(
                Category.name,
                Category.color,
                func.sum(Transaction.amount).label('total')
            ).join(
                Transaction
            ).filter(
                Transaction.date.between(start_date, end_date),
                Transaction.type == transaction_type
            ).group_by(
                Category.id
            ).order_by(
                func.sum(Transaction.amount).desc()
            ).all()
            
            # Convert SQLAlchemy Row objects to a list of tuples (name, total, color)
            # as expected by the pie chart function
            return [(row[0], row[2], row[1]) for row in result]
        finally:
            session.close()
    
    @staticmethod
    def get_budget_status(month, year):
        """Get budget status for each category"""
        session = Session()
        
        try:
            # Get all budgets for the specified month and year
            budgets = session.query(
                Budget.category_id,
                Budget.amount,
                Category.name,
                Category.color
            ).join(
                Category
            ).filter(
                Budget.month == month,
                Budget.year == year,
                Category.type == TransactionType.EXPENSE
            ).all()
            
            # Calculate actual spending for each category
            results = []
            for budget in budgets:
                start_date = datetime(year, month, 1).date()
                
                # Calculate end date (last day of the month)
                if month == 12:
                    end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
                
                # Get actual spending
                actual = session.query(
                    func.sum(Transaction.amount)
                ).filter(
                    Transaction.category_id == budget.category_id,
                    Transaction.date.between(start_date, end_date),
                    Transaction.type == TransactionType.EXPENSE
                ).scalar() or 0
                
                results.append({
                    'category_id': budget.category_id,
                    'category_name': budget.name,
                    'color': budget.color,
                    'budget_amount': budget.amount,
                    'actual_amount': actual,
                    'remaining': budget.amount - actual,
                    'percentage': (actual / budget.amount) * 100 if budget.amount > 0 else 0
                })
            
            return results
        finally:
            session.close()
    
    @staticmethod
    def set_budget(category_id, amount, month, year):
        """Set or update a budget for a category"""
        session = Session()
        
        try:
            # Check if budget already exists
            existing_budget = session.query(Budget).filter_by(
                category_id=category_id,
                month=month,
                year=year
            ).first()
            
            if existing_budget:
                existing_budget.amount = amount
            else:
                new_budget = Budget(
                    category_id=category_id,
                    amount=amount,
                    month=month,
                    year=year
                )
                session.add(new_budget)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @staticmethod
    def get_income_vs_expenses(start_date=None, end_date=None, group_by='month'):
        """Get income vs expenses over time"""
        session = Session()
        
        try:
            if not start_date:
                start_date = datetime.now().date() - timedelta(days=365)
            
            if not end_date:
                end_date = datetime.now().date()
            
            # Different grouping based on the time period requested
            if group_by == 'day':
                results = session.query(
                    Transaction.date,
                    Transaction.type,
                    func.sum(Transaction.amount).label('total')
                ).filter(
                    Transaction.date.between(start_date, end_date)
                ).group_by(
                    Transaction.date,
                    Transaction.type
                ).order_by(
                    Transaction.date
                ).all()
                
                # Convert to a more useful format
                data = {}
                for result in results:
                    date_str = result.date.strftime('%Y-%m-%d')
                    if date_str not in data:
                        data[date_str] = {'date': date_str, 'income': 0, 'expense': 0}
                    
                    if result.type == TransactionType.INCOME:
                        data[date_str]['income'] = result.total
                    elif result.type == TransactionType.EXPENSE:
                        data[date_str]['expense'] = result.total
                
                return list(data.values())
            
            elif group_by == 'month':
                results = session.query(
                    extract('year', Transaction.date).label('year'),
                    extract('month', Transaction.date).label('month'),
                    Transaction.type,
                    func.sum(Transaction.amount).label('total')
                ).filter(
                    Transaction.date.between(start_date, end_date)
                ).group_by(
                    extract('year', Transaction.date),
                    extract('month', Transaction.date),
                    Transaction.type
                ).order_by(
                    extract('year', Transaction.date),
                    extract('month', Transaction.date)
                ).all()
                
                # Convert to a more useful format
                data = {}
                for result in results:
                    date_str = f"{int(result.year)}-{int(result.month):02d}"
                    if date_str not in data:
                        data[date_str] = {'date': date_str, 'income': 0, 'expense': 0}
                    
                    if result.type == TransactionType.INCOME:
                        data[date_str]['income'] = result.total
                    elif result.type == TransactionType.EXPENSE:
                        data[date_str]['expense'] = result.total
                
                return list(data.values())
            
            else:  # year
                results = session.query(
                    extract('year', Transaction.date).label('year'),
                    Transaction.type,
                    func.sum(Transaction.amount).label('total')
                ).filter(
                    Transaction.date.between(start_date, end_date)
                ).group_by(
                    extract('year', Transaction.date),
                    Transaction.type
                ).order_by(
                    extract('year', Transaction.date)
                ).all()
                
                # Convert to a more useful format
                data = {}
                for result in results:
                    year_str = str(int(result.year))
                    if year_str not in data:
                        data[year_str] = {'date': year_str, 'income': 0, 'expense': 0}
                    
                    if result.type == TransactionType.INCOME:
                        data[year_str]['income'] = result.total
                    elif result.type == TransactionType.EXPENSE:
                        data[year_str]['expense'] = result.total
                
                return list(data.values())
        finally:
            session.close() 