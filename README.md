# Personal Finance Analytics System

A command line application for recording income and expenses, managing budgets, generating reports and creating financial charts

## Features

- Add income and expense transactions
- Store transaction dates and descriptions
- Use JSON CSV or SQLite storage
- Set a monthly expense budget
- Set category budgets
- View budget usage and warning status
- Filter transactions by category type date and amount
- View monthly financial reports
- Export monthly reports to CSV
- Create category spending pie charts
- Create monthly income and expense bar charts
- Validate user input
- Handle storage and validation errors
- Write application activity to a log file

## Requirements

- Python 3.13 or newer
- uv


## Installation

Clone the repository

```bash
git clone https://github.com/fizza-org/personal-finance-analytics-system.git
cd personal-finance-analytics-system


## FastAPI backend

The project includes a FastAPI backend for managing transactions, budgets, and financial reports

Run the API:

```bash
uv run fastapi dev src/personal_finance_analytics_system/api/app.py