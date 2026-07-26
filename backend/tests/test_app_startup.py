from app import main


def test_startup_initializes_database_by_default(monkeypatch):
    calls: list[str] = []

    monkeypatch.delenv("SKIP_DB_INIT_ON_STARTUP", raising=False)
    monkeypatch.setattr(main, "init_db", lambda: calls.append("init"))

    main.initialize_database_on_startup()

    assert calls == ["init"]


def test_startup_database_initialization_can_be_skipped(monkeypatch):
    calls: list[str] = []

    monkeypatch.setenv("SKIP_DB_INIT_ON_STARTUP", "true")
    monkeypatch.setattr(main, "init_db", lambda: calls.append("init"))

    main.initialize_database_on_startup()

    assert calls == []
