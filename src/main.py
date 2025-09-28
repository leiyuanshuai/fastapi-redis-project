from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from loguru import logger

from src.config import settings
from src.redis_client import redis_client
from src.routes.root import router as root_router
from src.routes.redis_string import router as redis_string_router
from src.routes.redis_hash import router as redis_hash_router
from src.routes.redis_list import router as redis_list_router
from src.routes.redis_set import router as redis_set_router
from src.routes.redis_zset import router as redis_zset_router


# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭时执行的操作"""
    logger.info(f"Starting {settings.app.name} v{settings.app.version}")

    # 启动时测试Redis连接
    if not await redis_client.async_ping():
        logger.warning("Could not connect to Redis during startup")
    else:
        logger.info("Successfully connected to Redis")

    yield  # 应用运行期间

    # 关闭时清理资源
    logger.info(f"Shutting down {settings.app.name}")
    await redis_client.async_close()
    logger.info("Resources cleaned up")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description="A production-ready FastAPI application with advanced Redis integration",
    lifespan=lifespan
)


# 依赖项：检查Redis连接状态
async def check_redis_connection():
    """检查Redis连接状态的依赖项"""
    if not await redis_client.async_ping():
        raise HTTPException(status_code=503, detail="Redis service is unavailable")
    return True


# 注册路由
app.include_router(root_router)
app.include_router(redis_string_router, prefix="/redis/string")
app.include_router(redis_hash_router, prefix="/redis/hash")
app.include_router(redis_list_router, prefix="/redis/list")
app.include_router(redis_set_router, prefix="/redis/set")
app.include_router(redis_zset_router, prefix="/redis/zset")


# 启动应用
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug
    )