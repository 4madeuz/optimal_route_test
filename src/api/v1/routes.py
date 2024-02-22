import pandas as pd
from fastapi import (APIRouter, Depends, File, Header, HTTPException, Request,
                     UploadFile, status)
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_session
from src.schemas.routes import RouteInDB
from src.services.routes import RouteSolver, get_route_service

router = APIRouter()


@router.post("/routes", response_model=RouteInDB, status_code=status.HTTP_201_CREATED)
async def create_route(file: UploadFile = File(...),
                       service: RouteSolver = Depends(get_route_service)):
    route = await service.build_optimal_route(file)
    return route


@router.get(
    '/routes/{route_id}', response_model=RouteInDB, status_code=status.HTTP_200_OK,
)
async def update_role(route_id: int, service: RouteSolver = Depends(get_route_service)):
    route = await service.get_route_by_id(route_id)
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Route with id {route_id} not found')
    return route
