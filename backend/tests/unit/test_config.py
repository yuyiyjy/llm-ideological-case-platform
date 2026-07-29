"""应用配置模型测试。"""

from typing import Any

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_synthetic_settings_are_isolated_from_local_env(
    test_settings: Settings,
) -> None:
    """普通测试必须使用合成值，而不是开发者本地真实配置。"""
    assert test_settings.app_name == "test-backend"
    assert test_settings.app_env == "testing"
    assert test_settings.maxkb_mock_enabled is True
    database_hosts = test_settings.database_url.hosts()
    assert database_hosts[0]["host"] == "127.0.0.1"
    assert database_hosts[0]["port"] == 1


def test_database_url_requires_asyncpg_driver(
    settings_values: dict[str, Any],
) -> None:
    """业务数据库地址必须显式选择 SQLAlchemy asyncpg 方言。"""
    values = dict(settings_values)
    values["database_url"] = (
        "postgresql://synthetic_user:synthetic_password"
        "@127.0.0.1:1/synthetic_database"
    )

    with pytest.raises(ValidationError, match="postgresql\\+asyncpg"):
        Settings.model_validate(values)


def test_real_maxkb_mode_requires_api_key(
    settings_values: dict[str, Any],
) -> None:
    """切换 HTTP 模式时必须同时提供有效的服务端 API Key。"""
    values = dict(settings_values)
    values.update(
        maxkb_mock_enabled=False,
        maxkb_base_url="http://127.0.0.1:1",
        maxkb_api_key=None,
    )

    with pytest.raises(ValidationError, match="MAXKB_API_KEY"):
        Settings.model_validate(values)


def test_production_environment_rejects_debug(
    settings_values: dict[str, Any],
) -> None:
    """生产环境不得启用应用调试模式。"""
    values = dict(settings_values)
    values.update(app_env="production", app_debug=True)

    with pytest.raises(ValidationError, match="生产环境不能启用 APP_DEBUG"):
        Settings.model_validate(values)


def test_cors_origins_are_normalized_and_deduplicated(
    settings_values: dict[str, Any],
) -> None:
    """跨域来源应去除末尾斜杠和重复项。"""
    values = dict(settings_values)
    values["cors_origins"] = (
        "http://localhost:5173/,"
        "http://localhost:5173,"
        "http://127.0.0.1:5173"
    )

    settings = Settings.model_validate(values)

    assert settings.cors_origins == (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    )
