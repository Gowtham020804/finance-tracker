import streamlit as st
import pandas as pd

from app.charts import show_charts
from app.prediction import predict_expense
from app.utils import load_finance_data, get_expense_status
from app.smtp_service import (
    send_email,
    create_monthly_report
)


def dashboard_page():

    st.sidebar.success(
        f"Welcome {st.session_state.username} 👋"
    )

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

        st.caption(
            "Dataset loaded successfully"
        )

        st.dataframe(dataset)

    else:

        st.info(
            "No dataset found in dataset/finance.csv"
        )

    st.subheader("➕ Add New Expense")

    with st.form(
            "expense_form",
            clear_on_submit=True
    ):

        amount = st.number_input(
            "Amount",
            min_value=0.0,
            format="%.2f"
        )

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

        submitted = st.form_submit_button(
            "Add Expense"
        )

        if submitted:

            st.session_state.expense_data.append({

                "Amount": float(amount),
                "Category": category

            })

            st.success(
                "Expense added successfully"
            )

    st.subheader("🎯 Budget Settings")

    st.session_state.budget_limit = st.number_input(

        "Monthly Budget Limit",

        min_value=0.0,

        value=float(
            st.session_state.budget_limit
        ),

        format="%.2f"

    )

    if (
            dataset is not None and
            len(st.session_state.expense_data) > 0
    ):

        manual_df = pd.DataFrame(
            st.session_state.expense_data
        )

        working_df = pd.concat(

            [dataset, manual_df],

            ignore_index=True

        )

    elif dataset is not None:

        working_df = dataset.copy()

    else:

        working_df = pd.DataFrame(
            st.session_state.expense_data
        )

    if not working_df.empty:

        st.subheader("📊 Expense Summary")

        st.dataframe(working_df)

        if "Date" in working_df.columns:

            try:

                working_df["Date"] = pd.to_datetime(

                    working_df["Date"],
                    errors="coerce"

                )

                monthly_totals = (

                    working_df
                    .dropna(subset=["Date"])
                    .groupby(

                        working_df["Date"]
                        .dt.to_period("M")

                    )["Amount"]
                    .sum()
                    .reset_index()

                )

                monthly_totals["Date"] = (

                    monthly_totals["Date"]
                    .dt.to_timestamp()

                )

                st.markdown(
                    "### 📅 Monthly Expense Totals"
                )

                st.dataframe(monthly_totals)

            except Exception:

                pass

        total_expense = working_df["Amount"].sum()

        st.metric(

            "💸 Total Expense",

            f"₹{total_expense:,.2f}"

        )

        status = get_expense_status(

            total_expense,

            st.session_state.budget_limit

        )

        if st.session_state.budget_limit > 0:

            if status == "Profit":

                savings = (

                    st.session_state.budget_limit
                    - total_expense

                )

                st.success(

                    f"✅ Great! "
                    f"You saved ₹{savings:,.2f}"

                )

            else:

                loss = (

                    total_expense
                    - st.session_state.budget_limit

                )

                st.error(

                    f"⚠ Budget exceeded "
                    f"by ₹{loss:,.2f}"

                )

        else:

            st.info(
                "Set a monthly budget limit"
            )

        st.subheader("📈 Expense Charts")

        show_charts(working_df)

        prediction = predict_expense(
            working_df
        )

        st.info(

            f"🔮 Predicted Next Month "
            f"Expense: ₹{prediction:,.2f}"

        )

        st.subheader("📧 Email Summary")

        receiver = st.text_input(

            "Recipient Email Address",

            key="receiver_email"

        )

        if st.button(
                "Generate Email Summary"
        ):

            savings = max(

                st.session_state.budget_limit
                - total_expense,

                0

            )

            email_body = create_monthly_report(

                st.session_state.username,

                total_expense,

                st.session_state.budget_limit,

                savings,

                prediction

            )

            st.text_area(

                "📨 Email Preview",

                email_body,

                height=300

            )

            if not receiver:

                st.warning(
                    "Please enter an email address"
                )

            else:

                with st.spinner(
                        "Sending Email..."
                ):

                    success, msg = send_email(

                        receiver,

                        email_body

                    )

                if success:

                    st.success(

                        f"✅ Email sent successfully "
                        f"to {receiver}"

                    )

                else:

                    st.error(

                        f"❌ Failed to send email: {msg}"

                    )

    else:

        st.info(

            "Add expenses or load dataset "
            "to continue"

        )
