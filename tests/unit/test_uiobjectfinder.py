# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import pytest
from phoneauto.scriptgenerator import uiobjectfinder
from phoneauto.scriptgenerator import view_hierarchy_dump


DIRNAME = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'testdata')

DEVICE_INFO = {
    'displayHeight': 1920,
    'displayWidth': 1080
}


def read_xml(filename):
    filepath = os.path.join(DIRNAME, filename)
    with open(filepath) as f:
        return f.read()


def create_finder():
    xml = read_xml('dump_home.xml')
    hd = view_hierarchy_dump.ViewHierarchyDump(DEVICE_INFO, xml)
    return uiobjectfinder.UiObjectFinder(hd)


def test_find_contains_clickable():
    finder = create_finder()
    x, y = 150, 1280
    locator = finder.find_object_contains(
        (x, y), False, clickable=True, enabled=True)
    assert 'Gmail' in locator.filters.values()


def test_find_contains_textContains():
    finder = create_finder()
    x, y = 150, 1280
    locator = finder.find_object_contains(
        (x, y), False, textContains='mai', enabled=True)
    assert 'Gmail' in locator.filters.values()


def test_find_contains_textStartsWith():
    finder = create_finder()
    x, y = 150, 1280
    locator = finder.find_object_contains(
        (x, y), False, textStartsWith='Gmai', enabled=True)
    assert 'Gmail' in locator.filters.values()


def test_find_contains_textMatches():
    finder = create_finder()
    x, y = 150, 1280
    locator = finder.find_object_contains(
        (x, y), False, textMatches='.+ail$', enabled=True)
    assert 'Gmail' in locator.filters.values()


def test_find_contains_index():
    finder = create_finder()
    x, y = 700, 1300
    locator = finder.find_object_contains(
        (x, y), False, index=5, enabled=True)
    assert 'Camera' in locator.filters.values()


def test_find_contains_notimplemented():
    finder = create_finder()
    x, y = 700, 1300
    with pytest.raises(NotImplementedError):
        finder.find_object_contains(
            (x, y), False, nosuchkey=True, enabled=True)


CORRUPTED_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id=""
    class="android.widget.FrameLayout" package="com.sec.android.app.launcher"
    content-desc="" checkable="false" checked="false" clickable="false"
    enabled="true" focusable="false" focused="false" scrollable="false"
    long-clickable="false" password="false" selected="false"
    bounds="invalid bounds value">
  </node>
</hierarchy>
"""


def test_find_contains_invalidbounds():
    hd = view_hierarchy_dump.ViewHierarchyDump(DEVICE_INFO, CORRUPTED_XML)
    finder = uiobjectfinder.UiObjectFinder(hd)
    x, y = 700, 1300
    with pytest.raises(ValueError):
        finder.find_object_contains(
            (x, y), False, checkable=False, enabled=True)


def test_find_contains_by_className():
    finder = create_finder()
    x, y = 500, 900
    cname = 'android.appwidget.AppWidgetHostView'
    locator = finder.find_object_contains(
        (x, y), False, className=cname)
    assert 'Google App' in locator.filters.values()


def test_find_contains_by_description():
    finder = create_finder()
    x, y = 500, 900
    locator = finder.find_object_contains(
        (x, y), False, description='Google App')
    assert 'Google App' in locator.filters.values()


def test_find_contains_by_resourceId():
    finder = create_finder()
    x, y = 500, 900
    rid = 'com.google.android.googlequicksearchbox:id/search_widget_voice_hint'
    locator = finder.find_object_contains((x, y), False, resourceId=rid)
    assert locator.filters['resourceId'] == rid


NOUNIQUENODE_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id=""
    class="android.widget.FrameLayout" package="com.sec.android.app.launcher"
    content-desc="" checkable="false" checked="false" clickable="false"
    enabled="true" focusable="false" focused="false" scrollable="false"
    long-clickable="false" password="false" selected="false"
    bounds="[0,0][1080,1920]">
  </node>
  <node index="1" text="" resource-id=""
    class="android.widget.FrameLayout" package="com.sec.android.app.launcher"
    content-desc="" checkable="false" checked="false" clickable="false"
    enabled="true" focusable="false" focused="false" scrollable="false"
    long-clickable="false" password="false" selected="false"
    bounds="[0,0][1080,1920]">
  </node>
</hierarchy>
"""


def test_find_contains_has_non_unique():
    hd = view_hierarchy_dump.ViewHierarchyDump(DEVICE_INFO, NOUNIQUENODE_XML)
    finder = uiobjectfinder.UiObjectFinder(hd)
    x, y = 500, 900
    locator = finder.find_object_contains(
        (x, y), False, className='android.widget.FrameLayout')
    assert locator.index is not None

