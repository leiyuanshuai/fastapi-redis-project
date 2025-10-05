import time
import traceback

from fastapi import FastAPI, HTTPException
from passlib.exc import InvalidTokenError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.config.env import env
from src.controller.add_user_route import unauthorized_exception, get_current_user
from src.utils.db_utils import async_session


def add_app_middlewares(app: FastAPI):
  @app.middleware("http")
  async def add_process_time_header(request: Request, call_next):
    print("time start")
    start_time = time.time()
    response = await call_next(request)
    process_time = f"time:{time.time() - start_time}s"
    response.headers['x-Process-Time'] = process_time
    print("time end")
    return response

  # @app.middleware("http")
  # async def middleware2(request: Request, call_next):
  #   print("middleware2 start")
  #   response = await call_next(request)
  #   print("middleware2 end")
  #   return response

  @app.middleware("http")
  async def add_oauth_middleware(request: Request, call_next):
    if not env.jwt_global_enable or request.method == "OPTIONS":
      # 没有开启全局的接口认证功能
      request.state.user = None
      request.state.token = None
      return await call_next(request)

    # 判断接口是否为认证白名单中的接口
    if request.url.path in env.jwt_white_list:
      return await call_next(request)

    token: str | None = None
    oauth_header = request.headers.get("Authorization")
    if oauth_header and oauth_header.startswith("Bearer "):
      token = oauth_header.split(" ")[1].strip()

    if not token:
      raise unauthorized_exception

    async with async_session() as session:
      try:
        public_user = await get_current_user(session, token)
        request.state.user = public_user
        request.state.token = token
      except InvalidTokenError:
        raise unauthorized_exception

    response = await call_next(request)
    return response

  @app.middleware("http")
  async def catch_authorized(request: Request, call_next):
    try:
      response = await call_next(request)
    except HTTPException as e:
      print(e)
      if e.status_code == status.HTTP_401_UNAUTHORIZED:
        return JSONResponse(content={"message": e.detail}, status_code=status.HTTP_401_UNAUTHORIZED)
      else:
        return JSONResponse(content={"message": e.detail}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
      print(e)
      traceback.print_exc()
      return JSONResponse(content={"message": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
