from typing import Optional

from pydantic import computed_field
from sqlalchemy.orm import selectinload
from sqlmodel import Field, Relationship, select

from src.model.BasicModel import BasicModel
from src.utils.create_module_service import create_model_service


class OrgModel(BasicModel, table=True):
  __tablename__ = "pl_org"

  name: str = Field(default=None, description="组织名称")
  code: str = Field(default=None, description="组织编码")
  # parent_code: str = Field(default=None, description="父组织编码")
  remarks: str = Field(default=None, description="备注信息")

  parent_code: str = Field(
    default=None,
    description="父组织编码",
    foreign_key="pl_org.code",  # 添加外键约束
    nullable=True
  )

  parent: Optional["OrgModel"] = Relationship(
    sa_relationship_kwargs={
      # 指定外键字段
      # "OrgModel.parent_code" 表示使用 OrgModel 类的 parent_code 字段作为外键
      # 这个字段引用了另一个 OrgModel 实例（父组织）
      "foreign_keys": "OrgModel.parent_code",
      # remote_side: 指定关系的远程端（被引用的一侧）
      # "OrgModel.code" 表示关系的另一端是 OrgModel 的 code 字段
      # 这是自引用关系中被引用的字段
      "remote_side": "OrgModel.code",
      # 指定关系是否返回列表
      # False 表示这是一个一对多关系中的"一"端，返回单个对象而不是列表
      # 一个组织只有一个父组织，所以设为 False
      "uselist": False
    }
  )

  @computed_field
  @property
  def parent_name(self) -> Optional[str]:
    try:
      return self.parent.name if self.parent else None
    except:
      return None

  @parent_name.setter
  def parent_name(self, value: Optional[str]) -> None:
    pass


OrgService = create_model_service(
  Cls=OrgModel,
  custom_query=lambda: select(OrgModel).options(selectinload(OrgModel.parent)),
)
