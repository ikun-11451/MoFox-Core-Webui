"""
HTTP路由组件模块
"""

from .auth_router import WebUIAuthRouter
from .config_router import WebUIConfigRouter
from .plugin_router import WebUIPluginRouter
from .stats_router import WebUIStatsRouter

__all__ = [
    "WebUIAuthRouter",
    "WebUIConfigRouter",
    "WebUIPluginRouter",
    "WebUIStatsRouter",
]
