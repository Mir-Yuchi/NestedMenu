from collections import defaultdict
from django import template
from django.core.cache import cache
from django.utils.html import escape
from django.utils.safestring import mark_safe
from menus.models import MenuItem

register = template.Library()


@register.simple_tag(takes_context=True)
def draw_menu(context, menu_name):
    """
    Render a tree-structured <ul> menu for `menu_name`, expanding:
      1. All ancestors of the active item
      2. The immediate children of the active item
    Performs exactly one DB query.
    """
    request = context["request"]
    current_path = request.path.rstrip('/') or '/'

    render_cache = context.render_context.setdefault("menus_draw_cache", {})
    if menu_name in render_cache:
        id_to_item, resolved, children = render_cache[menu_name]
    else:
        cached = cache.get(f"menu_tree:{menu_name}")
        if cached:
            id_to_item, resolved, children = cached
        else:
            items = list(
                MenuItem.objects.filter(menu_name=menu_name)
                .select_related("parent")
                .order_by("order")
            )
            id_to_item = {item.id: item for item in items}
            resolved = {item.id: item.resolved_url().rstrip('/') or '/' for item in items}
            children = defaultdict(list)
            for item in items:
                children[item.parent_id].append(item)
            cache.set(f"menu_tree:{menu_name}", (id_to_item, resolved, children), 3600)
        render_cache[menu_name] = (id_to_item, resolved, children)

    active, to_expand = None, set()
    for item_id, url in resolved.items():
        if url == current_path:
            active = id_to_item[item_id]
            break
    if active:
        node = active
        while node:
            to_expand.add(node.id)
            node = id_to_item.get(node.parent_id)
        for child in children.get(active.id, []):
            to_expand.add(child.id)

    def render_branch(parent_id, level=0):
        html = [f'<ul class="space-y-2 level-{level} ml-{level * 4}">']
        for node in children.get(parent_id, []):
            css = []
            if active and node.id == active.id:
                css.append("active")
            if node.id in to_expand:
                css.append("open")
            class_attr = f' class="{' '.join(css)}"' if css else ""
            has_children = node.id in children and children[node.id]
            toggle_class = 'menu-toggle' if has_children else ''
            html.append(f'<li{class_attr}>')
            html.append(
                f'<a href="{escape(resolved[node.id])}" class="{toggle_class} block px-4 py-2 rounded-lg text-gray-800 font-medium">'
                f'{escape(node.title)}</a>'
            )
            if node.id in to_expand and has_children:
                html.append(render_branch(node.id, level + 1))
            else:
                html.append(f'<ul class="hidden level-{level + 1} ml-{(level + 1) * 4}"></ul>')
            html.append("</li>")
        html.append("</ul>")
        return "".join(html)

    return mark_safe(f'<nav aria-label="Main Menu">{render_branch(None)}</nav>')
