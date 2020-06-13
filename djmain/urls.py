from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.urls import include, path
from django.views.generic import TemplateView

import djmain.forms as forms
import djmain.views as views

urlpatterns = [
    path("", views.HomeView.as_view(template_name="home.html"), name="home"),
    path("login/",
         auth_views.LoginView.as_view(template_name="login.html",
                                      authentication_form=forms.LoginForm,
                                      redirect_authenticated_user=True),
         name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("login-error/",
         TemplateView.as_view(template_name="login-error.html"),
         name="login-error"),
    path("register/", TemplateView.as_view(template_name="register.html"), name="register"),
    path("", include("social_django.urls")),
    path("admin/", admin.site.urls),
    path("api/1.0/", include("api.urls")),
]

if settings.SERVE_MEDIA:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
