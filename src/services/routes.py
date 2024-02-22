import folium
import numpy as np
import pandas as pd
from fastapi import Depends
from sqlalchemy import and_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.db.postgres import get_session
from src.models.routes import Point, Route


class RouteSolver:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _read_csv(self, file):
        df = pd.read_csv(file.file)
        points = [{'lat': row['lat'], 'lng': row['lng']} for _, row in df.iterrows()]
        return points

    def _calculate_distance(self, point1, point2):
        return np.linalg.norm([point1['lat'] - point2['lat'], point1['lng'] - point2['lng']])

    async def _create_route(self, route):
        db_route = Route()
        # Связываем существующие точки с созданным маршрутом
        existing_points_chunk = await self.db.execute(
            select(Point).where(
                and_(
                    Point.lat.in_([point["lat"] for point in route]),
                    Point.lng.in_([point["lng"] for point in route])
                )
            )
        )
        existing_points = existing_points_chunk.scalars().all()

        new_addresses = [
            Point(lat=point["lat"], lng=point["lng"]) for point in route
            if (point["lat"], point["lng"]) not in [(existing.lat, existing.lng) for existing in existing_points]
        ]
        db_route.points.extend(existing_points + new_addresses)
        self.db.add(db_route)
        await self.db.commit()
        return db_route

    def _nearest_neighbor(self, points):
        unvisited = set(range(1, len(points)))
        current_point = 0
        order = [current_point]

        while unvisited:
            nearest_point = min(unvisited, key=lambda x: self._calculate_distance(points[current_point], points[x]))
            current_point = nearest_point
            unvisited.remove(current_point)
            order.append(current_point)

        return order

    def visualize_route(self, route):
        m = folium.Map(location=[route[0]['lat'], route[0]['lng']], zoom_start=10)
        for point in route:
            folium.Marker(location=[point['lat'], point['lng']]).add_to(m)
        folium.PolyLine(locations=[[point['lat'], point['lng']] for point in route], color='blue').add_to(m)
        return m

    async def build_optimal_route(self, file):
        points = await self._read_csv(file)
        optimal_order = self._nearest_neighbor(points)
        optimal_points = [points[i] for i in optimal_order]
        optimal_route = await self._create_route(optimal_points)
        map_object = self.visualize_route(optimal_points)
        map_object.save('optimal_route_map.html')
        return optimal_route

    async def get_route_by_id(self, route_id):
        route = await self.db.get(Route, route_id, options=[joinedload(Route.points)])
        print(route)
        return route


async def get_route_service(db: AsyncSession = Depends(get_session)):
    return RouteSolver(db)
