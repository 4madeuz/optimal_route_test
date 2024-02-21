import pandas as pd
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, Header, HTTPException, File, UploadFile, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.postgres import get_session
from src.services.routes import RouteSolver, get_route_service

router = APIRouter()


@router.post("/routes", response_model=dict)
async def create_route(file: UploadFile = File(...),
                       db: AsyncSession = Depends(get_session),
                       solver: RouteSolver = Depends(get_route_service)):
    try:
        df = pd.read_csv(file.file)
        points = [{'lat': row['lat'], 'lng': row['lng']} for _, row in df.iterrows()]

        solver.points = points
        solver.db_session = db
        route = await solver.solve()

        return {"id": 1, "points": route}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))