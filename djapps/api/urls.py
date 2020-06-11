from django.conf.urls import url

import api.views as api_views

urlpatterns = [
    url(r'^thing/?$', api_views.ListThingsView.as_view()),
]
