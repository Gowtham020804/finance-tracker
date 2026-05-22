import streamlit as st
import pandas as pd
import requests
import datetime

from app.charts import show_charts
from app.prediction import predict_expense
from app.utils import load_finance_data, get_expense_status
from app.smtp_service import (
    send_email,
    create_monthly_report
)

# Backend API base URL — override via Streamlit secrets if present
API_URL = st.secrets.get("API_URL", "https://finance-tracker-mv0i.onrender.com")


def dashboard_page():
    st.sidebar.success(f"Welcome {st.session_state.username} 👋")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("💰 Financial Expense Tracker")

    if "expense_data" not in st.session_state:
        st.session_state.expense_data = []

    if "budget_limit" not in st.session_state:
        st.session_state.budget_limit = 0.0

    dataset = load_finance_data()

    if dataset is not None:
        st.subheader("📂 Loaded Expense Dataset")
        st.caption("Dataset loaded successfully")
        st.dataframe(dataset)
    else:
        st.info("No dataset found in dataset/finance.csv")
    
        # Show backend DB health status
        try:
            h = requests.get(f"{API_URL}/health", timeout=3).json()
            if h.get("database") == "ok":
                st.sidebar.success("Backend DB: connected")
            else:
                st.sidebar.warning("Backend DB: unreachable — using fallback or remote DB")
        except Exception:
            st.sidebar.warning("Backend health check failed")

    backend_expenses = []
    if st.session_state.get("logged_in") and st.session_state.get("username"):
        try:
            headers = {}
            token = st.session_state.get("token")
            if token:
                headers["Authorization"] = f"Bearer {token}"

            resp = requests.get(
                f"{API_URL}/expenses/{st.session_state.username}",
                timeout=5,
                headers=headers,
            )
            if resp.status_code == 200:
                backend_expenses = resp.json()
        except Exception:
            backend_expenses = []

    st.subheader("➕ Add New Expense")
    with st.form("expense_form", clear_on_submit=True):
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        category = st.selectbox(
            "Category",
            [
                "Food",
                "Transport",
                "Shopping",
                "Bills",
                "Entertainment",
                "Healthcare",
                "Investments"
            ]
        )
        submitted = st.form_submit_button("Add Expense")

        if submitted:
            expense_payload = {
                "username": st.session_state.get("username", "anonymous"),
                "amount": float(amount),
                "category": category,
                "description": "",
                "date": datetime.datetime.utcnow().isoformat(),
            }
            try:
                headers = {}
                token = st.session_state.get("token")
                if token:
                    headers["Authorization"] = f"Bearer {token}"

                resp = requests.post(
                    f"{API_URL}/expense",
                    json=expense_payload,
                    timeout=5,
                    headers=headers,
                )

                if resp.status_code == 200:
                    st.success("Expense added successfully")
                else:
                    st.warning("Could not save to backend; saved locally only")
                    st.session_state.expense_data.append({
                        "Amount": float(amount),
                        "Category": category,
                        "Date": expense_payload["date"],
                    })
            except Exception:
                st.warning("Backend unreachable; saved locally only")
                st.session_state.expense_data.append({
                    "Amount": float(amount),
                    "Category": category,
                    "Date": expense_payload["date"],
                })

    st.subheader("🎯 Budget Settings")
    st.session_state.budget_limit = st.number_input(
        "Monthly Budget Limit",
        min_value=0.0,
        value=float(st.session_state.budget_limit),
        format="%.2f"
    )

    frames = []
    if dataset is not None:
        frames.append(dataset.copy())

    if st.session_state.expense_data:
        frames.append(pd.DataFrame(st.session_state.expense_data))

    if backend_expenses:
        try:
            be_df = pd.DataFrame(backend_expenses)
            if not be_df.empty:
                if "amount" in be_df.columns:
                    be_df = be_df.rename(columns={"amount": "Amount"})
                if "category" in be_df.columns:
                    be_df = be_df.rename(columns={"category": "Category"})
                if "date" in be_df.columns:
                    be_df = be_df.rename(columns={"date": "Date"})
                cols = [c for c in ["Amount", "Category", "Date"] if c in be_df.columns]
                be_df = be_df[cols]
                frames.append(be_df)
        except Exception:
            pass

    if frames:
        working_df = pd.concat(frames, ignore_index=True)
    else:
        working_df = pd.DataFrame()

    if working_df.empty:
        st.info("Add expenses or load dataset to continue")
        return

    st.subheader("📊 Expense Summary")
    st.dataframe(working_df)

    if "Date" in working_df.columns:
        try:
            working_df["Date"] = pd.to_datetime(working_df["Date"], errors="coerce")
            monthly_totals = (
                working_df.dropna(subset=["Date"])                     .groupby(working_df["Date"].dt.to_period("M"))["Amount"]                     .sum()                     .reset_index()
            )
            monthly_totals["Date"] = monthly_totals["Date"].dt.to_timestamp()
            st.markdown("### 📅 Monthly Expense Totals")
            st.dataframe(monthly_totals)
        except Exception:
            pass

    total_expense = working_df["Amount"].sum()
    st.metric("💸 Total Expense", f"₹{total_expense:,.2f}")

    status = get_expense_status(total_expense, st.session_state.budget_limit)
    if st.session_state.budget_limit > 0:
        if status == "Profit":
            savings = st.session_state.budget_limit - total_expense
            st.success(f"✅ Great! You saved ₹{savings:,.2f}")
        else:
            loss = total_expense - st.session_state.budget_limit
            st.error(f"⚠ Budget exceeded by ₹{loss:,.2f}")
    else:
        st.info("Set a monthly budget limit")

    st.subheader("📈 Expense Charts")
    show_charts(working_df)

    prediction = predict_expense(working_df)
    st.info(f"🔮 Predicted Next Month Expense: ₹{prediction:,.2f}")

    st.subheader("📧 Email Summary")
    receiver = st.text_input("Recipient Email Address", key="receiver_email")

    if st.button("Generate Email Summary"):
        savings = max(st.session_state.budget_limit - total_expense, 0)
        email_body = create_monthly_report(
            st.session_state.username,
            total_expense,
            st.session_state.budget_limit,
            savings,
            prediction
        )
        st.text_area("📨 Email Preview", email_body, height=300)

        if not receiver:
            st.warning("Please enter an email address")
        else:
            with st.spinner("Sending Email..."):
                success, msg = send_email(receiver, email_body)
            if success:
                st.success(f"✅ Email sent successfully to {receiver}")
            else:
                st.error(f"❌ Failed to send email: {msg}")
