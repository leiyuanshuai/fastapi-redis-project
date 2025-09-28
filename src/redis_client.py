import redis.asyncio as aredis
from redis.asyncio.cluster import RedisCluster as ARedisCluster
from loguru import logger
from typing import Optional, Union, Any, List, Dict, Tuple, Callable, Awaitable
from src.config import settings
import backoff
import orjson
from datetime import timedelta


class RedisClient:
    """
    高级Redis客户端封装类，提供异步操作接口，遵循生产环境最佳实践
    
    该类提供了完整的Redis功能封装，包括：
    1. 自动连接管理（单机/集群模式）
    2. 异步操作支持
    3. 自动重试机制
    4. 数据序列化/反序列化
    5. 错误处理和日志记录
    6. 连接池管理
    """

    def __init__(self):
        """
        初始化Redis客户端
        
        初始化过程包括：
        1. 创建异步客户端占位符
        2. 调用初始化方法建立连接
        3. 记录初始化成功日志
        """
        # 异步客户端连接池/集群客户端
        self._async_client = None

        # 初始化客户端
        self._init_client()

        logger.info("Redis client initialized successfully")

    def _init_client(self) -> None:
        """
        初始化Redis客户端（根据配置决定是单机还是集群）
        
        根据配置文件中的 is_cluster 和 cluster_nodes 参数决定初始化单机还是集群模式：
        - 如果 is_cluster 为 True 且 cluster_nodes 不为空，则初始化集群模式
        - 否则初始化单机模式
        """
        try:
            if settings.redis.is_cluster and settings.redis.cluster_nodes:
                # 初始化集群客户端
                self._init_cluster_clients()
            else:
                # 初始化单机客户端
                self._init_standalone_clients()

        except Exception as e:
            logger.error(f"Failed to initialize Redis clients: {str(e)}")
            raise

    def _init_standalone_clients(self) -> None:
        """
        初始化单机模式的Redis客户端
        
        创建异步连接池并初始化异步客户端，配置包括：
        - 主机地址和端口
        - 认证密码
        - 数据库编号
        - 响应解码设置
        - 连接池最大连接数
        - Socket超时时间
        - 超时重试设置
        """
        # 异步连接池
        async_pool = aredis.ConnectionPool(
            host=settings.redis.host,
            port=settings.redis.port,
            password=settings.redis.password,
            db=settings.redis.db,
            decode_responses=settings.redis.decode_responses,
            max_connections=settings.redis.max_connections,
            socket_timeout=settings.redis.socket_timeout,
            retry_on_timeout=settings.redis.retry_on_timeout
        )
        self._async_client = aredis.Redis(connection_pool=async_pool)

        logger.info(f"Standalone Redis clients initialized for {settings.redis.host}:{settings.redis.port}")

    def _init_cluster_clients(self) -> None:
        """
        初始化集群模式的Redis客户端
        
        创建异步集群客户端，配置包括：
        - 集群节点信息
        - 认证密码
        - 响应解码设置
        - 连接池最大连接数
        - Socket超时时间
        - 超时重试设置
        """
        # 异步集群客户端
        self._async_client = ARedisCluster(
            startup_nodes=settings.redis.cluster_nodes,
            password=settings.redis.password,
            decode_responses=settings.redis.decode_responses,
            max_connections=settings.redis.max_connections,
            socket_timeout=settings.redis.socket_timeout,
            retry_on_timeout=settings.redis.retry_on_timeout
        )

        logger.info(f"Redis Cluster clients initialized with nodes: {settings.redis.cluster_nodes}")

    @property
    def async_(self) -> Union[aredis.Redis, ARedisCluster]:
        """
        获取异步Redis客户端，自动重连
        
        如果客户端未初始化或连接断开，会尝试重新初始化连接。
        返回值可以是单机客户端(aredis.Redis)或集群客户端(ARedisCluster)。
        
        Returns:
            Union[aredis.Redis, ARedisCluster]: 异步Redis客户端实例
        """
        if not self._async_client:
            logger.warning("Async Redis client not connected, reconnecting...")
            self._init_client()
        return self._async_client

    def _is_connected(self) -> bool:
        """
        检查客户端是否连接正常
        
        在FastAPI应用中，不要使用asyncio.run()，因为事件循环已经在运行
        我们简单地检查客户端是否存在
        
        Returns:
            bool: 客户端是否存在
        """
        # 在FastAPI应用中，不要使用asyncio.run()，因为事件循环已经在运行
        # 我们简单地检查客户端是否存在
        return self._async_client is not None

    # ------------------------------
    # 重试装饰器
    # ------------------------------
    @staticmethod
    def _async_retry_decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        """
        异步方法重试装饰器
        
        为异步方法提供自动重试功能，使用指数退避算法：
        - 最大重试次数由配置决定
        - 基础延迟时间和延迟因子
        - 使用全抖动避免惊群效应
        
        Args:
            func: 需要添加重试功能的异步方法
            
        Returns:
            Callable[..., Awaitable[Any]]: 添加了重试功能的装饰器
        """

        @backoff.on_exception(
            backoff.expo,
            (aredis.RedisError, ConnectionError),
            max_tries=settings.redis.retry_attempts,
            base=2,
            factor=settings.redis.retry_delay,
            jitter=backoff.full_jitter
        )
        async def wrapper(self, *args, **kwargs):
            return await func(self, *args, **kwargs)

        return wrapper

    # ------------------------------
    # 通用工具方法
    # ------------------------------
    @_async_retry_decorator
    async def async_ping(self) -> bool:
        """
        测试Redis连接（异步）
        
        通过发送PING命令测试Redis连接是否正常，如果连接正常会返回PONG。
        使用重试装饰器确保在网络不稳定时能自动重试。
        
        Returns:
            bool: 连接是否正常
        """
        try:
            return await self.async_.ping()
        except Exception as e:
            logger.error(f"Async Redis ping failed: {str(e)}")
            return False

    # ------------------------------
    # 序列化工具
    # ------------------------------
    @staticmethod
    def _serialize(value: Any) -> Union[str, bytes]:
        """
        序列化数据，支持复杂类型
        
        将Python对象序列化为字符串或字节，支持的数据类型包括：
        - 基本类型：None, str, int, float, bool
        - 复杂类型：使用orjson进行序列化
        
        Args:
            value: 需要序列化的值
            
        Returns:
            Union[str, bytes]: 序列化后的字符串或字节
            
        Raises:
            Exception: 序列化失败时抛出异常
        """
        if value is None:
            return ""

        if isinstance(value, (str, int, float, bool)):
            return str(value)

        # 对于复杂类型，使用orjson序列化
        try:
            return orjson.dumps(value).decode()
        except Exception as e:
            logger.error(f"Failed to serialize value: {str(e)}")
            raise

    @staticmethod
    def _deserialize(value: Union[str, bytes, None]) -> Any:
        """
        反序列化数据
        
        将字符串或字节反序列化为Python对象：
        - None或空字符串返回None
        - 尝试使用orjson解析JSON格式数据
        - 如果不是JSON格式，直接返回原始值
        
        Args:
            value: 需要反序列化的值
            
        Returns:
            Any: 反序列化后的Python对象
        """
        if value is None or value == "":
            return None

        if isinstance(value, bytes):
            value = value.decode()

        # 尝试解析为JSON
        try:
            return orjson.loads(value)
        except (orjson.JSONDecodeError, TypeError):
            # 如果不是JSON，直接返回原始值
            return value

    # ------------------------------
    # String 类型操作 - 异步版
    # ------------------------------
    @_async_retry_decorator
    async def async_set(
            self,
            key: str,
            value: Any,
            expire: Optional[Union[int, timedelta]] = None,
            nx: bool = False,
            xx: bool = False,
            keep_ttl: bool = False
    ) -> bool:
        """
        异步设置键值对，支持复杂类型
        
        将值与键关联，支持多种选项：
        - 自动序列化复杂数据类型
        - 设置过期时间（秒或timedelta对象）
        - nx: 仅当键不存在时设置
        - xx: 仅当键存在时设置
        - keep_ttl: 保持现有TTL
        
        Args:
            key: 键名
            value: 值（支持复杂类型）
            expire: 过期时间（秒或timedelta对象）
            nx: 仅当键不存在时设置
            xx: 仅当键存在时设置
            keep_ttl: 保持现有TTL
            
        Returns:
            bool: 是否设置成功
        """
        try:
            serialized_value = self._serialize(value)

            # 处理过期时间
            ex = expire.total_seconds() if isinstance(expire, timedelta) else expire

            return await self.async_.set(
                name=key,
                value=serialized_value,
                ex=ex,
                nx=nx,
                xx=xx,
                keepttl=keep_ttl
            )
        except Exception as e:
            logger.error(f"Failed to async set key {key}: {str(e)}")
            return False

    @_async_retry_decorator
    async def async_get(self, key: str) -> Any:
        """
        获取键值（异步）
        
        获取与键关联的值并自动反序列化：
        - 如果键不存在，返回None
        - 自动反序列化复杂数据类型
        
        Args:
            key: 键名
            
        Returns:
            Any: 反序列化后的值
        """
        try:
            value = await self.async_.get(key)
            return self._deserialize(value)
        except Exception as e:
            logger.error(f"Failed to get key {key}: {str(e)}")
            return None

    @_async_retry_decorator
    async def async_delete(self, *keys: str) -> int:
        """
        删除一个或多个键（异步）
        
        删除指定的一个或多个键，返回实际删除的键数量。
        
        Args:
            keys: 键名列表
            
        Returns:
            int: 被删除的键数量
        """
        try:
            return await self.async_.delete(*keys)
        except Exception as e:
            logger.error(f"Failed to delete keys {keys}: {str(e)}")
            return 0

    @_async_retry_decorator
    async def async_exists(self, *keys: str) -> int:
        """
        检查键是否存在（异步）
        
        检查一个或多个键是否存在，返回存在的键数量。
        
        Args:
            keys: 键名列表
            
        Returns:
            int: 存在的键数量
        """
        try:
            return await self.async_.exists(*keys)
        except Exception as e:
            logger.error(f"Failed to check existence of keys {keys}: {str(e)}")
            return 0

    @_async_retry_decorator
    async def async_expire(
            self,
            key: str,
            time: Union[int, timedelta],
            nx: bool = False,
            xx: bool = False,
            gt: bool = False,
            lt: bool = False
    ) -> bool:
        """
        设置键的过期时间（异步）
        
        为键设置过期时间，支持多种选项：
        - nx: 仅当键没有过期时间时设置
        - xx: 仅当键有过期时间时设置
        - gt: 仅当新过期时间大于当前过期时间时设置
        - lt: 仅当新过期时间小于当前过期时间时设置
        
        Args:
            key: 键名
            time: 过期时间（秒或timedelta对象）
            nx: 仅当键没有过期时间时设置
            xx: 仅当键有过期时间时设置
            gt: 仅当新过期时间大于当前过期时间时设置
            lt: 仅当新过期时间小于当前过期时间时设置
            
        Returns:
            bool: 是否设置成功
        """
        try:
            ex = time.total_seconds() if isinstance(time, timedelta) else time
            return await self.async_.expire(key, ex, nx=nx, xx=xx, gt=gt, lt=lt)
        except Exception as e:
            logger.error(f"Failed to set expire time for key {key}: {str(e)}")
            return False

    @_async_retry_decorator
    async def async_ttl(self, key: str) -> int:
        """
        获取键的剩余生存时间（异步）
        
        获取键的剩余生存时间（TTL）：
        - -1 表示永不过期
        - -2 表示键不存在
        - 其他值表示剩余秒数
        
        Args:
            key: 键名
            
        Returns:
            int: 剩余生存时间（秒）
        """
        try:
            return await self.async_.ttl(key)
        except Exception as e:
            logger.error(f"Failed to get TTL for key {key}: {str(e)}")
            return -2

    # ------------------------------
    # Hash 类型操作 - 异步版
    # ------------------------------
    @_async_retry_decorator
    async def async_hset(
            self,
            name: str,
            key: Optional[str] = None,
            value: Optional[Any] = None,
            mapping: Optional[Dict] = None
    ) -> int:
        """
        设置哈希表字段值（异步）
        
        设置哈希表中的字段值，支持两种方式：
        1. 设置单个字段：提供name, key, value参数
        2. 批量设置：提供name和mapping参数
        
        Args:
            name: 哈希表名
            key: 字段名
            value: 字段值
            mapping: 字段值映射
            
        Returns:
            int: 被设置的字段数量
        """
        try:
            serialized_mapping = None
            if mapping:
                serialized_mapping = {
                    k: self._serialize(v) for k, v in mapping.items()
                }

            return await self.async_.hset(
                name=name,
                key=key,
                value=self._serialize(value) if value is not None else None,
                mapping=serialized_mapping
            )
        except Exception as e:
            logger.error(f"Failed to hset for hash {name}: {str(e)}")
            return 0

    @_async_retry_decorator
    async def async_hget(self, name: str, key: str) -> Any:
        """
        获取哈希表字段值（异步）
        
        获取哈希表中指定字段的值并自动反序列化。
        
        Args:
            name: 哈希表名
            key: 字段名
            
        Returns:
            Any: 反序列化后的字段值
        """
        try:
            value = await self.async_.hget(name, key)
            return self._deserialize(value)
        except Exception as e:
            logger.error(f"Failed to hget for hash {name}, key {key}: {str(e)}")
            return None

    @_async_retry_decorator
    async def async_hgetall(self, name: str) -> Dict[str, Any]:
        """
        获取哈希表所有字段和值（异步）
        
        获取哈希表中所有字段和值的映射，并自动反序列化所有值。
        
        Args:
            name: 哈希表名
            
        Returns:
            Dict[str, Any]: 字段值映射
        """
        try:
            result = await self.async_.hgetall(name)
            return {
                k.decode() if isinstance(k, bytes) else k:
                self._deserialize(v) for k, v in result.items()
            }
        except Exception as e:
            logger.error(f"Failed to hgetall for hash {name}: {str(e)}")
            return {}

    @_async_retry_decorator
    async def async_hdel(self, name: str, *keys: str) -> int:
        """
        删除哈希表一个或多个字段（异步）
        
        删除哈希表中一个或多个字段，返回实际删除的字段数量。
        
        Args:
            name: 哈希表名
            keys: 字段名列表
            
        Returns:
            int: 被删除的字段数量
        """
        try:
            return await self.async_.hdel(name, *keys)
        except Exception as e:
            logger.error(f"Failed to hdel for hash {name}, keys {keys}: {str(e)}")
            return 0

    # ------------------------------
    # List 类型操作 - 异步版
    # ------------------------------
    @_async_retry_decorator
    async def async_lpush(self, name: str, *values: Any) -> int:
        """
        将一个或多个值插入到列表头部（异步）
        
        将值插入到列表的头部（左侧），如果键不存在会创建新列表。
        
        Args:
            name: 列表名
            values: 值列表
            
        Returns:
            int: 操作后列表的长度
        """
        try:
            serialized_values = [self._serialize(v) for v in values]
            return await self.async_.lpush(name, *serialized_values)
        except Exception as e:
            logger.error(f"Failed to lpush for list {name}: {str(e)}")
            return 0

    @_async_retry_decorator
    async def async_rpush(self, name: str, *values: Any) -> int:
        """
        将一个或多个值插入到列表尾部（异步）
        
        将值插入到列表的尾部（右侧），如果键不存在会创建新列表。
        
        Args:
            name: 列表名
            values: 值列表
            
        Returns:
            int: 操作后列表的长度
        """
        try:
            serialized_values = [self._serialize(v) for v in values]
            return await self.async_.rpush(name, *serialized_values)
        except Exception as e:
            logger.error(f"Failed to rpush for list {name}: {str(e)}")
            return 0

    @_async_retry_decorator
    async def async_lpop(self, name: str, count: Optional[int] = None) -> Union[Any, List[Any], None]:
        """
        移除并返回列表的第一个元素（异步）
        
        移除并返回列表的第一个元素（左侧）：
        - 如果列表为空，返回None
        - 如果指定count，返回包含count个元素的列表
        - 否则返回单个元素
        
        Args:
            name: 列表名
            count: 返回元素的数量
            
        Returns:
            Union[Any, List[Any], None]: 元素或元素列表
        """
        try:
            result = await self.async_.lpop(name, count=count)
            if isinstance(result, list):
                return [self._deserialize(item) for item in result]
            return self._deserialize(result)
        except Exception as e:
            logger.error(f"Failed to lpop for list {name}: {str(e)}")
            return None

    @_async_retry_decorator
    async def async_rpop(self, name: str, count: Optional[int] = None) -> Union[Any, List[Any], None]:
        """
        移除并返回列表的最后一个元素（异步）
        
        移除并返回列表的最后一个元素（右侧）：
        - 如果列表为空，返回None
        - 如果指定count，返回包含count个元素的列表
        - 否则返回单个元素
        
        Args:
            name: 列表名
            count: 返回元素的数量
            
        Returns:
            Union[Any, List[Any], None]: 元素或元素列表
        """
        try:
            result = await self.async_.rpop(name, count=count)
            if isinstance(result, list):
                return [self._deserialize(item) for item in result]
            return self._deserialize(result)
        except Exception as e:
            logger.error(f"Failed to rpop for list {name}: {str(e)}")
            return None

    @_async_retry_decorator
    async def async_llen(self, name: str) -> int:
        """
        获取列表长度（异步）
        
        获取列表中元素的数量。
        
        Args:
            name: 列表名
            
        Returns:
            int: 列表长度
        """
        try:
            return await self.async_.llen(name)
        except Exception as e:
            logger.error(f"Failed to llen for list {name}: {str(e)}")
            return 0

    # ------------------------------
    # Set 类型操作 - 异步版
    # ------------------------------
    @_async_retry_decorator
    async def async_sadd(self, name: str, *values: Any) -> int:
        """
        向集合添加一个或多个成员（异步）
        
        向集合中添加一个或多个成员，已存在的成员会被忽略。
        
        Args:
            name: 集合名
            values: 成员列表
            
        Returns:
            int: 被添加的成员数量
        """
        try:
            serialized_values = [self._serialize(v) for v in values]
            return await self.async_.sadd(name, *serialized_values)
        except Exception as e:
            logger.error(f"Failed to sadd for set {name}: {str(e)}")
            return 0

    @_async_retry_decorator
    async def async_srem(self, name: str, *values: Any) -> int:
        """
        移除集合中一个或多个成员（异步）
        
        从集合中移除一个或多个成员，不存在的成员会被忽略。
        
        Args:
            name: 集合名
            values: 成员列表
            
        Returns:
            int: 被移除的成员数量
        """
        try:
            serialized_values = [self._serialize(v) for v in values]
            return await self.async_.srem(name, *serialized_values)
        except Exception as e:
            logger.error(f"Failed to srem for set {name}: {str(e)}")
            return 0

    @_async_retry_decorator
    async def async_smembers(self, name: str) -> set:
        """
        获取集合所有成员（异步）
        
        获取集合中的所有成员。
        
        Args:
            name: 集合名
            
        Returns:
            set: 成员集合
        """
        try:
            result = await self.async_.smembers(name)
            return {self._deserialize(item) for item in result}
        except Exception as e:
            logger.error(f"Failed to smembers for set {name}: {str(e)}")
            return set()

    @_async_retry_decorator
    async def async_sismember(self, name: str, value: Any) -> bool:
        """
        判断成员是否是集合的成员（异步）
        
        判断指定值是否是集合的成员。
        
        Args:
            name: 集合名
            value: 成员值
            
        Returns:
            bool: 是否为集合成员
        """
        try:
            serialized_value = self._serialize(value)
            return await self.async_.sismember(name, serialized_value)
        except Exception as e:
            logger.error(f"Failed to sismember for set {name}: {str(e)}")
            return False

    # ------------------------------
    # Sorted Set 类型操作 - 异步版
    # ------------------------------
    @_async_retry_decorator
    async def async_zadd(
            self,
            name: str,
            mapping: Dict[Any, float],
            nx: bool = False,
            xx: bool = False,
            ch: bool = False,
            incr: bool = False
    ) -> Union[int, float, None]:
        """
        向有序集合添加一个或多个成员（异步）
        
        向有序集合中添加一个或多个成员，或更新已存在成员的分数：
        - nx: 仅添加新成员，忽略已存在的成员
        - xx: 仅更新已存在的成员，不添加新成员
        - ch: 返回影响的成员数，而不是新添加的成员数
        - incr: 增加成员的分数，而不是设置分数
        
        Args:
            name: 有序集合名
            mapping: 成员分数映射
            nx: 仅添加新成员
            xx: 仅更新已存在成员
            ch: 返回影响的成员数
            incr: 增加分数而不是设置分数
            
        Returns:
            Union[int, float, None]: 添加的成员数或增加后的分数
        """
        try:
            serialized_mapping = {
                self._serialize(k): v for k, v in mapping.items()
            }
            return await self.async_.zadd(
                name=name,
                mapping=serialized_mapping,
                nx=nx,
                xx=xx,
                ch=ch,
                incr=incr
            )
        except Exception as e:
            logger.error(f"Failed to zadd for sorted set {name}: {str(e)}")
            return None

    @_async_retry_decorator
    async def async_zrange(
            self,
            name: str,
            start: int,
            end: int,
            desc: bool = False,
            withscores: bool = False,
            score_cast_func: Callable = float
    ) -> List[Union[Any, Tuple[Any, float]]]:
        """
        获取有序集合的指定范围成员（异步）
        
        获取有序集合指定范围内的成员：
        - start: 开始索引（包含）
        - end: 结束索引（包含）
        - desc: 是否降序排列
        - withscores: 是否包含分数
        - score_cast_func: 分数转换函数
        
        Args:
            name: 有序集合名
            start: 开始索引
            end: 结束索引
            desc: 是否降序
            withscores: 是否包含分数
            score_cast_func: 分数转换函数
            
        Returns:
            List[Union[Any, Tuple[Any, float]]]: 成员列表或成员分数元组列表
        """
        try:
            result = await self.async_.zrange(
                name=name,
                start=start,
                end=end,
                desc=desc,
                withscores=withscores,
                score_cast_func=score_cast_func
            )
            if withscores:
                return [(self._deserialize(item[0]), item[1]) for item in result]
            return [self._deserialize(item) for item in result]
        except Exception as e:
            logger.error(f"Failed to zrange for sorted set {name}: {str(e)}")
            return []

    @_async_retry_decorator
    async def async_zrem(self, name: str, *values: Any) -> int:
        """
        移除有序集合中的一个或多个成员（异步）
        
        从有序集合中移除一个或多个成员。
        
        Args:
            name: 有序集合名
            values: 成员列表
            
        Returns:
            int: 被移除的成员数量
        """
        try:
            serialized_values = [self._serialize(v) for v in values]
            return await self.async_.zrem(name, *serialized_values)
        except Exception as e:
            logger.error(f"Failed to zrem for sorted set {name}: {str(e)}")
            return 0

    # ------------------------------
    # 事务操作 - 异步版
    # ------------------------------
    @_async_retry_decorator
    async def async_multi_exec(self) -> 'RedisClient':
        """
        开始一个事务（异步）
        
        开始一个Redis事务，后续的命令会被加入到事务队列中，
        直到调用execute方法时一起执行。
        
        Returns:
            RedisClient: Redis客户端实例，用于链式调用
        """
        try:
            await self.async_.multi()
            return self
        except Exception as e:
            logger.error(f"Failed to start transaction: {str(e)}")
            raise

    @_async_retry_decorator
    async def async_execute(self) -> List:
        """
        执行事务（异步）
        
        执行之前通过multi方法开始的事务，返回事务中各命令的执行结果。
        
        Returns:
            List: 执行结果列表
        """
        try:
            return await self.async_.execute()
        except Exception as e:
            logger.error(f"Failed to execute transaction: {str(e)}")
            raise

    # ------------------------------
    # 管道操作 - 异步版
    # ------------------------------
    async def async_pipeline(self) -> 'aredis.Pipeline':
        """
        创建一个异步管道
        
        创建一个异步管道对象，用于批量执行命令以提高性能。
        
        Returns:
            aredis.Pipeline: 异步管道对象
        """
        try:
            return self.async_.pipeline()
        except Exception as e:
            logger.error(f"Failed to create pipeline: {str(e)}")
            raise

    # ------------------------------
    # 清理资源
    # ------------------------------
    async def async_close(self) -> None:
        """
        关闭异步连接
        
        关闭异步Redis客户端连接，释放相关资源。
        """
        try:
            if self._async_client:
                await self._async_client.aclose()
                logger.info("Async Redis connection closed")
        except Exception as e:
            logger.error(f"Failed to close async Redis connection: {str(e)}")


# 创建Redis客户端实例
redis_client = RedisClient()