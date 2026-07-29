"""本地 PostgreSQL 与 Alembic 状态集成测试。"""

from pathlib import Path

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text

from app.core.config import Settings
from app.db.session import DatabaseManager

BACKEND_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_postgresql_connection_and_alembic_revision() -> None:
    """显式启用时，验证真实数据库可连接且版本位于迁移头。"""
    settings = Settings()
    manager = DatabaseManager(str(settings.database_url))

    try:
        async with manager.engine.connect() as connection:
            probe = await connection.scalar(text("SELECT 1"))
            database_revisions = (
                await connection.execute(
                    text("SELECT version_num FROM alembic_version")
                )
            ).scalars().all()
    except Exception as exception:
        raise AssertionError(
            f"本地 PostgreSQL 集成验证失败：{type(exception).__name__}"
        ) from None
    finally:
        await manager.dispose()

    alembic_config = Config(str(BACKEND_ROOT / "alembic.ini"))
    script = ScriptDirectory.from_config(alembic_config)

    assert probe == 1
    assert set(database_revisions) == set(script.get_heads())
