from datetime import datetime, timezone
from memory_engine.clustering import cluster_assets
from memory_engine.models import Asset


def test_empty_assets():
    assert cluster_assets([], {}) == []


def test_participants_count():
    assets = [
        Asset(id="1", owner="paul", taken_at=datetime(2025, 1, 1, tzinfo=timezone.utc)),
        Asset(id="2", owner="wife", taken_at=datetime(2025, 1, 1, 1, tzinfo=timezone.utc)),
    ]
    clusters = cluster_assets(assets, {"clustering": {"time_gap_hours": 6}})
    assert clusters[0].participants == {"paul": 1, "wife": 1}
