from fastapi import APIRouter, Body
from typing import Any, Optional, List
from src.redis_client import redis_client

router = APIRouter(tags=["Redis String Operations"])

@router.post("/set")
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

@router.get("/get")
async def get_string_key(key: str):
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

@router.delete("/delete")
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