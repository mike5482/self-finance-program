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
#   session management, and transaction submission.
# ------------------------------------------------------------

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

# Create a reusable database connection
def get_db_connection():
    conn = sqlite3.connect("finance.db")
    conn.row_factory = sqlite3.Row  # Allows column access by name
    return conn

app = Flask(__name__)
app.secret_key = "capstone_secret_key_2026"  # Used for session security

# Example admin user (not used for DB login)
users = {
    "admin": {
        "password": generate_password_hash("password")
    }
}

@app.route("/")
def home():
    # Show the homepage
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    # Handles new user registration
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username already exists.")
            conn.close()
            return redirect(url_for("register"))

        # Hash the password before saving
        hashed_pw = generate_password_hash(password)

        # Insert new user into the database
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_pw)
        )

        conn.commit()
        conn.close()

        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))

    # Show registration page
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    # Handles user login
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Look up the user in the database
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user is None:
            flash("User not recognized. Please check your username.", "error")
            return redirect(url_for("login"))

        # Verify password
        if not check_password_hash(user["password"], password):
            flash("Incorrect password. Please try again.", "error")
            return redirect(url_for("login"))

        # Login successful → store user info in session
        flash("Login successful. Welcome!", "success")
        session["user_id"] = user["id"]   # Needed for linking transactions
        session["user"] = username        # Optional display name

        return redirect(url_for("dashboard"))

    # Show login page
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    # Only logged-in users can view the dashboard
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html", user=session["user"])

@app.route("/add", methods=["GET", "POST"])
def add_transaction():
    # Ensure user is logged in
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in to add transactions.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        # Collect form data
        amount = request.form["amount"]
        date = request.form["date"]
        description = request.form["description"]
        type_ = request.form["type"]                # income or expense
        primary_category = request.form["category"] # dropdown category

        conn = sqlite3.connect("finance.db")
        cursor = conn.cursor()

        # Insert transaction with primary category only
        cursor.execute("""
            INSERT INTO transactions (user_id, amount, date, description, type, category_id)
            VALUES (?, ?, ?, ?, ?, NULL)
        """, (user_id, amount, date, description, primary_category))

        conn.commit()
        conn.close()

        flash("Transaction added successfully!", "success")
        return redirect(url_for("dashboard"))

    # Show the Add Transaction form
    return render_template("add_transaction.html")

@app.route("/logout")
def logout():
    # Clear session and log the user out
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
