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

import os
import sqlite3

from category_map import CATEGORY_MAP


def init_database(db_path: str) -> None:
    """Create tables and seed categories at the given SQLite path."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL
        );
    """)

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

    for type_name, category_list in CATEGORY_MAP.items():
        for category in category_list:
            cursor.execute("""
                INSERT OR IGNORE INTO categories (name, type)
                VALUES (?, ?)
            """, (category, type_name))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "finance.db")
    init_database(default_path)
    print("Database initialized successfully with all tables and categories.")
