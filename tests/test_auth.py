from .helpers import login_user, register_user


def test_register_success(client):
    resp = register_user(client, "alice", "secret123")
    assert resp.status_code == 200
    assert b"Registration successful" in resp.data or b"login" in resp.data.lower()


def test_register_duplicate_username(client):
    register_user(client, "bob", "pw1")
    resp = register_user(client, "bob", "pw2")
    assert resp.status_code == 200
    assert b"already exists" in resp.data


def test_login_success(client):
    register_user(client, "carol", "goodpass")
    resp = login_user(client, "carol", "goodpass")
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data


def test_login_unknown_user(client):
    resp = login_user(client, "nobody_here", "any")
    assert resp.status_code == 200
    assert b"not recognized" in resp.data.lower()


def test_login_wrong_password(client):
    register_user(client, "dave", "rightpass")
    resp = login_user(client, "dave", "wrongpass")
    assert resp.status_code == 200
    assert b"Incorrect password" in resp.data


def test_logout_clears_session(client):
    register_user(client, "eve", "evepass")
    login_user(client, "eve", "evepass")
    client.get("/logout", follow_redirects=True)
    resp = client.get("/dashboard", follow_redirects=False)
    assert resp.status_code in (301, 302)
    assert "/login" in resp.headers.get("Location", "")
