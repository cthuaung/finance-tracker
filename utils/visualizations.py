"""
Data visualization utilities for the finance tracker
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import io

# Set the style for all visualizations
sns.set_style("whitegrid")
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'sans-serif']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10


class MplCanvas(FigureCanvasQTAgg):
    """Canvas for matplotlib figures in PyQt"""
    
    def __init__(self, fig=None, width=5, height=4, dpi=100):
        if fig is None:
            self.fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = self.fig.add_subplot(111)
        else:
            self.fig = fig
        super(MplCanvas, self).__init__(self.fig)


def create_pie_chart(data: List[Tuple[str, float, str]], title: str = "Category Breakdown") -> Figure:
    """
    Create a pie chart for category breakdown
    
    Args:
        data: List of tuples (category_name, amount, color)
        title: Chart title
    
    Returns:
        Matplotlib figure
    """
    # Extract data
    labels = [item[0] for item in data]
    values = [item[1] for item in data]
    colors = [item[2] for item in data]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 7), subplot_kw=dict(aspect="equal"))
    
    # Plot pie chart
    wedges, texts, autotexts = ax.pie(
        values, 
        autopct=lambda pct: f"{pct:.1f}%\n(${sum(values)*pct/100:.2f})" if pct > 3 else "",
        colors=colors,
        wedgeprops=dict(width=0.5, edgecolor='w'),
        startangle=90
    )
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax.set_title(title, fontweight='bold', pad=20)
    
    # Create legend
    ax.legend(
        wedges, 
        labels,
        title="Categories",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1)
    )
    
    plt.setp(autotexts, size=9, weight="bold")
    fig.tight_layout()
    
    return fig


def create_bar_chart(
    data: List[Dict[str, Any]], 
    x_key: str, 
    y_keys: List[str], 
    labels: List[str],
    title: str,
    colors: List[str] = None,
    x_label: str = "",
    y_label: str = "Amount ($)"
) -> Figure:
    """
    Create a bar chart for comparing multiple data series
    
    Args:
        data: List of dictionaries containing the data
        x_key: Key for x-axis values
        y_keys: List of keys for different data series
        labels: Labels for the data series
        title: Chart title
        colors: Colors for the different data series
        x_label: X-axis label
        y_label: Y-axis label
    
    Returns:
        Matplotlib figure
    """
    if colors is None:
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(data)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Set width of bars
    bar_width = 0.8 / len(y_keys)
    
    # Calculate positions for each series of bars
    positions = range(len(df))
    
    # Create bars for each data series
    for i, (y_key, label, color) in enumerate(zip(y_keys, labels, colors)):
        offset = -0.4 + (i + 0.5) * bar_width
        ax.bar(
            [p + offset for p in positions], 
            df[y_key],
            bar_width, 
            label=label,
            color=color
        )
    
    # Add labels and title
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title, fontweight='bold')
    
    # Set x-axis ticks and labels
    ax.set_xticks(positions)
    ax.set_xticklabels(df[x_key])
    
    # Add legend
    ax.legend()
    
    # Add grid
    ax.yaxis.grid(True, alpha=0.3)
    
    # Add value labels on top of bars
    for i, (y_key, color) in enumerate(zip(y_keys, colors)):
        offset = -0.4 + (i + 0.5) * bar_width
        for j, v in enumerate(df[y_key]):
            ax.text(
                j + offset, 
                v + 0.1, 
                f"${v:.0f}", 
                ha='center', 
                fontsize=8,
                fontweight='bold',
                color='black'
            )
    
    fig.tight_layout()
    
    return fig


def create_line_chart(
    data: List[Dict[str, Any]], 
    x_key: str, 
    y_keys: List[str], 
    labels: List[str],
    title: str,
    colors: List[str] = None,
    x_label: str = "",
    y_label: str = "Amount ($)",
    x_date_format: bool = False
) -> Figure:
    """
    Create a line chart for time series data
    
    Args:
        data: List of dictionaries containing the data
        x_key: Key for x-axis values (typically dates)
        y_keys: List of keys for different data series
        labels: Labels for the data series
        title: Chart title
        colors: Colors for the different data series
        x_label: X-axis label
        y_label: Y-axis label
        x_date_format: Whether to format x-axis as dates
    
    Returns:
        Matplotlib figure
    """
    if colors is None:
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(data)
    
    # Convert date strings to datetime objects if x_date_format is True
    if x_date_format and df[x_key].dtype == 'object':
        if '-' in df[x_key].iloc[0] and len(df[x_key].iloc[0].split('-')) >= 2:
            # If it's in format like "2023-01"
            if len(df[x_key].iloc[0].split('-')) == 2:
                df[x_key] = df[x_key].apply(lambda x: datetime.strptime(x, '%Y-%m'))
            else:  # Format like "2023-01-15"
                df[x_key] = pd.to_datetime(df[x_key])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create lines for each data series
    for i, (y_key, label, color) in enumerate(zip(y_keys, labels, colors)):
        ax.plot(
            df[x_key], 
            df[y_key],
            marker='o',
            linestyle='-',
            linewidth=2,
            label=label,
            color=color
        )
    
    # Add labels and title
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title, fontweight='bold')
    
    # Format x-axis for dates if needed
    if x_date_format:
        # Determine the date format based on the range
        date_range = (max(df[x_key]) - min(df[x_key])).days
        
        if date_range > 365:  # More than a year
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        elif date_range > 60:  # More than 2 months
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        else:  # Less than 2 months
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        
        fig.autofmt_xdate()
    
    # Add legend
    ax.legend()
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Add totals to the legend
    if len(y_keys) > 0:
        # Create a secondary legend with totals
        totals = [f"{label}: ${df[y_key].sum():.2f}" for y_key, label in zip(y_keys, labels)]
        ax.annotate(
            '\n'.join(totals),
            xy=(0.02, 0.02),
            xycoords='axes fraction',
            bbox=dict(boxstyle="round,pad=0.5", fc="white", alpha=0.8)
        )
    
    fig.tight_layout()
    
    return fig


def create_stacked_bar_chart(
    data: List[Dict[str, Any]], 
    x_key: str, 
    y_keys: List[str], 
    labels: List[str],
    title: str,
    colors: List[str] = None,
    x_label: str = "",
    y_label: str = "Amount ($)"
) -> Figure:
    """
    Create a stacked bar chart
    
    Args:
        data: List of dictionaries containing the data
        x_key: Key for x-axis values
        y_keys: List of keys for different data series
        labels: Labels for the data series
        title: Chart title
        colors: Colors for the different data series
        x_label: X-axis label
        y_label: Y-axis label
    
    Returns:
        Matplotlib figure
    """
    if colors is None:
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(data)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create the stacked bars
    bottom = np.zeros(len(df))
    for i, (y_key, label, color) in enumerate(zip(y_keys, labels, colors)):
        ax.bar(
            df[x_key], 
            df[y_key],
            bottom=bottom,
            label=label,
            color=color
        )
        bottom += df[y_key]
    
    # Add labels and title
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title, fontweight='bold')
    
    # Add legend
    ax.legend()
    
    # Add grid
    ax.yaxis.grid(True, alpha=0.3)
    
    fig.tight_layout()
    
    return fig


def create_progress_bars(
    data: List[Dict[str, Any]], 
    title: str = "Budget Progress"
) -> Figure:
    """
    Create horizontal progress bars for budget tracking
    
    Args:
        data: List of dictionaries with budget data
              Each dict should have: category_name, budget_amount, actual_amount, color
        title: Chart title
    
    Returns:
        Matplotlib figure
    """
    # Sort data by percentage (highest first)
    sorted_data = sorted(data, key=lambda x: x['percentage'], reverse=True)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, max(5, len(sorted_data) * 0.5)))
    
    # Extract data
    categories = [item['category_name'] for item in sorted_data]
    budgets = [item['budget_amount'] for item in sorted_data]
    actuals = [item['actual_amount'] for item in sorted_data]
    colors = [item['color'] for item in sorted_data]
    percentages = [min(item['percentage'], 100) for item in sorted_data]
    
    # Y positions for each bar
    y_pos = range(len(categories))
    
    # Create the "empty" bars (budgets)
    ax.barh(
        y_pos, 
        budgets, 
        height=0.5, 
        color='lightgray'
    )
    
    # Create the "filled" bars (actual expenditures)
    bars = ax.barh(
        y_pos, 
        actuals, 
        height=0.5, 
        color=colors
    )
    
    # Add percentage and amount labels
    for i, (bar, percentage, actual, budget) in enumerate(zip(bars, percentages, actuals, budgets)):
        # Add percentage label
        ax.text(
            bar.get_width() + 5, 
            bar.get_y() + bar.get_height()/2, 
            f"{percentage:.1f}% (${actual:.2f} / ${budget:.2f})",
            va='center', 
            fontsize=9
        )
    
    # Set y-axis ticks and labels
    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories)
    
    # Remove x-axis ticks, we'll show values in the labels
    ax.set_xticks([])
    
    # Add title
    ax.set_title(title, fontweight='bold')
    
    # Add grid
    ax.xaxis.grid(True, alpha=0.3)
    
    # Add a vertical line at 100% of budget
    for i, budget in enumerate(budgets):
        ax.axvline(
            x=budget, 
            ymin=i/len(categories), 
            ymax=(i+1)/len(categories), 
            color='red', 
            linestyle='--', 
            alpha=0.5,
            linewidth=1
        )
    
    fig.tight_layout()
    
    return fig 