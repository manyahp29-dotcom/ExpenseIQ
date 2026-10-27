<<<<<<< HEAD
# ExpenseIQ — Personal Expense Tracker & Analytics

ExpenseIQ is a Python + Streamlit application for recording expenses, storing them in SQLite, monitoring a monthly budget, and exploring spending patterns with interactive charts.

## Features

- Add, view, edit, and delete expense transactions
- Persistent SQLite storage
- Monthly budgets and budget usage indicators
- Category-level and monthly spending analysis
- Daily spending trend chart
- Explainable rule-based spending insights
- CSV export for Excel, Power BI, or Python analysis
- Automated tests for analytics and database operations

## Tech stack

- Python 3.11+
- Streamlit
- SQLite
- Pandas
- Plotly
- pytest

## Project structure

```text
ExpenseIQ/
├── app.py
├── analytics.py
├── database.py
├── insights.py
├── visualizations.py
├── schema.sql
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── pytest.ini
└── tests/
    ├── test_analytics.py
    └── test_database.py
```

The SQLite database is created automatically as `expenseiq.db` when the app starts. It is intentionally excluded from Git because it may contain private financial information.

## Setup

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\\Scripts\\Activate.ps1
```

Windows Command Prompt:

```bat
python -m venv .venv
.venv\\Scripts\\activate.bat
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py
```

Streamlit normally opens the app in your browser at `http://localhost:8501`.

### 4. Run automated tests

In a second terminal, with the virtual environment activated:

```bash
pytest -v
```

## How to use

1. Open **Manage expenses** and add transactions.
2. Open **Dashboard** to view totals and charts.
3. Open **Budget & insights** to set a monthly budget.
4. Open **Export data** to download a CSV file.

## Data and privacy

- All data is stored locally in SQLite by default.
- The database and CSV exports are ignored by Git.
- Do not commit real financial records, credentials, or personal information.
- This starter project does not connect to bank accounts or provide financial advice.

## Future improvements

- Login and multi-user support
- Recurring expenses
- Budget recommendations based on historical patterns
- Unit and integration test coverage for the Streamlit interface
- Continuous integration with GitHub Actions
- Deployment with a persistent database solution

## Portfolio description

**ExpenseIQ — Expense Tracking and Analytics Dashboard:** Built a Python application with Streamlit and SQLite to manage expense records, analyze spending by category and month, track budgets, generate rule-based insights, and export data for downstream analysis. Added automated tests with pytest.
=======
# ExpenseIQ
Python Expense Tracker with Analytics
>>>>>>> 5e557a0bcda77d281fd9a7ae647c42c4506ac2b4
