from .auth import router as auth_router
from .users import router as users_router
from .projects import router as projects_router
from .matching import router as matching_router
from .notifications import router as notifications_router

__all__ = [
    "auth_router",
    "users_router",
    "projects_router",
    "matching_router",
    "notifications_router"
]
