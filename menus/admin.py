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

    def get_queryset(self, request):
        """
        Override to use select_related for the parent field to optimize queries.
        """
        return super().get_queryset(request).select_related("parent")

    def get_parent_display(self, obj):
        """
        Display the path of parent MenuItems for the current object.
        """
        if obj.parent:
            ancestors = obj.get_ancestors()
            return " → ".join([ancestor.title for ancestor in ancestors])
        return "-"

    get_parent_display.short_description = "Parent Path"
