"""MaxKB 适配层模式与生命周期测试。"""

from typing import Any

import httpx
import pytest
from fastapi import FastAPI, Request
from pydantic import SecretStr

from app.core.config import Settings
from app.factory import create_app
from app.integrations.maxkb.dependencies import get_maxkb_adapter
from app.integrations.maxkb.factory import create_maxkb_adapter
from app.integrations.maxkb.http import HttpMaxKBAdapter
from app.integrations.maxkb.mock import MockMaxKBAdapter

pytestmark = pytest.mark.asyncio


async def test_mock_factory_returns_network_free_adapter(
    test_settings: Settings,
) -> None:
    """Mock 模式应选择不持有 HTTP 客户端的实现。"""
    adapter = create_maxkb_adapter(test_settings)

    assert isinstance(adapter, MockMaxKBAdapter)
    assert adapter.mode == "mock"
    assert adapter.is_closed is False

    await adapter.aclose()
    assert adapter.is_closed is True


async def test_http_adapter_construction_sends_no_request() -> None:
    """创建和关闭 HTTP 适配器期间不得发送 MaxKB 请求。"""
    requests: list[httpx.Request] = []

    async def handle_request(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    api_key = SecretStr("synthetic-maxkb-key-never-sent")
    adapter = HttpMaxKBAdapter(
        base_url="http://127.0.0.1:1",
        api_key=api_key,
        timeout_seconds=0.1,
        transport=httpx.MockTransport(handle_request),
    )

    assert requests == []
    assert api_key.get_secret_value() not in repr(adapter)
    assert "127.0.0.1" not in repr(adapter)

    await adapter.aclose()
    assert adapter.is_closed is True
    assert requests == []


async def test_http_mode_health_does_not_require_maxkb(
    settings_values: dict[str, Any],
) -> None:
    """即使配置的 MaxKB 地址不可达，非 AI 健康检查仍应正常响应。"""
    values = dict(settings_values)
    values.update(
        maxkb_mock_enabled=False,
        maxkb_base_url="http://127.0.0.1:1",
        maxkb_api_key="synthetic-maxkb-key-never-sent",
    )
    settings = Settings.model_validate(values)
    app = create_app(settings)
    adapter = app.state.maxkb_adapter

    assert isinstance(adapter, HttpMaxKBAdapter)

    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
        ) as client:
            response = await client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        assert adapter.is_closed is False

    assert adapter.is_closed is True


async def test_request_dependency_returns_application_adapter(
    app: FastAPI,
) -> None:
    """请求依赖应返回应用工厂创建的同一个适配器实例。"""
    request = Request({"type": "http", "app": app})

    assert get_maxkb_adapter(request) is app.state.maxkb_adapter
