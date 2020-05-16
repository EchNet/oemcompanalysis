from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class UsernameOrEmailModelBackend(ModelBackend):
  def authenticate(self, request, username=None, password=None, **kwargs):
    User = get_user_model()
    if username is None:
      username = kwargs.get(User.USERNAME_FIELD)
    # `username` field does not restring using `@`, so technically email
    # can be as username and email, even with different users
    users = User._default_manager.filter(
        Q(**{User.USERNAME_FIELD: username}) | Q(email__iexact=username))
    # Check for any password match
    for user in users:
      if user.check_password(password):
        return user
    if not users:
      # Run the default password hasher once to reduce the timing
      # difference between an existing and a non-existing user (#20760).
      User().set_password(password)
