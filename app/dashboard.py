import streamlit as st
import pandas as pd
from app.charts import show_charts
from app.prediction import predict_expense
from app.utils import load_finance_data, create_email_body, get_expense_status


def dashboard_page():
    st.sidebar.success(f"Welcome {st.session_state.username} 👋")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("Financial Expense Tracker")

    if "expense_data" not in st.session_state:
        st.session_state.expense_data = []

    if "budget_limit" not in st.session_state:
        st.session_state.budget_limit = 0.0

    dataset = load_finance_data()

    if dataset is not None:
        st.subheader("Loaded Expense Dataset")
        st.caption("Data loaded from dataset files")
        st.dataframe(dataset)
    else:
        st.info("No valid dataset found in dataset/finance.csv. Use manual entries below.")

    st.subheader("Add New Expense")
    with st.form("expense_form", clear_on_submit=True):
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        category = st.selectbox(
            "Category",
            ["Food", "Transport", "Shopping", "Bills", "Entertainment"]
        )
        submitted = st.form_submit_button("Add Expense")

        if submitted:
            st.session_state.expense_data.append({
                "Amount": float(amount),
                "Category": category
            })
            st.success("Expense added successfully")

    st.subheader("Budget Settings")
    st.session_state.budget_limit = st.number_input(
        "Monthly Budget Limit",
        min_value=0.0,
        value=float(st.session_state.budget_limit),
        format="%.2f"
    )

    if dataset is not None and len(st.session_state.expense_data) > 0:
        manual_df = pd.DataFrame(st.session_state.expense_data)
        working_df = pd.concat([dataset, manual_df], ignore_index=True)
    elif dataset is not None:
        working_df = dataset.copy()
    else:
        working_df = pd.DataFrame(st.session_state.expense_data)

    if not working_df.empty:
        st.subheader("Expense Summary")
        st.dataframe(working_df)

        if "Date" in working_df.columns:
            try:
                working_df["Date"] = pd.to_datetime(working_df["Date"], errors="coerce")
                monthly_totals = (
                    working_df.dropna(subset=["Date"])
                    .groupby(working_df["Date"].dt.to_period("M"))["Amount"]
                    .sum()
                    .reset_index()
                )
                monthly_totals["Date"] = monthly_totals["Date"].dt.to_timestamp()
                st.markdown("**Monthly totals from dataset:**")
                st.dataframe(monthly_totals)
            except Exception:
                pass

        total_expense = working_df["Amount"].sum()
        st.metric("Total Expense", f"₹{total_expense:,.2f}")

        status = get_expense_status(total_expense, st.session_state.budget_limit)

        if st.session_state.budget_limit > 0:
            if status == "Profit":
                st.success(
                    f"Good job! This month is in PROFIT — under budget by ₹{st.session_state.budget_limit - total_expense:,.2f}"
                )
            else:
                st.error(
                    f"This month is in LOSS — over budget by ₹{total_expense - st.session_state.budget_limit:,.2f}"
                )
        else:
            st.info("Set a monthly budget to see profit/loss status.")

        show_charts(working_df)

        prediction = predict_expense(working_df)
        st.info(f"Predicted Next Month Expense: ₹{prediction:,.2f}")

        st.subheader("Email Summary")
        receiver = st.text_input("Recipient email address", key="receiver_email")

        if st.button("Generate Email Summary"):
            email_body = create_email_body(
                st.session_state.username,
                total_expense,
                st.session_state.budget_limit,
                prediction,
                status,
            )
            st.text_area("Email Preview", email_body, height=240)
            if receiver:
                st.success("Email preview generated. Configure SMTP settings to send actual messages.")
            else:
                st.warning("Enter a recipient email address to use this summary for email sending.")
    else:
        st.info("Add expenses or load a valid dataset to see predictions and profit/loss status.")
