# ------------------------------------------------------------
# File: main.py
# Date: April 2026
# Authors:
#   - Karan Gosai
#   - Michael Groves
#   - Kamal Al Shawa
#   - James Smith
#
# Description:
#   Main Flask application handling routing, authentication,
#   session management, category mapping, and transaction submission.
# ------------------------------------------------------------

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3


# ------------------------------------------------------------
# CATEGORY MAP (Top-level → Subcategories)
# Used to populate dynamic dropdowns in add_transaction.html
# ------------------------------------------------------------
CATEGORY_MAP = {
    "income": ["Salary", "Bonus", "Interest", "Gift Income"],
    "expense": ["Groceries", "Rent", "Utilities", "Dining", "Shopping", "Gas"],
    "transfer": ["Bank Transfer", "Credit Card Payment"],
    "gift": ["Gift Sent", "Donation"]
}


# ------------------------------------------------------------
# Database connection helper
# ------------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect("finance.db")
    conn.row_factory = sqlite3.Row
    return conn


app = Flask(__name__)
app.secret_key = "capstone_secret_key_2026"


# ------------------------------------------------------------
# ROUTE: Home Page
# ------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ------------------------------------------------------------
# ROUTE: User Registration
# ------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username already exists.")
            conn.close()
            return redirect(url_for("register"))

        # Insert new user
        hashed_pw = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_pw)
        )

        conn.commit()
        conn.close()

        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


# ------------------------------------------------------------
# ROUTE: User Login
# ------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user is None:
            flash("User not recognized.", "error")
            return redirect(url_for("login"))

        if not check_password_hash(user["password"], password):
            flash("Incorrect password.", "error")
            return redirect(url_for("login"))

        # Login successful
        session["user_id"] = user["id"]
        session["user"] = username
        flash("Login successful!", "success")

        return redirect(url_for("dashboard"))

    return render_template("login.html")


# ------------------------------------------------------------
# ROUTE: Dashboard (Requires Login)
# ------------------------------------------------------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=session["user"])


# ------------------------------------------------------------
# ROUTE: Add Transaction (GET + POST)
# ------------------------------------------------------------
@app.route("/add", methods=["GET", "POST"])
def add_transaction():
    # Must be logged in
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in to add transactions.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        amount = request.form["amount"]
        date = request.form["date"]
        description = request.form["description"]
        type_selected = request.form["type"]        # income / expense / transfer / gift
        category_selected = request.form["category"]  # subcategory name

        conn = get_db_connection()
        cursor = conn.cursor()

        # Look up category_id from the categories table
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category_selected,))
        category_row = cursor.fetchone()

        if category_row is None:
            conn.close()
            flash("Selected category not found in database.", "error")
            return redirect(url_for("add_transaction"))

        category_id = category_row["id"]

        # Insert transaction with category_id
        cursor.execute("""
            INSERT INTO transactions (user_id, amount, date, description, type, category_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, amount, date, description, type_selected, category_id))

        conn.commit()
        conn.close()

        flash("Transaction added successfully!", "success")
        return redirect(url_for("dashboard"))

    # GET request → show form
    return render_template(
        "add_transaction.html",
        category_map=CATEGORY_MAP,
        default_categories=CATEGORY_MAP["expense"]
    )

# ------------------------------------------------------------
# ROUTE: View All Transactions (Requires Login)
# ------------------------------------------------------------
@app.route("/view_transactions")
def view_transactions():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.id, t.date, t.amount, t.description, t.type,
               c.name AS category
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
        ORDER BY t.date DESC
    """, (user_id,))

    transactions = cursor.fetchall()
    conn.close()

    return render_template("view_transactions.html", transactions=transactions)

# ------------------------------------------------------------
# ROUTE: Monthly Summary (Requires Login)
# ------------------------------------------------------------
@app.route("/monthly_summary")
def monthly_summary():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    # Monthly totals
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN type='income' THEN amount ELSE 0 END) AS total_income,
            SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS total_expense
        FROM transactions
        WHERE user_id = ?
          AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    """, (user_id,))
    totals = cursor.fetchone()

    # Category breakdown (expenses only)
    cursor.execute("""
        SELECT c.name AS category, SUM(t.amount) AS total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
          AND t.type = 'expense'
          AND strftime('%Y-%m', t.date) = strftime('%Y-%m', 'now')
        GROUP BY c.name
        ORDER BY total DESC
    """, (user_id,))
    category_totals = cursor.fetchall()

    # All transactions for the month
    cursor.execute("""
        SELECT t.*, c.name AS category
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
          AND strftime('%Y-%m', t.date) = strftime('%Y-%m', 'now')
        ORDER BY t.date DESC
    """, (user_id,))
    transactions = cursor.fetchall()

    conn.close()

    return render_template(
        "monthly_summary.html",
        totals=totals,
        category_totals=category_totals,
        transactions=transactions
    )




# ------------------------------------------------------------
# ROUTE: Logout
# ------------------------------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ------------------------------------------------------------
# Run the Flask App
# ------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
