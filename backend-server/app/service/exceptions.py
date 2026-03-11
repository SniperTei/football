"""
自定义业务异常
"""
from typing import Optional


class BusinessException(Exception):
    """业务异常基类"""

    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundException(BusinessException):
    """资源不存在异常"""

    def __init__(self, resource: str, id: int = None):
        message = f"{resource}不存在"
        if id is not None:
            message = f"{resource} ID {id} 不存在"
        super().__init__(message, "NOT_FOUND")


class DuplicateException(BusinessException):
    """重复数据异常"""

    def __init__(self, resource: str, field: str, value: str):
        super().__init__(f"{resource}的{field} '{value}' 已存在", "DUPLICATE")


class ValidationException(BusinessException):
    """验证异常"""

    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")
