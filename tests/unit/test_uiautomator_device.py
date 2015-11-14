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
    uielem = d.find_clickable_element_contains((0, 0))
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


def test_find_click_on_non_element(mocks):
    mocks.device.return_value = []
    d = uiautomator_device.UiautomatorDevice()
    d.find_click((0, 0))
    mocks.device.click.assert_called_with(0, 0)


def test_find_long_click_on_non_element(mocks):
    mocks.device.return_value = []
    d = uiautomator_device.UiautomatorDevice()
    d.find_long_click((0, 0))
    mocks.device.long_click.assert_called_with(0, 0)


def test_find_swipe_with_non_element(mocks):
    mocks.device.return_value = []
    d = uiautomator_device.UiautomatorDevice()
    d.find_swipe((0, 0), (1, 1))
    mocks.device.swipe.assert_called_with(0, 0, 1, 1)


def test_find_swipe_with_element(mocks):
    elem = set_mock_device_return(mocks)
    d = uiautomator_device.UiautomatorDevice()
    d.find_swipe((0, 0), (0, 1))
    elem.swipe.assert_called_with('down')
    d.find_swipe((1, 0), (0, 0))
    elem.swipe.assert_called_with('left')
    d.find_swipe((0, 1), (0, 0))
    elem.swipe.assert_called_with('up')


def test_find_drag_with_start_element(mocks):
    elem = set_mock_device_return(mocks, visibleBounds=bounds(0, 0, 1, 1))
    d = uiautomator_device.UiautomatorDevice()
    d.find_drag((0, 0), (2, 2), find_target_element=True)
    elem.drag.to.assert_called_with(2, 2)



