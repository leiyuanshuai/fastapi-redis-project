from datetime import datetime, timezone, timedelta, date

from pydantic import model_validator
from sqlmodel import SQLModel, Field

# 定义北京时区（UTC+8）
beijing_timezone = timezone(timedelta(hours=8))

# 定义获取当前北京时区时间的匿名函数，用于默认值生成
current_datetime = lambda: datetime.now(beijing_timezone)


# 定义基础模型类，所有其他模型类的父类，包含通用字段和配置
class BasicModel(SQLModel):
  # 唯一标识字段，主键，默认为None（通常由系统生成），描述为“唯一标识，编号”
  id: str = Field(default=None, primary_key=True, description="唯一标识，编号")
  # 创建时间字段，默认值为当前北京时区时间，描述为“创建时间”
  created_at: datetime = Field(default_factory=current_datetime, description="创建时间")
  # 更新时间字段，默认值为当前北京时区时间，描述为“更新时间”
  updated_at: datetime = Field(default_factory=current_datetime, description="更新时间")
  # 创建人ID字段，默认为None，描述为“创建人id”
  created_by: str | None = Field(default=None, description="创建人id")
  # 更新人ID字段，默认为None，描述为“更新人id”
  updated_by: str | None = Field(default=None, description="更新人id")

  # 模型配置类，用于设置JSON序列化等配置
  class Config:
    # 定义datetime和date类型的JSON编码器，将其格式化为指定字符串
    json_encoders = {
      # 若为datetime类型，格式化为“年-月-日 时:分:秒”，若为None则保持None
      datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S") if dt is not None else None,
      # 若为date类型，格式化为“年-月-日”，若为None则保持None
      date: lambda dt: dt.strftime("%Y-%m-%d") if dt is not None else None
    }

  # 定义模型验证器，在数据解析前（mode='before'）执行，用于处理字符串格式的日期时间
  @model_validator(mode='before')
  def parse_string_datetimes(cls, data: dict | None) -> dict:
    if not data:
      return
      # 处理datetime类型字段：将字符串格式的日期时间转换为datetime对象
    datetime_fields = {
      k: datetime.strptime(v, "%Y-%m-%d %H:%M:%S")  # 使用strptime解析字符串为datetime
      for k, v in data.items()  # 遍历输入数据的键值对
      if isinstance(v, str)  # 只处理值为字符串的项
         and k in cls.model_fields  # 键必须是模型中定义的字段
         and cls.model_fields[k].annotation is datetime  # 字段的注解类型是datetime
    }
    # 处理date类型字段：将字符串格式的日期转换为date对象（通过datetime解析后取date部分）
    date_fields = {
      k: datetime.strptime(v, "%Y-%m-%d").date()  # 使用strptime解析字符串为datetime后取date
      for k, v in data.items()  # 遍历输入数据的键值对
      if isinstance(v, str)  # 只处理值为字符串的项
         and k in cls.model_fields  # 键必须是模型中定义的字段
         and cls.model_fields[k].annotation is date  # 字段的注解类型是date
    }
    # 打印转换后的datetime字段，用于调试
    # print("datetime_fields", datetime_fields)
    # 合并原始数据、转换后的datetime字段和date字段，转换后的字段会覆盖原始数据中的对应键
    result = {**data, **datetime_fields, **date_fields}
    # 打印合并后的结果，用于调试
    # print("result", result)
    # 返回处理后的数据字典
    return result
