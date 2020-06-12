import logging

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class LoginForm(forms.Form):
  email = forms.EmailField(widget=forms.TextInput(attrs={
      "class": "form-control",
      "placeholder": _("email"),
      "type": "email",
  }))
  password = forms.CharField(widget=forms.PasswordInput(
      attrs={
          "class": "form-control",
          "placeholder": _("password"),
          "type": "password",
      }))
  error_messages = {
      "inactive": _("Your account is inactive."),
      "invalid": _("The email address or password you have entered is invalid."),
  }

  def __init__(self, *args, **kwargs):
    self.request = kwargs.pop("request", None)
    super().__init__(*args, **kwargs)

  def clean_email(self):
    return self.cleaned_data.get("email").lower()

  def clean(self):
    email = self.cleaned_data.get("email")
    password = self.cleaned_data.get("password")

    if email and password:
      User = get_user_model()
      try:
        user = User.objects.get(email=email)
        user = authenticate(username=user.username, password=password)
      except User.DoesNotExist:
        user = None
      if not user:
        raise forms.ValidationError(self.error_messages["invalid"], code="invalid")

      logger.info(
          f"authenticated user={user} is_active={user.is_active} is_authenticated={user.is_authenticated}"
      )

      if not user.is_active:
        raise forms.ValidationError(
            self.error_messages["inactive"],
            code="inactive",
        )

      self.user = user

    return self.cleaned_data

  def get_user(self):
    # Required by Django auth.
    return self.user
