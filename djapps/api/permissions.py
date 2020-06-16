import logging

from rest_framework import permissions

logger = logging.getLogger(__name__)


class IsActiveUser(permissions.IsAuthenticated):
  def has_permission(self, request, view):
    is_authenticated = super().has_permission(request, view)
    logger.info(f"{request.user} is_auth={is_authenticated} is_active={request.user.is_active}")
    return is_authenticated and request.user.is_active
