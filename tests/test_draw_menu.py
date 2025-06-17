import re

import pytest
from django.db import connection, transaction
from django.template import Context, Template
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext

from menus.models import MenuItem


@pytest.fixture
def menu_items():
    with transaction.atomic():
        MenuItem.objects.filter(menu_name="test_menu").delete()
        root = MenuItem.objects.create(
            menu_name="test_menu", title="Root", url="/root/", order=0
        )
        child = MenuItem.objects.create(
            menu_name="test_menu", title="Child", url="/child/", parent=root, order=0
        )
        grandchild = MenuItem.objects.create(
            menu_name="test_menu",
            title="Grandchild",
            url="/grandchild/",
            parent=child,
            order=0,
        )
    return {"root": root, "child": child, "grandchild": grandchild}


@pytest.mark.django_db
def test_draw_menu_single_query_with_interactivity(menu_items):
    from django.core.cache import cache

    cache.clear()
    rf = RequestFactory()
    request = rf.get("/child/")
    template = Template("{% load menus %}{% draw_menu 'test_menu' %}")
    context = Context({"request": request})
    with CaptureQueriesContext(connection) as ctx:
        rendered = template.render(context)
    assert len(ctx) == 1, f"Expected exactly 1 query, but got {len(ctx)}"
    new_context = Context({"request": request})
    with CaptureQueriesContext(connection) as ctx2:
        rendered_again = template.render(new_context)
    assert len(ctx2) == 0, "Expected cached result (0 queries) on second render"
