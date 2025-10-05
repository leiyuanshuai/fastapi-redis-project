from create_app import create_app
from src.config.env import env
from src.routes.root import router as root_router
from src.routes.redis_string import router as redis_string_router
from src.routes.redis_hash import router as redis_hash_router
from src.routes.redis_list import router as redis_list_router
from src.routes.redis_set import router as redis_set_router
from src.routes.redis_zset import router as redis_zset_router
app = create_app()

# 注册redis 路由
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
        host=env.app_host,
        port=env.app_port,
        reload=env.app_debug
    )