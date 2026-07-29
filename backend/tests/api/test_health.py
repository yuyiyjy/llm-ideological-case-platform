"""健康检查和接口文档端点测试。"""

import httpx
import pytest

pytestmark = pytest.mark.asyncio


async def test_health_check_returns_ok(client: httpx.AsyncClient) -> None:
    """健康检查应返回稳定且最小的成功响应。"""
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_openapi_contains_health_path(client: httpx.AsyncClient) -> None:
    """OpenAPI 文档应包含对外公开的健康检查路径。"""
    response = await client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/health" in response.json()["paths"]


async def test_swagger_ui_is_available(client: httpx.AsyncClient) -> None:
    """Swagger UI 应由 FastAPI 正常提供。"""
    response = await client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
