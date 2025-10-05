from datetime import timedelta, datetime, timezone
from typing import TypedDict, Literal, TypeAlias

import jwt
from passlib.context import CryptContext

from src.config.env import env

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# token的类型，access用于接口认证，refresh用于刷新access token，verify用于激活用户账号
AccessTokenType: TypeAlias = Literal["access", "refresh", "verify"]


class TokenInfo(TypedDict):
  # 用户名信息
  username: str
  # token过期时间
  exp: datetime
  type: AccessTokenType


class CryptUtils:
  @staticmethod
  def get_password_hash(password: str):
    return pwd_context.hash(password)

  @staticmethod
  def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

  @staticmethod
  def create_token(
    username: str,
    type: AccessTokenType,
    expires_delta: timedelta
  ):
    data: TokenInfo = {
      "username": username,
      "type": type,
      "exp": datetime.now(timezone.utc) + expires_delta
    }
    return jwt.encode(data, env.jwt_secret_key, env.jwt_algorithm)

  @staticmethod
  def get_token_info(token: str) -> TokenInfo:
    data = jwt.decode(token, env.jwt_secret_key, algorithms=[env.jwt_algorithm])
    return data
