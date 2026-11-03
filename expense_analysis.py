
import pandas as pd


# 1. Calculate total expenses
def calculate_total_expenses(df):

    if df.empty:
        return 0

    return df["amount"].sum()


# 2. Department-wise expense analysis
def department_analysis(df):

    if df.empty:
        return pd.DataFrame(
            columns=["department", "amount"]
        )

    result = df.groupby("department")["amount"].sum()

    return result.reset_index()


# 3. Category-wise expense analysis
def category_analysis(df):

    if df.empty:
        return pd.DataFrame(
            columns=["category", "amount"]
        )

    result = df.groupby("category")["amount"].sum()

    return result.reset_index()


# 4. Monthly expense analysis
def monthly_analysis(df):

    if df.empty:
        return pd.DataFrame(
            columns=["month", "amount"]
        )

    data = df.copy()

    data["expense_date"] = pd.to_datetime(
        data["expense_date"],
        errors="coerce"
    )

    data = data.dropna(subset=["expense_date"])

    data["month"] = (
        data["expense_date"].dt.to_period("M").astype(str)
    )

    result = (
        data.groupby("month")["amount"]
        .sum()
        .reset_index()
    )

    return result


# 5. Find the highest spending department
def highest_spending_department(df):

    if df.empty:
        return "No data available"

    result = df.groupby("department")["amount"].sum()

    return result.idxmax()


# 6. Find unusual expenses using a simple rule
def find_unusual_expenses(df):

    if df.empty:
        return df.copy()

    # Flag expenses greater than twice
    # the overall average expense amount.
    average = df["amount"].mean()

    unusual = df[df["amount"] > average * 2].copy()

    return unusual


# 7. Generate a simple financial summary
def generate_insights(df):

    if df.empty:
        return "No expense records available for analysis."

    total = calculate_total_expenses(df)

    average = df["amount"].mean()

    highest_department = highest_spending_department(df)

    unusual = find_unusual_expenses(df)

    summary = f"""
    COMPANY EXPENSE ANALYSIS

    Total Expenses: Rs. {total:,.2f}

    Number of Expense Records: {len(df)}

    Average Expense: Rs. {average:,.2f}

    Highest Spending Department: {highest_department}

    Unusual Expense Records: {len(unusual)}
    """

    return summary
