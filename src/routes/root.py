from fastapi import APIRouter
from src.config import settings
from src.redis_client import redis_client

router = APIRouter(tags=["Root"])

@router.get("/")
async def read_root():
    """根路由，返回应用信息"""
    return {
        "name": settings.app.name,
        "version": settings.app.version,
        "description": "FastAPI with advanced Redis integration",
        "redis_connected": await redis_client.async_ping()
    }