# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from mock import MagicMock
from phoneauto.scriptgenerator import uiautomator_device
from tests.uiautomator_mock import uia_element_info, bounds


def test_device_name_is_uiautomator_device_serial(mocks):
    mocks.device.server.adb.device_serial.return_value = 'abcde'
    d = uiautomator_device.UiautomatorDevice()
    assert d.device_name == 'abcde'


def set_mock_device_return(mocks, **element_creation_args):
    elem = MagicMock()
    elem.info = uia_element_info(**element_creation_args)
    mocks.device.return_value = [elem]
    return elem


def exec_find():
    d = uiautomator_device.UiautomatorDevice()
    uielem = d.find_element_contains((0, 0), clickable=True, enabled=True)
    assert uielem is not None
    codefrag = str(uielem).format(instance='d')
    return  codefrag


def test_find_can_create_content_desc_codefragment(mocks):
    set_mock_device_return(mocks, contentDescription='abcde')
    assert exec_find() == 'd(description=\'abcde\')'


def test_find_can_create_index_codefragment(mocks):
    set_mock_device_return(mocks)
    s = exec_find()
    assert 'd(' in s
    assert ')[0]' in s


def test_find_can_create_text_codefragment(mocks):
    set_mock_device_return(mocks, text='abcde')
    assert exec_find() == 'd(text=\'abcde\')'


def test_find_send_keys_to_non_element(mocks):
    mocks.device.return_value = []
    d = uiautomator_device.UiautomatorDevice()
    d.find_send_keys((0, 0), 'abcde')


class _Object(object): pass


def test_find_element_outside_rect(mocks):
    elem = _Object()
    elem.info = uia_element_info(visibleBounds=bounds(0, 0, 10, 10))
    mocks.device.return_value = [ elem ]
    d = uiautomator_device.UiautomatorDevice()
    assert d.find_element_contains((11, 11)) is None


def test_get_info_on_non_element(mocks):
    mocks.device.return_value = []
    d = uiautomator_device.UiautomatorDevice()
    assert d.get_info((0, 0)) is None


DUMP_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id=""
    class="android.widget.FrameLayout" package="com.sec.android.app.launcher"
    content-desc="" checkable="false" checked="false" clickable="false"
    enabled="true" focusable="false" focused="false" scrollable="false"
    long-clickable="false" password="false" selected="false"
    bounds="[0,0][1080,100]">
  </node>
  <node index="0" text="" resource-id=""
    class="android.widget.FrameLayout" package="com.sec.android.app.launcher"
    content-desc="" checkable="false" checked="false" clickable="false"
    enabled="true" focusable="false" focused="false" scrollable="false"
    long-clickable="false" password="false" selected="false"
    bounds="[0,100][1080,1920]">
  </node>
</hierarchy>
"""


def test_update_view_hierarchy_dump(mocks):
    mocks.device.dump.return_value = DUMP_XML
    elem0 = _Object()
    elem0.info = uia_element_info(text='abc')
    elem1 = _Object()
    elem1.info = uia_element_info(text='def')
    mocks.device.return_value = [elem0, elem1]
    d = uiautomator_device.UiautomatorDevice()
    d.update_view_hierarchy_dump()
    uielem = d.find_element_contains(
        (500, 500),
        ignore_distant_element=False,
        className='android.widget.FrameLayout')
    assert uielem.info['text'] == 'def'
    assert uielem._index == 1
