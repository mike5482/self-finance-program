import sqlite3

from category_map import CATEGORY_MAP
from init_db import init_database


def _expected_category_rows():
    return sum(len(names) for names in CATEGORY_MAP.values())


def test_init_database_creates_tables(db_path):
    init_database(db_path)
    conn = sqlite3.connect(db_path)
    names = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    conn.close()
    assert "users" in names
    assert "categories" in names
    assert "transactions" in names


def test_init_database_seeds_categories(db_path):
    init_database(db_path)
    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    conn.close()
    assert count == _expected_category_rows()
