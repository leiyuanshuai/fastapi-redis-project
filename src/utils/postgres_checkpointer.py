import asyncio
import sys
import time
from typing import Optional, AsyncContextManager, Annotated, TypedDict

from fastapi import Depends
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.config.env import env

# 构造PostgreSQL数据库连接字符串
POSTGRES_DATABASE_URL = (f"postgresql://{env.pg_db_username}:{env.pg_db_password}@"
                         f"{env.pg_db_host}:{env.pg_db_port}/{env.pg_db_database}"
                         f"?connect_timeout=10&keepalives=1&keepalives_idle=30"
                         f"&keepalives_interval=10&keepalives_count=3")


class PostgresCheckpointerManager:
  # 单例实例，存储AsyncPostgresSaver对象
  _instance: Optional[AsyncPostgresSaver] = None
  # 存储异步上下文管理器，用于正确管理数据库连接的生命周期
  _context_manger: Optional[AsyncContextManager] = None
  # 异步锁，确保在并发环境下单例实例的创建是线程安全的
  _lock = asyncio.Lock()
  # 最后一次检测连接是否有效的时间
  _last_check_time = time.time()
  # 一个图用来测试连接是否仍然有效
  _graph: Optional[CompiledStateGraph] = None

  @staticmethod
  async def get_instance() -> AsyncPostgresSaver:
    is_connection_alive = await PostgresCheckpointerManager.is_connection_alive()
    if not is_connection_alive:

      # 使用异步锁确保并发安全
      async with PostgresCheckpointerManager._lock:
        if PostgresCheckpointerManager._instance:
          await PostgresCheckpointerManager.close_instance()

        # 从连接字符串创建AsyncPostgresSaver上下文管理器
        PostgresCheckpointerManager._context_manger = AsyncPostgresSaver.from_conn_string(POSTGRES_DATABASE_URL)
        # 进入异步上下文，初始化数据库连接
        PostgresCheckpointerManager._instance = await PostgresCheckpointerManager._context_manger.__aenter__()
        # 创建用来测试连接是否有效的图
        PostgresCheckpointerManager._graph = create_test_graph(PostgresCheckpointerManager._instance)
        # 打印调试信息
        print("Create AsyncPostgresSaver:", PostgresCheckpointerManager._instance)

    # 返回单例实例
    return PostgresCheckpointerManager._instance

  @staticmethod
  async def close_instance():
    """
    关闭并清理单例实例和相关资源
    """
    # 清理实例引用
    if PostgresCheckpointerManager._instance is not None:
      PostgresCheckpointerManager._instance = None
    # 退出上下文管理器，正确关闭数据库连接
    if PostgresCheckpointerManager._context_manger is not None:
      await PostgresCheckpointerManager._context_manger.__aexit__(None, None, None)
      PostgresCheckpointerManager._context_manger = None

    # 清理掉测试连接的图
    PostgresCheckpointerManager._graph = None
    return

  @staticmethod
  async def is_connection_alive() -> bool:
    """检查数据库连接是否仍然存活"""
    if PostgresCheckpointerManager._instance is None:
      return False

    # 检测间隔小于60秒，直接返回True
    if time.time() - PostgresCheckpointerManager._last_check_time < 60:
      return True

    try:
      print("\n\nCheck Postgres connection...\n\n")
      await PostgresCheckpointerManager._graph.aget_state(config={"configurable": {"thread_id": "@@TestAsyncPostgresSaverConnectionIsKeepAlive"}})
      PostgresCheckpointerManager._last_check_time = time.time()
      return True
    except Exception as e:
      print(f"Postgres connection check failed: {e}")
      return False


# 定义依赖注入类型，用于FastAPI自动注入AsyncPostgresSaver实例
AsyncPostgresSaverDep = Annotated[AsyncPostgresSaver, Depends(PostgresCheckpointerManager.get_instance)]


async def check_postgres_connection():
  """
  用于启动服务的时候检查Postgres数据库连接是否正常
  """
  try:
    print("Connecting Postgres...")
    # 尝试获取数据库连接实例
    await PostgresCheckpointerManager.get_instance()
    # 连接成功，打印成功信息
    print("✅ Postgres connection successful：", POSTGRES_DATABASE_URL)
  except Exception as e:
    # 打印连接失败信息及错误详情
    print(f"❌ Postgres connection failed: {e}")
    # 重新抛出异常，让上层处理
    raise e


async def close_postgres_connection():
  await PostgresCheckpointerManager.close_instance()


# 在Windows平台上设置事件循环策略为WindowsSelectorEventLoopPolicy
if sys.platform == "win32":
  from asyncio import WindowsSelectorEventLoopPolicy

  asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())


def create_test_graph(checkpointer: AsyncPostgresSaver):
  class StateSchema(TypedDict):
    input: str

  builder = StateGraph(StateSchema)

  def node(state: StateSchema):
    return {}

  builder.add_node(node)
  builder.set_entry_point("node")
  builder.set_finish_point("node")

  return builder.compile(checkpointer=checkpointer)
