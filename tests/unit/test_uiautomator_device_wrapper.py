# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from mock import Mock, call
import pytest
from phoneauto.scriptgenerator import uiautomator_device
from tests.uiautomator_mock import uia_element_info, bounds
from phoneauto.helpers.uiautomator_device_wrapper import DeviceWrapper


@pytest.fixture
def wdev(mocks):
    device_wrap = DeviceWrapper(mocks.device)
    return device_wrap


def test_selector(mocks, wdev):
    wdev(text='abc', className='def')
    mocks.device.assert_called_with(text='abc', className='def')


def test_click(mocks, wdev):
    wdev.click(123, 456)
    mocks.device.click.assert_called_with(123, 456)
    assert mocks.device.wait.idle.called
    assert mocks.device.wait.update.called


def test_press_home(mocks, wdev):
    wdev.press.home()
    assert mocks.device.press.home.called
    assert mocks.device.wait.idle.called
    assert mocks.device.wait.update.called


def test_press_with_keycode(mocks, wdev):
    wdev.press(4, 2)
    mocks.device.press.assert_called_with(4, 2)
    assert mocks.device.wait.idle.called
    assert mocks.device.wait.update.called


def test_screen_eq(mocks, wdev):
    wdev.screen == 'on'
    assert mocks.device.screen.__eq__.called


def test_screen_ne(mocks, wdev):
    wdev.screen != 'on'
    assert mocks.device.screen.__ne__.called


def test_wait_idle(mocks, wdev):
    wdev.wait.idle()
    assert mocks.device.wait.idle.called
    assert not mocks.device.wait.update.called


def test_set_orientation(mocks, wdev):
    wdev.orientation = 'left'
    assert mocks.device.wait.idle.called
    assert mocks.device.wait.update.called
    assert mocks.device.orientation == 'left'


def test_get_orientation(mocks, wdev):
    mocks.device.orientation = 'right'
    assert wdev.orientation == 'right'
