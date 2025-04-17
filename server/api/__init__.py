from server.api.routes.auth import (
    auth_router,
    users_router,
    projects_router,
    matching_router,
    notifications_router
)

__all__ = [
    "auth_router",
    "users_router",
    "projects_router",
    "matching_router",
    "notifications_router"
]
