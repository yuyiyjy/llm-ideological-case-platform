"""数据库资源管理和请求会话依赖测试。"""

from types import TracebackType

import pytest
from fastapi import FastAPI, Request

from app.core.config import Settings
from app.db.session import DatabaseManager, get_db_session

pytestmark = pytest.mark.asyncio


class FakeSession:
    """记录回滚行为的最小异步会话替身。"""

    def __init__(self) -> None:
        self.rolled_back = False

    async def rollback(self) -> None:
        """记录依赖是否在异常路径执行回滚。"""
        self.rolled_back = True


class FakeSessionContext:
    """模拟 async_sessionmaker 返回的异步上下文管理器。"""

    def __init__(self, session: FakeSession) -> None:
        self.session = session
        self.exited = False

    async def __aenter__(self) -> FakeSession:
        return self.session

    async def __aexit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.exited = True


class FakeSessionFactory:
    """每次调用都返回同一个可观察的会话上下文。"""

    def __init__(self, context: FakeSessionContext) -> None:
        self.context = context

    def __call__(self) -> FakeSessionContext:
        return self.context


async def test_database_manager_creation_does_not_connect(
    test_settings: Settings,
) -> None:
    """创建数据库管理器时不应访问合成地址上的 PostgreSQL。"""
    manager = DatabaseManager(str(test_settings.database_url))

    assert manager.engine.url.host == "127.0.0.1"
    assert manager.engine.url.port == 1

    await manager.dispose()


async def test_session_dependency_rolls_back_on_error(
    test_settings: Settings,
) -> None:
    """请求处理抛出异常时，会话依赖应回滚并退出上下文。"""
    manager = DatabaseManager(str(test_settings.database_url))
    fake_session = FakeSession()
    fake_context = FakeSessionContext(fake_session)
    setattr(manager, "session_factory", FakeSessionFactory(fake_context))

    app = FastAPI()
    app.state.database = manager
    request = Request({"type": "http", "app": app})
    dependency = get_db_session(request)

    yielded_session = await anext(dependency)
    assert yielded_session is fake_session

    with pytest.raises(RuntimeError, match="synthetic-session-error"):
        await dependency.athrow(RuntimeError("synthetic-session-error"))

    assert fake_session.rolled_back is True
    assert fake_context.exited is True
    await manager.dispose()


async def test_session_dependency_does_not_auto_commit(
    test_settings: Settings,
) -> None:
    """正常结束请求时，基础依赖不应擅自提交或回滚事务。"""
    manager = DatabaseManager(str(test_settings.database_url))
    fake_session = FakeSession()
    fake_context = FakeSessionContext(fake_session)
    setattr(manager, "session_factory", FakeSessionFactory(fake_context))

    app = FastAPI()
    app.state.database = manager
    dependency = get_db_session(Request({"type": "http", "app": app}))

    assert await anext(dependency) is fake_session
    await dependency.aclose()

    assert fake_session.rolled_back is False
    assert fake_context.exited is True
    await manager.dispose()


async def test_session_dependency_rejects_missing_manager() -> None:
    """应用接线错误时，不应静默创建或回退到全局数据库连接。"""
    app = FastAPI()
    dependency = get_db_session(Request({"type": "http", "app": app}))

    with pytest.raises(RuntimeError, match="数据库资源尚未初始化"):
        await anext(dependency)
