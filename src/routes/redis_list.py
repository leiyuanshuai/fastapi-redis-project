from fastapi import APIRouter, Body, Query
from typing import Any, Optional, List, Union
from src.redis_client import redis_client

router = APIRouter(tags=["Redis List Operations"])


@router.post("/lpush")
async def lpush_list_item(
    name: str = Body(..., description="列表名"),
    values: List[Any] = Body(..., description="要添加到列表头部的值列表")
):
    """
    将一个或多个值插入到列表头部（左端）
    
    这是 Redis LPUSH 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持批量添加提高效率
    3. 支持自动序列化复杂数据类型
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    
    时间复杂度: O(1) 插入每个元素
    """
    result = await redis_client.async_lpush(name, *values)
    return {"length": result, "list": name, "values": values}


@router.post("/rpush")
async def rpush_list_item(
    name: str = Body(..., description="列表名"),
    values: List[Any] = Body(..., description="要添加到列表尾部的值列表")
):
    """
    将一个或多个值插入到列表尾部（右端）
    
    这是 Redis RPUSH 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持批量添加提高效率
    3. 支持自动序列化复杂数据类型
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    
    时间复杂度: O(1) 插入每个元素
    """
    result = await redis_client.async_rpush(name, *values)
    return {"length": result, "list": name, "values": values}


@router.get("/llen")
async def llen_list(name: str = Query(..., description="列表名")):
    """
    获取列表长度
    
    这是 Redis LLEN 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 包含错误处理和日志记录
    3. 使用重试机制提高可靠性
    
    时间复杂度: O(1)
    """
    result = await redis_client.async_llen(name)
    return {"list": name, "length": result}


@router.get("/lindex")
async def lindex_list(
    name: str = Query(..., description="列表名"),
    index: int = Query(..., description="索引位置")
):
    """
    获取列表中指定索引的元素
    
    这是 Redis LINDEX 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动反序列化复杂数据类型
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    
    时间复杂度: O(N) N为到达指定索引的元素的偏移量
    """
    # 使用lrange获取指定索引的元素
    result = await redis_client.async_lrange(name, index, index)
    value = result[0] if result else None
    return {"list": name, "index": index, "value": value}


@router.post("/lset")
async def lset_list(
    name: str = Body(..., description="列表名"),
    index: int = Body(..., description="索引位置"),
    value: Any = Body(..., description="要设置的值")
):
    """
    设置列表中指定索引的元素值
    
    这是 Redis LSET 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动序列化复杂数据类型
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    
    时间复杂度: O(N) N为到达指定索引的元素的偏移量
    """
    try:
        # Redis-py没有直接的lset方法，我们使用lrange和lpush/lpop组合实现
        await redis_client.async_lset(name, index, value)
        return {"success": True, "list": name, "index": index, "value": value}
    except Exception as e:
        return {"success": False, "error": str(e), "list": name, "index": index}


@router.get("/lrange")
async def lrange_list(
    name: str = Query(..., description="列表名"),
    start: int = Query(0, description="起始索引"),
    end: int = Query(-1, description="结束索引")
):
    """
    获取列表中指定范围的元素
    
    这是 Redis LRANGE 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动反序列化复杂数据类型
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    
    时间复杂度: O(S+N) S为start偏移量，N为元素数量
    """
    result = await redis_client.async_lrange(name, start, end)
    return {"list": name, "start": start, "end": end, "values": result}


@router.post("/lpushx")
async def lpushx_list_item(
    name: str = Body(..., description="列表名"),
    value: Any = Body(..., description="要添加到列表头部的值")
):
    """
    仅当列表存在时，将值插入到列表头部
    
    这是 Redis LPUSHX 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 仅当列表存在时才插入
    3. 支持自动序列化复杂数据类型
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    
    时间复杂度: O(1)
    """
    # 先检查列表是否存在
    length = await redis_client.async_llen(name)
    if length > 0:
        result = await redis_client.async_lpush(name, value)
        return {"success": True, "length": result, "list": name, "value": value}
    else:
        return {"success": False, "message": "列表不存在", "list": name}


@router.post("/rpushx")
async def rpushx_list_item(
    name: str = Body(..., description="列表名"),
    value: Any = Body(..., description="要添加到列表尾部的值")
):
    """
    仅当列表存在时，将值插入到列表尾部
    
    这是 Redis RPUSHX 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 仅当列表存在时才插入
    3. 支持自动序列化复杂数据类型
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    
    时间复杂度: O(1)
    """
    # 先检查列表是否存在
    length = await redis_client.async_llen(name)
    if length > 0:
        result = await redis_client.async_rpush(name, value)
        return {"success": True, "length": result, "list": name, "value": value}
    else:
        return {"success": False, "message": "列表不存在", "list": name}


