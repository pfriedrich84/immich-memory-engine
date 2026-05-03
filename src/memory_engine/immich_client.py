from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
import httpx

from .models import Asset


DEFAULT_PAGE_SIZE = 1000


class ImmichClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        owner: str,
        *,
        client: Optional[httpx.Client] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ):
        self.owner = owner
        self.page_size = page_size
        self.client = client or httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={"x-api-key": api_key},
            timeout=60,
        )

    def fetch_assets(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> List[Asset]:
        """Fetch and normalize assets from Immich's metadata search endpoint.

        Immich has changed response envelopes over time. This method accepts the
        current `assets.items` shape and simpler `items`/list shapes to keep the
        MVP usable across common server versions.
        """
        assets: List[Asset] = []
        page = 1
        endpoint: Optional[str] = None

        while True:
            body: Dict[str, Any] = {
                "page": page,
                "size": self.page_size,
                "withExif": True,
            }
            if date_from:
                body["takenAfter"] = date_from
            if date_to:
                body["takenBefore"] = date_to

            response, endpoint = self._post_search(body, endpoint)
            data = response.json()
            items = _extract_items(data)
            assets.extend(
                asset
                for asset in (normalize_asset(item, self.owner) for item in items)
                if _within_date_range(asset.taken_at, date_from, date_to)
            )

            next_page = _extract_next_page(data)
            if not next_page:
                break
            page = int(next_page)

        return assets

    def _post_search(self, body: Dict[str, Any], endpoint: Optional[str]) -> tuple[httpx.Response, str]:
        endpoints = [endpoint] if endpoint else ["/api/search/metadata", "/search/metadata"]
        last_response: Optional[httpx.Response] = None
        for candidate in endpoints:
            if candidate is None:
                continue
            response = self.client.post(candidate, json=body)
            if response.status_code != 404:
                response.raise_for_status()
                return response, candidate
            last_response = response
        assert last_response is not None
        last_response.raise_for_status()
        raise RuntimeError("unreachable")


def normalize_asset(raw: Dict[str, Any], owner: str) -> Asset:
    taken = raw.get("localDateTime") or raw.get("fileCreatedAt") or raw.get("createdAt")
    if isinstance(taken, str):
        taken_at = datetime.fromisoformat(taken.replace("Z", "+00:00"))
    elif isinstance(taken, datetime):
        taken_at = taken
    else:
        raise ValueError(f"Asset {raw.get('id')} has no usable timestamp")

    exif = raw.get("exifInfo") or {}
    latitude = _first_present(raw, exif, "latitude")
    longitude = _first_present(raw, exif, "longitude")

    return Asset(
        id=raw["id"],
        owner=owner,
        filename=raw.get("originalFileName") or raw.get("originalPath"),
        taken_at=taken_at,
        latitude=latitude,
        longitude=longitude,
        city=exif.get("city"),
        country=exif.get("country"),
        is_favorite=bool(raw.get("isFavorite", False)),
        type=raw.get("type") or raw.get("assetType") or "IMAGE",
    )


def _first_present(primary: Dict[str, Any], secondary: Dict[str, Any], key: str) -> Any:
    if key in primary and primary[key] is not None:
        return primary[key]
    return secondary.get(key)


def _extract_items(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return data
    if not isinstance(data, dict):
        return []
    assets = data.get("assets")
    if isinstance(assets, dict) and isinstance(assets.get("items"), list):
        return assets["items"]
    if isinstance(data.get("items"), list):
        return data["items"]
    return []


def _extract_next_page(data: Any) -> Optional[int]:
    if not isinstance(data, dict):
        return None
    assets = data.get("assets")
    if isinstance(assets, dict) and assets.get("nextPage"):
        return int(assets["nextPage"])
    if data.get("nextPage"):
        return int(data["nextPage"])
    return None


def _within_date_range(taken_at: datetime, date_from: Optional[str], date_to: Optional[str]) -> bool:
    if date_from and taken_at < _compatible_boundary(taken_at, date_from):
        return False
    if date_to and taken_at > _compatible_boundary(taken_at, date_to, end_of_day=True):
        return False
    return True


def _compatible_boundary(taken_at: datetime, value: str, *, end_of_day: bool = False) -> datetime:
    boundary = _parse_boundary(value, end_of_day=end_of_day)
    if taken_at.tzinfo is not None and boundary.tzinfo is None:
        return boundary.replace(tzinfo=taken_at.tzinfo)
    if taken_at.tzinfo is None and boundary.tzinfo is not None:
        return boundary.replace(tzinfo=None)
    return boundary


def _parse_boundary(value: str, *, end_of_day: bool = False) -> datetime:
    if len(value) == 10:
        suffix = "T23:59:59.999999" if end_of_day else "T00:00:00"
        value = f"{value}{suffix}"
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
