import pandas as pd
from fastapi import Depends
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.postgres import get_session


class RouteSolver:
    def __init__(self, points,  db: AsyncSession):
        self.points = points
        self.db = db

    def _create_data_model(self):
        data = {}
        data['distance_matrix'] = self._calculate_distance_matrix()
        data['num_vehicles'] = 1
        data['depot'] = 0
        return data

    def _calculate_distance_matrix(self):
        num_points = len(self.points)
        distance_matrix = [[0] * num_points for _ in range(num_points)]
        for i in range(num_points):
            for j in range(num_points):
                lat1, lng1 = self.points[i]['lat'], self.points[i]['lng']
                lat2, lng2 = self.points[j]['lat'], self.points[j]['lng']
                distance_matrix[i][j] = self._calculate_distance(lat1, lng1, lat2, lng2)
        return distance_matrix

    @staticmethod
    def _calculate_distance(lat1, lng1, lat2, lng2):
        return ((lat1 - lat2)**2 + (lng1 - lng2)**2)**0.5

    def _save_route_to_db(self, route):
        for i, point in enumerate(route):
            db_route = Route(id=1, point_order=i, lat=point['lat'], lng=point['lng'])
            self.db.add(db_route)
        self.db.commit()

    def solve(self):
        data = self._create_data_model()

        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.time_limit.seconds = 1

        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            route = self._get_route(manager, routing, solution)
            self._save_route_to_db(route)
            return route
        else:
            raise Exception("No solution found")

    @staticmethod
    def _get_route(manager, routing, solution):
        index = routing.Start(0)
        route = [{'lat': manager.IndexToNode(index), 'lng': manager.IndexToNode(index)}]
        while not routing.IsEnd(index):
            index = solution.Value(routing.NextVar(index))
            route.append({'lat': manager.IndexToNode(index), 'lng': manager.IndexToNode(index)})
        return route


async def get_route_service(points, db: AsyncSession = Depends(get_session)):
    return RouteSolver(points, db)
