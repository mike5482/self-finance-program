import sqlite3

connection = sqlite3.connect("finance.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
""")

connection.commit()
connection.close()

print("Database initialized successfully.")
