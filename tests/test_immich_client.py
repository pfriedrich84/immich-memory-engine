from datetime import datetime, timezone

import httpx

from memory_engine.immich_client import ImmichClient, normalize_asset


def test_normalize_asset_maps_fields_and_preserves_zero_gps():
    asset = normalize_asset(
        {
            "id": "asset-1",
            "localDateTime": "2025-01-02T03:04:05Z",
            "originalFileName": "photo.jpg",
            "latitude": 0.0,
            "longitude": 0.0,
            "exifInfo": {"latitude": 48.1, "longitude": 16.2, "city": "Vienna", "country": "Austria"},
            "isFavorite": True,
            "type": "VIDEO",
        },
        "paul",
    )

    assert asset.id == "asset-1"
    assert asset.owner == "paul"
    assert asset.filename == "photo.jpg"
    assert asset.taken_at == datetime(2025, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    assert asset.latitude == 0.0
    assert asset.longitude == 0.0
    assert asset.city == "Vienna"
    assert asset.country == "Austria"
    assert asset.is_favorite is True
    assert asset.type == "VIDEO"


def test_normalize_asset_handles_missing_gps_and_asset_type():
    asset = normalize_asset(
        {
            "id": "asset-2",
            "fileCreatedAt": "2025-01-02T03:04:05",
            "assetType": "IMAGE",
        },
        "wife",
    )

    assert asset.latitude is None
    assert asset.longitude is None
    assert asset.type == "IMAGE"


def test_fetch_assets_paginates_and_filters_date_range():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        body = request.read().decode()
        if '"page":1' in body or '"page": 1' in body:
            return httpx.Response(
                200,
                json={
                    "assets": {
                        "items": [
                            {"id": "old", "localDateTime": "2024-12-31T23:00:00Z"},
                            {"id": "one", "localDateTime": "2025-01-01T12:00:00Z"},
                        ],
                        "nextPage": 2,
                    }
                },
            )
        return httpx.Response(
            200,
            json={
                "assets": {
                    "items": [
                        {"id": "two", "localDateTime": "2025-01-02T12:00:00Z"},
                        {"id": "late", "localDateTime": "2025-01-03T00:00:01Z"},
                    ]
                }
            },
        )

    client = httpx.Client(base_url="http://immich.test", transport=httpx.MockTransport(handler))
    assets = ImmichClient("http://immich.test", "secret", "paul", client=client, page_size=2).fetch_assets(
        "2025-01-01", "2025-01-02"
    )

    assert [asset.id for asset in assets] == ["one", "two"]
    assert all(asset.owner == "paul" for asset in assets)
    assert len(requests) == 2
    assert requests[0].headers["host"] == "immich.test"
