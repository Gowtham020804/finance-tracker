import streamlit as st
import smtplib
import calendar
import datetime

from email.mime.text import MIMEText


def create_monthly_report(

        username,
        total,
        budget,
        savings,
        prediction

):

    month = calendar.month_name[
        datetime.datetime.now().month
    ]

    report = f"""

📊 Monthly Expense Report


👤 User:
{username}


📅 Month:
{month}


💸 Total Expenses:
₹{total:.2f}


🎯 Budget:
₹{budget:.2f}


💰 Savings:
₹{savings:.2f}


🔮 Predicted Future Expense:
₹{prediction:.2f}


Thank you for using Financial Expense Tracker 🚀

"""

    return report


def send_email(

        receiver,
        report

):

    sender = st.secrets["EMAIL_USER"]

    app_password = st.secrets["EMAIL_PASSWORD"]

    try:

        msg = MIMEText(report)

        msg["Subject"] = "Monthly Expense Summary"

        msg["From"] = sender

        msg["To"] = receiver

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        server.starttls()

        server.login(
            sender,
            app_password
        )

        server.sendmail(
            sender,
            receiver,
            msg.as_string()
        )

        server.quit()

        return True, "Email sent successfully"

    except Exception as e:

        return False, str(e)
