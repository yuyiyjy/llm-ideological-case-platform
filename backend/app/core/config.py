"""应用配置加载与校验。"""

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import (
    AnyHttpUrl,
    Field,
    PostgresDsn,
    SecretStr,
    TypeAdapter,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"

AppEnvironment = Literal["development", "testing", "production"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
CorsOrigins = Annotated[tuple[str, ...], NoDecode]

_HTTP_URL_ADAPTER = TypeAdapter(AnyHttpUrl)


class Settings(BaseSettings):
    """集中管理并校验应用环境变量。"""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        frozen=True,
        case_sensitive=False,
        hide_input_in_errors=True,
    )

    app_name: str = Field(min_length=1)
    app_env: AppEnvironment
    app_host: str = Field(min_length=1)
    app_port: int = Field(ge=1, le=65535)
    app_debug: bool
    api_v1_prefix: str
    log_level: LogLevel

    database_url: PostgresDsn = Field(repr=False)

    cors_origins: CorsOrigins

    secret_key: SecretStr = Field(repr=False)
    access_token_expire_minutes: int = Field(gt=0)

    maxkb_base_url: AnyHttpUrl | None = None
    maxkb_api_key: SecretStr | None = Field(default=None, repr=False)
    maxkb_timeout_seconds: float = Field(gt=0)
    maxkb_mock_enabled: bool

    maxkb_qa_application_id: str | None = None
    maxkb_generation_application_id: str | None = None
    maxkb_evaluation_application_id: str | None = None

    @field_validator("app_name", "app_host")
    @classmethod
    def validate_non_empty_text(cls, value: str) -> str:
        """拒绝仅包含空白字符的文本配置。"""
        normalized = value.strip()
        if not normalized:
            raise ValueError("配置值不能为空")
        return normalized

    @field_validator("app_env", mode="before")
    @classmethod
    def normalize_app_environment(cls, value: object) -> object:
        """统一运行环境名称的大小写。"""
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: object) -> object:
        """统一日志级别的大小写。"""
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("api_v1_prefix")
    @classmethod
    def validate_api_v1_prefix(cls, value: str) -> str:
        """校验 API 前缀格式。"""
        normalized = value.strip()
        if not normalized.startswith("/"):
            raise ValueError("API_V1_PREFIX 必须以 / 开头")
        if normalized == "/" or normalized.endswith("/"):
            raise ValueError("API_V1_PREFIX 不能为 / 或以 / 结尾")
        return normalized

    @field_validator("database_url")
    @classmethod
    def validate_database_driver(cls, value: PostgresDsn) -> PostgresDsn:
        """限定业务数据库使用 PostgreSQL 异步驱动。"""
        if value.scheme != "postgresql+asyncpg":
            raise ValueError("DATABASE_URL 必须使用 postgresql+asyncpg 驱动")
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        """解析英文逗号分隔的跨域来源。"""
        if isinstance(value, str):
            origins = tuple(
                origin.strip() for origin in value.split(",") if origin.strip()
            )
            if not origins:
                raise ValueError("CORS_ORIGINS 至少需要一个来源")
            return origins
        return value

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, origins: tuple[str, ...]) -> tuple[str, ...]:
        """校验、规范化并去重跨域来源。"""
        normalized_origins: list[str] = []
        seen_origins: set[str] = set()

        for origin in origins:
            url = _HTTP_URL_ADAPTER.validate_python(origin)
            if (
                url.username is not None
                or url.password is not None
                or url.query is not None
                or url.fragment is not None
                or url.path not in {"", "/"}
            ):
                raise ValueError("CORS_ORIGINS 只能包含协议、主机和端口")

            normalized = str(url).rstrip("/")
            if normalized not in seen_origins:
                normalized_origins.append(normalized)
                seen_origins.add(normalized)

        if not normalized_origins:
            raise ValueError("CORS_ORIGINS 至少需要一个来源")
        return tuple(normalized_origins)

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: SecretStr) -> SecretStr:
        """拒绝弱密钥和模板占位值。"""
        secret = value.get_secret_value()
        if secret == "replace-with-a-random-secret":
            raise ValueError("SECRET_KEY 必须替换模板占位值")
        if len(secret) < 32:
            raise ValueError("SECRET_KEY 长度不能少于 32 个字符")
        return value

    @field_validator(
        "maxkb_qa_application_id",
        "maxkb_generation_application_id",
        "maxkb_evaluation_application_id",
        mode="before",
    )
    @classmethod
    def normalize_optional_application_id(cls, value: object) -> object:
        """将空白的 MaxKB 应用标识视为未配置。"""
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None
        return value

    @model_validator(mode="after")
    def validate_environment_combinations(self) -> Self:
        """校验跨字段的运行环境约束。"""
        if self.app_env == "production" and self.app_debug:
            raise ValueError("生产环境不能启用 APP_DEBUG")

        if not self.maxkb_mock_enabled:
            if self.maxkb_base_url is None:
                raise ValueError("真实 MaxKB 模式必须配置 MAXKB_BASE_URL")

            api_key = (
                self.maxkb_api_key.get_secret_value()
                if self.maxkb_api_key is not None
                else ""
            )
            if not api_key or api_key == "replace-with-your-maxkb-api-key":
                raise ValueError("真实 MaxKB 模式必须配置有效的 MAXKB_API_KEY")

        return self


@lru_cache
def get_settings() -> Settings:
    """加载并缓存应用配置。"""
    return Settings()
