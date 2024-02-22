from typing import List

from pydantic import BaseModel


class Point(BaseModel):
    lat: float
    lng: float


class RouteInDB(BaseModel):
    id: int
    points: List[Point]

