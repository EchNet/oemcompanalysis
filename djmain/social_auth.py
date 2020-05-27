import logging

logger = logging.getLogger(__name__)


def trace(backend, user, response, *args, **kwargs):
  logger.info(
      f"social auth pipeline backend={backend.name} user={user.get_full_name()} response={response}"
  )
