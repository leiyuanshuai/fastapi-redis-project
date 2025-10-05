from fastapi import APIRouter
from src.config.env import env
from src.redis_client import redis_client

router = APIRouter(tags=["Root"])

@router.get("/")
async def read_root():
    """根路由，返回应用信息"""
    return {
        "name": 'fastapi project',
        "version": env.app_version,
        "description": "FastAPI with advanced Redis integration",
        "redis_connected": await redis_client.async_ping()
    }