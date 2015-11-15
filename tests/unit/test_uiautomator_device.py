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


def test_str_get_screenshot_as_file(mocks):
    d = uiautomator_device.UiautomatorDevice()
    fmt = d.str_get_screenshot_as_file('/path/to/file.png')
    txt = fmt.format(instance='d')
    assert txt == 'd.get_screenshot_as_file(\'/path/to/file.png\')'


def test_find_send_keys_to_non_element(mocks):
    mocks.device.return_value = []
    d = uiautomator_device.UiautomatorDevice()
    d.find_send_keys((0, 0), 'abcde')


def test_find_element_outside_rect(mocks):
    class _Object(object): pass
    elem = _Object()
    elem.info = uia_element_info(visibleBounds=bounds(0, 0, 10, 10))
    mocks.device.return_value = [ elem ]
    d = uiautomator_device.UiautomatorDevice()
    assert d.find_element_contains((11, 11)) is None

