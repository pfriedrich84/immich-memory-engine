from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class ImmichUserConfig(BaseModel):
    name: str
    api_key_env: str


class Asset(BaseModel):
    id: str
    owner: str
    filename: Optional[str] = None
    taken_at: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    country: Optional[str] = None
    is_favorite: bool = False
    type: str = "IMAGE"


class EventCluster(BaseModel):
    id: str
    assets: List[Asset]
    start: datetime
    end: datetime
    center_lat: Optional[float] = None
    center_lon: Optional[float] = None
    participants: Dict[str, int] = Field(default_factory=dict)
    is_home: bool = False


class AlbumProposal(BaseModel):
    id: str
    title: str
    description: str = ""
    asset_ids: List[str]
    confidence: float
    reasons: List[str] = Field(default_factory=list)
    participants: Dict[str, int] = Field(default_factory=dict)
    cluster_id: str
