from django.contrib import admin

from .models import MenuItem


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """
    Admin interface for managing MenuItem objects.
    """

    list_display = ("title", "menu_name", "parent", "order")
    list_filter = ("menu_name",)
    search_fields = ("title", "url")
    ordering = ("menu_name", "parent__id", "order")
    list_editable = ("order",)
    raw_id_fields = ("parent",)
