from fastapi import APIRouter, Body, Query
from typing import Any, Optional, List, Dict
from src.redis_client import redis_client

router = APIRouter(tags=["Redis String Operations"])

@router.post("/set")
async def set_string_key(
    key: str = Body(..., description="键名"),
    value: Any = Body(..., description="键值"),
    expire: Optional[int] = Body(None, description="过期时间（秒）"),
    nx: bool = Body(False, description="仅当键不存在时设置（SET if Not eXists）"),
    xx: bool = Body(False, description="仅当键存在时设置（SET if eXists）"),
    keep_ttl: bool = Body(False, description="保持现有TTL（Keep Time To Live）")
):
    """
    设置字符串键值对
    
    这是 Redis 字符串操作的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动序列化复杂数据类型
    3. 支持设置过期时间
    4. 支持NX/XX选项
    5. 支持KEEP_TTL选项
    6. 包含错误处理和日志记录
    7. 使用重试机制提高可靠性
    """
    result = await redis_client.async_set(key, value, expire=expire, nx=nx, xx=xx, keep_ttl=keep_ttl)
    return {"success": result, "key": key, "value": value, "nx": nx, "xx": xx, "keep_ttl": keep_ttl}

@router.post("/set-multiple")
async def set_multiple_string_keys(
    key_value_pairs: Dict[str, Any] = Body(..., description="键值对映射"),
    expire: Optional[int] = Body(None, description="过期时间（秒）"),
    nx: bool = Body(False, description="仅当键不存在时设置（SET if Not eXists）"),
    xx: bool = Body(False, description="仅当键存在时设置（SET if eXists）")
):
    """
    批量设置多个字符串键值对
    
    这是 Redis 字符串批量操作的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动序列化复杂数据类型
    3. 支持设置过期时间
    4. 支持NX/XX选项
    5. 包含错误处理和日志记录
    6. 使用重试机制提高可靠性
    """
    results = {}
    success_count = 0
    
    for key, value in key_value_pairs.items():
        try:
            result = await redis_client.async_set(key, value, expire=expire, nx=nx, xx=xx)
            results[key] = result
            if result:
                success_count += 1
        except Exception as e:
            results[key] = f"Error: {str(e)}"
    
    return {
        "success_count": success_count,
        "total_count": len(key_value_pairs),
        "results": results
    }

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

@router.post("/get-multiple")
async def get_multiple_string_keys(keys: List[str] = Body(..., description="键名列表")):
    """
    批量获取多个字符串键值
    
    这是 Redis 字符串批量读取的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持自动反序列化复杂数据类型
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    """
    results = {}
    found_count = 0
    
    for key in keys:
        try:
            value = await redis_client.async_get(key)
            results[key] = value
            if value is not None:
                found_count += 1
        except Exception as e:
            results[key] = f"Error: {str(e)}"
    
    return {
        "found_count": found_count,
        "total_count": len(keys),
        "results": results
    }

@router.get("/strlen")
async def get_string_length(key: str = Query(..., description="键名")):
    """
    获取键值的字符串长度
    
    这是 Redis STRLEN 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 如果键不存在，则返回0
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    """
    try:
        length = await redis_client.async_strlen(key)
        return {"key": key, "length": length}
    except Exception as e:
        return {"error": f"Failed to get string length for key {key}: {str(e)}"}

@router.get("/getrange")
async def get_string_range(
    key: str = Query(..., description="键名"),
    start: int = Query(..., description="起始位置（包含）"),
    end: int = Query(..., description="结束位置（包含）")
):
    """
    获取键值字符串指定范围的子串
    
    这是 Redis GETRANGE 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持负数索引（从末尾开始计算）
    3. 如果键不存在，则返回空字符串
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    """
    try:
        substring = await redis_client.async_getrange(key, start, end)
        return {"key": key, "substring": substring, "start": start, "end": end}
    except Exception as e:
        return {"error": f"Failed to get range for key {key}: {str(e)}"}

@router.post("/setrange")
async def set_string_range(
    key: str = Body(..., description="键名"),
    offset: int = Body(..., description="偏移量"),
    value: str = Body(..., description="要设置的值")
):
    """
    从指定偏移量开始覆写键值字符串
    
    这是 Redis SETRANGE 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 如果键不存在，则在执行操作前将其设置为空字符串
    3. 如果偏移量超出字符串长度，则用零字节填充
    4. 包含错误处理和日志记录
    5. 使用重试机制提高可靠性
    """
    try:
        new_length = await redis_client.async_setrange(key, offset, value)
        return {"key": key, "new_length": new_length, "offset": offset, "value": value}
    except Exception as e:
        return {"error": f"Failed to set range for key {key}: {str(e)}"}

