from pydantic import BaseModel, Field


class PageQueryParams(BaseModel):
  page: int = Field(default=0, description="分页查询的页数")
  page_size: int = Field(default=5, description="分页查询每页条数")

  all: bool = Field(default=False, description="是否查询所有数据，也就是不分页")
  count: bool = Field(default=True, description="是否查询总数")

  sort_field: str = Field(default="created_at", description="排序字段")
  sort_desc: str = Field(default="desc", description="排序方式")

  filters: dict = Field(default=None, description="筛选参数")
