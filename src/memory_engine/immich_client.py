from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional
import httpx

from .models import Asset


class ImmichClient:
    def __init__(self, base_url: str, api_key: str, owner: str):
        self.owner = owner
        self.client = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={"x-api-key": api_key},
            timeout=60,
        )

    def fetch_assets(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> List[Asset]:
        """Fetch assets from Immich.

        Placeholder implementation target for Milestone 1.
        Agents should replace this with the correct Immich search/pagination API.
        """
        raise NotImplementedError("Implement Immich API pagination in Milestone 1")


def normalize_asset(raw: Dict[str, Any], owner: str) -> Asset:
    taken = raw.get("localDateTime") or raw.get("fileCreatedAt") or raw.get("createdAt")
    if isinstance(taken, str):
        taken_at = datetime.fromisoformat(taken.replace("Z", "+00:00"))
    elif isinstance(taken, datetime):
        taken_at = taken
    else:
        raise ValueError(f"Asset {raw.get('id')} has no usable timestamp")

    exif = raw.get("exifInfo") or {}
    latitude = raw.get("latitude") or exif.get("latitude")
    longitude = raw.get("longitude") or exif.get("longitude")

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
        type=raw.get("type", "IMAGE"),
    )
