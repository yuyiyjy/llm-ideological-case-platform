"""${message}

版本号：${up_revision}
上一版本：${down_revision | comma,n}
创建时间：${create_date}
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# Alembic 用于识别迁移顺序、分支和依赖关系的版本标识。
revision: str = ${repr(up_revision)}
down_revision: str | Sequence[str] | None = ${repr(down_revision)}
branch_labels: str | Sequence[str] | None = ${repr(branch_labels)}
depends_on: str | Sequence[str] | None = ${repr(depends_on)}


def upgrade() -> None:
    """将数据库结构升级到当前版本。"""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """将数据库结构回退到上一版本。"""
    ${downgrades if downgrades else "pass"}
