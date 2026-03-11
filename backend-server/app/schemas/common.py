from typing import Optional, Any, Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应格式"""
    code: int = Field(200, description="状态码")
    msg: str = Field("success", description="消息")
    data: Optional[T] = Field(None, description="数据")


class PageData(BaseModel, Generic[T]):
    """分页数据"""
    list: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(0, description="总数")
    page: int = Field(1, description="当前页")
    page_size: int = Field(10, description="每页数量")


# 响应辅助函数
def success(data: Any = None, msg: str = "success", code: int = 200) -> ApiResponse:
    """成功响应"""
    return ApiResponse(code=code, msg=msg, data=data)


def error(msg: str = "error", code: int = 500, data: Any = None) -> ApiResponse:
    """错误响应"""
    return ApiResponse(code=code, msg=msg, data=data)
