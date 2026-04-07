import sqlite3
import os

# Path to the project root (one folder up from /tests)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to finance.db inside the project root
DB_PATH = os.path.join(BASE_DIR, "finance.db")

# Safety check: prevent accidental creation of a new DB
if not os.path.exists(DB_PATH):
    raise FileNotFoundError(f"ERROR: finance.db not found at:\n{DB_PATH}\n"
                            "Make sure you ran init_db.py and that you're in the correct project structure.")

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
    print("\nDatabase test complete.\n")
