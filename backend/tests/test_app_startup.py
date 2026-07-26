from app import main


def test_startup_schedules_database_initialization_by_default(monkeypatch):
    calls: list[str] = []
    started: list[tuple[str, bool]] = []

    class FakeThread:
        def __init__(self, target, daemon):
            self.target = target
            self.daemon = daemon

        def start(self):
            started.append((self.target.__name__, self.daemon))

    monkeypatch.delenv("SKIP_DB_INIT_ON_STARTUP", raising=False)
    monkeypatch.setattr(main, "init_db", lambda: calls.append("init"))
    monkeypatch.setattr(main, "Thread", FakeThread, raising=False)

    main.initialize_database_on_startup()

    assert calls == []
    assert started == [("run_database_initialization", True)]


def test_startup_database_initialization_can_be_skipped(monkeypatch):
    calls: list[str] = []
    started: list[tuple[str, bool]] = []

    class FakeThread:
        def __init__(self, target, daemon):
            self.target = target
            self.daemon = daemon

        def start(self):
            started.append((self.target.__name__, self.daemon))

    monkeypatch.setenv("SKIP_DB_INIT_ON_STARTUP", "true")
    monkeypatch.setattr(main, "init_db", lambda: calls.append("init"))
    monkeypatch.setattr(main, "Thread", FakeThread, raising=False)

    main.initialize_database_on_startup()

    assert calls == []
    assert started == []


def test_database_initialization_uses_advisory_lock(monkeypatch):
    calls: list[str] = []
    statements: list[str] = []

    class FakeConnection:
        def execute(self, statement, params=None):
            statements.append(str(statement))

    class FakeBeginContext:
        def __enter__(self):
            return FakeConnection()

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeEngine:
        def begin(self):
            return FakeBeginContext()

    monkeypatch.setattr(main, "engine", FakeEngine(), raising=False)
    monkeypatch.setattr(main, "init_db", lambda: calls.append("init"))

    main.run_database_initialization()

    assert calls == ["init"]
    assert any("pg_advisory_xact_lock" in statement for statement in statements)


def test_database_initialization_errors_do_not_escape(monkeypatch):
    class FakeBeginContext:
        def __enter__(self):
            raise RuntimeError("connection unavailable")

        def __exit__(self, exc_type, exc, tb):
            return False

    class FakeEngine:
        def begin(self):
            return FakeBeginContext()

    monkeypatch.setattr(main, "engine", FakeEngine(), raising=False)

    main.run_database_initialization()
