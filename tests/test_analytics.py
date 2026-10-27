import pandas as pd
from datetime import date
from analytics import (
    filter_expenses, summarize_expenses, category_summary,
    monthly_summary, calculate_budget_status
)

def sample_df():
    return pd.DataFrame([
        {"id": 1, "expense_date": "2026-01-02", "category": "Food", "description": "Lunch", "amount": 100.0, "payment_method": "UPI"},
        {"id": 2, "expense_date": "2026-01-15", "category": "Transport", "description": "Bus", "amount": 50.0, "payment_method": "Cash"},
        {"id": 3, "expense_date": "2026-02-03", "category": "Food", "description": "Dinner", "amount": 200.0, "payment_method": "UPI"},
    ])

def test_summary_calculations():
    result = summarize_expenses(sample_df())
    assert result["total"] == 350.0
    assert result["count"] == 3
    assert round(result["average"], 2) == 116.67
    assert result["max"] == 200.0

def test_empty_summary():
    result = summarize_expenses(pd.DataFrame())
    assert result["total"] == 0
    assert result["count"] == 0

def test_filter_inclusive_dates():
    result = filter_expenses(sample_df(), date(2026, 1, 2), date(2026, 1, 15))
    assert len(result) == 2

def test_category_summary():
    result = category_summary(sample_df())
    assert result.iloc[0]["category"] == "Food"
    assert result.iloc[0]["total"] == 300.0
    assert round(result["share_pct"].sum(), 2) == 100.0

def test_monthly_summary():
    result = monthly_summary(sample_df())
    assert result.to_dict("records") == [
        {"month": "2026-01", "amount": 150.0},
        {"month": "2026-02", "amount": 200.0},
    ]

def test_budget_status():
    result = calculate_budget_status(1200, 1000)
    assert result["over_budget"] is True
    assert result["remaining"] == -200
    assert result["percentage"] == 120.0

def test_zero_budget_does_not_divide_by_zero():
    result = calculate_budget_status(200, 0)
    assert result["percentage"] == 0
    assert result["over_budget"] is False
