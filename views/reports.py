"""
Reports widget for the finance tracker application
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QDateEdit, QFrame, QTabWidget, QScrollArea,
    QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt, QDate

from datetime import datetime, timedelta
import calendar

from ..models.data_manager import DataManager
from ..models.database import TransactionType
from ..utils.visualizations import (
    MplCanvas, create_pie_chart, create_bar_chart, 
    create_line_chart, create_stacked_bar_chart
)


class ReportsWidget(QWidget):
    """Widget for displaying financial reports"""
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the reports UI"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        
        # Header section
        header_layout = QHBoxLayout()
        reports_title = QLabel("Financial Reports")
        reports_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(reports_title)
        
        # Add date range selector
        self.setup_date_range_selector(header_layout)
        
        self.main_layout.addLayout(header_layout)
        
        # Tab widget for different reports
        self.tab_widget = QTabWidget()
        
        # Create tabs for different reports
        self.income_expenses_tab = IncomeExpensesTab()
        self.category_breakdown_tab = CategoryBreakdownTab()
        self.trends_tab = TrendsTab()
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.income_expenses_tab, "Income vs Expenses")
        self.tab_widget.addTab(self.category_breakdown_tab, "Category Breakdown")
        self.tab_widget.addTab(self.trends_tab, "Spending Trends")
        
        # Connect tab changed signal
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        self.main_layout.addWidget(self.tab_widget)
    
    def setup_date_range_selector(self, parent_layout):
        """Set up the date range selector controls"""
        # Preset selector
        parent_layout.addWidget(QLabel("Period:"))
        
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Last 30 days",
            "This month",
            "Last month",
            "Last 3 months",
            "Last 6 months",
            "This year",
            "Last year",
            "All time",
            "Custom"
        ])
        self.period_combo.setCurrentIndex(0)
        self.period_combo.currentIndexChanged.connect(self.on_period_changed)
        
        parent_layout.addWidget(self.period_combo)
        
        # Custom date range
        parent_layout.addWidget(QLabel("From:"))
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.dateChanged.connect(self.on_date_changed)
        parent_layout.addWidget(self.start_date)
        
        parent_layout.addWidget(QLabel("To:"))
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.dateChanged.connect(self.on_date_changed)
        parent_layout.addWidget(self.end_date)
        
        # Add update button
        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self.update_report)
        parent_layout.addWidget(self.update_button)
    
    def on_period_changed(self, index):
        """Handle period combobox change"""
        today = datetime.now().date()
        
        # Disable date inputs unless "Custom" is selected
        custom_selected = (index == 8)  # "Custom" is the 9th item (index 8)
        self.start_date.setEnabled(custom_selected)
        self.end_date.setEnabled(custom_selected)
        
        # Update date range based on selection
        if index == 0:  # Last 30 days
            self.start_date.setDate(QDate(today - timedelta(days=29)))
            self.end_date.setDate(QDate(today))
        elif index == 1:  # This month
            self.start_date.setDate(QDate(today.replace(day=1)))
            self.end_date.setDate(QDate(today))
        elif index == 2:  # Last month
            last_month = today.month - 1
            last_month_year = today.year
            if last_month == 0:
                last_month = 12
                last_month_year -= 1
            
            start_date = today.replace(year=last_month_year, month=last_month, day=1)
            if last_month == 12:
                end_date = today.replace(year=last_month_year, month=last_month, day=31)
            else:
                end_date = today.replace(year=last_month_year, month=last_month + 1, day=1) - timedelta(days=1)
            
            self.start_date.setDate(QDate(start_date))
            self.end_date.setDate(QDate(end_date))
        elif index == 3:  # Last 3 months
            self.start_date.setDate(QDate(today - timedelta(days=90)))
            self.end_date.setDate(QDate(today))
        elif index == 4:  # Last 6 months
            self.start_date.setDate(QDate(today - timedelta(days=180)))
            self.end_date.setDate(QDate(today))
        elif index == 5:  # This year
            self.start_date.setDate(QDate(today.replace(month=1, day=1)))
            self.end_date.setDate(QDate(today))
        elif index == 6:  # Last year
            self.start_date.setDate(QDate(today.replace(year=today.year - 1, month=1, day=1)))
            self.end_date.setDate(QDate(today.replace(year=today.year - 1, month=12, day=31)))
        elif index == 7:  # All time
            # Just set to a very old date, we'll handle this specially
            self.start_date.setDate(QDate(2000, 1, 1))
            self.end_date.setDate(QDate(today))
    
    def on_date_changed(self):
        """Handle custom date changes"""
        # If dates are changed manually, set selector to "Custom"
        self.period_combo.setCurrentIndex(8)  # "Custom" is the 9th item (index 8)
    
    def on_tab_changed(self, index):
        """Handle tab change"""
        self.update_report()
    
    def update_report(self):
        """Update the currently displayed report"""
        start_date = None if self.period_combo.currentIndex() == 7 else self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        
        # Update the active tab
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            current_tab.update_report(start_date, end_date)


class IncomeExpensesTab(QWidget):
    """Tab for income vs expenses reports"""
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the income vs expenses tab UI"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(20)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create a widget for the scroll area
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(20)
        
        # Create charts
        self.setup_charts()
        
        # Set the scroll content
        scroll_area.setWidget(scroll_content)
        
        # Add to main layout
        self.main_layout.addWidget(scroll_area)
    
    def setup_charts(self):
        """Set up the charts for this tab"""
        # Income vs Expenses Overview Chart
        self.overview_frame = self.create_chart_frame("Income vs Expenses Overview")
        self.overview_container = QVBoxLayout()
        self.overview_frame.layout().addLayout(self.overview_container)
        self.scroll_layout.addWidget(self.overview_frame)
        
        # Monthly Comparison Chart
        self.monthly_frame = self.create_chart_frame("Monthly Comparison")
        self.monthly_container = QVBoxLayout()
        self.monthly_frame.layout().addLayout(self.monthly_container)
        self.scroll_layout.addWidget(self.monthly_frame)
        
        # Income vs Expenses Ratio Chart
        self.ratio_frame = self.create_chart_frame("Income vs Expenses Ratio")
        self.ratio_container = QVBoxLayout()
        self.ratio_frame.layout().addLayout(self.ratio_container)
        self.scroll_layout.addWidget(self.ratio_frame)
    
    def create_chart_frame(self, title):
        """Create a frame for a chart"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #e1e1e1;")
        
        layout = QVBoxLayout(frame)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        return frame
    
    def update_report(self, start_date, end_date):
        """Update the report with the specified date range"""
        # Clear previous charts
        self.clear_charts()
        
        # Update the charts
        self.update_overview_chart(start_date, end_date)
        self.update_monthly_chart(start_date, end_date)
        self.update_ratio_chart(start_date, end_date)
    
    def clear_charts(self):
        """Clear all charts"""
        self.clear_layout(self.overview_container)
        self.clear_layout(self.monthly_container)
        self.clear_layout(self.ratio_container)
    
    def clear_layout(self, layout):
        """Clear all widgets from a layout"""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
    
    def update_overview_chart(self, start_date, end_date):
        """Update the income vs expenses overview chart"""
        # Get data for the chart
        data = DataManager.get_income_vs_expenses(start_date, end_date)
        
        if data:
            # Create chart
            fig = create_line_chart(
                data=data,
                x_key='date',
                y_keys=['income', 'expense'],
                labels=['Income', 'Expenses'],
                title='Income vs Expenses Over Time',
                colors=['#27ae60', '#e74c3c'],
                x_label='Date',
                y_label='Amount ($)',
                x_date_format=True
            )
            
            # Create canvas for the chart
            chart_canvas = MplCanvas(fig)
            
            # Add to layout
            self.overview_container.addWidget(chart_canvas)
        else:
            # Show message when no data is available
            no_data_label = QLabel("No data available for the selected period.")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
            self.overview_container.addWidget(no_data_label)
    
    def update_monthly_chart(self, start_date, end_date):
        """Update the monthly comparison chart"""
        # Get data for the chart
        data = DataManager.get_income_vs_expenses(start_date, end_date, group_by='month')
        
        if data:
            # Create chart
            fig = create_bar_chart(
                data=data,
                x_key='date',
                y_keys=['income', 'expense'],
                labels=['Income', 'Expenses'],
                title='Monthly Income vs Expenses',
                colors=['#27ae60', '#e74c3c'],
                x_label='Month',
                y_label='Amount ($)'
            )
            
            # Create canvas for the chart
            chart_canvas = MplCanvas(fig)
            
            # Add to layout
            self.monthly_container.addWidget(chart_canvas)
        else:
            # Show message when no data is available
            no_data_label = QLabel("No data available for the selected period.")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
            self.monthly_container.addWidget(no_data_label)
    
    def update_ratio_chart(self, start_date, end_date):
        """Update the income vs expenses ratio chart"""
        # Get income and expense totals
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
        
        total_income = sum(t.amount for t in income_transactions)
        total_expenses = sum(t.amount for t in expense_transactions)
        savings = total_income - total_expenses
        
        if total_income > 0 or total_expenses > 0:
            # Create data for the chart
            data = [
                ("Income", total_income, "#27ae60"),
                ("Expenses", total_expenses, "#e74c3c"),
                ("Savings", max(0, savings), "#3498db")
            ]
            
            # Create chart
            fig = create_pie_chart(
                data=data,
                title='Income, Expenses and Savings Distribution'
            )
            
            # Create canvas for the chart
            chart_canvas = MplCanvas(fig)
            
            # Add to layout
            self.ratio_container.addWidget(chart_canvas)
            
            # Add summary
            summary_label = QLabel(
                f"<b>Summary:</b><br>"
                f"Total Income: ${total_income:.2f}<br>"
                f"Total Expenses: ${total_expenses:.2f}<br>"
                f"Net Savings: ${savings:.2f} ({(savings/total_income*100 if total_income > 0 else 0):.1f}% of income)"
            )
            summary_label.setStyleSheet("padding: 10px; background-color: #f9f9f9; border-radius: 5px;")
            self.ratio_container.addWidget(summary_label)
        else:
            # Show message when no data is available
            no_data_label = QLabel("No data available for the selected period.")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
            self.ratio_container.addWidget(no_data_label)


