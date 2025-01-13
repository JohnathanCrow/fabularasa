# Common type definitions used throughout the application

from typing import Any, Dict, List, Optional, TypedDict


class BookData(TypedDict):
    title: str
    author: str
    length: int
    rating: float
    member: str
    score: float
    date_added: str
    read_date: Optional[str]


class ConfigData(TypedDict):
    rating: Dict[str, float]
    length: Dict[str, int]
    member_penalties: Dict[str, int]


class ProfileState(TypedDict):
    last_profile: str
