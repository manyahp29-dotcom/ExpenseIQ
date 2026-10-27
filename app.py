from datetime import date, timedelta
import pandas as pd
import streamlit as st

from database import (
    init_db, add_expense, get_expenses, update_expense, delete_expense,
    get_budget, set_budget, export_expenses_csv
)
from analytics import (
    filter_expenses, summarize_expenses, category_summary,
    monthly_summary, calculate_budget_status
)
from visualizations import category_donut, monthly_bar, daily_line
from insights import generate_insights

st.set_page_config(page_title="ExpenseIQ", page_icon="💸", layout="wide")

st.markdown("""
<style>
[data-testid="stMetricValue"] {
    font-size: clamp(16px, 1.8vw, 25px) !important;
    white-space: nowrap !important;
}
[data-testid="stMetricLabel"] {
    font-size: 13px !important;
}
[data-testid="stMetric"] {
    min-width: 0;
}
</style>
""", unsafe_allow_html=True)

init_db()

CATEGORIES = [
    "Food", "Transport", "Shopping", "Bills", "Entertainment",
    "Health", "Education", "Travel", "Groceries", "Other"
]
PAYMENT_METHODS = ["UPI", "Cash", "Debit Card", "Credit Card", "Net Banking", "Other"]

def money(value):
    return f"₹{float(value):,.2f}"

st.sidebar.title("💸 ExpenseIQ")
st.sidebar.caption("Personal finance, made clearer.")
page = st.sidebar.radio("Navigate", ["Dashboard", "Manage expenses", "Budget & insights", "Export data"])
st.sidebar.divider()
st.sidebar.caption("Your data is stored locally in SQLite.")

all_expenses = get_expenses()

if page == "Dashboard":
    st.title("ExpenseIQ Dashboard")
    st.write("Understand where your money goes.")
    today = date.today()
    default_start = today.replace(day=1)
    c1, c2 = st.columns(2)
    start_date = c1.date_input("From", value=default_start, key="dash_start")
    end_date = c2.date_input("To", value=today, key="dash_end")
    if start_date > end_date:
        st.error("The start date must be on or before the end date.")
        st.stop()

    df = filter_expenses(all_expenses, start_date, end_date)
    summary = summarize_expenses(df)
    budget = get_budget(start_date.strftime("%Y-%m"))
    budget_status = calculate_budget_status(summary["total"], budget)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total expenses", money(summary["total"]))
    m2.metric("Transactions", f'{summary["count"]:,}')
    m3.metric("Average transaction", money(summary["average"]))
    m4.metric("Monthly budget", money(budget) if budget else "Not set")

    if budget:
        st.progress(min(summary["total"] / budget, 1.0) if budget > 0 else 0.0)
        st.caption(f'Budget used: {budget_status["percentage"]:.1f}% · Remaining: {money(budget_status["remaining"])}')
        if budget_status["over_budget"]:
            st.warning("You have exceeded the budget for this selected period.")
    st.divider()

    left, right = st.columns(2)
    with left:
        st.subheader("Spending by category")
        cat = category_summary(df)
        if cat.empty:
            st.info("No expenses in this date range yet. Add one under Manage expenses.")
        else:
            st.plotly_chart(category_donut(cat), use_container_width=True)
    with right:
        st.subheader("Monthly spending")
        monthly = monthly_summary(all_expenses)
        if monthly.empty:
            st.info("Add expenses to see monthly trends.")
        else:
            st.plotly_chart(monthly_bar(monthly), use_container_width=True)

    st.subheader("Daily spending")
    if df.empty:
        st.info("No transactions to chart for this date range.")
    else:
        st.plotly_chart(daily_line(df), use_container_width=True)

    st.subheader("Recent expenses")
    if df.empty:
        st.info("No expenses found.")
    else:
        recent = df.sort_values(["expense_date", "id"], ascending=False).head(10)
        st.dataframe(recent[["expense_date", "category", "description", "payment_method", "amount"]], use_container_width=True, hide_index=True)

