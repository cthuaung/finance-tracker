# Finance Tracker

A personal finance tracking application built with Python and PyQt6.

## Features

- **Dashboard**: View your financial summary, income vs expenses, spending by category, and more
- **Transactions**: Add, edit, and filter your income and expense transactions
- **Categories**: Manage income and expense categories with custom colors
- **Budgets**: Set monthly budgets for expense categories and track your progress
- **Reports**: Generate detailed financial reports with visualizations
  - Income vs Expenses
  - Category Breakdown
  - Spending Trends

## Screenshots

*Add screenshots here*

## Requirements

- Python 3.8 or higher
- PyQt6
- Matplotlib
- Pandas
- SQLAlchemy
- Seaborn
- NumPy

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/finance_tracker.git
   cd finance_tracker
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

3. Install dependencies using uv:
   ```
   uv pip install .
   ```

## Usage

Run the application:

```
python main.py
```

## Database

The application uses SQLite to store data in `finance_tracker/data/finance.db`. This file is created automatically on first run.

## License

[MIT License](LICENSE)
