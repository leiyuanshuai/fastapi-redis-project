from typing import Optional

from pydantic import computed_field
from sqlalchemy.orm import selectinload
from sqlmodel import Field, Relationship, select

from src.model.BasicModel import BasicModel
from src.model.OrgModel import OrgModel
from src.utils.create_module_service import create_model_service


class PosModel(BasicModel, table=True):
  __tablename__ = "pl_pos"

  name: str = Field(default=None, description="职位名称")
  code: str = Field(default=None, description="职位编码")
  # parent_code: str = Field(default=None, description="父职位编码")
  # organization_code: str = Field(default=None, description="所属组织编码")
  remarks: str = Field(default=None, description="备注信息")
  pos_level: int = Field(default=None, description="职位层级")

  # /*---------------------------------------parent_code-------------------------------------------*/

  parent_code: str = Field(
    default=None,
    description="父职位编码",
    foreign_key="pl_pos.code",  # 添加外键约束
    nullable=True
  )

  parent: Optional["PosModel"] = Relationship(
    sa_relationship_kwargs={
      "foreign_keys": "PosModel.parent_code",
      "remote_side": "PosModel.code",
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

  # /*---------------------------------------organization_code-------------------------------------------*/

  organization_code: str = Field(
    default=None,
    description="所属组织编码",
    foreign_key="pl_org.code",  # 添加外键约束
    nullable=True
  )

  organization: Optional["OrgModel"] = Relationship(
    sa_relationship_kwargs={
      "foreign_keys": "PosModel.organization_code",
      "remote_side": "OrgModel.code",
      "uselist": False
    }
  )

  @computed_field
  @property
  def org_name(self) -> Optional[str]:
    try:
      return self.organization.name if self.organization else None
    except:
      return None

  @org_name.setter
  def org_name(self, value: Optional[str]) -> None:
    pass


PosService = create_model_service(
  Cls=PosModel,
  custom_query=(lambda: select(PosModel)
                .options(selectinload(PosModel.parent))
                .options(selectinload(PosModel.organization))),
)