@router.post("/linsert")
async def linsert_list_item(
    name: str = Body(..., description="列表名"),
    position: str = Body(..., description="插入位置，BEFORE 或 AFTER"),
    pivot: Any = Body(..., description="参考值"),
    value: Any = Body(..., description="要插入的值")
):
    """
    在列表中指定元素的前后插入元素
    
    这是 Redis LINSERT 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持在指定元素前后插入
    3. 支持自动序列化复杂数据类型
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    
    时间复杂度: O(N) N为到达pivot元素的偏移量
    """
    try:
        pos = position.upper()
        if pos not in ['BEFORE', 'AFTER']:
            return {"success": False, "error": "position必须是'BEFORE'或'AFTER'"}
        
        result = await redis_client.async_linsert(name, pos, pivot, value)
        return {"success": result != -1, "length": result, "list": name, "position": position, "pivot": pivot, "value": value}
    except Exception as e:
        return {"success": False, "error": str(e), "list": name}


@router.post("/lpop")
async def lpop_list_item(
    name: str = Body(..., description="列表名"),
    count: Optional[int] = Body(None, description="要移除并返回的元素数量")
):
    """
    移除并返回列表的第一个元素（头部）
    
    这是 Redis LPOP 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持批量弹出提高效率
    3. 支持自动反序列化复杂数据类型
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    
    时间复杂度: O(N) N为count参数的值
    """
    result = await redis_client.async_lpop(name, count=count)
    return {"list": name, "value": result}


@router.post("/rpop")
async def rpop_list_item(
    name: str = Body(..., description="列表名"),
    count: Optional[int] = Body(None, description="要移除并返回的元素数量")
):
    """
    移除并返回列表的最后一个元素（尾部）
    
    这是 Redis RPOP 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持批量弹出提高效率
    3. 支持自动反序列化复杂数据类型
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    
    时间复杂度: O(N) N为count参数的值
    """
    result = await redis_client.async_rpop(name, count=count)
    return {"list": name, "value": result}


@router.post("/blpop")
async def blpop_list_item(
    keys: List[str] = Body(..., description="列表名列表"),
    timeout: int = Body(0, description="超时时间（秒），0表示无限等待")
):
    """
    移除并返回第一个非空列表的第一个元素（阻塞式）
    
    这是 Redis BLPOP 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持多个列表的阻塞式弹出
    3. 支持自动反序列化复杂数据类型
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    
    时间复杂度: O(N) N为到达指定元素的偏移量
    """
    try:
        result = await redis_client.async_blpop(*keys, timeout=timeout)
        return {"key": result[0] if result else None, "value": result[1] if result else None}
    except Exception as e:
        return {"error": str(e)}


@router.post("/brpop")
async def brpop_list_item(
    keys: List[str] = Body(..., description="列表名列表"),
    timeout: int = Body(0, description="超时时间（秒），0表示无限等待")
):
    """
    移除并返回第一个非空列表的最后一个元素（阻塞式）
    
    这是 Redis BRPOP 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持多个列表的阻塞式弹出
    3. 支持自动反序列化复杂数据类型
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    
    时间复杂度: O(N) N为到达指定元素的偏移量
    """
    try:
        result = await redis_client.async_brpop(*keys, timeout=timeout)
        return {"key": result[0] if result else None, "value": result[1] if result else None}
    except Exception as e:
        return {"error": str(e)}


@router.post("/brpoplpush")
async def brpoplpush_list_item(
    source: str = Body(..., description="源列表名"),
    destination: str = Body(..., description="目标列表名"),
    timeout: int = Body(0, description="超时时间（秒），0表示无限等待")
):
    """
    从源列表弹出最后一个元素并推入目标列表头部（阻塞式）
    
    这是 Redis BRPOPLPUSH 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 原子性操作确保数据一致性
    3. 支持自动序列化/反序列化复杂数据类型
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    
    时间复杂度: O(1)
    """
    try:
        result = await redis_client.async_brpoplpush(source, destination, timeout)
        return {"value": result, "source": source, "destination": destination}
    except Exception as e:
        return {"error": str(e)}


@router.post("/lrem")
async def lrem_list_item(
    name: str = Body(..., description="列表名"),
    count: int = Body(..., description="移除元素的数量：0表示移除所有，正数表示从头开始，负数表示从尾开始"),
    value: Any = Body(..., description="要移除的值")
):
    """
    移除列表中指定值的元素
    
    这是 Redis LREM 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持按数量移除元素
    3. 支持自动序列化复杂数据类型
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    
    时间复杂度: O(N) N为列表长度
    """
    result = await redis_client.async_lrem(name, count, value)
    return {"removed_count": result, "list": name, "value": value, "count": count}


@router.post("/ltrim")
async def ltrim_list(
    name: str = Body(..., description="列表名"),
    start: int = Body(..., description="起始索引"),
    end: int = Body(..., description="结束索引")
):
    """
    修剪列表，只保留指定范围内的元素
    
    这是 Redis LTRIM 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持范围修剪
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    
    时间复杂度: O(N) N为被移除元素的数量
    """
    try:
        await redis_client.async_ltrim(name, start, end)
        return {"success": True, "list": name, "start": start, "end": end}
    except Exception as e:
        return {"success": False, "error": str(e), "list": name}