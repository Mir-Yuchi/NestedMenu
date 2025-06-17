from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from menus.models import MenuItem


@receiver([post_save, post_delete], sender=MenuItem)
def clear_menu_cache(sender, instance, **kwargs):
    """
    Invalidate the cached menu tree whenever a MenuItem is created,
    updated, or deleted.
    """
    cache_key = f"menu_tree:{instance.menu_name}"
    cache.delete(cache_key)
