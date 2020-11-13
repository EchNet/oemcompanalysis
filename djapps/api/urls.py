from django.conf.urls import url

import api.views as api_views

urlpatterns = [
    url(r'^manufacturer/?$', api_views.ManufacturerView.as_view()),
    url(r'^manufacturer/(?P<manufacturer_id>[0-9]+)/website/?$',
        api_views.ManufacturerWebsiteView.as_view()),
    url(r'^website/?$', api_views.WebsiteView.as_view()),
    url(r'^part/?$', api_views.PartView.as_view(), name="parts"),
    url(r'^price/?$', api_views.PriceView.as_view(), name="prices"),
    url(r'^cost/?$', api_views.CostView.as_view(), name="costs"),
]
