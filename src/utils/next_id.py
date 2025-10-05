from fastapi import FastAPI
from sqlalchemy import text

from src.utils.db_utils import async_session


async def next_id(num: int = 1):
  async with async_session() as session:
    sql_string = "select " + ",".join([f"uuid() as _{index}" for index in range(num)])
    print(sql_string)
    result = await session.execute(text(sql_string))
    val = result.first()
    print(val)
    arr = list(val or [])
    return arr[0] if num == 1 else arr


def add_next_id_route(app: FastAPI):
  @app.get("/next_id")
  async def _next_id(num: int = 1):
    return {
      "data": await next_id(num),
    }
