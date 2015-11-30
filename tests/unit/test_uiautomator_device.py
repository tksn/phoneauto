# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pytest
from mock import MagicMock
from phoneauto.scriptgenerator import uiautomator_device
from phoneauto.scriptgenerator import uiobjectfinder
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


def test_find_send_keys_to_non_element(mocks):
    mocks.device.return_value = []
    d = uiautomator_device.UiautomatorDevice()
    d.find_send_keys((0, 0), 'abcde')


def test_get_info_on_non_element(mocks):
    mocks.device.return_value = []
    d = uiautomator_device.UiautomatorDevice()
    with pytest.raises(uiobjectfinder.UiObjectNotFound):
        d.get_info((0, 0))

