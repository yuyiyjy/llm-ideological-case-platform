"""统一异常类型与响应处理。"""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException

logger = logging.getLogger(__name__)


class ErrorDetail(BaseModel):
    """统一错误详情。"""

    code: str = Field(description="稳定的错误代码")
    message: str = Field(description="可安全展示的错误提示")
    details: list[dict[str, Any]] | None = Field(
        default=None,
        description="不包含敏感输入值的补充详情",
    )


class ErrorResponse(BaseModel):
    """统一错误响应。"""

    error: ErrorDetail


DEFAULT_ERROR_RESPONSES: dict[int, dict[str, Any]] = {
    422: {
        "model": ErrorResponse,
        "description": "请求参数校验失败",
    },
    500: {
        "model": ErrorResponse,
        "description": "服务器内部错误",
    },
}


class ApplicationError(Exception):
    """可安全返回给客户端的应用异常。"""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = 400,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


def build_error_content(
    *,
    code: str,
    message: str,
    details: list[dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    """构造统一错误响应。"""
    response = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
            details=details,
        )
    )
    return response.model_dump(mode="json", exclude_none=True)


async def handle_application_error(
    request: Request,
    exception: ApplicationError,
) -> JSONResponse:
    """处理可预期的应用异常。"""
    logger.warning(
        "应用异常 method=%s path=%s code=%s",
        request.method,
        request.url.path,
        exception.code,
    )
    return JSONResponse(
        status_code=exception.status_code,
        content=build_error_content(
            code=exception.code,
            message=exception.message,
            details=exception.details,
        ),
    )


async def handle_http_exception(
    request: Request,
    exception: HTTPException,
) -> JSONResponse:
    """将 FastAPI HTTP 异常转换为统一响应。"""
    message = (
        exception.detail
        if isinstance(exception.detail, str)
        else "请求处理失败"
    )
    logger.info(
        "HTTP 异常 method=%s path=%s status_code=%s",
        request.method,
        request.url.path,
        exception.status_code,
    )
    return JSONResponse(
        status_code=exception.status_code,
        content=build_error_content(
            code=f"http_{exception.status_code}",
            message=message,
        ),
        headers=exception.headers,
    )


async def handle_request_validation_error(
    request: Request,
    exception: RequestValidationError,
) -> JSONResponse:
    """返回不包含原始输入值的参数校验详情。"""
    details = [
        {
            "location": [str(item) for item in error["loc"]],
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exception.errors()
    ]
    logger.info(
        "请求参数校验失败 method=%s path=%s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=422,
        content=build_error_content(
            code="request_validation_error",
            message="请求参数校验失败",
            details=details,
        ),
    )


async def handle_unexpected_error(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    """记录未知异常并返回不含内部细节的响应。"""
    logger.exception(
        "未处理异常 method=%s path=%s",
        request.method,
        request.url.path,
        exc_info=exception,
    )
    return JSONResponse(
        status_code=500,
        content=build_error_content(
            code="internal_server_error",
            message="服务暂时不可用",
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器。"""
    app.add_exception_handler(ApplicationError, handle_application_error)
    app.add_exception_handler(HTTPException, handle_http_exception)
    app.add_exception_handler(
        RequestValidationError,
        handle_request_validation_error,
    )
    app.add_exception_handler(Exception, handle_unexpected_error)
