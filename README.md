# Personal Finance Analytics System

A personal finance application with a FastAPI backend, Streamlit interface, command-line tools, SQLite storage, authentication, multi-user data isolation, reporting, and caching

## Features

- Register and log in with email and password
- Protect finance endpoints with bearer authentication
- Keep transactions and budgets isolated per user
- Add income and expense transactions
- Store transaction dates, categories, and descriptions
- Filter transactions by category, type, date, and amount
- View transaction summaries
- Create and update category budgets
- View budget usage and status
- Generate monthly and date-range reports
- Download reports as CSV or JSON
- Restrict report downloads to the permitted historical cutoff
- Cache transaction summaries, budget statuses, and reports per user
- Use SQLite for API transactions, users, and budgets
- Use JSON, CSV, or SQLite storage in the CLI
- Validate input and handle storage, authentication, and API errors
- Use Streamlit for the authenticated web interface

## Report date rule

Reports may be generated through the current date.

Future end dates are rejected with HTTP 422.

## Requirements

- Python 3.13 or newer
- uv

## Installation

Clone the repository:

```bash
git clone https://github.com/fizza-org/personal-finance-analytics-system.git
cd personal-finance-analytics-system