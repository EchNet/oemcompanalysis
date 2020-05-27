from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.views.generic import TemplateView

import djmain.views as views

urlpatterns = [
    path("", views.HomeView.as_view(template_name="home.html"), name="home"),
    path("login/", TemplateView.as_view(template_name="login.html"), name="login"),
    path("login-error/",
         TemplateView.as_view(template_name="login-error.html"),
         name="login-error"),
    path("", include("social_django.urls")),
    path("admin/", admin.site.urls),
]

if settings.SERVE_MEDIA:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
