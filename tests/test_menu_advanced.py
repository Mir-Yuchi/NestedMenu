import re

import pytest
from django.db import IntegrityError, connection, transaction
from django.template import Context, Template
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext

from menus.models import MenuItem


@pytest.fixture
def menu_items():
    """Create a menu structure for tests with a unique menu_name."""
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
def test_draw_menu_empty_menu():
    rf = RequestFactory()
    request = rf.get("/")
    template = Template("{% load menus %}{% draw_menu 'empty' %}")
    context = Context({"request": request})
    rendered = template.render(context)
    assert (
        '<nav aria-label="Main Menu"><ul class="space-y-2 level-0 ml-0"></ul></nav>'
        in rendered
    )
    assert "menu-toggle" not in rendered


@pytest.mark.django_db
def test_draw_menu_interactive_classes(menu_items):
    rf = RequestFactory()
    request = rf.get("/child/")
    template = Template("{% load menus %}{% draw_menu 'test_menu' %}")
    context = Context({"request": request})
    rendered = template.render(context)
    assert '<nav aria-label="Main Menu">' in rendered
    assert "menu-toggle" in rendered
    assert "level-0" in rendered
    assert "level-1" in rendered
    assert "level-2" in rendered
    active_pattern = r'<li class="[^"]*active[^"]*">.*<a href="/child"'
    assert re.search(
        active_pattern, rendered, re.DOTALL
    ), "Active item 'Child' not found with class 'active'"


@pytest.mark.django_db
def test_cyclic_reference_prevention():
    with transaction.atomic():
        MenuItem.objects.filter(menu_name="main").delete()
        root = MenuItem.objects.create(
            menu_name="main", title="Root", url="/root/", order=0
        )
        child = MenuItem.objects.create(
            menu_name="main", title="Child", url="/child/", parent=root, order=0
        )
        with pytest.raises(ValueError):
            root.parent = child
            root.save()


@pytest.mark.django_db
def test_draw_menu_home_page():
    with transaction.atomic():
        MenuItem.objects.filter(menu_name="main").delete()
        MenuItem.objects.create(menu_name="main", title="Home", url="/", order=0)
        MenuItem.objects.create(menu_name="main", title="About", url="/about/", order=1)
    rf = RequestFactory()
    request = rf.get("/")
    template = Template("{% load menus %}{% draw_menu 'main' %}")
    context = Context({"request": request})
    rendered = template.render(context)
    active_pattern = r'<li class="[^"]*active[^"]*">.*<a href="/"'
    assert re.search(
        active_pattern, rendered, re.DOTALL
    ), "Active item 'Home' not found with class 'active'"
    assert "Home" in rendered and "About" in rendered
    assert '<nav aria-label="Main Menu">' in rendered
