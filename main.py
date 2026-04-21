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
#
#   create_app() supports tests via app.config["DATABASE"].
# ------------------------------------------------------------

import datetime
import os
import sqlite3

from flask import (
    Flask,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from category_map import CATEGORY_MAP


def to_timestamp(date_str):
    """Convert YYYY-MM-DD to JS timestamp (ms)."""
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp() * 1000)


def six_months_ago_timestamp():
    six_months_ago = datetime.datetime.now() - datetime.timedelta(days=180)
    return int(six_months_ago.timestamp() * 1000)


def get_db_connection():
    conn = sqlite3.connect(current_app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def create_app(test_config=None):
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config.from_mapping(
        SECRET_KEY="capstone_secret_key_2026",
        DATABASE=os.path.join(basedir, "finance.db"),
    )
    if test_config:
        app.config.update(test_config)

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

        user_id = session["user_id"]
        conn = get_db_connection()
        cursor = conn.cursor()

        # Calculate income and expense totals
        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) AS income_total,
                COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) AS expense_total
            FROM transactions
            WHERE user_id = ?
        """, (user_id,))
        totals = cursor.fetchone()
        income_total = totals["income_total"]
        expense_total = totals["expense_total"]
        balance = income_total - expense_total

        # Get 10 most recent transactions
        cursor.execute("""
            SELECT t.date, t.type, t.amount, c.name AS category
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
            ORDER BY t.date DESC
            LIMIT 10
        """, (user_id,))
        transactions = cursor.fetchall()

        # Category breakdown for spending chart (expenses only)
        cursor.execute("""
            SELECT c.name AS category, SUM(t.amount) AS total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? AND t.type = 'expense'
            GROUP BY c.name
            ORDER BY total DESC
        """, (user_id,))
        category_totals = cursor.fetchall()
        conn.close()

        chart_labels = [row["category"] for row in category_totals]
        chart_data = [float(row["total"]) for row in category_totals]

        return render_template(
            "dashboard.html",
            user=session["user"],
            income_total=f"{income_total:.2f}",
            expense_total=f"{expense_total:.2f}",
            balance=f"{balance:.2f}",
            transactions=transactions,
            chart_labels=chart_labels,
            chart_data=chart_data
        )


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
            default_categories=CATEGORY_MAP["income"]
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

    @app.route("/insights")
    def insights():
        if "user_id" not in session:
            return redirect(url_for("login"))

        user_id = session["user_id"]

        conn = get_db_connection()
        cursor = conn.cursor()

        # -------------------------------
        # Chart 1: Category Trends (expenses only)
        # -------------------------------
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', t.date) AS month,
                c.name AS category,
                SUM(t.amount) AS total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
              AND t.type = 'expense'
              AND t.date >= date('now', '-6 months')
            GROUP BY month, category
            ORDER BY month;
        """, (user_id,))

        rows = cursor.fetchall()

        months = sorted(list({row["month"] for row in rows}))
        categories = sorted(list({row["category"] for row in rows}))

        data_by_category = {cat: [0] * len(months) for cat in categories}
        total_by_month = [0] * len(months)

        for row in rows:
            idx = months.index(row["month"])
            data_by_category[row["category"]][idx] = row["total"]
            total_by_month[idx] += row["total"]

        # -------------------------------
        # Chart 2: Income vs Expense
        # -------------------------------
        cursor.execute("""
            SELECT 
                strftime('%Y-%m', date) AS month,
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS total_income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS total_expense
            FROM transactions
            WHERE user_id = ?
              AND date >= date('now', '-6 months')
            GROUP BY month
            ORDER BY month;
        """, (user_id,))

        rows2 = cursor.fetchall()

        months_ie = [row["month"] for row in rows2]
        income = [row["total_income"] for row in rows2]
        expenses = [row["total_expense"] for row in rows2]

        # -------------------------------
        # Chart 3: Top 5 Categories
        # -------------------------------
        cursor.execute("""
            SELECT 
                c.name AS category,
                SUM(t.amount) AS total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
              AND t.type = 'expense'
              AND t.date >= date('now', '-6 months')
            GROUP BY c.name
            ORDER BY total DESC
            LIMIT 5;
        """, (user_id,))

        top_rows = cursor.fetchall()
        top_categories = [row["category"] for row in top_rows]
        top_totals = [row["total"] for row in top_rows]

        # -------------------------------
        # Chart 4: Transaction Timeline (income + expense)
        # -------------------------------
        cursor.execute("""
            SELECT 
                t.date,
                t.amount,
                t.description,
                c.name AS category,
                t.type
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
              AND t.date >= date('now', '-6 months')
            ORDER BY t.date;
        """, (user_id,))

        timeline_rows = cursor.fetchall()

        timeline_points = [
            {
                "x": to_timestamp(row["date"]),
                "y": row["amount"],
                "category": row["category"],
                "type": row["type"],
                "description": row["description"]
            }
            for row in timeline_rows
        ]

        six_months_ago_ts = six_months_ago_timestamp()

        # -------------------------------
        # Summary Cards
        # -------------------------------
        total_spending_6mo = sum(total_by_month) if total_by_month else 0
        top_category_name = top_categories[0] if top_categories else "N/A"

        if total_by_month:
            max_month_index = total_by_month.index(max(total_by_month))
            most_expensive_month = months[max_month_index]
        else:
            most_expensive_month = "N/A"

        conn.close()

        return render_template(
            "insights.html",
            months=months,
            data_by_category=data_by_category,
            total_by_month=total_by_month,
            months_ie=months_ie,
            income=income,
            expenses=expenses,
            top_categories=top_categories,
            top_totals=top_totals,
            timeline_points=timeline_points,
            six_months_ago_ts=six_months_ago_ts,
            total_spending_6mo=total_spending_6mo,
            top_category_name=top_category_name,
            most_expensive_month=most_expensive_month
        )
    # ------------------------------------------------------------
    # ROUTE: Edit Transaction (GET + POST)
    # ------------------------------------------------------------
    @app.route("/edit/<int:transaction_id>", methods=["GET", "POST"])
    def edit_transaction(transaction_id):
        user_id = session.get("user_id")
        if not user_id:
            flash("You must be logged in.", "error")
            return redirect(url_for("login"))

        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch the transaction (ensure it belongs to the logged-in user)
        cursor.execute("""
            SELECT t.*, c.name AS category
            FROM transactions t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE t.id = ? AND t.user_id = ?
        """, (transaction_id, user_id))
        transaction = cursor.fetchone()

        if not transaction:
            conn.close()
            flash("Transaction not found.", "error")
            return redirect(url_for("view_transactions"))

        if request.method == "POST":
            amount = request.form["amount"]
            date = request.form["date"]
            description = request.form["description"]
            type_selected = request.form["type"]
            category_selected = request.form["category"]

            cursor.execute("SELECT id FROM categories WHERE name = ?", (category_selected,))
            category_row = cursor.fetchone()

            if category_row is None:
                conn.close()
                flash("Selected category not found.", "error")
                return redirect(url_for("edit_transaction", transaction_id=transaction_id))

            cursor.execute("""
                UPDATE transactions
                SET amount = ?, date = ?, description = ?, type = ?, category_id = ?
                WHERE id = ? AND user_id = ?
            """, (amount, date, description, type_selected, category_row["id"], transaction_id, user_id))

            conn.commit()
            conn.close()
            flash("Transaction updated!", "success")
            return redirect(url_for("view_transactions"))

        conn.close()
        return render_template(
            "edit_transaction.html",
            transaction=transaction,
            category_map=CATEGORY_MAP,
            default_categories=CATEGORY_MAP.get(transaction["type"], [])
        )


    # ------------------------------------------------------------
    # ROUTE: Delete Transaction
    # ------------------------------------------------------------
    @app.route("/delete/<int:transaction_id>", methods=["POST"])
    def delete_transaction(transaction_id):
        user_id = session.get("user_id")
        if not user_id:
            flash("You must be logged in.", "error")
            return redirect(url_for("login"))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id))
        conn.commit()
        conn.close()

        flash("Transaction deleted.", "success")
        return redirect(url_for("view_transactions"))


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

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
