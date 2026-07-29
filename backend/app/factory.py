"""FastAPI 应用工厂。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import Settings, get_settings
from app.core.exceptions import (
    DEFAULT_ERROR_RESPONSES,
    register_exception_handlers,
)
from app.core.lifespan import create_lifespan
from app.core.logging import configure_logging
from app.db.session import DatabaseManager
from app.integrations.maxkb.factory import create_maxkb_adapter

OPENAPI_TAGS = [
    {
        "name": "系统",
        "description": "服务运行状态及基础信息。",
    }
]


def create_app(settings: Settings | None = None) -> FastAPI:
    """创建并配置 FastAPI 应用。"""
    app_settings = settings or get_settings()
    configure_logging(app_settings.log_level)

    # 每个应用实例创建独立的数据库资源管理器。这里只构造异步引擎和
    # 会话工厂，不会尝试连接 PostgreSQL，也不会执行建表操作。
    database_manager = DatabaseManager(str(app_settings.database_url))
    # 模式选择只发生在应用工厂。Mock 模式不创建 HTTP 客户端；HTTP 模式
    # 只构造客户端资源，启动阶段不会向真实 MaxKB 发出请求。
    maxkb_adapter = create_maxkb_adapter(app_settings)

    app = FastAPI(
        title=app_settings.app_name,
        version="0.1.0",
        description="基于大语言模型的课程思政案例库业务后端。",
        debug=app_settings.app_debug,
        openapi_tags=OPENAPI_TAGS,
        responses=DEFAULT_ERROR_RESPONSES,
        lifespan=create_lifespan(database_manager, maxkb_adapter),
    )
    app.state.settings = app_settings
    # 请求级会话依赖从 app.state 获取当前应用的资源，避免使用难以替换的
    # 模块级全局引擎，并为后续测试覆盖数据库依赖保留清晰入口。
    app.state.database = database_manager
    # 后续 MaxKB 业务依赖统一从 app.state 取得抽象适配器，前端、路由和
    # 业务服务都不能直接持有 API Key 或自行创建 HTTPX 客户端。
    app.state.maxkb_adapter = maxkb_adapter

    register_exception_handlers(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(app_settings.cors_origins),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(
        api_v1_router,
        prefix=app_settings.api_v1_prefix,
    )

    return app
