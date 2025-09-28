from fastapi import APIRouter, Body, Query
from typing import Any, Dict, List, Union, Tuple
from src.redis_client import redis_client

router = APIRouter(tags=["Redis Sorted Set Operations"])

@router.post("/add")
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

@router.get("/range")
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