"""MaxKB 适配层公开入口。"""

from app.integrations.maxkb.base import MaxKBAdapter, MaxKBAdapterMode
from app.integrations.maxkb.factory import create_maxkb_adapter
from app.integrations.maxkb.http import HttpMaxKBAdapter
from app.integrations.maxkb.mock import MockMaxKBAdapter

__all__ = [
    "HttpMaxKBAdapter",
    "MaxKBAdapter",
    "MaxKBAdapterMode",
    "MockMaxKBAdapter",
    "create_maxkb_adapter",
]
