import glob
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset')
CSV_FILE = os.path.join(DATA_DIR, 'finance.csv')


def _load_csv(path):
    try:
        df = pd.read_csv(path)
    except Exception:
        return None

    if df.empty or 'Amount' not in df.columns:
        return None

    return df


def _load_excel(path):
    try:
        df = pd.read_excel(path, engine='openpyxl')
    except Exception:
        return None

    if df.empty or 'Amount' not in df.columns:
        return None

    return df


def load_finance_data():
    if os.path.isfile(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
        df = _load_csv(CSV_FILE)
        if df is not None:
            return df

    excel_files = sorted(glob.glob(os.path.join(DATA_DIR, '*.xlsx')))
    for excel_file in excel_files:
        df = _load_excel(excel_file)
        if df is not None:
            try:
                df.to_csv(CSV_FILE, index=False)
            except Exception:
                pass
            return df

    return None


def get_expense_status(total_expense, budget_limit):
    if budget_limit is None or budget_limit <= 0:
        return 'Budget not set'

    return 'Profit' if total_expense <= budget_limit else 'Loss'


def create_email_body(username, total_expense, budget_limit, prediction, status):
    lines = [
        f'Hello {username},',
        '',
        'Here is your monthly expense summary:',
        f'- Total expense this month: ₹{total_expense:,.2f}',
    ]

    if budget_limit is not None and budget_limit > 0:
        lines.append(f'- Monthly budget limit: ₹{budget_limit:,.2f}')
        if status == 'Profit':
            lines.append('- Status: PROFIT (within budget)')
        elif status == 'Loss':
            lines.append('- Status: LOSS (over budget)')
        else:
            lines.append(f'- Status: {status}')
    else:
        lines.append('- Status: Budget not set, so profit/loss cannot be determined.')

    lines.append(f'- Predicted expense next month: ₹{prediction:,.2f}')
    lines.append('')
    lines.append('Keep tracking your expenses to stay on budget.')
    lines.append('Thank you.')

    return '\n'.join(lines)
