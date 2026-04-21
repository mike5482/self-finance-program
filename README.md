Project Title: Personal Finance Tracker (Flask + SQLite)

Overview:  
This project is a lightweight personal finance tracking application built using Python, Flask, and SQLite. It allows users to create accounts, log in securely, and record financial transactions such as income, expenses, gifts, and transfers. Each transaction stores a primary category selected by the user and supports a secondary refined category that can be assigned later through categorization logic. The application is designed to be modular, easy to extend, and suitable for team collaboration.

The software was developed in PyCharm because it provides excellent tools for managing Python virtual environments and dependencies. Using PyCharm helps ensure that packages remain consistent across machines and reduces the risk of version conflicts. Anyone running or extending this project should use a virtual environment and a reliable dependency management workflow.

Features
• User registration and secure login
• Session-based authentication
• Add income and expense transactions
• Primary category selection (income, expense, gift, transfer)
• Support for secondary refined categories (such as Groceries, Rent, Utilities)
• Dashboard, monthly summary, and insights views
• SQLite database backend
• Utility script for inspecting database contents

Technologies Used
• Python 3
• Flask web framework
• SQLite database
• Werkzeug for password hashing
• HTML templates using Jinja2
• pytest for automated testing
• PyCharm IDE for development and package management

Project Structure
The project contains the following main components:

• [main.py](main.py) – Flask application factory (`create_app`) and route definitions
• [category_map.py](category_map.py) – Shared category names for the UI and database seeding
• [init_db.py](init_db.py) – Initializes SQLite tables and seeds the categories table
• [finance.db](finance.db) – SQLite database file (gitignored; created when you run `init_db.py`)
• [templates/](templates/) – HTML templates (login, dashboard, transactions, insights, etc.)
• [static/](static/) – CSS and optional JavaScript
• [tests/](tests/) – pytest suite (auth, transactions, dashboard, database schema)
• [scripts/inspect_db.py](scripts/inspect_db.py) – Optional CLI to print users and transactions from `finance.db`

Database Schema
Users Table:  
Stores login credentials.  
Fields include: id, username, password (hashed)

Transactions Table:  
Stores all financial entries for each user.  
Fields include: id, user_id, amount, date, description, type (primary category), category_id (secondary category)

Categories Table:  
Stores refined category names such as Groceries, Rent, Utilities.  
Fields include: id, name, type

This structure supports both user-selected categories and more detailed categorization logic added later.

Installation and Setup
Install Python 3 if it is not already installed.

Create and activate a virtual environment.

Install dependencies:

```bash
pip install -r requirements.txt
```

Initialize the database (creates `finance.db` in the project folder):

```bash
python init_db.py
```

Run the application:

```bash
python main.py
```

Open a browser at `http://127.0.0.1:5000` to use the site.

Optional: inspect the local database from the command line:

```bash
python scripts/inspect_db.py
```

Running the tests
Automated tests use **pytest** and Flask’s **test client**. They do **not** use your real `finance.db`: each test uses its own temporary SQLite file via `app.config["DATABASE"]` in [tests/conftest.py](tests/conftest.py).

```bash
pytest
```

Useful variants:

```bash
pytest -v
pytest tests/test_auth.py
```

Test coverage (summary)
• **Authentication** ([tests/test_auth.py](tests/test_auth.py)): registration, duplicate username, login success and failures, logout.
• **Transactions** ([tests/test_transactions.py](tests/test_transactions.py)): add income and expense, invalid category, missing field (HTTP 400), edit, delete.
• **Dashboard and pages** ([tests/test_dashboard.py](tests/test_dashboard.py)): auth redirect, dashboard content, data after insert, monthly summary, insights page.
• **Database** ([tests/test_db.py](tests/test_db.py)): tables exist after `init_database`, category seed count.

Limitations: no real-browser tests; client-side chart scripts are not executed by the test client; monthly summary tests use today’s date so they match SQL `strftime` filters.
