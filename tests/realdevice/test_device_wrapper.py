# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import uiautomator
import pytest
from phoneauto.helpers.uiautomator_device_wrapper import DeviceWrapper

needsrealdevice = pytest.mark.skipif(
    not pytest.config.getvalue('use_real_device'),
    reason="--use_real_device is not specified")


@pytest.fixture(scope='module')
def device():
    device_inst = uiautomator.Device()
    return device_inst


@pytest.fixture
def wdev(device):
    device_wrap = DeviceWrapper(device)
    return device_wrap


@needsrealdevice
def test_selector_and_info_works(wdev):
    wdev.press.home()
    assert wdev(text='Gmail').info['text'] == 'Gmail'


_CLICK_X = 124
_CLICK_Y = 1274

@needsrealdevice
def test_click(wdev):
    wdev.press.home()
    wdev.click(_CLICK_X, _CLICK_Y)


@needsrealdevice
def test_long_click(wdev):
    wdev.press.home()
    wdev.long_click(_CLICK_X, _CLICK_Y)


_SWIPE_X0 = 910
_SWIPE_Y0 = 1564
_SWIPE_X1 = 125
_SWIPE_Y1 = 1564


@needsrealdevice
def test_swipe(wdev):
    wdev.press.home()
    wdev.swipe(_SWIPE_X0, _SWIPE_Y0, _SWIPE_X1, _SWIPE_Y1, steps=10)
    wdev.swipe(_SWIPE_X1, _SWIPE_Y1, _SWIPE_X0, _SWIPE_Y0, steps=10)


@needsrealdevice
def test_swipe_points(wdev):
    points = [
        (_SWIPE_X0, _SWIPE_Y0),
        (_SWIPE_X1, _SWIPE_Y1),
        (_SWIPE_X0, _SWIPE_Y0)
    ]
    wdev.press.home()
    wdev.swipePoints(points, steps=20)


_DRAG_X0 = _SWIPE_X0
_DRAG_Y0 = _SWIPE_Y0
_DRAG_X1 = _DRAG_X0
_DRAG_Y1 = 1400


@needsrealdevice
def test_drag(wdev):
    wdev.press.home()
    wdev.drag(_DRAG_X0, _DRAG_Y0, _DRAG_X1, _DRAG_Y1, steps=10)


@needsrealdevice
def test_freeze_rotation(wdev):
    wdev.freeze_rotation(freeze=True)
    wdev.freeze_rotation(freeze=False)


@needsrealdevice
def test_orientation_set(wdev):
    wdev.orientation = 'right'
    wdev.freeze_rotation(freeze=False)


@needsrealdevice
def test_orientation_get(wdev):
    assert wdev.orientation == 'natural'


@needsrealdevice
def test_last_traversed_text(wdev):
    text = wdev.last_traversed_text
    assert text is None or isinstance(text, type(''))


@needsrealdevice
def test_open_notification(wdev):
    wdev.open.notification()


@needsrealdevice
def test_open_quick_settings(wdev):
    wdev.open.quick_settings()


@needsrealdevice
def test_canset_handler(wdev):
    def dummy_handler(device):
        pass
    wdev.handlers.on(dummy_handler)
    wdev.handlers.off(dummy_handler)


@needsrealdevice
def test_canset_watcher(wdev):
    wdev.watcher('DUMMY').when(text='NOSUCHTEXT').press.back.home()
    wdev.watcher('DUMMY').remove()


@needsrealdevice
def test_canaccess_watchers(wdev):
    assert wdev.watchers.triggered or True
    wdev.watchers.reset()


@needsrealdevice
def test_press_keycode(wdev):
    wdev.press(4)
    wdev.press(4, None)


@needsrealdevice
def test_wakeup(wdev):
    wdev.wakeup()


@needsrealdevice
def test_sleep(wdev):
    wdev.sleep()
    wdev.wakeup()


@needsrealdevice
def test_screen_off_and_on(wdev):
    wdev.screen.off()
    wdev.screen.on()


@needsrealdevice
def test_screen_off_and_on_as_arg(wdev):
    wdev.screen('off')
    wdev.screen('on')


@needsrealdevice
def test_screen_state_eq(wdev):
    wdev.screen.off()
    assert wdev.screen == 'off'
    assert wdev.screen != 'on'
    wdev.screen.on()
    assert wdev.screen == 'on'
    assert wdev.screen != 'off'


@needsrealdevice
def test_wait_idle(wdev):
    wdev.wait.idle(timeout=1000)
    wdev.wait.idle()


@needsrealdevice
def test_wait_update(wdev):
    wdev.wait.update(timeout=100)
    wdev.wait.update()
