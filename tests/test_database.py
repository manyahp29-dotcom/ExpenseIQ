import database

def test_database_crud_and_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test_expenses.db")
    database.init_db()
    expense_id = database.add_expense("2026-01-01", "Food", "Test lunch", 120, "UPI")
    df = database.get_expenses()
    assert len(df) == 1
    assert df.iloc[0]["amount"] == 120

    updated = database.update_expense(expense_id, "2026-01-02", "Food", "Updated lunch", 150, "Cash")
    assert updated is True
    assert database.get_expenses().iloc[0]["amount"] == 150

    database.set_budget("2026-01", 3000)
    assert database.get_budget("2026-01") == 3000

    assert database.delete_expense(expense_id) is True
    assert database.get_expenses().empty

def test_reject_invalid_amount(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test_expenses.db")
    database.init_db()
    try:
        database.add_expense("2026-01-01", "Food", "Invalid", 0, "Cash")
        assert False, "Expected ValueError"
    except ValueError:
        pass
