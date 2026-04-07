from fastapi import APIRouter

from app.routers.transform_router import transform_router
from app.routers.zone_router import zone_router

api_router = APIRouter()

# ==================== REGISTRAR RUTAS HIJAS ====================


api_router.include_router(transform_router)

api_router.include_router(zone_router)