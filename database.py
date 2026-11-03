
import sqlite3
import pandas as pd

DATABASE_NAME = "company_expenses.db"


# 1. Connect to the database
def get_connection():
    return sqlite3.connect(DATABASE_NAME)


# 2. Create the expense table
def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_name TEXT NOT NULL,
            employee_id TEXT NOT NULL,
            department TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            expense_date TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# 3. Add a new expense
def add_expense(
    employee_name,
    employee_id,
    department,
    category,
    amount,
    expense_date,
    description
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses (
            employee_name,
            employee_id,
            department,
            category,
            amount,
            expense_date,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        employee_name,
        employee_id,
        department,
        category,
        amount,
        expense_date,
        description
    ))

    conn.commit()
    conn.close()


# 4. Get all expense records
def get_all_expenses():

    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM expenses ORDER BY expense_date DESC, id DESC",
        conn
    )

    conn.close()

    return df


# 5. Update an expense
def update_expense(
    expense_id,
    employee_name,
    employee_id,
    department,
    category,
    amount,
    expense_date,
    description
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE expenses
        SET employee_name = ?,
            employee_id = ?,
            department = ?,
            category = ?,
            amount = ?,
            expense_date = ?,
            description = ?
        WHERE id = ?
    """, (
        employee_name,
        employee_id,
        department,
        category,
        amount,
        expense_date,
        description,
        expense_id
    ))

    conn.commit()
    conn.close()


# 6. Delete an expense
def delete_expense(expense_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()
    conn.close()


# 7. Get total expenses
def get_total_expenses():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses")

    result = cursor.fetchone()[0]

    conn.close()

    return result if result is not None else 0


# 8. Get expense count
def get_expense_count():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM expenses")

    result = cursor.fetchone()[0]

    conn.close()

    return result
