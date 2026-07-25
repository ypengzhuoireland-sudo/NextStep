from datetime import datetime, timezone
from types import SimpleNamespace
from unittest import TestCase

from app.services.practice_service import build_dashboard_series_from_records


class PracticeDashboardSeriesTests(TestCase):
    def test_daily_series_uses_submissions_mastery_events_and_hints(self) -> None:
        first_day = datetime(2026, 7, 21, 9, tzinfo=timezone.utc)
        second_day = datetime(2026, 7, 22, 10, tzinfo=timezone.utc)
        profile = SimpleNamespace(
            items=[
                SimpleNamespace(code="KC001", mastery=0.7),
                SimpleNamespace(code="KC002", mastery=0.4),
            ]
        )
        submissions = [
            SimpleNamespace(created_at=first_day),
            SimpleNamespace(created_at=first_day),
            SimpleNamespace(created_at=second_day),
        ]
        mastery_events = [
            SimpleNamespace(created_at=first_day, kc_id="KC001", new_mastery=0.3),
            SimpleNamespace(created_at=second_day, kc_id="KC002", new_mastery=0.4),
        ]
        hint_events = [SimpleNamespace(created_at=second_day)]

        series = build_dashboard_series_from_records(
            profile,
            submissions,
            mastery_events,
            hint_events,
        )

        self.assertEqual([item.label for item in series], ["Jul 21", "Jul 22"])
        self.assertEqual([item.attempts for item in series], [2, 1])
        self.assertEqual([item.hints for item in series], [0, 1])
        self.assertEqual([item.masteryAverage for item in series], [0.15, 0.35])
