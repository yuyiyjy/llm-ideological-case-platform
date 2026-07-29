"""根据应用配置创建 MaxKB 适配器。"""

from app.core.config import Settings
from app.integrations.maxkb.base import MaxKBAdapter
from app.integrations.maxkb.http import HttpMaxKBAdapter
from app.integrations.maxkb.mock import MockMaxKBAdapter


def create_maxkb_adapter(settings: Settings) -> MaxKBAdapter:
    """创建与当前运行模式匹配的 MaxKB 适配器。

    模式判断集中在此处，路由和业务服务不应自行读取
    ``MAXKB_MOCK_ENABLED``。这样切换 Mock/HTTP 实现时，调用方始终依赖
    同一个抽象接口，也不会在代码各处散落条件分支。
    """
    if settings.maxkb_mock_enabled:
        return MockMaxKBAdapter()

    # Settings 已负责真实模式的组合校验。这里保留显式检查，防止未来有
    # 调用方绕过标准配置加载流程构造不完整对象，并确保错误信息不含密钥。
    if settings.maxkb_base_url is None or settings.maxkb_api_key is None:
        raise RuntimeError("真实 MaxKB 模式缺少必要配置")

    return HttpMaxKBAdapter(
        base_url=str(settings.maxkb_base_url),
        api_key=settings.maxkb_api_key,
        timeout_seconds=settings.maxkb_timeout_seconds,
    )
