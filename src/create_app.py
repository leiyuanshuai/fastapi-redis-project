import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html, get_redoc_html
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from src.config.env import settings,env
from src.middlewares.app_middlewares import add_app_middlewares
from src.utils.db_utils import check_database_connection
# from src.utils.milvus_utils import milvus_service
from src.utils.postgres_checkpointer import check_postgres_connection, close_postgres_connection
from src.redis_client import redis_client
async def check_redis_connection():
    """检查Redis连接状态的依赖项"""
    if not await redis_client.async_ping():
        raise HTTPException(status_code=503, detail="Redis service is unavailable")
    return True
def create_app():
  @asynccontextmanager
  async def lifespan(app: FastAPI):
    print("lifespan：启动阶段")
    async_results = await asyncio.gather(
      asyncio.create_task(check_database_connection()),
      asyncio.create_task(check_postgres_connection()),
      asyncio.create_task(check_redis_connection()),
      # asyncio.create_task(milvus_service.check_milvus_connection()),
    )
    async_engine = async_results[0]
    yield
    print("lifespan：销毁阶段")
    await async_engine.dispose()
    await redis_client.async_close()
    await close_postgres_connection()

  app = FastAPI(
    docs_url=None,  # 禁用默认 Swagger
    redoc_url=None,  # 禁用默认 ReDoc
    title='Fastapi App',
    version=env.app_version,
    description="fastapi redis mysql langraph langchain llama-index milvus pyjwt pyjwt python dify sqlmodel pyjwt pydantic",
    lifespan=lifespan,
  )

  app.mount("/static", StaticFiles(directory="static"), name="static")

  # 自定义 Swagger 页面（使用本地资源）
  @app.get("/docs", include_in_schema=False)
  async def custom_swagger_ui():
    return get_swagger_ui_html(
      openapi_url=app.openapi_url,
      title=app.title + " - Swagger UI",
      oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
      swagger_js_url="/static/swagger-ui-bundle.min.js",
      swagger_css_url="/static/swagger-ui.min.css",
    )

  @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
  async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

  @app.get("/redoc", include_in_schema=False)
  async def redoc_html():
    return get_redoc_html(
      openapi_url=app.openapi_url,
      title=app.title + " - ReDoc",
      redoc_js_url="/static/redoc.standalone.js",
    )

  add_app_middlewares(app)

  app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
  )

  # @app.get("/")
  # async def redirect_root_to_docs():
  #   return RedirectResponse("/docs")

  return app
