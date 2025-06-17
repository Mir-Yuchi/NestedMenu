import pytest
from django.db import connection
from django.template import Context, Template
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext

from menus.models import MenuItem


@pytest.mark.django_db
def test_draw_menu_single_query_and_structure():
    root = MenuItem.objects.create(
        menu_name="main", title="Root", url="/root/", order=0
    )
    child = MenuItem.objects.create(
        menu_name="main", title="Child", url="/child/", parent=root, order=0
    )
    grandchild = MenuItem.objects.create(
        menu_name="main", title="Grandchild", url="/grandchild/", parent=child, order=0
    )

    rf = RequestFactory()
    request = rf.get("/child/")

    template = Template("{% load menus %}{% draw_menu 'main' %}")
    context = Context({"request": request})

    rendered = template.render(context)
    assert 'class="active open"' in rendered or 'class="open active"' in rendered

    with CaptureQueriesContext(connection) as ctx:
        _ = template.render(context)
    assert len(ctx) <= 2, f"Expected at most 2 queries, but got {len(ctx)}"

    assert '<li class="open"><a href="/root/">' in rendered

    assert '<a href="/child/">Child</a>' in rendered
