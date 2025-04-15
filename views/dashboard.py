"""
Dashboard widget for the Finance Tracker application
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSplitter, QSizePolicy, QComboBox, QGridLayout, QGroupBox,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QDate, pyqtSlot
from PyQt6.QtGui import QFont

from datetime import datetime, timedelta
import matplotlib.pyplot as plt

from ..utils.visualizations import MplCanvas, create_pie_chart, create_bar_chart, create_line_chart
from ..models.data_manager import DataManager
from ..models.database import TransactionType


class DashboardWidget(QWidget):
    """Dashboard widget for the Finance Tracker application"""
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.refresh_dashboard()
    
    def setup_ui(self):
        """Set up the dashboard UI"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Header section
        self.setup_header()
        
        # Time period selector
        self.setup_time_period_selector()
        
        # Main dashboard content
        self.setup_dashboard_content()
    
    def setup_header(self):
        """Set up the dashboard header"""
        header_layout = QHBoxLayout()
        
        # Dashboard title
        dashboard_title = QLabel("Finance Dashboard")
        dashboard_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        
        # Add to layout
        header_layout.addWidget(dashboard_title)
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_dashboard)
        header_layout.addWidget(self.refresh_button)
        
        self.main_layout.addLayout(header_layout)
    
    def setup_time_period_selector(self):
        """Set up the time period selector controls"""
        time_period_layout = QHBoxLayout()
        
        # Label
        time_period_label = QLabel("Show data for:")
        time_period_layout.addWidget(time_period_label)
        
        # Time period combobox
        self.time_period_combo = QComboBox()
        self.time_period_combo.addItems([
            "Last 7 days",
            "Last 30 days",
            "This month",
            "Last month",
            "Last 3 months",
            "Last 6 months",
            "This year",
            "Last year",
            "All time"
        ])
        self.time_period_combo.setCurrentIndex(1)  # Default to "Last 30 days"
        self.time_period_combo.currentIndexChanged.connect(self.refresh_dashboard)
        
        time_period_layout.addWidget(self.time_period_combo)
        time_period_layout.addStretch()
        
        self.main_layout.addLayout(time_period_layout)
    
    def setup_dashboard_content(self):
        """Set up the main dashboard content"""
        # Create a scroll area for the dashboard content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create a widget for the scroll area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # Create summary cards section
        self.setup_summary_cards(scroll_layout)
        
        # Create charts section
        self.setup_charts(scroll_layout)
        
        # Set the scroll content
        scroll_area.setWidget(scroll_content)
        
        # Add to main layout
        self.main_layout.addWidget(scroll_area)
    
    def setup_summary_cards(self, parent_layout):
        """Set up the summary cards section"""
        # Create group box for summary cards
        summary_group = QGroupBox("Financial Summary")
        summary_layout = QGridLayout()
        summary_group.setLayout(summary_layout)
        
        # Create summary cards
        # Income Card
        self.income_card = SummaryCard("Total Income", "$0.00", "#27ae60")
        summary_layout.addWidget(self.income_card, 0, 0)
        
        # Expenses Card
        self.expenses_card = SummaryCard("Total Expenses", "$0.00", "#e74c3c")
        summary_layout.addWidget(self.expenses_card, 0, 1)
        
        # Balance Card
        self.balance_card = SummaryCard("Net Balance", "$0.00", "#3498db")
        summary_layout.addWidget(self.balance_card, 0, 2)
        
        # Transactions Card
        self.transactions_card = SummaryCard("Transactions", "0", "#9b59b6")
        summary_layout.addWidget(self.transactions_card, 1, 0)
        
        # Avg. Expense Card
        self.avg_expense_card = SummaryCard("Avg. Daily Expense", "$0.00", "#e67e22")
        summary_layout.addWidget(self.avg_expense_card, 1, 1)
        
        # Largest Expense Card
        self.largest_expense_card = SummaryCard("Largest Expense", "$0.00", "#c0392b")
        summary_layout.addWidget(self.largest_expense_card, 1, 2)
        
        # Add to parent layout
        parent_layout.addWidget(summary_group)
    
    def setup_charts(self, parent_layout):
        """Set up the charts section"""
        # Create charts layout
        charts_layout = QGridLayout()
        charts_layout.setVerticalSpacing(20)
        charts_layout.setHorizontalSpacing(20)
        
        # Create Income vs Expenses chart container
        self.income_expenses_chart = ChartWidget("Income vs Expenses")
        charts_layout.addWidget(self.income_expenses_chart, 0, 0)
        
        # Create Expense Categories chart container
        self.expense_categories_chart = ChartWidget("Expense Categories")
        charts_layout.addWidget(self.expense_categories_chart, 0, 1)
        
        # Create Daily Spending chart container
        self.daily_spending_chart = ChartWidget("Daily Spending")
        charts_layout.addWidget(self.daily_spending_chart, 1, 0)
        
        # Create Income Categories chart container
        self.income_categories_chart = ChartWidget("Income Sources")
        charts_layout.addWidget(self.income_categories_chart, 1, 1)
        
        parent_layout.addLayout(charts_layout)
    
    def refresh_dashboard(self):
        """Refresh all dashboard data and charts"""
        # Get date range from the combobox selection
        start_date, end_date = self.get_selected_date_range()
        
        # Load and display summary data
        self.update_summary_cards(start_date, end_date)
        
        # Load and display charts
        self.update_charts(start_date, end_date)
    
    def get_selected_date_range(self):
        """Get the date range based on the selected time period"""
        today = datetime.now().date()
        
        index = self.time_period_combo.currentIndex()
        
        if index == 0:  # Last 7 days
            start_date = today - timedelta(days=6)
            end_date = today
        elif index == 1:  # Last 30 days
            start_date = today - timedelta(days=29)
            end_date = today
        elif index == 2:  # This month
            start_date = today.replace(day=1)
            end_date = today
        elif index == 3:  # Last month
            last_month = today.month - 1
            last_month_year = today.year
            if last_month == 0:
                last_month = 12
                last_month_year -= 1
            
            start_date = today.replace(year=last_month_year, month=last_month, day=1)
            # Get the last day of last month
            if last_month == 12:
                end_date = today.replace(year=last_month_year, month=last_month, day=31)
            else:
                end_date = today.replace(year=last_month_year, month=last_month + 1, day=1) - timedelta(days=1)
        elif index == 4:  # Last 3 months
            start_date = today - timedelta(days=90)
            end_date = today
        elif index == 5:  # Last 6 months
            start_date = today - timedelta(days=180)
            end_date = today
        elif index == 6:  # This year
            start_date = today.replace(month=1, day=1)
            end_date = today
        elif index == 7:  # Last year
            start_date = today.replace(year=today.year - 1, month=1, day=1)
            end_date = today.replace(year=today.year - 1, month=12, day=31)
        else:  # All time
            start_date = None
            end_date = None
        
        return start_date, end_date
    
    def update_summary_cards(self, start_date, end_date):
        """Update the summary cards with data from the selected period"""
        # Get transactions for the period
        income_transactions = DataManager.get_transactions(
            start_date=start_date,
            end_date=end_date,
            transaction_type=TransactionType.INCOME
        )
        
        expense_transactions = DataManager.get_transactions(
            start_date=start_date,
            end_date=end_date,
            transaction_type=TransactionType.EXPENSE
        )
        
        # Calculate total income
        total_income = sum(t.amount for t in income_transactions)
        
        # Calculate total expenses
        total_expenses = sum(t.amount for t in expense_transactions)
        
        # Calculate net balance
        net_balance = total_income - total_expenses
        
        # Calculate total number of transactions
        total_transactions = len(income_transactions) + len(expense_transactions)
        
        # Calculate average daily expense
        if start_date and end_date:
            days_in_period = (end_date - start_date).days + 1
        else:
            # Get the date of the first transaction as a fallback
            all_transactions = income_transactions + expense_transactions
            if all_transactions:
                first_transaction_date = min(t.date for t in all_transactions)
                days_in_period = (datetime.now().date() - first_transaction_date).days + 1
            else:
                days_in_period = 1
        
        avg_daily_expense = total_expenses / days_in_period if days_in_period > 0 else 0
        
        # Find largest expense
        largest_expense = max(expense_transactions, key=lambda t: t.amount).amount if expense_transactions else 0
        
        # Update summary cards
        self.income_card.set_value(f"${total_income:.2f}")
        self.expenses_card.set_value(f"${total_expenses:.2f}")
        
        # Set balance color based on value
        balance_color = "#27ae60" if net_balance >= 0 else "#e74c3c"
        self.balance_card.set_value(f"${net_balance:.2f}", balance_color)
        
        self.transactions_card.set_value(str(total_transactions))
        self.avg_expense_card.set_value(f"${avg_daily_expense:.2f}")
        self.largest_expense_card.set_value(f"${largest_expense:.2f}")
    
    def update_charts(self, start_date, end_date):
        """Update all charts with data from the selected period"""
        # Update Income vs Expenses chart
        self.update_income_expenses_chart(start_date, end_date)
        
        # Update Expense Categories chart
        self.update_expense_categories_chart(start_date, end_date)
        
        # Update Daily Spending chart
        self.update_daily_spending_chart(start_date, end_date)
        
        # Update Income Categories chart
        self.update_income_categories_chart(start_date, end_date)
    
    def update_income_expenses_chart(self, start_date, end_date):
        """Update the Income vs Expenses chart"""
        # Determine appropriate grouping based on the date range
        if start_date and end_date:
            days_in_period = (end_date - start_date).days + 1
            
            if days_in_period <= 31:
                group_by = 'day'
            elif days_in_period <= 180:
                group_by = 'month'
            else:
                group_by = 'month'
        else:
            group_by = 'month'
        
        # Get income vs expenses data
        data = DataManager.get_income_vs_expenses(start_date, end_date, group_by)
        
        if data:
            # Create chart
            fig = create_line_chart(
                data=data,
                x_key='date',
                y_keys=['income', 'expense'],
                labels=['Income', 'Expenses'],
                title='Income vs Expenses',
                colors=['#27ae60', '#e74c3c'],
                x_label='Date',
                y_label='Amount ($)',
                x_date_format=True
            )
            
            # Set chart in widget
            self.income_expenses_chart.set_chart(fig)
        else:
            self.income_expenses_chart.clear_chart()
            self.income_expenses_chart.set_message("No data available for the selected period")
    
    def update_expense_categories_chart(self, start_date, end_date):
        """Update the Expense Categories chart"""
        # Get category breakdown data
        data = DataManager.get_category_breakdown(
            start_date=start_date,
            end_date=end_date,
            transaction_type=TransactionType.EXPENSE
        )
        
        if data:
            # Create chart
            fig = create_pie_chart(
                data=data,
                title='Expense Categories'
            )
            
            # Set chart in widget
            self.expense_categories_chart.set_chart(fig)
        else:
            self.expense_categories_chart.clear_chart()
            self.expense_categories_chart.set_message("No expense data available for the selected period")
    
    def update_daily_spending_chart(self, start_date, end_date):
        """Update the Daily Spending chart"""
        # Determine appropriate grouping based on the date range
        if start_date and end_date:
            days_in_period = (end_date - start_date).days + 1
            
            if days_in_period <= 31:
                group_by = 'day'
            elif days_in_period <= 180:
                group_by = 'month'
            else:
                group_by = 'month'
        else:
            group_by = 'month'
        
        # Get transaction totals
        data = DataManager.get_transaction_totals(start_date, end_date, group_by)
        
        if data:
            # Convert data to format needed for chart
            chart_data = []
            
            for item in data:
                if item.type == TransactionType.EXPENSE:
                    date_str = item.date.strftime('%Y-%m-%d') if group_by == 'day' else f"{item.date.year}-{item.date.month}"
                    chart_data.append({
                        'date': date_str,
                        'amount': item.total
                    })
            
            if chart_data:
                # Create chart
                fig = create_bar_chart(
                    data=chart_data,
                    x_key='date',
                    y_keys=['amount'],
                    labels=['Expenses'],
                    title='Daily Spending',
                    colors=['#e74c3c'],
                    x_label='Date',
                    y_label='Amount ($)'
                )
                
                # Set chart in widget
                self.daily_spending_chart.set_chart(fig)
            else:
                self.daily_spending_chart.clear_chart()
                self.daily_spending_chart.set_message("No expense data available for the selected period")
        else:
            self.daily_spending_chart.clear_chart()
            self.daily_spending_chart.set_message("No expense data available for the selected period")
    
    def update_income_categories_chart(self, start_date, end_date):
        """Update the Income Categories chart"""
        # Get category breakdown data
        data = DataManager.get_category_breakdown(
            start_date=start_date,
            end_date=end_date,
            transaction_type=TransactionType.INCOME
        )
        
        if data:
            # Create chart
            fig = create_pie_chart(
                data=data,
                title='Income Sources'
            )
            
            # Set chart in widget
            self.income_categories_chart.set_chart(fig)
        else:
            self.income_categories_chart.clear_chart()
            self.income_categories_chart.set_message("No income data available for the selected period")


