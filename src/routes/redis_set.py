from fastapi import APIRouter, Body, Query
from typing import Any, List
from src.redis_client import redis_client

router = APIRouter(tags=["Redis Set Operations"])

@router.post("/add")
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

@router.get("/members")
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