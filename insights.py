from analytics import category_summary, summarize_expenses

def generate_insights(df, budget=0):
    """Generate simple, explainable insights from the selected transactions."""
    if df.empty:
        return ["No expenses recorded for this period yet. Add transactions to unlock insights."]

    summary = summarize_expenses(df)
    categories = category_summary(df)
    messages = [
        f'You recorded {summary["count"]} transaction(s), totalling ₹{summary["total"]:,.2f}.'
    ]
    if not categories.empty:
        top = categories.iloc[0]
        messages.append(
            f'Your highest-spending category is {top["category"]} '
            f'(₹{top["total"]:,.2f}, {top["share_pct"]:.1f}% of spending).'
        )
    if budget and budget > 0:
        used = summary["total"] / budget * 100
        if used > 100:
            messages.append(f'You are ₹{summary["total"] - budget:,.2f} over your budget.')
        elif used >= 80:
            messages.append(f'You have used {used:.1f}% of your budget; consider reviewing upcoming expenses.')
        else:
            messages.append(f'You have used {used:.1f}% of your budget.')
    if summary["count"] >= 2:
        messages.append(f'Your average transaction is ₹{summary["average"]:,.2f}.')
    return messages