class CategoryBreakdownTab(QWidget):
    """Tab for category breakdown reports"""
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the category breakdown tab UI"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(20)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create a widget for the scroll area
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(20)
        
        # Create charts
        self.setup_charts()
        
        # Set the scroll content
        scroll_area.setWidget(scroll_content)
        
        # Add to main layout
        self.main_layout.addWidget(scroll_area)
    
    def setup_charts(self):
        """Set up the charts for this tab"""
        # Expense Categories Chart
        self.expense_frame = self.create_chart_frame("Expense Categories")
        self.expense_container = QVBoxLayout()
        self.expense_frame.layout().addLayout(self.expense_container)
        self.scroll_layout.addWidget(self.expense_frame)
        
        # Income Categories Chart
        self.income_frame = self.create_chart_frame("Income Categories")
        self.income_container = QVBoxLayout()
        self.income_frame.layout().addLayout(self.income_container)
        self.scroll_layout.addWidget(self.income_frame)
    
    def create_chart_frame(self, title):
        """Create a frame for a chart"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #e1e1e1;")
        
        layout = QVBoxLayout(frame)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        return frame
    
    def update_report(self, start_date, end_date):
        """Update the report with the specified date range"""
        # Clear previous charts
        self.clear_charts()
        
        # Update the charts
        self.update_expense_chart(start_date, end_date)
        self.update_income_chart(start_date, end_date)
    
    def clear_charts(self):
        """Clear all charts"""
        self.clear_layout(self.expense_container)
        self.clear_layout(self.income_container)
    
    def clear_layout(self, layout):
        """Clear all widgets from a layout"""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
    
    def update_expense_chart(self, start_date, end_date):
        """Update the expense categories chart"""
        # Get data for the chart
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
            
            # Create canvas for the chart
            chart_canvas = MplCanvas(fig)
            
            # Add to layout
            self.expense_container.addWidget(chart_canvas)
        else:
            # Show message when no data is available
            no_data_label = QLabel("No expense data available for the selected period.")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
            self.expense_container.addWidget(no_data_label)
    
    def update_income_chart(self, start_date, end_date):
        """Update the income categories chart"""
        # Get data for the chart
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
            
            # Create canvas for the chart
            chart_canvas = MplCanvas(fig)
            
            # Add to layout
            self.income_container.addWidget(chart_canvas)
        else:
            # Show message when no data is available
            no_data_label = QLabel("No income data available for the selected period.")
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
            self.income_container.addWidget(no_data_label)


class TrendsTab(QWidget):
    """Tab for spending trend reports"""
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the trends tab UI"""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(20)
        
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create a widget for the scroll area
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(20)
        
        # Create charts
        self.setup_charts()
        
        # Set the scroll content
        scroll_area.setWidget(scroll_content)
        
        # Add to main layout
        self.main_layout.addWidget(scroll_area)
    
    def setup_charts(self):
        """Set up the charts for this tab"""
        # Daily Spending Chart
        self.daily_frame = self.create_chart_frame("Daily Spending Trend")
        self.daily_container = QVBoxLayout()
        self.daily_frame.layout().addLayout(self.daily_container)
        self.scroll_layout.addWidget(self.daily_frame)
        
        # Monthly Spending Chart
        self.monthly_frame = self.create_chart_frame("Monthly Spending Trend")
        self.monthly_container = QVBoxLayout()
        self.monthly_frame.layout().addLayout(self.monthly_container)
        self.scroll_layout.addWidget(self.monthly_frame)
    
    def create_chart_frame(self, title):
        """Create a frame for a chart"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #e1e1e1;")
        
        layout = QVBoxLayout(frame)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        return frame
    
    def update_report(self, start_date, end_date):
        """Update the report with the specified date range"""
        # Clear previous charts
        self.clear_charts()
        
        # Update the charts
        self.update_daily_chart(start_date, end_date)
        self.update_monthly_chart(start_date, end_date)
    
    def clear_charts(self):
        """Clear all charts"""
        self.clear_layout(self.daily_container)
        self.clear_layout(self.monthly_container)
    
    def clear_layout(self, layout):
        """Clear all widgets from a layout"""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
    
    def update_daily_chart(self, start_date, end_date):
        """Update the daily spending chart"""
        # Determine appropriate grouping based on the date range
        if start_date and end_date:
            days_in_period = (end_date - start_date).days + 1
            
            if days_in_period <= 31:
                group_by = 'day'
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
                if group_by == 'day':
                    fig = create_line_chart(
                        data=chart_data,
                        x_key='date',
                        y_keys=['amount'],
                        labels=['Expenses'],
                        title='Daily Spending Trend',
                        colors=['#e74c3c'],
                        x_label='Date',
                        y_label='Amount ($)',
                        x_date_format=True
                    )
                else:
                    fig = create_bar_chart(
                        data=chart_data,
                        x_key='date',
                        y_keys=['amount'],
                        labels=['Expenses'],
                        title='Daily Spending Trend',
                        colors=['#e74c3c'],
                        x_label='Date',
                        y_label='Amount ($)'
                    )
                
                # Create canvas for the chart
                chart_canvas = MplCanvas(fig)
                
                # Add to layout
                self.daily_container.addWidget(chart_canvas)
            else:
                self.show_no_data_message(self.daily_container)
        else:
            self.show_no_data_message(self.daily_container)
    
    def update_monthly_chart(self, start_date, end_date):
        """Update the monthly spending chart"""
        # Get transaction totals by month
        data = DataManager.get_transaction_totals(start_date, end_date, 'month')
        
        if data:
            # Convert data to format needed for chart
            chart_data = []
            
            for item in data:
                if item.type == TransactionType.EXPENSE:
                    date_str = f"{item.date.year}-{item.date.month}"
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
                    title='Monthly Spending Trend',
                    colors=['#e74c3c'],
                    x_label='Month',
                    y_label='Amount ($)'
                )
                
                # Create canvas for the chart
                chart_canvas = MplCanvas(fig)
                
                # Add to layout
                self.monthly_container.addWidget(chart_canvas)
            else:
                self.show_no_data_message(self.monthly_container)
        else:
            self.show_no_data_message(self.monthly_container)
    
    def show_no_data_message(self, container):
        """Show a message when no data is available"""
        no_data_label = QLabel("No expense data available for the selected period.")
        no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_data_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
        container.addWidget(no_data_label) 