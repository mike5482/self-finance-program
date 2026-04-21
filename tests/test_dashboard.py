from datetime import date

from .helpers import login_user, register_user, transaction_form


def test_dashboard_redirects_when_not_logged_in(client):
    resp = client.get("/dashboard", follow_redirects=False)
    assert resp.status_code in (301, 302)
    assert "login" in resp.headers.get("Location", "").lower()


def test_dashboard_loads_when_logged_in(client):
    register_user(client, "dash1", "pw")
    login_user(client, "dash1", "pw")
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data
    assert b"Total Income" in resp.data


def test_dashboard_reflects_transaction(client):
    register_user(client, "dash2", "pw")
    login_user(client, "dash2", "pw")
    client.post(
        "/add",
        data=transaction_form(
            amount="150.00",
            txn_type="income",
            category="Bonus",
            description="Year-end",
        ),
        follow_redirects=True,
    )
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert b"150.00" in resp.data or b"150" in resp.data
    assert b"Bonus" in resp.data


def test_monthly_summary_loads_with_current_month_transaction(client):
    register_user(client, "dash3", "pw")
    login_user(client, "dash3", "pw")
    client.post(
        "/add",
        data=transaction_form(
            amount="25.00",
            txn_type="expense",
            category="Gas",
            day=date.today().isoformat(),
        ),
        follow_redirects=True,
    )
    resp = client.get("/monthly_summary")
    assert resp.status_code == 200
    assert b"Monthly Summary" in resp.data
    assert b"Totals for This Month" in resp.data


def test_insights_page_loads_when_logged_in(client):
    register_user(client, "dash4", "pw")
    login_user(client, "dash4", "pw")
    resp = client.get("/insights")
    assert resp.status_code == 200
    assert b"Insights Dashboard" in resp.data