@router.get("/exists")
async def exists_string_key(key: str):
    """
    检查字符串键是否存在
    
    这是 Redis 键存在性检查的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持检查单个键的存在性
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    """
    exists = await redis_client.async_exists(key)
    return {"key": key, "exists": exists > 0}

@router.post("/exists-multiple")
async def exists_multiple_string_keys(keys: List[str] = Body(..., description="键名列表")):
    """
    批量检查多个字符串键是否存在
    
    这是 Redis 键存在性批量检查的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持检查多个键的存在性
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    """
    results = {}
    exists_count = 0
    
    for key in keys:
        try:
            exists = await redis_client.async_exists(key)
            exists_result = exists > 0
            results[key] = exists_result
            if exists_result:
                exists_count += 1
        except Exception as e:
            results[key] = f"Error: {str(e)}"
    
    return {
        "exists_count": exists_count,
        "total_count": len(keys),
        "results": results
    }

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

@router.post("/incr")
async def increment_key(
    key: str = Body(..., description="键名"),
    expire: Optional[int] = Body(None, description="过期时间（秒）")
):
    """
    将键的值增1（原子操作）
    
    如果键不存在，则在执行操作前将其设置为0。
    如果键的值不是整数，则返回错误。
    
    这是 Redis INCR 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持设置过期时间
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    """
    try:
        result = await redis_client.async_incr(key)
        
        # 如果指定了过期时间，则设置过期时间
        if expire is not None:
            await redis_client.async_expire(key, expire)
            
        return {"key": key, "value": result}
    except Exception as e:
        return {"error": f"Failed to increment key {key}: {str(e)}"}

@router.post("/decr")
async def decrement_key(
    key: str = Body(..., description="键名"),
    expire: Optional[int] = Body(None, description="过期时间（秒）")
):
    """
    将键的值减1（原子操作）
    
    如果键不存在，则在执行操作前将其设置为0。
    如果键的值不是整数，则返回错误。
    
    这是 Redis DECR 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持设置过期时间
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    """
    try:
        result = await redis_client.async_decr(key)
        
        # 如果指定了过期时间，则设置过期时间
        if expire is not None:
            await redis_client.async_expire(key, expire)
            
        return {"key": key, "value": result}
    except Exception as e:
        return {"error": f"Failed to decrement key {key}: {str(e)}"}

@router.post("/incrby")
async def increment_key_by(
    key: str = Body(..., description="键名"),
    increment: int = Body(..., description="增量值"),
    expire: Optional[int] = Body(None, description="过期时间（秒）")
):
    """
    将键的值增加指定的整数（原子操作）
    
    如果键不存在，则在执行操作前将其设置为0。
    如果键的值不是整数，则返回错误。
    
    这是 Redis INCRBY 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持设置过期时间
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    """
    try:
        result = await redis_client.async_incrby(key, increment)
        
        # 如果指定了过期时间，则设置过期时间
        if expire is not None:
            await redis_client.async_expire(key, expire)
            
        return {"key": key, "value": result, "increment": increment}
    except Exception as e:
        return {"error": f"Failed to increment key {key} by {increment}: {str(e)}"}

@router.post("/decrby")
async def decrement_key_by(
    key: str = Body(..., description="键名"),
    decrement: int = Body(..., description="减量值"),
    expire: Optional[int] = Body(None, description="过期时间（秒）")
):
    """
    将键的值减少指定的整数（原子操作）
    
    如果键不存在，则在执行操作前将其设置为0。
    如果键的值不是整数，则返回错误。
    
    这是 Redis DECRBY 命令的最佳实践示例：
    1. 使用异步操作避免阻塞
    2. 支持设置过期时间
    3. 包含错误处理和日志记录
    4. 使用重试机制提高可靠性
    """
    try:
        result = await redis_client.async_decrby(key, decrement)
        
        # 如果指定了过期时间，则设置过期时间
        if expire is not None:
            await redis_client.async_expire(key, expire)
            
        return {"key": key, "value": result, "decrement": decrement}
    except Exception as e:
        return {"error": f"Failed to decrement key {key} by {decrement}: {str(e)}"}