import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def predict_expense(df):
    if df is None or df.empty or 'Amount' not in df.columns:
        return 0.0

    df = df.copy()

    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

        if df.empty:
            return 0.0

        monthly = (
            df.groupby(df['Date'].dt.to_period('M'))['Amount']
            .sum()
            .reset_index()
        )
        X = np.arange(len(monthly)).reshape(-1, 1)
        y = monthly['Amount'].values
    else:
        X = np.arange(len(df)).reshape(-1, 1)
        y = df['Amount'].values

    if len(X) < 2:
        return round(float(y[-1]), 2)

    model = LinearRegression()
    model.fit(X, y)

    future = model.predict([[len(X)]])[0]
    return round(float(future), 2)
