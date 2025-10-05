from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlmodel import select
from starlette import status

from src.config.env import env
from src.model.UserModel import RegistryUser, UserModel, UserValidate, PublicUser, UserService
from src.utils.CrpyUtils import CryptUtils, TokenInfo
from src.utils.db_utils import AsyncSessionDep
from src.utils.next_id import next_id


# 添加用户相关的端点接口
def add_user_route(app: FastAPI):
  UserService.add_route(app=app, path="/user")

  # 用户注册接口
  @app.post("/registry")
  async def _registry(registry_user: RegistryUser, session: AsyncSessionDep):

    # /*---------------------------------------检查用户名是否已经注册-------------------------------------------*/
    query = select(UserModel).where(UserModel.username == registry_user.username)
    result = await session.execute(query)
    item_cls = result.scalars().first()

    if item_cls:
      return {"result": None, "error": f"用户名：{registry_user.username} 已经存在"}

    # /*---------------------------------------检查邮箱是否已经注册-------------------------------------------*/

    query = select(UserModel).where(UserModel.email == registry_user.email)
    result = await session.execute(query)
    item_cls = result.scalars().first()

    if item_cls:
      return {"result": None, "error": f"邮箱：{registry_user.email} 已经注册"}

    # /*---------------------------------------开始注册流程-------------------------------------------*/

    hash_password = CryptUtils.get_password_hash(registry_user.password)
    user = UserModel(
      username=registry_user.username,
      email=registry_user.email,
      full_name=registry_user.full_name,
      hash_password=hash_password,
      valid=UserValidate.N,
      pos_code=registry_user.pos_code,
    )
    user.id = await next_id()
    session.add(user)
    await session.commit()
    await session.refresh(user)

    public_user = PublicUser(**user.model_dump())

    verify_user_token = CryptUtils.create_token(
      username=public_user.username,
      type="verify",
      expires_delta=timedelta(days=365 * 3),
    )
    active_url = f"{env.server_domain}:{env.server_port}/verify?token={verify_user_token}"

    return {
      "result": public_user,
      "active_url": active_url
    }

  # 验证用户账号接口
  @app.get("/verify")
  async def _verify(token: str, session: AsyncSessionDep):
    token_info = CryptUtils.get_token_info(token)
    username = token_info.get('username')

    if not username or token_info.get('type') != 'verify':
      return {"result": None, "error": "token无效或者已经过期"}

    query = select(UserModel).where(UserModel.username == username)
    result = await session.execute(query)
    item_cls: UserModel | None = result.scalars().first()

    if not item_cls:
      return {"result": None, "error": f"用户 {username} 不存在"}

    item_cls.valid = UserValidate.Y
    session.add(item_cls)
    await session.commit()
    await session.refresh(item_cls)

    public_user = PublicUser(**item_cls.model_dump())

    return {
      "result": public_user,
      "message": f"用户 {username} 激活成功"
    }

  # 登录接口
  @app.post("/login")
  @app.post("/token")
  async def _token(session: AsyncSessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    print("login", form_data)
    user = await authenticate_user(session, form_data.username, form_data.password)

    if not user:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="用户名或者密码不正确",
        headers={"WWW-Authenticate": "Bearer"},
      )

    access_token = CryptUtils.create_token(
      username=user.username,
      type="access",
      expires_delta=timedelta(seconds=env.jwt_access_token_expire_seconds),
    )
    access_expires = env.jwt_access_token_expire_seconds * 1000

    refresh_token = CryptUtils.create_token(
      username=user.username,
      type="refresh",
      expires_delta=timedelta(minutes=env.jwt_refresh_token_expire_seconds),
    )
    refresh_expires = env.jwt_refresh_token_expire_seconds * 1000

    return {
      "result": user,
      "access_token": access_token,
      "access_expires": access_expires,

      "refresh_token": refresh_token,
      "refresh_expires": refresh_expires,
    }

  @app.post("/refresh")
  async def refresh_token(data: dict):
    refresh_token: TokenInfo = data.get('refresh_token')
    token_info = CryptUtils.get_token_info(refresh_token)
    if token_info.get('type') != 'refresh':
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token类型不正确",
      )
    access_token = CryptUtils.create_token(
      username=token_info.get("username"),
      type="access",
      expires_delta=timedelta(minutes=env.jwt_access_token_expire_seconds),
    )
    access_expires = env.jwt_access_token_expire_seconds * 1000
    return {
      "access_token": access_token,
      "access_expires": access_expires,
    }

  # 获取用户信息接口
  @app.get("/users/me")
  async def _me(session: AsyncSessionDep, current_user: PublicUser = Depends(get_current_user)):
    return await UserService.query_item(
      session=session,
      row_dict={"id": current_user.id},
    )

  # 订单查询接口
  @app.post("/order")
  async def _query_order(product_name: str, current_user: PublicUser = Depends(get_current_user)):
    return [product_name]


# 用户登录信息验证处理,验证账号密码通过会返回用户信息，否则返回None
async def authenticate_user(session: AsyncSessionDep, username: str, password: str):
  query = select(UserModel).where(UserModel.username == username)
  result = await session.execute(query)
  item_cls: UserModel | None = result.scalars().first()
  if not item_cls:
    return None

  if item_cls.valid != UserValidate.Y:
    return None

  if not CryptUtils.verify_password(password, item_cls.hash_password):
    return None

  public_user = PublicUser(**item_cls.model_dump())

  return public_user


# 用于注入token字符串
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 当token失效或者不存在时抛出的异常
unauthorized_exception = HTTPException(
  status_code=status.HTTP_401_UNAUTHORIZED,
  detail="The token is invalid or had expired",
  headers={"WWW-Authenticate": "Bearer"},
)


# 获取当前用户信息，通过注入的token来获取当前用户信息，如果token有效则返回用户信息，无效则抛出异常
async def get_current_user(session: AsyncSessionDep, token: str = Depends(oauth2_scheme)):
  try:
    token_info: TokenInfo = CryptUtils.get_token_info(token)
    username = token_info.get('username')
    if not username or token_info.get('type') != 'access':
      raise unauthorized_exception
  except InvalidTokenError:
    raise unauthorized_exception

  user_model = await get_user_by_username(username, session)
  if not user_model:
    raise unauthorized_exception

  return PublicUser(**user_model.model_dump())


# 根据用户名获取用户信息
async def get_user_by_username(username: str, session: AsyncSessionDep):
  query = (
    select(UserModel)
    .where(UserModel.username == username)
    .where(UserModel.valid == UserValidate.Y)
  )
  result = await session.execute(query)
  item_cls: UserModel | None = result.scalars().first()
  return item_cls
