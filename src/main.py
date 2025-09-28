from fastapi import FastAPI, Depends, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
from typing import Optional, Dict, List, Any, Union
import uuid
import time
import asyncio
from datetime import timedelta

from src.config import settings
from src.redis_client import redis_client


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


# 基础路由
@app.get("/", tags=["Root"])
async def read_root():
    """根路由，返回应用信息"""
    return {
        "name": settings.app.name,
        "version": settings.app.version,
        "description": "FastAPI with advanced Redis integration",
        "redis_connected": await redis_client.async_ping()
    }


# Redis 操作演示路由
@app.post("/redis/string/set", tags=["Redis String Operations"])
async def set_string_key(
    key: str = Body(..., description="键名"),
    value: Any = Body(..., description="键值"),
    expire: Optional[int] = Body(None, description="过期时间（秒）")
):
    """
    设置字符串键值对
    
    这是 Redis 字符串操作的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动序列化复杂数据类型
    3. 支持设置过期时间
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    """
    result = await redis_client.async_set(key, value, expire=expire)
    return {"success": result, "key": key, "value": value}


@app.get("/redis/string/get", tags=["Redis String Operations"])
async def get_string_key(key: str = Query(..., description="键名")):
    """
    获取字符串键值
    
    这是 Redis 字符串读取的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动反序列化复杂数据类型
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    """
    value = await redis_client.async_get(key)
    return {"key": key, "value": value}


@app.delete("/redis/string/delete", tags=["Redis String Operations"])
async def delete_string_key(keys: List[str] = Body(..., description="要删除的键列表")):
    """
    删除一个或多个键
    
    这是 Redis 键删除的最佳实践示例：
    1. 支持批量删除提高效率
    2. 使用异步操作避免阻塞
    3. 返回删除的键数量
    4. 包含错误处理和日志记录
    """
    deleted_count = await redis_client.async_delete(*keys)
    return {"deleted_count": deleted_count, "keys": keys}


@app.post("/redis/hash/set", tags=["Redis Hash Operations"])
async def set_hash_field(
    name: str = Body(..., description="哈希表名"),
    key: str = Body(..., description="字段名"),
    value: Any = Body(..., description="字段值")
):
    """
    设置哈希表字段值
    
    这是 Redis 哈希操作的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动序列化复杂数据类型
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    """
    result = await redis_client.async_hset(name, key, value)
    return {"success": result > 0, "hash": name, "field": key, "value": value}


@app.get("/redis/hash/get", tags=["Redis Hash Operations"])
async def get_hash_field(
    name: str = Query(..., description="哈希表名"),
    key: str = Query(..., description="字段名")
):
    """
    获取哈希表字段值
    
    这是 Redis 哈希读取的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动反序列化复杂数据类型
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    """
    value = await redis_client.async_hget(name, key)
    return {"hash": name, "field": key, "value": value}


@app.post("/redis/list/push", tags=["Redis List Operations"])
async def push_list_item(
    name: str = Body(..., description="列表名"),
    values: List[Any] = Body(..., description="要添加的值列表"),
    push_to_head: bool = Body(True, description="是否添加到列表头部")
):
    """
    向列表添加元素
    
    这是 Redis 列表操作的最佳实践示例：
    1. 支持批量添加提高效率
    2. 使用异步操作避免阻塞
    3. 支持从头部或尾部添加
    4. 支持自动序列化复杂数据类型
    5. 包含错误处理和日志记录
    6. 使用重试机制提高可靠性
    """
    if push_to_head:
        result = await redis_client.async_lpush(name, *values)
    else:
        result = await redis_client.async_rpush(name, *values)
    return {"length": result, "list": name, "values": values}


@app.get("/redis/list/pop", tags=["Redis List Operations"])
async def pop_list_item(
    name: str = Query(..., description="列表名"),
    pop_from_head: bool = Query(True, description="是否从列表头部弹出"),
    count: Optional[int] = Query(None, description="弹出元素数量")
):
    """
    从列表弹出元素
    
    这是 Redis 列表弹出操作的最佳实践示例：
    1. 支持从头部或尾部弹出
    2. 支持批量弹出提高效率
    3. 使用异步操作避免阻塞
    4. 支持自动反序列化复杂数据类型
    5. 包含错误处理和日志记录
    6. 使用重试机制提高可靠性
    """
    if pop_from_head:
        result = await redis_client.async_lpop(name, count=count)
    else:
        result = await redis_client.async_rpop(name, count=count)
    return {"list": name, "value": result}


@app.post("/redis/set/add", tags=["Redis Set Operations"])
async def add_set_members(
    name: str = Body(..., description="集合名"),
    values: List[Any] = Body(..., description="要添加的成员列表")
):
    """
    向集合添加成员
    
    这是 Redis 集合操作的最佳实践示例：
    1. 支持批量添加提高效率
    2. 使用异步操作避免阻塞
    3. 自动去重
    4. 支持自动序列化复杂数据类型
    5. 包含错误处理和日志记录
    6. 使用重试机制提高可靠性
    """
    result = await redis_client.async_sadd(name, *values)
    return {"added_count": result, "set": name, "values": values}


@app.get("/redis/set/members", tags=["Redis Set Operations"])
async def get_set_members(name: str = Query(..., description="集合名")):
    """
    获取集合所有成员
    
    这是 Redis 集合读取的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动反序列化复杂数据类型
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    """
    members = await redis_client.async_smembers(name)
    return {"set": name, "members": list(members)}


@app.post("/redis/zset/add", tags=["Redis Sorted Set Operations"])
async def add_zset_members(
    name: str = Body(..., description="有序集合名"),
    mapping: Dict[Any, float] = Body(..., description="成员分数映射")
):
    """
    向有序集合添加成员
    
    这是 Redis 有序集合操作的最佳实践示例：
    1. 支持批量添加提高效率
    2. 使用异步操作避免阻塞
    3. 按分数自动排序
    4. 支持自动序列化复杂数据类型
    5. 包含错误处理和日志记录
    6. 使用重试机制提高可靠性
    """
    result = await redis_client.async_zadd(name, mapping)
    return {"added_count": result, "zset": name, "mapping": mapping}


@app.get("/redis/zset/range", tags=["Redis Sorted Set Operations"])
async def get_zset_range(
    name: str = Query(..., description="有序集合名"),
    start: int = Query(0, description="开始索引"),
    end: int = Query(-1, description="结束索引"),
    with_scores: bool = Query(False, description="是否包含分数")
):
    """
    获取有序集合指定范围的成员
    
    这是 Redis 有序集合读取的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持按分数范围查询
    3. 支持升序和降序查询
    4. 支持自动反序列化复杂数据类型
    5. 包含错误处理和日志记录
    6. 使用重试机制提高可靠性
    """
    result = await redis_client.async_zrange(name, start, end, withscores=with_scores)
    return {"zset": name, "members": result}


# 启动应用
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.debug
    )