# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from phoneauto.scriptgenerator import uiautomator_device


def test_device_name_is_uiautomator_device_serial(mocks):
    mocks.device.server.adb.device_serial.return_value = 'abcde'
    d = uiautomator_device.UiautomatorDevice()
    assert d.device_name == 'abcde'


