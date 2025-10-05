import asyncio
import datetime
import json
from typing import Type, List, Any, Union, Optional

from fastapi import FastAPI, APIRouter, HTTPException, Body
from pydantic import create_model, BaseModel
from sqlalchemy import func
from sqlmodel import select
from starlette.requests import Request

from src.model.BasicModel import BasicModel
from src.utils.PageQueryParams import PageQueryParams
from src.utils.db_utils import AsyncSessionDep
from src.utils.next_id import next_id


class ModelPublicUser(BaseModel):
  id: str


def create_model_service(
  #/*@formatter:off*/
  Cls: Type[BasicModel],              # model实体类

  custom_query = None,

  before_query_list=None,             # 分页查询前异步处理函数，参数：(query_param, session)
  after_query_list=None,              # 分页查询后异步处理函数，参数：(query_cls_list, has_next, query_param, session)
  before_query_item=None,             # 单条查询前异步处理函数，参数：(row_dict, session)
  after_query_item=None,              # 单条查询后异步处理函数，参数：(item_cls, row_dict, session)
  before_insert=None,                 # 单条新建前异步处理函数，参数：(row_dict, session)
  after_insert=None,                  # 单条新建后异步处理函数，参数：(insert_cls, row_dict, session)
  before_update=None,                 # 单条更新前异步处理函数，参数：(row_dict, session)
  after_update=None,                  # 单条更新后异步处理函数，参数：(update_cls, row_dict, session)
  before_delete=None,                 # 单条删除前异步处理函数，参数：(row_dict, session)
  after_delete=None,                  # 单条删除后异步处理函数，参数：(delete_cls, row_dict, session)

  before_batch_insert=None,           # 批量新建前异步处理函数，参数：(row_dict_list, session)
  after_batch_insert=None,            # 批量新建后异步处理函数，参数：(refresh_cls_list, row_dict_list, session)
  before_batch_update=None,           # 批量更新前异步处理函数，参数：(row_dict_list, session)
  after_batch_update=None,            # 批量更新后异步处理函数，参数：(refresh_cls_list, row_dict_list, session)
  before_batch_delete=None,           # 批量删除前异步处理函数，参数：(row_dict_list, session)
  after_batch_delete=None,            # 批量删除后异步处理函数，参数：(delete_cls_list, row_dict_list, session)
  # /*@formatter:on*/
):
  # 定义模型服务类，封装模型相关的CRUD接口及业务逻辑
  class ModelService:
    # 支持的所有端点列表，包含常用的CRUD及批量操作
    END_POINTS = ['list', 'item', 'insert', 'batch_insert', 'update', 'batch_update', 'delete', 'batch_delete']

    def __init__(self):
      # 验证传入的模型类是否继承自BasicModel，确保基础字段存在
      if not issubclass(Cls, BasicModel):
        raise TypeError(f"{Cls.__name__} 必须继承自 BasicModel")
      # 保存当前操作的模型类
      self.Cls = Cls

    # 检查字典中的键是否为模型类的有效属性
    # 参数:
    #   row_dict: 待检查的字典（通常为请求参数）
    def check_invalid_keys(self, row_dict: dict):
      # 筛选出所有不在模型类属性中的键（无效键）
      invalid_keys = [key for key in row_dict.keys() if not hasattr(Cls, key)]
      if invalid_keys:
        # 若存在无效键，抛出HTTP 500异常，提示无效键和有效键列表
        raise HTTPException(
          status_code=500,
          detail=f"Invalid filter keys: {invalid_keys}. Valid keys are: {Cls.__annotations__.keys()}"
        )

    # 检查要新建的行数据
    async def check_insert_row_dict(self, row_dict: dict, user: ModelPublicUser):
      # 若未提供id，自动生成唯一id
      if row_dict.get("id", None) is None:
        row_dict["id"] = await next_id()

      if user:
        if not row_dict.get("created_by", None):
          row_dict["created_by"] = user.id

        if not row_dict.get("updated_by", None):
          row_dict["updated_by"] = user.id

    # 检查要更新的行数据
    async def check_update_row_dict(self, row_dict: dict, user: ModelPublicUser):
      if user:
        row_dict["updated_by"] = user.id
        row_dict["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_route(
      self,
      app: FastAPI,  # FastAPI实例，用来注册路由
      path: str,  # 路由前缀地址
      end_points: List[str] = None,  # 生成的端点入口接口清单
    ):
      # 确定启用的端点，默认为全部支持的端点
      if not end_points:
        end_points = self.END_POINTS

      # 动态创建分页查询的响应模型：包含数据列表和是否有下一页的标识
      ListResponse = create_model(f"{Cls.__name__}ListResponse", list=(List[Cls], ...), has_next=(bool, ...), total=(Union[int, None], None))
      # 动态创建单条查询的响应模型：包含单个模型实例
      ItemResponse = create_model(f"{Cls.__name__}ItemResponse", result=(Optional[Cls], ...))
      # 动态创建批量操作的响应模型：包含操作后的模型实例列表
      BatchResponse = create_model(f"{Cls.__name__}BatchResponse", result=(List[Cls], ...))
      # 动态创建批量删除的响应模型：包含删除操作是否成功的标识
      DeleteResponse = create_model(f"{Cls.__name__}BatchResponse", result=(bool, ...))

      # 创建APIRouter实例，设置路由前缀和标签（标签用于API文档分组）
      router = APIRouter(prefix=path, tags=[path])

      # 若启用"list"端点，注册列表查询接口
      if 'list' in end_points:
        # 列表查询接口：支持过滤和分页，响应模型为ListResponse
        @router.post("/list", response_model=ListResponse)
        async def _list(query_param: PageQueryParams, session: AsyncSessionDep):
          # 调用query_list方法执行查询，获取数据列表和是否有下一页
          query_cls_list, has_next, total = await self.query_list(query_param, session)
          # 返回符合响应模型的结果
          return {
            "list": query_cls_list,
            "has_next": has_next,
            "total": total,
          }

      # 若启用"item"端点，注册单条查询接口
      if 'item' in end_points:
        # 单条查询接口：根据条件查询单条记录，响应模型为ItemResponse
        @router.post("/item", response_model=ItemResponse)
        async def _item(
          session: AsyncSessionDep,
          row_dict: dict = Body(..., description=f"插入的数据，字段参考{Cls.__name__}")
        ):
          # 调用query_item方法查询单条记录并返回
          return {"result": await self.query_item(session, row_dict)}

      # 若启用"insert"端点，注册单条插入接口
      if 'insert' in end_points:
        # 单条插入接口：新增一条记录，响应模型为ItemResponse
        @router.post("/insert", response_model=ItemResponse)
        async def _insert(
          session: AsyncSessionDep,
          request: Request,
          row_dict: dict = Body(..., description=f"插入的数据，字段参考{Cls.__name__}"),
        ):
          # 调用item_insert方法执行插入并返回结果
          return {"result": await self.item_insert(session, row_dict, request.state.user)}

      # 若启用"batch_insert"端点，注册批量插入接口
      if 'batch_insert' in end_points:
        # 批量插入接口：批量新增记录，响应模型为BatchResponse
        @router.post("/batch_insert", response_model=BatchResponse)
        async def _batch_insert(
          session: AsyncSessionDep,
          row_dict_list: List[dict] = Body(..., description=f"批量插入的数据数组，字段参考{Cls.__name__}"),
          request: Request = None,
        ):
          # 调用batch_insert方法执行批量插入并返回结果
          return {"result": await self.batch_insert(session, row_dict_list, request.state.user)}

      # 若启用"update"端点，注册单条更新接口
      if 'update' in end_points:
        # 单条更新接口：更新一条记录，响应模型为ItemResponse
        @router.post("/update", response_model=ItemResponse)
        async def _update(
          session: AsyncSessionDep,
          row_dict: dict = Body(..., description=f"更新的数据，字段参考{Cls.__name__}"),
          request: Request = None,
        ):
          # 调用item_update方法执行更新并返回结果
          return {"result": await self.item_update(session, row_dict, request.state.user)}

      # 若启用"batch_update"端点，注册批量更新接口
      if 'batch_update' in end_points:
        # 批量更新接口：批量更新记录，响应模型为BatchResponse
        @router.post("/batch_update", response_model=BatchResponse)
        async def _batch_update(
          session: AsyncSessionDep,
          row_dict_list: List[dict] = Body(..., description=f"批量更新的数据数组，字段参考{Cls.__name__}"),
          request: Request = None,
        ):
          # 调用batch_update方法执行批量更新并返回结果
          return {"result": await self.batch_update(session, row_dict_list, request.state.user)}

      # 若启用"delete"端点，注册单条删除接口
      if 'delete' in end_points:
        # 单条删除接口：删除一条记录，响应模型为DeleteResponse
        @router.post("/delete", response_model=DeleteResponse)
        async def _delete(
          session: AsyncSessionDep,
          row_dict: dict = Body(..., description=f"删除的数据，字段参考{Cls.__name__}")
        ):
          # 调用item_delete方法执行删除并返回结果
          return {"result": await self.item_delete(session, row_dict)}

      # 若启用"batch_delete"端点，注册批量删除接口
      if 'batch_delete' in end_points:
        # 批量删除接口：批量删除记录，响应模型为DeleteResponse
        @router.post("/batch_delete", response_model=DeleteResponse)
        async def _delete(
          session: AsyncSessionDep,
          row_dict_list: List[dict] = Body(..., description=f"批量删除的数据数组，字段参考{Cls.__name__}")
        ):
          # 调用batch_delete方法执行批量删除并返回结果
          return {"result": await self.batch_delete(session, row_dict_list)}

      # 将路由添加到FastAPI应用
      app.include_router(router)

    def select_cls(self):
      if custom_query is not None:
        query = custom_query()
      else:
        query = select(Cls)
      return query

    # 分页查询工具方法：执行带过滤和分页的查询
    async def query_list(self, query_param: PageQueryParams, session: AsyncSessionDep):

      if before_query_list is not None:
        await before_query_list(query_param, session)

      # 创建基础查询：查询当前模型类的所有记录
      query = self.select_cls()
      count_query = select(func.count()).select_from(Cls)

      # 若有过滤条件，验证并应用过滤
      if query_param.filters:
        self.check_invalid_keys(query_param.filters)
        # 为每个过滤条件添加WHERE子句（字段=值）
        for key, value in query_param.filters.items():
          # 判断value是否为列表或元组类型
          if isinstance(value, (list, tuple)):
            # 如果是数组，使用in查询
            query = query.where(getattr(Cls, key).in_(value))
            count_query = count_query.where(getattr(Cls, key).in_(value))
          else:
            # 如果不是数组，使用等于查询
            query = query.where(getattr(Cls, key) == value)
            count_query = count_query.where(getattr(Cls, key) == value)

      if query_param.sort_field:
        # 为排序字段添加ORDER BY子句
        cls_attr = getattr(Cls, query_param.sort_field)
        order_value = cls_attr.desc() if query_param.sort_desc == 'desc' else cls_attr.asc();
        query = query.order_by(order_value)

      # 若不查询全部数据（即启用分页）
      if query_param.all is False:
        # 计算偏移量（跳过前N条），并查询比一页多1条的记录（用于判断是否有下一页）
        query = query.offset(query_param.page * query_param.page_size).limit(query_param.page_size + 1)

      # 执行查询并获取结果
      result = await session.execute(query)

      if query_param.count:
        total, = (await session.execute(count_query)).one()
      else:
        total = None

      # 将查询结果转换为标量列表（模型实例列表）
      query_cls_list: List[Any] = result.scalars().all()

      # 打印查询结果类型和内容（调试用）
      print("query_cls_list", type(query_cls_list), query_cls_list)

      # 判断是否有下一页：若查询结果数量等于一页大小+1，则说明有下一页
      has_next = len(query_cls_list) == query_param.page_size + 1

      # 若有下一页，移除多查询的那一条记录
      if has_next:
        query_cls_list.pop()

      if after_query_list is not None:
        await after_query_list(query_cls_list, has_next, query_param, session)

      # 返回处理后的结果列表和是否有下一页的标识
      return (query_cls_list, has_next, total)

    # 单条查询工具方法：根据条件查询单条记录
    async def query_item(self, session: AsyncSessionDep, row_dict: dict = Body(..., description=f"查询数据的字段筛选值，字段参考{Cls.__name__}")):
      if before_query_item is not None:
        await before_query_item(row_dict, session)

      # 创建基础查询：查询当前模型类的所有记录
      query = self.select_cls()

      # 验证查询条件中的键是否有效
      self.check_invalid_keys(row_dict)
      # 为每个条件添加WHERE子句（字段=值）
      for key, value in row_dict.items():
        query = query.where(getattr(Cls, key) == value)

      # 执行查询
      result = await session.execute(query)
      # 返回第一条匹配的记录（若存在）
      item_cls = result.scalars().first()

      if after_query_item is not None and item_cls is not None:
        await after_query_item(item_cls, row_dict, session)

      return item_cls

    # 单条插入工具方法：新增一条记录
    async def item_insert(
      self,
      session: AsyncSessionDep,
      row_dict: dict = Body(..., description=f"插入的数据，字段参考{Cls.__name__}"),
      user: ModelPublicUser = None,
    ):
      if before_insert is not None:
        await before_insert(row_dict, session)

      await self.check_insert_row_dict(row_dict, user)

      try:
        # 使用模型类验证数据并创建实例（校验字段类型和约束）
        insert_cls = Cls.model_validate(row_dict)
      except ValueError as e:
        # 数据验证失败时，抛出HTTP 500异常并返回错误详情
        raise HTTPException(status_code=500, detail=str(e))
      # 将实例添加到数据库会话
      session.add(insert_cls)
      # 提交事务（保存到数据库）
      await session.commit()
      # 刷新实例，获取数据库生成的最新数据（如自动更新的时间字段）
      await session.refresh(insert_cls)
      insert_cls = await self.query_item(session, {"id": insert_cls.id})

      if after_insert is not None:
        await after_insert(insert_cls, row_dict, session)

      # 返回插入的实例
      return insert_cls

    # 批量插入工具方法：批量新增记录
    async def batch_insert(
      self,
      session: AsyncSessionDep,
      row_dict_list: List[dict] = Body(..., description=f"批量插入的数据数组，字段参考{Cls.__name__}"),
      user: ModelPublicUser = None,
    ):

      if before_batch_insert is not None:
        await before_batch_insert(row_dict_list, session)

      # 筛选出没有id的记录（需要自动生成id）
      row_dict_list_without_id = []

      for row_dict in row_dict_list:
        if row_dict.get("id") is None:
          row_dict_list_without_id.append(row_dict)

      # 若存在需要自动生成id的记录
      if len(row_dict_list_without_id):
        # 批量生成唯一id（数量等于需要生成id的记录数）
        new_id_list = await next_id(len(row_dict_list_without_id))
        # 为每条记录分配生成的id
        for index, id in enumerate(new_id_list):
          row_dict_list_without_id[index]["id"] = id

      for row_dict in row_dict_list_without_id:
        await self.check_insert_row_dict(row_dict, user)

      try:
        # 验证所有记录并转换为模型实例列表
        insert_cls_list = [Cls.model_validate(row_dict) for row_dict in row_dict_list]
      except ValueError as e:
        # 验证失败时抛出异常
        raise HTTPException(status_code=500, detail=str(e))

      # 将所有实例添加到会话
      session.add_all(insert_cls_list)

      # 提交事务，保存数据到数据库
      await session.commit()

      # 查询并返回所有插入的实例（刷新数据，确保获取最新状态）
      refresh_cls_list = (await session.execute(self.select_cls().where(Cls.id.in_([obj.id for obj in insert_cls_list])))).scalars().all()

      if after_batch_insert is not None:
        await after_batch_insert(refresh_cls_list, row_dict_list, session)

      # 返回刷新后的实例列表
      return refresh_cls_list

    # 单条更新工具方法：更新一条记录
    async def item_update(
      self,
      session: AsyncSessionDep,
      row_dict: dict = Body(..., description=f"更新的数据，字段参考{Cls.__name__}"),
      user: ModelPublicUser = None
    ):

      if before_update is not None:
        await before_update(row_dict, session)

      await self.check_update_row_dict(row_dict, user)

      # 检查id是否存在（更新必须指定id）
      if not row_dict.get('id'):
        raise HTTPException(status_code=400, detail="ID不能为空")
      # 根据id查询要更新的记录
      update_cls = (await session.exec(self.select_cls().where(Cls.id == row_dict.get('id')))).first()
      if not update_cls:
        # 若记录不存在，抛出异常
        raise HTTPException(status_code=500, detail="Update row not found")

      # 遍历更新字段：为记录的每个键设置新值
      for key, value in row_dict.items():
        setattr(update_cls, key, value)

      # 将更新后的实例添加到会话
      session.add(update_cls)
      # 提交事务
      await session.commit()
      # 刷新实例，获取最新数据
      await session.refresh(update_cls)
      # update_cls = await self.query_item(session, {"id": update_cls.id})

      if after_update is not None:
        await after_update(update_cls, row_dict, session)

      # 返回更新后的实例
      return update_cls

    # 批量更新工具方法：批量更新记录
    async def batch_update(
      self,
      session: AsyncSessionDep,
      row_dict_list: List[dict] = Body(..., description=f"批量更新的数据数组，字段参考{Cls.__name__}"),
      user: ModelPublicUser = None
    ):

      if before_batch_update is not None:
        await before_batch_update(row_dict_list, session)

      for row_dict in row_dict_list:
        await self.check_update_row_dict(row_dict, user)

      # 提取所有待更新记录的id
      update_id_list = [row_dict['id'] for row_dict in row_dict_list]
      # 根据id查询所有待更新的记录
      update_cls_list = (await session.exec(self.select_cls().where(Cls.id.in_(update_id_list)))).all()
      # 若查询到的记录数量与待更新数量不一致，说明部分id不存在
      if len(update_cls_list) != len(row_dict_list):
        # 抛出异常并提示不存在的id
        raise HTTPException(status_code=500, detail="Update row not found：" + json.dumps(row_dict_list, ensure_ascii=False))

      # 创建id到更新数据的映射（便于快速查找）
      id_2_row_dict = {row_dict["id"]: row_dict for row_dict in row_dict_list}

      # 遍历每条查询到的记录，更新其字段
      for update_cls in update_cls_list:
        # 获取当前记录对应的更新数据（根据id）
        row_dict = id_2_row_dict.get(update_cls.id, None)
        # 遍历更新字段
        for key, value in row_dict.items():
          setattr(update_cls, key, value)

      # 将所有更新后的实例添加到会话
      session.add_all(update_cls_list)

      # 提交事务
      await session.commit()
      # 查询并返回所有更新后的实例（刷新数据）
      refresh_cls_list = (await session.execute(self.select_cls().where(Cls.id.in_([obj.id for obj in update_cls_list])))).scalars().all()

      if after_batch_update is not None:
        await after_batch_update(refresh_cls_list, row_dict_list, session)

      # 返回刷新后的实例列表
      return refresh_cls_list

    # 单条删除工具方法：删除一条记录
    async def item_delete(self, session: AsyncSessionDep, row_dict: dict = Body(..., description=f"删除的数据，字段参考{Cls.__name__}")):

      if before_delete is not None:
        await before_delete(row_dict, session)

      # 根据id查询要删除的记录
      delete_cls = (await session.exec(self.select_cls().where(Cls.id == row_dict.get('id')))).first()
      if not delete_cls:
        # 若记录不存在，返回删除失败
        return False

      # 从会话中删除记录
      await session.delete(delete_cls)
      # 提交事务，执行删除
      await session.commit()

      if after_delete is not None:
        await after_delete(delete_cls, row_dict, session)

      # 返回删除成功
      return True

    # 批量删除工具方法：批量删除记录
    async def batch_delete(self, session: AsyncSessionDep, row_dict_list: List[dict] = Body(..., description=f"批量删除的数据数组，字段参考{Cls.__name__}")):

      if before_batch_delete is not None:
        await before_batch_delete(row_dict_list, session)

      # 若待删除列表为空，返回失败
      if not row_dict_list:
        return False
      # 提取所有待删除记录的id
      row_id_list = [row_dict.get("id") for row_dict in row_dict_list]

      # 根据id查询所有待删除的记录
      delete_cls_list = (await session.exec(self.select_cls().where(Cls.id.in_(row_id_list)))).all()
      # 若查询到的记录数量与待删除数量不一致，说明部分id不存在
      if len(delete_cls_list) != len(row_id_list):
        # 抛出异常并提示不存在的id
        raise HTTPException(status_code=500, detail="Delete row not found：" + json.dumps(row_id_list, ensure_ascii=False))

      # 异步批量删除所有记录（使用gather并发执行删除操作）
      await asyncio.gather(*[asyncio.create_task(session.delete(delete_cls)) for delete_cls in delete_cls_list])

      # 提交事务，执行删除
      await session.commit()

      if after_batch_delete is not None:
        await after_batch_delete(delete_cls_list, row_dict_list, session)

      # 返回删除成功
      return True

  # 创建并返回ModelService实例
  return ModelService()
