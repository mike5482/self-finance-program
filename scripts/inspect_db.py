"""Print users and transactions from the local finance.db (development utility)."""
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "finance.db")

if not os.path.exists(DB_PATH):
    raise FileNotFoundError(
        f"finance.db not found at:\n{DB_PATH}\n"
        "Run: python init_db.py\n"
        "Then use the app or tests to add data."
    )


def show_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("\n=== USERS ===")
    cursor.execute("SELECT id, username FROM users;")
    for row in cursor.fetchall():
        print(row)
    conn.close()


def show_transactions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print("\n=== TRANSACTIONS ===")
    cursor.execute("""
        SELECT id, user_id, amount, date, description, type
        FROM transactions;
    """)
    for row in cursor.fetchall():
        print(row)
    conn.close()


if __name__ == "__main__":
    show_users()
    show_transactions()
    print("\nDatabase inspection complete.\n")
