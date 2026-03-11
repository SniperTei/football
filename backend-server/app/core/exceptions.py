"""
全局异常处理
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.service.exceptions import BusinessException, NotFoundException, DuplicateException, ValidationException


async def business_exception_handler(request: Request, exc: BusinessException):
    """业务异常处理器"""
    http_status = status.HTTP_400_BAD_REQUEST
    if isinstance(exc, NotFoundException):
        http_status = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, DuplicateException):
        http_status = status.HTTP_409_CONFLICT

    return JSONResponse(
        status_code=http_status,
        content={
            "code": http_status,
            "msg": exc.message,
            "data": None
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    # 开发环境打印详细错误
    import traceback
    print(f"Error: {str(exc)}")
    print(traceback.format_exc())

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "msg": "服务器内部错误",
            "data": None
        }
    )
