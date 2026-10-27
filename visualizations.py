import plotly.express as px
import plotly.graph_objects as go

def category_donut(category_df):
    fig = px.pie(category_df, names="category", values="total", hole=0.55,
                 title="Expense share by category")
    fig.update_traces(textposition="inside", textinfo="percent")
    fig.update_layout(legend_title_text="Category", margin=dict(t=55, b=10, l=10, r=10))
    return fig

def monthly_bar(monthly_df):
    fig = px.bar(
        monthly_df,
        x="month",
        y="amount",
        title="Total spending by month",
        labels={
            "month": "Month",
            "amount": "Expenses (₹)"
        },
        text_auto=".2s"
    )
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Expenses (₹)",
        margin=dict(t=55, b=10, l=10, r=10)
    )
    return fig

def daily_line(df):
    daily = df.copy()
    daily["expense_date"] = daily["expense_date"].astype(str)
    daily = daily.groupby("expense_date", as_index=False)["amount"].sum().sort_values("expense_date")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily["expense_date"], y=daily["amount"], mode="lines+markers", name="Daily expenses"))
    fig.update_layout(title="Daily spending trend", xaxis_title="Date", yaxis_title="Expenses (₹)",
                      margin=dict(t=55, b=10, l=10, r=10))
    return fig
