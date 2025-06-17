import pytest
from django.core.cache import cache
from django.db import connection
from django.template import Context, Template
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext

from menus.models import MenuItem


@pytest.mark.django_db
def test_draw_menu_request_cache_avoids_duplicate_queries():
    root = MenuItem.objects.create(
        menu_name="cache_menu", title="Root", url="/root/", order=0
    )
    child1 = MenuItem.objects.create(
        menu_name="cache_menu", title="Child1", url="/child1/", parent=root, order=0
    )
    child2 = MenuItem.objects.create(
        menu_name="cache_menu", title="Child2", url="/child2/", parent=root, order=1
    )

    rf = RequestFactory()
    request = rf.get("/child1/")
    template = Template(
        "{% load menus %}{% draw_menu 'cache_menu' %}{% draw_menu 'cache_menu' %}"
    )
    context = Context({"request": request})

    with CaptureQueriesContext(connection) as ctx:
        rendered = template.render(context)
    assert len(ctx) == 1, f"Expected 1 query for two draws, got {len(ctx)}"
    assert "Child1" in rendered and "Child2" in rendered


@pytest.mark.django_db
def test_draw_menu_site_cache_prevents_db_after_initial():
    cache.clear()

    root = MenuItem.objects.create(
        menu_name="site_menu", title="Root", url="/root/", order=0
    )
    MenuItem.objects.create(
        menu_name="site_menu", title="Item", url="/item/", parent=root, order=0
    )

    rf = RequestFactory()
    request = rf.get("/item/")
    template = Template("{% load menus %}{% draw_menu 'site_menu' %}")
    context = Context({"request": request})

    with CaptureQueriesContext(connection) as ctx1:
        _ = template.render(context)
    assert len(ctx1) == 1, f"Expected 1 query on initial render, got {len(ctx1)}"

    new_context = Context({"request": rf.get("/item/")})
    with CaptureQueriesContext(connection) as ctx2:
        _ = template.render(new_context)
    assert len(ctx2) == 0, f"Expected 0 queries on cached render, got {len(ctx2)}"
