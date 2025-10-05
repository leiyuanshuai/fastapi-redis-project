from enum import Enum
from typing import Optional

from pydantic import computed_field
from sqlalchemy.orm import selectinload
from sqlmodel import Field, Relationship, select

from src.model.BasicModel import BasicModel
from src.model.PosModel import PosModel
from src.utils.create_module_service import create_model_service


class UserValidate(str, Enum):
  Y = 'Y'
  N = 'N'


# 公共的，也是最后返回给前端的一个用户信息数据类型
class PublicUser(BasicModel):
  username: str = Field(..., description="用户名")
  email: str = Field(..., description="邮箱")
  full_name: str = Field(..., description="用户全名")
  valid: UserValidate = Field(default=UserValidate.N, description="用户账号是否已经激活")


# 注册的时候，客户端传入的用户信息，需要包含这个明文密码字段
class RegistryUser(PublicUser):
  password: str
  pos_code: str

# 对pl_user表进行增删改查时的这个model类
class UserModel(PublicUser, table=True):
  __tablename__ = "pl_user"
  hash_password: str
  pos_code: str


# 对pl_user表进行增删改查时的这个model类
class UserServiceModel(PublicUser, table=True):
  __tablename__ = "pl_user"
  # 允许重新定义已存在的表：如果数据库表已经被其他类映射，允许当前类也映射到同一张表
  __table_args__ = {'extend_existing': True}
  # 在SQLModel / SQLAlchemy中，定义外键有两种方式：
  # 1. 字段级别定义（显式外键约束） 数据库级别的真实定义
  pos_code: str = Field(
    default=None,
    description="用户职位编码",
    foreign_key="pl_pos.code",  # 添加外键约束
    nullable=True
  )
  # 2. 关系级别定义（仅 ORM 关系）
  position: Optional["PosModel"] = Relationship(
    sa_relationship_kwargs={
      "foreign_keys": "UserServiceModel.pos_code",
      "remote_side": "PosModel.code",
      "uselist": False
    }
  )

  @computed_field
  @property
  def pos(self) -> Optional[PosModel]:
    try:
      return self.position
    except:
      return None

  @pos.setter
  def pos(self, value: Optional[PosModel]) -> None:
    pass

  @computed_field
  @property
  def pos_name(self) -> Optional[str]:
    try:
      return self.position.name if self.position else None
    except:
      return None

  @pos_name.setter
  def pos_name(self, value: Optional[str]) -> None:
    pass

  @computed_field
  @property
  def org_name(self) -> Optional[str]:
    try:
      organization = self.position.organization if self.position else None
      return organization.name if organization else None
    except:
      return None

  @org_name.setter
  def org_name(self, value: Optional[str]) -> None:
    pass


UserService = create_model_service(
  Cls=UserServiceModel,
  custom_query=(lambda: select(UserServiceModel)
                .options(
    selectinload(UserServiceModel.position).
    selectinload(PosModel.organization)
  ))
)
