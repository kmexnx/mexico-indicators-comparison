from fastapi import APIRouter

from app.api.api_v1.endpoints import cities, indicators, comparisons, health, education

api_router = APIRouter()

api_router.include_router(cities.router, prefix="/cities", tags=["cities"])
api_router.include_router(indicators.router, prefix="/indicators", tags=["indicators"])
api_router.include_router(comparisons.router, prefix="/comparisons", tags=["comparisons"])
api_router.include_router(health.router, prefix="/health-indicators", tags=["health"])
api_router.include_router(education.router, prefix="/education-indicators", tags=["education"])
