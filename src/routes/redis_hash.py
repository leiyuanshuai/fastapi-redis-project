from fastapi import APIRouter, Body, Query
from typing import Any, Optional, Dict, List, Union
from src.redis_client import redis_client
from pydantic import BaseModel

router = APIRouter(tags=["Redis Hash Operations"])


class SingleFieldRequest(BaseModel):
    name: str
    key: str
    value: Any


class MultipleFieldsRequest(BaseModel):
    name: str
    mapping: Dict[str, Any]


@router.post("/hset")
async def hset_hash_field(request: Union[SingleFieldRequest, MultipleFieldsRequest]):
    """
    设置哈希表字段值
    
    这是 Redis HSET 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动序列化复杂数据类型
    3. 支持单个字段设置或批量字段设置
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    
    注意：Redis 4.0.0+版本中，HSET已完全替代HMSET功能，支持设置单个或多个字段
    
    使用方法：
    1. 设置单个字段：
       {
         "name": "user:1000",
         "key": "name",
         "value": "Alice"
       }
       
    2. 批量设置多个字段：
       {
         "name": "user:1001",
         "mapping": {
           "name": "Bob",
           "age": 30,
           "email": "bob@example.com"
           "mapping": {
             "name": "Bob",
             "age": 30,
             "email": "bob@example.com"
           }
         }
       }
    """
    # 检查请求类型
    if hasattr(request, 'mapping') and request.mapping is not None:
        # 批量设置模式
        result = await redis_client.async_hset(request.name, mapping=request.mapping)
        return {"success": result > 0, "hash": request.name, "mapping": request.mapping}
    elif hasattr(request, 'key') and hasattr(request, 'value'):
        # 单字段设置模式
        result = await redis_client.async_hset(request.name, request.key, request.value)
        return {"success": result > 0, "hash": request.name, "field": request.key, "value": request.value}
    else:
        return {"success": False, "error": "请求参数不正确"}


@router.post("/hsetnx")
async def hsetnx_hash_field(
    name: str = Body(..., description="哈希表名"),
    key: str = Body(..., description="字段名"),
    value: Any = Body(..., description="字段值")
):
    """
    仅当字段不存在时设置哈希表字段值
    
    这是 Redis HSETNX 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动序列化复杂数据类型
    3. 仅当字段不存在时才设置
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    
    应用场景：
    - 分布式锁实现
    - 防止重复操作
    - 唯一性约束检查
    """
    result = await redis_client.async_hsetnx(name, key, value)
    return {"success": result, "hash": name, "field": key, "value": value}


@router.get("/hscan")
async def hscan_hash_fields(
    name: str,
    cursor: int = Query(0, description="游标"),
    match: Optional[str] = Query(None, description="匹配模式"),
    count: Optional[int] = Query(None, description="每次迭代返回的元素数量提示")
):
    """
    增量迭代哈希表中的字段
    
    这是 Redis HSCAN 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动反序列化复杂数据类型
    3. 支持匹配模式过滤
    4. 支持返回元素数量提示
    5. 包含错误处理和日志记录
    6. 使用重试机制提高可靠性
    
    应用场景：
    - 大型哈希表的分页遍历
    - 按模式匹配字段
    - 避免阻塞Redis的全量扫描
    """
    new_cursor, result = await redis_client.async_hscan(name, cursor, match, count)
    return {"hash": name, "cursor": new_cursor, "fields": result}


@router.get("/hget")
async def hget_hash_field(
    name: str,
    key: str
):
    """
    获取哈希表字段值
    
    这是 Redis HGET 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动反序列化复杂数据类型
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    """
    value = await redis_client.async_hget(name, key)
    return {"hash": name, "field": key, "value": value}


@router.post("/hmget")
async def hmget_hash_fields(
    name: str = Body(..., description="哈希表名"),
    keys: List[str] = Body(..., description="字段名列表")
):
    """
    获取哈希表多个字段值
    
    这是 Redis HMGET 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动反序列化复杂数据类型
    3. 批量操作提高效率
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    """
    result = await redis_client.async_hmget(name, keys)
    return {"hash": name, "fields": result}


@router.get("/hgetall")
async def hgetall_hash_fields(name: str):
    """
    获取哈希表所有字段和值
    
    这是 Redis HGETALL 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动反序列化复杂数据类型
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    """
    result = await redis_client.async_hgetall(name)
    return {"hash": name, "fields": result}


@router.delete("/hdel")
async def hdel_hash_fields(
    name: str = Body(..., description="哈希表名"),
    keys: List[str] = Body(..., description="要删除的字段名列表")
):
    """
    删除哈希表一个或多个字段
    
    这是 Redis HDEL 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持批量删除提高效率
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    """
    result = await redis_client.async_hdel(name, *keys)
    return {"deleted_count": result, "hash": name, "fields": keys}


@router.get("/hexists")
async def hexists_hash_field(
    name: str,
    key: str
):
    """
    检查哈希表字段是否存在
    
    这是 Redis HEXISTS 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 包含错误处理和日志记录
    3. 使用重试机制提高可靠性
    """
    result = await redis_client.async_hexists(name, key)
    return {"hash": name, "field": key, "exists": result}


@router.get("/hlen")
async def hlen_hash(name: str):
    """
    获取哈希表字段数量
    
    这是 Redis HLEN 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 包含错误处理和日志记录
    3. 使用重试机制提高可靠性
    """
    result = await redis_client.async_hlen(name)
    return {"hash": name, "length": result}


@router.get("/hkeys")
async def hkeys_hash(name: str):
    """
    获取哈希表所有字段名
    
    这是 Redis HKEYS 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 包含错误处理和日志记录
    3. 使用重试机制提高可靠性
    """
    result = await redis_client.async_hkeys(name)
    return {"hash": name, "keys": result}


@router.get("/hvals")
async def hvals_hash(name: str):
    """
    获取哈希表所有字段值
    
    这是 Redis HVALS 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动反序列化复杂数据类型
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    """
    result = await redis_client.async_hvals(name)
    return {"hash": name, "values": result}


@router.post("/hincrby")
async def hincrby_hash(
    name: str = Body(..., description="哈希表名"),
    key: str = Body(..., description="字段名"),
    increment: int = Body(..., description="增量值")
):
    """
    哈希表字段值增加指定整数
    
    这是 Redis HINCRBY 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 包含错误处理和日志记录
    3. 使用重试机制提高可靠性
    """
    result = await redis_client.async_hincrby(name, key, increment)
    return {"hash": name, "field": key, "value": result, "increment": increment}