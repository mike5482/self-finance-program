from datetime import date

from category_map import CATEGORY_MAP


def register_user(client, username="testuser", password="testpass123"):
    return client.post(
        "/register",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def login_user(client, username="testuser", password="testpass123"):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def transaction_form(
    *,
    amount="100.50",
    day=None,
    description="Test txn",
    txn_type="expense",
    category=None,
):
    if day is None:
        day = date.today().isoformat()
    if category is None:
        category = CATEGORY_MAP[txn_type][0]
    return {
        "amount": amount,
        "date": day,
        "description": description,
        "type": txn_type,
        "category": category,
    }
