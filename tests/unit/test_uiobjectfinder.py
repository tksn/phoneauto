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
    mocks.device.assert_called_with(description='Gmail')


def test_find_contains_textContains(mocks):
    finder = create_finder(mocks.device)
    x, y = 150, 1280
    result = finder.find_object_contains(
        (x, y), False, textContains='mai', enabled=True)
    mocks.device.assert_called_with(description='Gmail')


def test_find_contains_textStartsWith(mocks):
    finder = create_finder(mocks.device)
    x, y = 150, 1280
    result = finder.find_object_contains(
        (x, y), False, textStartsWith='Gmai', enabled=True)
    mocks.device.assert_called_with(description='Gmail')


def test_find_contains_textMatches(mocks):
    finder = create_finder(mocks.device)
    x, y = 150, 1280
    result = finder.find_object_contains(
        (x, y), False, textMatches='.+ail$', enabled=True)
    mocks.device.assert_called_with(description='Gmail')


def test_find_contains_index(mocks):
    finder = create_finder(mocks.device)
    x, y = 700, 1300
    result = finder.find_object_contains(
        (x, y), False, index=5, enabled=True)
    mocks.device.assert_called_with(description='Camera')


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
    mocks.device.assert_called_with(description='Google App')


def test_find_contains_by_description(mocks):
    finder = create_finder(mocks.device)
    x, y = 500, 900
    result = finder.find_object_contains(
        (x, y), False, description='Google App')
    mocks.device.assert_called_with(description='Google App')


def test_find_contains_by_resourceId(mocks):
    finder = create_finder(mocks.device)
    x, y = 500, 900
    rid = 'com.google.android.googlequicksearchbox:id/search_widget_voice_hint'
    result = finder.find_object_contains((x, y), False, resourceId=rid)
    mocks.device.assert_called_with(resourceId=rid)


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


# class _Object(object): pass
#
#
# def test_find_element_outside_rect(mocks):
#     elem = _Object()
#     elem.info = uia_element_info(visibleBounds=bounds(0, 0, 10, 10))
#     mocks.device.return_value = [ elem ]
#     d = uiautomator_device.UiautomatorDevice()
#     with pytest.raises(uiobjectfinder.UiObjectNotFound):
#         d.find_element_contains((11, 11))


# DUMP_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
# <hierarchy rotation="0">
#   <node index="0" text="" resource-id=""
#     class="android.widget.FrameLayout" package="com.sec.android.app.launcher"
#     content-desc="" checkable="false" checked="false" clickable="false"
#     enabled="true" focusable="false" focused="false" scrollable="false"
#     long-clickable="false" password="false" selected="false"
#     bounds="[0,0][64,32]">
#   </node>
#   <node index="0" text="" resource-id=""
#     class="android.widget.FrameLayout" package="com.sec.android.app.launcher"
#     content-desc="" checkable="false" checked="false" clickable="false"
#     enabled="true" focusable="false" focused="false" scrollable="false"
#     long-clickable="false" password="false" selected="false"
#     bounds="[0,32][64,64]">
#   </node>
# </hierarchy>
# """
#
#
# def test_update_view_hierarchy_dump(mocks):
#     mocks.device.dump.return_value = DUMP_XML
#     elem0 = _Object()
#     elem0.info = uia_element_info(text='abc')
#     elem1 = _Object()
#     elem1.info = uia_element_info(text='def')
#     mocks.device.return_value = [elem0, elem1]
#     d = uiautomator_device.UiautomatorDevice()
#     d.update_view_hierarchy_dump()
#     uielem = d.find_element_contains(
#         (32, 48),
#         ignore_distant_element=False,
#         className='android.widget.FrameLayout')
#     assert uielem.info['text'] == 'def'
#     assert uielem._index == 1