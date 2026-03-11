from typing import Any, Optional, List
from app.schemas.common import ApiResponse


class ResponseHelper:
    """响应工具类"""

    @staticmethod
    def success(data: Any = None, msg: str = "success", code: int = 200) -> dict:
        """
        成功响应

        Args:
            data: 返回数据
            msg: 消息
            code: 状态码

        Returns:
            标准响应格式
        """
        return {
            "code": code,
            "msg": msg,
            "data": data
        }

    @staticmethod
    def success_list(list_data: List[Any], total: Optional[int] = None, msg: str = "success") -> dict:
        """
        列表数据成功响应

        Args:
            list_data: 列表数据
            total: 总数（可选）
            msg: 消息

        Returns:
            标准响应格式，data 中包含 list 字段
        """
        data = {"list": list_data}
        if total is not None:
            data["total"] = total

        return {
            "code": 200,
            "msg": msg,
            "data": data
        }

    @staticmethod
    def error(msg: str = "error", code: int = 500, data: Any = None) -> dict:
        """
        错误响应

        Args:
            msg: 错误消息
            code: 错误码
            data: 错误数据

        Returns:
            标准错误响应格式
        """
        return {
            "code": code,
            "msg": msg,
            "data": data
        }

    @staticmethod
    def validation_error(msg: str = "参数验证失败") -> dict:
        """参数验证错误"""
        return ResponseHelper.error(msg=msg, code=400)

    @staticmethod
    def not_found(resource: str = "资源") -> dict:
        """资源未找到"""
        return ResponseHelper.error(msg=f"{resource}不存在", code=404)

    @staticmethod
    def unauthorized(msg: str = "未授权") -> dict:
        """未授权"""
        return ResponseHelper.error(msg=msg, code=401)

    @staticmethod
    def forbidden(msg: str = "无权限") -> dict:
        """无权限"""
        return ResponseHelper.error(msg=msg, code=403)
