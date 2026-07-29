"""统一异常响应测试。"""

import httpx
import pytest
from fastapi import FastAPI

pytestmark = pytest.mark.asyncio


async def test_not_found_uses_unified_error_shape(
    client: httpx.AsyncClient,
) -> None:
    """不存在的路径也应使用项目统一错误结构。"""
    response = await client.get("/path-that-does-not-exist")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "http_404"
    assert isinstance(response.json()["error"]["message"], str)


async def test_validation_error_does_not_echo_invalid_input(
    app: FastAPI,
    client: httpx.AsyncClient,
) -> None:
    """参数校验详情不得回显请求者提交的原始输入。"""

    @app.get("/_test/validation")
    async def validation_endpoint(value: int) -> dict[str, int]:
        return {"value": value}

    response = await client.get(
        "/_test/validation",
        params={"value": "private-invalid-input"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "request_validation_error"
    assert "private-invalid-input" not in response.text


async def test_unexpected_error_hides_internal_details(
    app: FastAPI,
    client: httpx.AsyncClient,
) -> None:
    """未知异常不得向客户端暴露内部错误文本。"""

    @app.get("/_test/unexpected-error")
    async def unexpected_error_endpoint() -> None:
        raise RuntimeError("private-internal-error")

    response = await client.get("/_test/unexpected-error")

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "internal_server_error",
            "message": "服务暂时不可用",
        }
    }
    assert "private-internal-error" not in response.text