elif page == "Manage expenses":
    st.title("Manage expenses")
    st.write("Create and maintain your transaction records.")
    with st.expander("➕ Add a new expense", expanded=True):
        with st.form("add_expense_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            expense_date = c1.date_input("Date", value=date.today())
            amount = c2.number_input("Amount (₹)", min_value=0.01, value=100.00, step=10.0, format="%.2f")
            c3, c4 = st.columns(2)
            category = c3.selectbox("Category", CATEGORIES)
            payment_method = c4.selectbox("Payment method", PAYMENT_METHODS)
            description = st.text_input("Description", placeholder="e.g. Lunch with friends")
            submitted = st.form_submit_button("Save expense", type="primary")
            if submitted:
                if not description.strip():
                    st.error("Please enter a short description.")
                else:
                    add_expense(expense_date.isoformat(), category, description.strip(), amount, payment_method)
                    st.success("Expense saved.")
                    st.rerun()

    df = get_expenses()
    st.subheader("Your expenses")
    if df.empty:
        st.info("Your expense list is empty. Add your first expense above.")
    else:
        f1, f2 = st.columns(2)
        category_filter = f1.selectbox("Filter by category", ["All"] + CATEGORIES)
        search = f2.text_input("Search description")
        shown = df.copy()
        if category_filter != "All":
            shown = shown[shown["category"] == category_filter]
        if search.strip():
            shown = shown[shown["description"].str.contains(search.strip(), case=False, na=False)]
        st.dataframe(shown[["id", "expense_date", "category", "description", "payment_method", "amount"]], use_container_width=True, hide_index=True)

        st.subheader("Edit or delete an expense")
        ids = shown["id"].astype(int).tolist()
        if ids:
            selected_id = st.selectbox("Select transaction ID", ids)
            selected = shown[shown["id"] == selected_id].iloc[0]
            with st.form("edit_expense_form"):
                ec1, ec2 = st.columns(2)
                edit_date = ec1.date_input("Date", value=date.fromisoformat(str(selected["expense_date"])))
                edit_amount = ec2.number_input("Amount (₹)", min_value=0.01, value=float(selected["amount"]), step=10.0, format="%.2f")
                ec3, ec4 = st.columns(2)
                current_category = str(selected["category"])
                cat_index = CATEGORIES.index(current_category) if current_category in CATEGORIES else len(CATEGORIES)-1
                edit_category = ec3.selectbox("Category", CATEGORIES, index=cat_index)
                current_method = str(selected["payment_method"])
                method_index = PAYMENT_METHODS.index(current_method) if current_method in PAYMENT_METHODS else len(PAYMENT_METHODS)-1
                edit_method = ec4.selectbox("Payment method", PAYMENT_METHODS, index=method_index)
                edit_description = st.text_input("Description", value=str(selected["description"]))
                save_edit = st.form_submit_button("Update expense")
                if save_edit:
                    if not edit_description.strip():
                        st.error("Description cannot be empty.")
                    else:
                        update_expense(int(selected_id), edit_date.isoformat(), edit_category, edit_description.strip(), edit_amount, edit_method)
                        st.success("Expense updated.")
                        st.rerun()
            if st.button("🗑️ Delete selected expense", type="secondary"):
                st.session_state["confirm_delete_id"] = int(selected_id)
            if st.session_state.get("confirm_delete_id") == int(selected_id):
                st.warning(f"Delete transaction #{selected_id}? This cannot be undone.")
                yes, no = st.columns(2)
                if yes.button("Confirm delete", type="primary"):
                    delete_expense(int(selected_id))
                    st.session_state.pop("confirm_delete_id", None)
                    st.success("Expense deleted.")
                    st.rerun()
                if no.button("Cancel deletion"):
                    st.session_state.pop("confirm_delete_id", None)
                    st.rerun()

elif page == "Budget & insights":
    st.title("Budget & insights")
    st.write("Set a monthly spending target and review patterns in your transactions.")
    now = date.today()
    selected_month = st.date_input("Choose a month", value=now.replace(day=1), key="budget_month")
    month_key = selected_month.strftime("%Y-%m")
    current_budget = get_budget(month_key)
    with st.form("budget_form"):
        new_budget = st.number_input("Monthly budget (₹)", min_value=0.0, value=float(current_budget), step=500.0)
        save_budget = st.form_submit_button("Save monthly budget", type="primary")
        if save_budget:
            set_budget(month_key, new_budget)
            st.success(f"Budget saved for {month_key}.")
            st.rerun()

    df = get_expenses()
    if not df.empty:
        month_df = df[df["expense_date"].str.startswith(month_key)]
    else:
        month_df = df
    total = summarize_expenses(month_df)["total"]
    status = calculate_budget_status(total, get_budget(month_key))
    a, b, c = st.columns(3)
    a.metric("Spent this month", money(total))
    b.metric("Budget", money(get_budget(month_key)))
    c.metric("Remaining", money(status["remaining"]))
    if get_budget(month_key) > 0:
        st.progress(min(total / get_budget(month_key), 1.0))
        if status["over_budget"]:
            st.error("Budget exceeded. Review the category breakdown below.")
        else:
            st.success(f'{status["percentage"]:.1f}% of your budget used.')

    st.subheader("Insights")
    for insight in generate_insights(month_df, get_budget(month_key)):
        st.write(f"• {insight}")

    st.subheader("Category breakdown")
    cat = category_summary(month_df)
    if cat.empty:
        st.info("No expenses for this month yet.")
    else:
        st.dataframe(cat, use_container_width=True, hide_index=True)

elif page == "Export data":
    st.title("Export data")
    st.write("Download your records as a CSV file for Excel, Power BI, or further analysis.")
    csv_data = export_expenses_csv()
    if csv_data:
        st.download_button("⬇️ Download expenses.csv", data=csv_data, file_name="expenseiq_expenses.csv", mime="text/csv")
        st.caption("The export contains your expense records. Keep exported files private if they contain personal information.")
    else:
        st.info("There are no records to export yet.")
