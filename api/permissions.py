from rest_framework.permissions import IsAuthenticated
from rest_framework_api_key.permissions import HasAPIKey

DEFAULT_PERMISSIONS = IsAuthenticated | HasAPIKey
