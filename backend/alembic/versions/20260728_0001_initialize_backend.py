"""建立后端迁移基线，不创建业务表。

版本号：20260728_0001
上一版本：无
创建时间：2026-07-28
"""

from collections.abc import Sequence

# 这是 4B03 的空迁移，只用于建立后续迁移链起点。4B04 设计并确认
# 核心业务模型后，再通过新的迁移文件创建案例、用户和审核等业务表。
revision: str = "20260728_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """升级到初始迁移基线，不执行建表或数据写入。"""
    pass


def downgrade() -> None:
    """从初始迁移基线回退，不执行删表或数据删除。"""
    pass
