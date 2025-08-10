from fastapi import Request
from fastapi.responses import JSONResponse

from interfaces.http.base_response import ApiResponse


class BizException(Exception):
    """基础业务异常"""
    def __init__(self, code: int = 400, message: str = "业务异常"):
        self.code = code
        self.message = message

async def biz_exception_handler(request: Request, exc: BizException):  # noqa: ARG001
    return JSONResponse(
        status_code=200,  # 不抛 HTTP 错
        content=ApiResponse.error_response(
            message=exc.message,
            code=exc.code
        ).model_dump()
    )

async def global_exception_handler(request: Request, exc: Exception): # noqa: ARG001
    return JSONResponse(
        status_code=200,  # 不抛 HTTP 错
        content=ApiResponse.error_response(
            message=exc,
            code=500,
            data=exc
        ).model_dump()
    )
