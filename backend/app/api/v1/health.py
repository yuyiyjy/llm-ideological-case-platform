"""健康检查接口。"""

from typing import Literal

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

router = APIRouter()


class HealthResponse(BaseModel):
    """健康检查响应。"""

    status: Literal["ok"] = Field(description="服务状态", examples=["ok"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    tags=["系统"],
    summary="检查服务健康状态",
    description="检查业务后端进程是否正常响应，不检查 PostgreSQL 或 MaxKB。",
    response_description="服务正常响应",
)
async def health_check() -> HealthResponse:
    """返回业务后端的存活状态。"""
    return HealthResponse(status="ok")
