from django.conf.urls import url

import api.views as api_views

urlpatterns = [
    url(r'^manufacturer/?$', api_views.ManufacturerView.as_view()),
    url(r'^website/?$', api_views.WebsiteView.as_view()),
    url(r'^parts/?$', api_views.PartsView.as_view()),
    url(r'^prices/?$', api_views.PricesView.as_view()),
    url(r'^costs/?$', api_views.CostsView.as_view()),
    url(r'^progress/(?P<progress_id>[0-9]+)/?$', api_views.ProgressView.as_view()),
    url(r'^parts/per_cost_price_range/?$', api_views.PartsPerCostPriceRangeView.as_view()),
    url(r'^part/(?P<part_number>[^/]+)/pricing_on_date',
        api_views.PartPricingOnDateView.as_view()),
    url(r'^website_exclusions/?$', api_views.WebsiteExclusionView.as_view()),
]