class SummaryCard(QFrame):
    """A card widget for displaying a summary statistic"""
    
    def __init__(self, title, value, color="#3498db"):
        super().__init__()
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setObjectName("summaryCard")
        
        # Apply some custom styling
        self.setStyleSheet(f"""
            #summaryCard {{
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e1e1e1;
            }}
            #titleLabel {{
                color: #555;
                font-size: 14px;
            }}
            #valueLabel {{
                color: {color};
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        
        # Set up layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        # Create title label
        self.title_label = QLabel(title)
        self.title_label.setObjectName("titleLabel")
        layout.addWidget(self.title_label)
        
        # Create value label
        self.value_label = QLabel(value)
        self.value_label.setObjectName("valueLabel")
        layout.addWidget(self.value_label)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(120)
    
    def set_value(self, value, color=None):
        """Set the value displayed in the card"""
        self.value_label.setText(value)
        
        if color:
            self.value_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")


class ChartWidget(QFrame):
    """A widget for displaying a chart"""
    
    def __init__(self, title):
        super().__init__()
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setObjectName("chartWidget")
        
        # Apply some custom styling
        self.setStyleSheet("""
            #chartWidget {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e1e1e1;
            }
            #titleLabel {
                color: #333;
                font-size: 16px;
                font-weight: bold;
            }
            #messageLabel {
                color: #888;
                font-size: 14px;
                font-style: italic;
            }
        """)
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)
        
        # Create title label
        self.title_label = QLabel(title)
        self.title_label.setObjectName("titleLabel")
        self.layout.addWidget(self.title_label)
        
        # Create placeholder for chart or message
        self.chart_canvas = None
        self.message_label = QLabel("No data available")
        self.message_label.setObjectName("messageLabel")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.hide()
        self.layout.addWidget(self.message_label)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(300)
    
    def set_chart(self, fig):
        """Set the matplotlib figure to display"""
        # Clear previous chart if exists
        self.clear_chart()
        
        # Hide message label
        self.message_label.hide()
        
        # Create canvas for the figure
        self.chart_canvas = MplCanvas(fig)
        self.layout.addWidget(self.chart_canvas)
    
    def clear_chart(self):
        """Clear the current chart"""
        if self.chart_canvas:
            self.layout.removeWidget(self.chart_canvas)
            self.chart_canvas.deleteLater()
            self.chart_canvas = None
    
    def set_message(self, message):
        """Set a message to display instead of a chart"""
        self.message_label.setText(message)
        self.message_label.show()