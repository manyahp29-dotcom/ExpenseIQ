import os
import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(os.environ.get("EXPENSEIQ_DB_PATH", Path(__file__).resolve().parent / "expenseiq.db"))

def get_connection():
    """Create a SQLite connection. Row data is returned through Pandas queries."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Create database tables if they do not already exist."""
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    with get_connection() as conn:
        if schema_path.exists():
            conn.executescript(schema_path.read_text(encoding="utf-8"))
        else:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    expense_date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL CHECK(amount > 0),
                    payment_method TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS budgets (
                    month TEXT PRIMARY KEY,
                    amount REAL NOT NULL CHECK(amount >= 0)
                );
            """)

def add_expense(expense_date, category, description, amount, payment_method):
    if float(amount) <= 0:
        raise ValueError("Expense amount must be greater than zero.")
    if not str(description).strip():
        raise ValueError("Description cannot be empty.")
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO expenses (expense_date, category, description, amount, payment_method)
               VALUES (?, ?, ?, ?, ?)""",
            (str(expense_date), str(category), str(description).strip(), float(amount), str(payment_method))
        )
        return cursor.lastrowid

def get_expenses():
    """Return all expenses as a DataFrame, newest first."""
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT id, expense_date, category, description, amount, payment_method, created_at FROM expenses ORDER BY expense_date DESC, id DESC",
            conn
        )

def update_expense(expense_id, expense_date, category, description, amount, payment_method):
    if float(amount) <= 0:
        raise ValueError("Expense amount must be greater than zero.")
    if not str(description).strip():
        raise ValueError("Description cannot be empty.")
    with get_connection() as conn:
        cursor = conn.execute(
            """UPDATE expenses SET expense_date=?, category=?, description=?, amount=?, payment_method=?
               WHERE id=?""",
            (str(expense_date), str(category), str(description).strip(), float(amount), str(payment_method), int(expense_id))
        )
        return cursor.rowcount > 0

def delete_expense(expense_id):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM expenses WHERE id=?", (int(expense_id),))
        return cursor.rowcount > 0

def get_budget(month):
    with get_connection() as conn:
        row = conn.execute("SELECT amount FROM budgets WHERE month=?", (str(month),)).fetchone()
    return float(row[0]) if row else 0.0

def set_budget(month, amount):
    if float(amount) < 0:
        raise ValueError("Budget cannot be negative.")
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO budgets (month, amount) VALUES (?, ?)
               ON CONFLICT(month) DO UPDATE SET amount=excluded.amount""",
            (str(month), float(amount))
        )

def export_expenses_csv():
    df = get_expenses()
    if df.empty:
        return ""
    return df.to_csv(index=False)
