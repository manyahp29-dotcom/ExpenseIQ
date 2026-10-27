import pandas as pd

def filter_expenses(df, start_date, end_date):
    """Filter a DataFrame using inclusive ISO date boundaries."""
    if df.empty:
        return df.copy()
    dates = pd.to_datetime(df["expense_date"], errors="coerce").dt.date
    mask = (dates >= start_date) & (dates <= end_date)
    return df.loc[mask].copy()

def summarize_expenses(df):
    if df.empty:
        return {"total": 0.0, "count": 0, "average": 0.0, "median": 0.0, "max": 0.0}
    amounts = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    return {
        "total": float(amounts.sum()),
        "count": int(len(df)),
        "average": float(amounts.mean()),
        "median": float(amounts.median()),
        "max": float(amounts.max()),
    }

def category_summary(df):
    if df.empty:
        return pd.DataFrame(columns=["category", "total", "transactions", "share_pct"])
    grouped = df.groupby("category", as_index=False).agg(
        total=("amount", "sum"),
        transactions=("amount", "count")
    )
    grand_total = grouped["total"].sum()
    grouped["share_pct"] = (grouped["total"] / grand_total * 100) if grand_total else 0.0
    return grouped.sort_values("total", ascending=False).reset_index(drop=True)

def monthly_summary(df):
    if df.empty:
        return pd.DataFrame(columns=["month", "total"])
    working = df.copy()
    working["month"] = pd.to_datetime(working["expense_date"], errors="coerce").dt.to_period("M").astype(str)
    result = working.groupby("month", as_index=False)["amount"].sum()
    return result.sort_values("month").reset_index(drop=True)

def calculate_budget_status(spent, budget):
    spent, budget = float(spent), float(budget)
    remaining = budget - spent
    percentage = (spent / budget * 100) if budget > 0 else 0.0
    return {
        "spent": spent,
        "budget": budget,
        "remaining": remaining,
        "percentage": percentage,
        "over_budget": budget > 0 and spent > budget,
    }
