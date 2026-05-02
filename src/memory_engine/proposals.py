from __future__ import annotations

from typing import List
from .models import AlbumProposal, EventCluster


def proposal_from_cluster(cluster: EventCluster, prefix: str = "") -> AlbumProposal:
    title = f"{prefix}Event {cluster.start.date()}"
    reasons = [
        f"{len(cluster.assets)} assets",
        f"time range {cluster.start.isoformat()} to {cluster.end.isoformat()}",
    ]
    if len(cluster.participants) > 1:
        reasons.append("multiple Immich users contributed photos")
    if cluster.center_lat is not None and cluster.center_lon is not None:
        reasons.append("GPS location available")

    confidence = min(0.95, 0.35 + len(cluster.assets) / 100 + (0.15 if len(cluster.participants) > 1 else 0))
    return AlbumProposal(
        id=f"proposal_{cluster.id}_{cluster.start.date()}",
        title=title,
        description="",
        asset_ids=[a.id for a in cluster.assets],
        confidence=round(confidence, 2),
        reasons=reasons,
        participants=cluster.participants,
        cluster_id=cluster.id,
    )


def proposals_from_clusters(clusters: List[EventCluster], album_prefix: str) -> List[AlbumProposal]:
    return [proposal_from_cluster(c, prefix=album_prefix) for c in clusters]
