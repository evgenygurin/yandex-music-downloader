"""API routers."""

from .analysis import router as analysis_router
from .sets import router as sets_router
from .tracks import router as tracks_router
from .yandex import router as yandex_router

__all__ = ["analysis_router", "sets_router", "tracks_router", "yandex_router"]
