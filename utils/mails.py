import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.db.models.query import QuerySet
from django.template.loader import render_to_string

import html2text

from .context_processors import settings_constants

logger = logging.getLogger(__name__)


def format_user_email(user):
  """
    Formats the user email as "Full Name <email@example.com>"

    Params:
        user: a User instance, or a string email address.

    """
  User = get_user_model()
  if not isinstance(user, User):
    return user
  formatted_email = "{email}".format(email=user.email)
  if user.first_name and user.last_name:
    formatted_email = ("{user.first_name} {user.last_name} "
                       "<{from_email}>").format(
                           user=user, from_email=formatted_email)
  return formatted_email


def send_html_mail(template_name,
                   context=None,
                   from_email=settings.DEFAULT_FROM_EMAIL,
                   to=None,
                   bcc=None,
                   cc=None,
                   reply_to=None,
                   headers=None):
  """Sends email rendered via templates.

    If `from_email` is a list of user instances or a single one,
    it will build a custom formatting for them using the stored data
    "Full Name <email@example.com>".

    This allows us to keep base email templates and just edit the parts of
    the body or subject.

    Also we're using a single template for all related notifications.
    Both email subject/body are saved in the same template.

    Params:
        template_name: Relative template path. See 'notifications/base.html' for the
            block names to use.
        context: Dictionary containing values to plug into the template
        from_email: String, containing email address on behalf of whom this
                    email is sent. Provided by default in settings.
        to: a list of email addresses or User instances, for the TO field.
        bcc: a list of email addresses, for the BCC field
        cc: a list of email addresses, for the CC field
        headers: Eg. {"Reply-To": "another@example.com"}
    """
  # Set default values
  to = to or []
  cc = cc or []
  bcc = bcc or []
  context = context or {}
  context.update(**settings_constants())
  headers = headers or {}

  # Format email address with names if User instances
  if isinstance(to, (list, QuerySet)):
    to = [format_user_email(user) for user in to]
  else:
    to = [format_user_email(to)]

  if reply_to:
    headers["Reply-To"] = reply_to

  # Rendering subject
  context["render_subject"] = True
  subject = render_to_string(template_name, context)
  subject = subject.replace("\r", " ").replace("\n", " ").strip()
  subject = "".join(subject.splitlines())

  # Rendering body(both html + text version)
  context["render_subject"] = False
  html_version = render_to_string(template_name, context).strip()
  text_version = html2text.html2text(html_version)
  message = EmailMultiAlternatives(
      subject=subject,
      body=text_version,
      from_email=from_email,
      to=to,
      cc=cc,
      bcc=bcc,
      headers=headers)
  message.attach_alternative(html_version, "text/html")

  # Adds template_name as category for sendgrid,
  # so we can group stats by category
  message.categories = [template_name]

  return message.send()
