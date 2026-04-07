# ------------------------------------------------------------
# File: init_db.py
# Date: April 2026
# Authors:
#   - Karan Gosai
#   - Michael Groves
#   - Kamal Al Shawa
#   - James Smith
#
# Description:
#   Initializes the SQLite database for the Self-Finance Program.
#   Creates tables for users, categories, and transactions.
#   Seeds default categories for income, expense, transfer, and gift.
# ------------------------------------------------------------

import sqlite3

# Category map used for seeding the database
CATEGORY_MAP = {
    "income": ["Salary", "Bonus", "Interest", "Gift Income"],
    "expense": ["Groceries", "Rent", "Utilities", "Dining", "Shopping", "Gas"],
    "transfer": ["Bank Transfer", "Credit Card Payment"],
    "gift": ["Gift Sent", "Donation"]
}

def init_db():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()

    # ------------------------------------------------------------
    # Create USERS table
    # ------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)

    # ------------------------------------------------------------
    # Create CATEGORIES table
    # ------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL
        );
    """)

    # ------------------------------------------------------------
    # Create TRANSACTIONS table
    # ------------------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            category_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );
    """)

    # ------------------------------------------------------------
    # Seed categories (only if they don't already exist)
    # ------------------------------------------------------------
    for type_name, category_list in CATEGORY_MAP.items():
        for category in category_list:
            cursor.execute("""
                INSERT OR IGNORE INTO categories (name, type)
                VALUES (?, ?)
            """, (category, type_name))

    conn.commit()
    conn.close()
    print("Database initialized successfully with all tables and categories.")


if __name__ == "__main__":
    init_db()