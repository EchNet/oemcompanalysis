from django.contrib import admin

from . import models


@admin.register(models.WebProxy)
class WebProxyAdmin(admin.ModelAdmin):
  list_display = (
      "ip",
      "created_at",
  )


@admin.register(models.SeedPage)
class SeedPageAdmin(admin.ModelAdmin):
  list_display = (
      "url",
      "type",
  )


@admin.register(models.WebsiteCrawl)
class WebsiteCrawlAdmin(admin.ModelAdmin):
  list_display = (
      "website",
      "created_at",
  )
