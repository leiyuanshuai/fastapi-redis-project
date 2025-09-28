from fastapi import APIRouter, Body, Query
from typing import Any, Optional, List
from src.redis_client import redis_client

router = APIRouter(tags=["Redis List Operations"])

@router.post("/push")
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

@router.get("/pop")
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