import sqlite3

from .helpers import login_user, register_user, transaction_form


def _count_transactions(db_path):
    conn = sqlite3.connect(db_path)
    n = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    conn.close()
    return n


def test_add_income_transaction(client, db_path):
    register_user(client, "u1", "p1")
    login_user(client, "u1", "p1")
    resp = client.post(
        "/add",
        data=transaction_form(
            amount="2500.00",
            txn_type="income",
            category="Salary",
            description="Paycheck",
        ),
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data
    assert _count_transactions(db_path) == 1


def test_add_expense_transaction(client, db_path):
    register_user(client, "u2", "p2")
    login_user(client, "u2", "p2")
    client.post(
        "/add",
        data=transaction_form(
            amount="42.99",
            txn_type="expense",
            category="Groceries",
        ),
        follow_redirects=True,
    )
    assert _count_transactions(db_path) == 1


def test_add_transaction_invalid_category(client, db_path):
    register_user(client, "u3", "p3")
    login_user(client, "u3", "p3")
    data = transaction_form(category="NotARealCategory")
    data["category"] = "NotARealCategory"
    resp = client.post("/add", data=data, follow_redirects=True)
    assert resp.status_code == 200
    assert b"not found" in resp.data.lower()
    assert _count_transactions(db_path) == 0


def test_add_transaction_missing_amount_returns_400(client):
    register_user(client, "u4", "p4")
    login_user(client, "u4", "p4")
    resp = client.post(
        "/add",
        data={
            "date": "2026-01-15",
            "description": "x",
            "type": "expense",
            "category": "Groceries",
        },
    )
    assert resp.status_code == 400


def test_edit_transaction(client, db_path):
    register_user(client, "u5", "p5")
    login_user(client, "u5", "p5")
    client.post(
        "/add",
        data=transaction_form(amount="10", description="orig"),
        follow_redirects=True,
    )
    conn = sqlite3.connect(db_path)
    tid = conn.execute("SELECT id FROM transactions LIMIT 1").fetchone()[0]
    conn.close()

    resp = client.post(
        f"/edit/{tid}",
        data=transaction_form(amount="99.00", description="updated"),
        follow_redirects=True,
    )
    assert resp.status_code == 200

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT amount, description FROM transactions WHERE id = ?", (tid,)
    ).fetchone()
    conn.close()
    assert float(row[0]) == 99.0
    assert row[1] == "updated"


def test_delete_transaction(client, db_path):
    register_user(client, "u6", "p6")
    login_user(client, "u6", "p6")
    client.post(
        "/add",
        data=transaction_form(amount="5"),
        follow_redirects=True,
    )
    conn = sqlite3.connect(db_path)
    tid = conn.execute("SELECT id FROM transactions LIMIT 1").fetchone()[0]
    conn.close()

    resp = client.post(f"/delete/{tid}", follow_redirects=True)
    assert resp.status_code == 200
    assert _count_transactions(db_path) == 0
