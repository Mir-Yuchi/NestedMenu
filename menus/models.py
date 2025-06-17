from django.db import models
from django.urls import NoReverseMatch, reverse


class MenuItem(models.Model):
    """
    Represents an item in a menu, which can be a link to a page or another menu item.
    """

    menu_name = models.CharField(max_length=50, db_index=True)
    title = models.CharField(max_length=100)
    url = models.CharField(
        max_length=200,
        help_text="Named URL or explicit path (e.g., 'app:detail' or '/about/')",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = [("menu_name", "url", "parent")]

    def __str__(self):
        return f"{self.menu_name} - {self.title}"

    def get_ancestors(self):
        """
        Returns a list of all ancestor MenuItems, starting from the parent up to the root.
        """
        ancestors = []
        node = self.parent
        while node:
            ancestors.insert(0, node)
            node = node.parent
        return ancestors

    def get_children(self):
        """Return immediate children"""
        return self.children.all()

    def resolved_url(self):
        """
        Try to reverse() the stored string; if that fails, treat it as a literal URL.
        """
        try:
            return reverse(self.url)
        except (NoReverseMatch, ValueError):
            return self.url

    def save(self, *args, **kwargs):
        """
        Ensure that a MenuItem cannot be its own ancestor.
        """
        ancestors = self.get_ancestors()
        if self in ancestors:
            raise ValueError("A MenuItem cannot be its own ancestor.")
        super().save(*args, **kwargs)