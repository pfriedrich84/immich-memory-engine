from __future__ import annotations

from collections import Counter
from datetime import timedelta
from typing import Any, Dict, List

from .geoutil import center, haversine_m
from .models import Asset, EventCluster


def is_home_asset(asset: Asset, home_config: Dict[str, Any]) -> bool:
    if not home_config.get("enabled") or asset.latitude is None or asset.longitude is None:
        return False
    distance = haversine_m(asset.latitude, asset.longitude, home_config["lat"], home_config["lon"])
    return distance <= home_config.get("radius_meters", 500)


def cluster_assets(assets: List[Asset], config: Dict[str, Any]) -> List[EventCluster]:
    """Initial simple clustering stub.

    Agents should extend this for full time + GPS + home rules.
    """
    if not assets:
        return []

    clustering = config.get("clustering", {})
    home = config.get("home_location", {})
    time_gap = timedelta(hours=clustering.get("time_gap_hours", 6))

    sorted_assets = sorted(assets, key=lambda a: a.taken_at)
    raw_clusters: List[List[Asset]] = []
    current = [sorted_assets[0]]

    for asset in sorted_assets[1:]:
        previous = current[-1]
        if asset.taken_at - previous.taken_at <= time_gap:
            current.append(asset)
        else:
            raw_clusters.append(current)
            current = [asset]
    raw_clusters.append(current)

    clusters: List[EventCluster] = []
    for i, group in enumerate(raw_clusters):
        gps_points = [(a.latitude, a.longitude) for a in group if a.latitude is not None and a.longitude is not None]
        center_lat, center_lon = center(gps_points)
        participants = dict(Counter(a.owner for a in group))
        home_count = sum(1 for a in group if is_home_asset(a, home))
        clusters.append(
            EventCluster(
                id=f"cluster_{i:04d}",
                assets=group,
                start=group[0].taken_at,
                end=group[-1].taken_at,
                center_lat=center_lat,
                center_lon=center_lon,
                participants=participants,
                is_home=home_count > len(group) / 2,
            )
        )
    return clusters
