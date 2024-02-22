import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.api.v1 import routes
from src.core.config import settings

app = FastAPI(
    description='Сервис по созданию оптимального маршрута',
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=JSONResponse,
)

app.include_router(routes.router, prefix='/api', tags=['routes'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='127.0.0.1',
        port=8000,
        reload=True
    )
