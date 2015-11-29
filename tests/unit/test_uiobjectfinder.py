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


def create_finder(device):
    finder = uiobjectfinder.UiObjectFinder(device)
    xml = read_xml('dump_home.xml')
    hd = view_hierarchy_dump.ViewHierarchyDump(DEVICE_INFO, xml)
    finder.set_hierarchy_dump(hd)
    return finder


def test_find_contains_clickable(mocks):
    finder = create_finder(mocks.device)
    x, y = 150, 1280
    result = finder.find_object_contains(
        (x, y), False, clickable=True, enabled=True)
    assert result['object'].info['text'] == 'Gmail'


def test_find_contains_textContains(mocks):
    finder = create_finder(mocks.device)
    x, y = 150, 1280
    result = finder.find_object_contains(
        (x, y), False, textContains='mai', enabled=True)
    assert result['object'].info['text'] == 'Gmail'


def test_find_contains_textStartsWith(mocks):
    finder = create_finder(mocks.device)
    x, y = 150, 1280
    result = finder.find_object_contains(
        (x, y), False, textStartsWith='Gmai', enabled=True)
    assert result['object'].info['text'] == 'Gmail'


def test_find_contains_textMatches(mocks):
    finder = create_finder(mocks.device)
    x, y = 150, 1280
    result = finder.find_object_contains(
        (x, y), False, textMatches='.+ail$', enabled=True)
    assert result['object'].info['text'] == 'Gmail'


def test_find_contains_index(mocks):
    finder = create_finder(mocks.device)
    x, y = 700, 1300
    result = finder.find_object_contains(
        (x, y), False, index=5, enabled=True)
    assert result['object'].info['text'] == 'Camera'


def test_find_contains_notimplemented(mocks):
    finder = create_finder(mocks.device)
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


def test_find_contains_invalidbounds(mocks):
    finder = uiobjectfinder.UiObjectFinder(mocks.device)
    hd = view_hierarchy_dump.ViewHierarchyDump(DEVICE_INFO, CORRUPTED_XML)
    finder.set_hierarchy_dump(hd)
    x, y = 700, 1300
    with pytest.raises(ValueError):
        finder.find_object_contains(
            (x, y), False, checkable=False, enabled=True)


def test_find_contains_by_className(mocks):
    finder = create_finder(mocks.device)
    x, y = 500, 900
    cname = 'android.appwidget.AppWidgetHostView'
    result = finder.find_object_contains(
        (x, y), False, className=cname)
    assert result['object'].info['contentDescription'] == 'Google App'
    assert result['object'].info['className'] == cname
    assert result['object'].info['checkable'] == False
    assert result['object'].info['enabled'] == True
    assert result['object'].info['bounds'] == {
        'left': 8, 'top': 780, 'right': 1073, 'bottom': 1110
    }


def test_find_contains_by_description(mocks):
    finder = create_finder(mocks.device)
    x, y = 500, 900
    result = finder.find_object_contains(
        (x, y), False, description='Google App')
    assert result['object'].info['contentDescription'] == 'Google App'


def test_find_contains_by_resourceId(mocks):
    finder = create_finder(mocks.device)
    x, y = 500, 900
    rid = 'com.google.android.googlequicksearchbox:id/search_widget_voice_hint'
    result = finder.find_object_contains((x, y), False, resourceId=rid)
    assert result['object'].info['text'] == 'Say "Ok Google"'
    assert result['object'].info['resourceName'] == rid


OUTSCR_BOUNDS_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id=""
    class="android.widget.FrameLayout" package="com.sec.android.app.launcher"
    content-desc="" checkable="false" checked="false" clickable="false"
    enabled="true" focusable="false" focused="false" scrollable="false"
    long-clickable="false" password="false" selected="false"
    bounds="[-10,-10][1090,1930]">
  </node>
</hierarchy>
"""


def test_find_contains_outscr_bounds(mocks):
    finder = uiobjectfinder.UiObjectFinder(mocks.device)
    hd = view_hierarchy_dump.ViewHierarchyDump(DEVICE_INFO, OUTSCR_BOUNDS_XML)
    finder.set_hierarchy_dump(hd)
    x, y = 500, 900
    result = finder.find_object_contains((x, y), False, focused=False)
    assert result['object'].info['visibleBounds'] == {
        'left': 0, 'top': 0, 'right': 1080, 'bottom': 1920
    }


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


def test_find_contains_has_non_unique(mocks):
    finder = uiobjectfinder.UiObjectFinder(mocks.device)
    hd = view_hierarchy_dump.ViewHierarchyDump(DEVICE_INFO, NOUNIQUENODE_XML)
    finder.set_hierarchy_dump(hd)
    x, y = 500, 900
    result = finder.find_object_contains(
        (x, y), False, className='android.widget.FrameLayout')
    assert 'index' in result
