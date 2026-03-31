from fastapi import APIRouter

from app.routers.transform_router import transform_router

api_router = APIRouter()

# ==================== REGISTRAR RUTAS HIJAS ====================


api_router.include_router(transform_router)