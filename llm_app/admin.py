from django.contrib import admin

from .models import PropertySummary


@admin.register(PropertySummary)
class PropertySummaryAdmin(admin.ModelAdmin):
    list_display = ("id", "summary", "property_id", "create_date", "update_date")
    list_display_links = ["id", "summary", "property_id"]
    list_filter = ["create_date", "update_date"]
    search_fields = ["id", "property_id", "create_date"]
