from django.conf.urls import url
from rest_framework_jwt.views import refresh_jwt_token

import api.views as api_views

urlpatterns = [
    url(r'^auth-jwt/?$', api_views.ObtainJwtTokenView.as_view()),
    url(r'^auth-jwt-refresh/?$', refresh_jwt_token),
    #
    url(r'^thing/?$', api_views.ListThingsView.as_view()),
]
