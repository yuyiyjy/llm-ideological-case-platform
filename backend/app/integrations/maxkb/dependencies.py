"""FastAPI 路由使用的 MaxKB 适配器依赖。"""

from fastapi import Request

from app.integrations.maxkb.base import MaxKBAdapter


def get_maxkb_adapter(request: Request) -> MaxKBAdapter:
    """返回当前 FastAPI 应用持有的 MaxKB 适配器。

    依赖从 ``app.state`` 读取应用工厂创建的实例，确保同一应用共享同一个
    HTTP 连接池。若生命周期接线错误，则立即失败，不在请求处理中临时创建
    新客户端，也不会退回到可能意外访问真实 MaxKB 的全局实例。
    """
    adapter = getattr(request.app.state, "maxkb_adapter", None)
    if not isinstance(adapter, MaxKBAdapter):
        raise RuntimeError("MaxKB 适配器尚未初始化")
    return adapter
