from fastapi import APIRouter, Body
from typing import Any, Optional
from src.redis_client import redis_client

router = APIRouter(tags=["Redis Hash Operations"])

@router.post("/set")
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

@router.get("/get")
async def get_hash_field(
    name: str,
    key: str
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