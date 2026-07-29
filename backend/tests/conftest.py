"""Pytest 公共配置与隔离测试夹具。"""

from collections.abc import AsyncIterator
from typing import Any

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from app.core.config import Settings
from app.factory import create_app


def pytest_addoption(parser: pytest.Parser) -> None:
    """注册需要开发者主动选择的本地集成测试开关。"""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="运行需要本地 PostgreSQL 等外部服务的集成测试",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """默认跳过依赖外部服务的测试，保持普通测试可离线重复执行。"""
    if config.getoption("--run-integration"):
        return

    skip_integration = pytest.mark.skip(
        reason="需要使用 --run-integration 显式启用本地集成测试"
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


@pytest.fixture
def settings_values() -> dict[str, Any]:
    """返回完整的合成配置，不读取或复用根目录 .env 的真实值。"""
    return {
        "app_name": "test-backend",
        "app_env": "testing",
        "app_host": "127.0.0.1",
        "app_port": 8000,
        "app_debug": False,
        "api_v1_prefix": "/api/v1",
        "log_level": "CRITICAL",
        # 端口 1 不提供 PostgreSQL 服务，用于证明普通测试不会建立数据库连接。
        "database_url": (
            "postgresql+asyncpg://synthetic_user:synthetic_password"
            "@127.0.0.1:1/synthetic_database"
        ),
        "cors_origins": "http://testserver",
        "secret_key": "synthetic-secret-key-for-tests-only-1234567890",
        "access_token_expire_minutes": 60,
        "maxkb_base_url": None,
        "maxkb_api_key": None,
        "maxkb_timeout_seconds": 0.1,
        "maxkb_mock_enabled": True,
        "maxkb_qa_application_id": None,
        "maxkb_generation_application_id": None,
        "maxkb_evaluation_application_id": None,
    }


@pytest.fixture
def test_settings(settings_values: dict[str, Any]) -> Settings:
    """从合成字典直接创建测试配置，绕过 BaseSettings 环境变量来源。"""
    return Settings.model_validate(settings_values)


@pytest_asyncio.fixture
async def app(test_settings: Settings) -> AsyncIterator[FastAPI]:
    """创建并完整进入、退出应用生命周期的测试应用。"""
    test_app = create_app(test_settings)
    async with test_app.router.lifespan_context(test_app):
        yield test_app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    """提供不打开真实网络端口的异步 ASGI 测试客户端。"""
    transport = httpx.ASGITransport(
        app=app,
        raise_app_exceptions=False,
    )
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as test_client:
        yield test_client
